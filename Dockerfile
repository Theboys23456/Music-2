FROM python:3.11-slim

# Install FFmpeg & Opus
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg opus-tools && \
    rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Copy code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# a tiny silent mp3 for placeholder
RUN ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 1 -q:a 9 -acodec libmp3lame silence.mp3

CMD ["python", "main.py"]
