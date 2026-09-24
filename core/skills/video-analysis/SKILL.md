---
name: video-analysis
description: Download a video, transcribe it and break down its hook, structure, pacing and on-screen text. Use for any competitor, creator or ad video that needs to be understood or compared.
---

# Video analysis

## Steps
1. Download: `yt-dlp -o 'raw/<task>/%(id)s.%(ext)s' URL` (X, TikTok, YouTube, Instagram).
2. Audio: `ffmpeg -i VIDEO -ar 16000 -ac 1 raw/<task>/ID.wav`.
3. Transcribe: `whisper-cli -m models/ggml-tiny.en.bin -f raw/<task>/ID.wav -oj -of raw/<task>/ID`.
4. Frames: `ffmpeg -i VIDEO -vf "fps=1/5,scale=640:-1,tile=4x3" raw/<task>/ID-sheet%d.jpg` for contact sheets; look at them to read on-screen text and shots.
5. Check length and streams with `ffprobe` before trusting a download.
6. Write one record per video.

## Record per video
URL, creator, posted date, stats at capture, length, hook (first 3 seconds: words, visual, on-screen text), structure beat by beat, where the product appears, the call to action, pacing (cuts per 10 seconds), audio, and which of the twelve structures in `research/video-analysis-595/report.md` §8 it matches.

## Don'ts
- Don't analyze from the transcript alone. Why: most short-form hooks are on-screen text and visuals that the audio never says.
- Don't trust the tiny Whisper model for names and numbers. Why: it mishears them; check against the frames.
- Don't keep videos in the repo. Why: size and rights; `raw/` is gitignored.
