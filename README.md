# Telegram VC Music Bot

Streams music into Telegram **group voice chats**.

## Features
- /join, /leave
- /play <song name or YouTube URL>
- /queue, /skip, /pause, /resume, /stop

## Requirements
- Telegram API_ID & API_HASH (https://my.telegram.org)
- Bot token (@BotFather)
- FFmpeg (Dockerfile installs it)

## Deploy (Render - Docker)
1. Fork/Upload this repo to GitHub.
2. On Render: **New + → Web Service → Build from repo**.
3. Choose **Docker** runtime (render.yaml included).
4. Add ENV:
   - API_ID, API_HASH, BOT_TOKEN, OWNER_ID
5. Deploy.

## Usage
- Add the bot to a group, promote to **admin**.
- Start the group’s **voice chat**.
- In chat:
  - `/join`
  - `/play tum hi ho`
  - `/play https://www.youtube.com/watch?v=...`
  - `/queue`, `/skip`, `/pause`, `/resume`, `/stop`, `/leave`
