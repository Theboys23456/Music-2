from dataclasses import dataclass
from typing import List, Optional
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped, InputStream

@dataclass
class Track:
    title: str
    url: str  # direct audio or YouTube/HTTP URL to be piped by ffmpeg
    webpage_url: str

class Player:
    def __init__(self, chat_id: int, pytg: PyTgCalls):
        self.chat_id = chat_id
        self.pytg = pytg
        self.queue: List[Track] = []
        self.is_playing: bool = False

    async def join(self, message):
        # ensure voice chat exists and bot has rights
        await self.pytg.join_group_call(
            self.chat_id,
            InputStream(
                AudioPiped("silence.mp3")  # placeholder; will be replaced when playing
            ),
            stream_type=None
        )
        # Immediately pause since we just joined with a placeholder
        await self.pytg.pause_stream(self.chat_id)
        self.is_playing = False

    async def leave(self):
        await self.pytg.leave_group_call(self.chat_id)
        self.queue.clear()
        self.is_playing = False

    def enqueue(self, track: Track) -> int:
        self.queue.append(track)
        return len(self.queue)

    async def start_next(self):
        if not self.queue:
            self.is_playing = False
            try:
                await self.pytg.pause_stream(self.chat_id)
            except:
                pass
            return

        track = self.queue.pop(0)
        self.is_playing = True
        await self.pytg.change_stream(
            self.chat_id,
            InputStream(AudioPiped(track.url))
        )

    async def skip(self):
        await self.start_next()

    async def pause(self):
        await self.pytg.pause_stream(self.chat_id)
        self.is_playing = False

    async def resume(self):
        await self.pytg.resume_stream(self.chat_id)
        self.is_playing = True

    async def stop(self):
        self.queue.clear()
        await self.pytg.pause_stream(self.chat_id)
        self.is_playing = False

    def format_queue(self) -> str:
        if not self.is_playing and not self.queue:
            return "📭 Queue empty."
        lines = []
        if self.is_playing:
            lines.append("🎶 **Now Playing** (see VC)")
        if self.queue:
            lines.append("\n📝 **Up Next:**")
            for i, t in enumerate(self.queue, 1):
                lines.append(f"{i}. [{t.title}]({t.webpage_url})")
        return "\n".join(lines)
