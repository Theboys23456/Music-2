import os
from typing import Dict, List, Optional

from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from pytgcalls.types.input_stream import AudioPiped, InputStream
from pytgcalls.types.stream import StreamAudioEnded

from player import Player
from ytdl import get_audio_source

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))  # optional: for admin-only commands

app = Client("vc-music-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
pytg = PyTgCalls(app)

# chat_id -> Player
players: Dict[int, Player] = {}

def get_player(chat_id: int) -> Player:
    if chat_id not in players:
        players[chat_id] = Player(chat_id, pytg)
    return players[chat_id]

@app.on_message(filters.command(["start", "help"]))
async def start_handler(_, m: Message):
    await m.reply_text(
        "🎧 **VC Music Bot**\n\n"
        "**Commands**\n"
        "/join — join voice chat\n"
        "/play <query|url> — play/queue song\n"
        "/queue — show queue\n"
        "/skip — next track\n"
        "/pause — pause\n"
        "/resume — resume\n"
        "/stop — stop & clear queue\n"
        "/leave — leave voice chat\n\n"
        "Add me to a group, make me **admin**, start the group’s voice chat, then /join."
    )

@app.on_message(filters.command("join") & filters.group)
async def join_handler(_, m: Message):
    chat_id = m.chat.id
    player = get_player(chat_id)
    try:
        await player.join(m)
        await m.reply_text("✅ Joined voice chat.")
    except Exception as e:
        await m.reply_text(f"❌ Join failed: `{e}`")

@app.on_message(filters.command("leave") & filters.group)
async def leave_handler(_, m: Message):
    chat_id = m.chat.id
    player = get_player(chat_id)
    try:
        await player.leave()
        await m.reply_text("👋 Left voice chat.")
    except Exception as e:
        await m.reply_text(f"❌ Leave failed: `{e}`")

@app.on_message(filters.command("play") & filters.group)
async def play_handler(_, m: Message):
    chat_id = m.chat.id
    player = get_player(chat_id)
    args = m.text.split(None, 1)
    if len(args) == 1:
        return await m.reply_text("⚠️ Usage: `/play despacito` or `/play <YouTube URL>`", quote=True)
    query = args[1].strip()

    try:
        track = await get_audio_source(query)
        added = player.enqueue(track)
        if not player.is_playing:
            await player.start_next()
            await m.reply_text(f"▶️ Playing: **{track.title}**")
        else:
            await m.reply_text(f"➕ Queued: **{track.title}** (#{added})")
    except Exception as e:
        await m.reply_text(f"❌ Couldn’t add track: `{e}`")

@app.on_message(filters.command("queue") & filters.group)
async def queue_handler(_, m: Message):
    chat_id = m.chat.id
    player = get_player(chat_id)
    txt = player.format_queue()
    await m.reply_text(txt, disable_web_page_preview=True)

@app.on_message(filters.command("skip") & filters.group)
async def skip_handler(_, m: Message):
    chat_id = m.chat.id
    player = get_player(chat_id)
    try:
        await player.skip()
        await m.reply_text("⏭️ Skipped.")
    except Exception as e:
        await m.reply_text(f"❌ Skip failed: `{e}`")

@app.on_message(filters.command("pause") & filters.group)
async def pause_handler(_, m: Message):
    chat_id = m.chat.id
    player = get_player(chat_id)
    try:
        await player.pause()
        await m.reply_text("⏸️ Paused.")
    except Exception as e:
        await m.reply_text(f"❌ Pause failed: `{e}`")

@app.on_message(filters.command("resume") & filters.group)
async def resume_handler(_, m: Message):
    chat_id = m.chat.id
    player = get_player(chat_id)
    try:
        await player.resume()
        await m.reply_text("▶️ Resumed.")
    except Exception as e:
        await m.reply_text(f"❌ Resume failed: `{e}`")

@app.on_message(filters.command("stop") & filters.group)
async def stop_handler(_, m: Message):
    chat_id = m.chat.id
    player = get_player(chat_id)
    try:
        await player.stop()
        await m.reply_text("⏹️ Stopped & cleared queue.")
    except Exception as e:
        await m.reply_text(f"❌ Stop failed: `{e}`")

@pytg.on_stream_end()
async def on_stream_end(_, update: Update):
    if isinstance(update, StreamAudioEnded):
        chat_id = update.chat_id
        player = get_player(chat_id)
        await player.start_next()

async def main():
    await app.start()
    await pytg.start()
    print("✅ VC Music Bot is up.")
    await app.idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
