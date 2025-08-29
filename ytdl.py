import asyncio
from dataclasses import dataclass
from typing import Optional

import yt_dlp

from player import Track

YDL_OPTS = {
    "format": "bestaudio/best",
    "quiet": True,
    "nocheckcertificate": True,
    "skip_download": True,
    "default_search": "ytsearch",
    "extract_flat": "in_playlist",
}

async def get_audio_source(query: str) -> Track:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _extract, query)

def _extract(query: str) -> Track:
    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        info = ydl.extract_info(query, download=False)
        if "entries" in info:
            info = info["entries"][0]
        # get direct URL for ffmpeg piping
        if "url" in info:
            direct_url = info["url"]
        else:
            # fallback
            fmts = info.get("formats") or []
            audio = next((f for f in fmts if f.get("acodec") != "none"), None)
            if not audio:
                raise RuntimeError("No audio format found")
            direct_url = audio["url"]

        title = info.get("title") or "Unknown Title"
        webpage_url = info.get("webpage_url") or query
        return Track(title=title, url=direct_url, webpage_url=webpage_url)
