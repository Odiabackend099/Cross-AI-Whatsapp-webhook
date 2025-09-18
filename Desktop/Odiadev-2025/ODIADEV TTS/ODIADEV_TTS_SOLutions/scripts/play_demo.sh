#!/bin/bash
# Linux script to play the demo audio
set -euo pipefail

FILE="${1:-outputs/demo_multilang_30s.wav}"

echo "🎵 Playing Naija TTS Demo..."

if [ ! -f "$FILE" ]; then
    echo "Error: File not found: $FILE"
    exit 1
fi

if command -v ffplay >/dev/null 2>&1; then
    ffplay -nodisp -autoexit "$FILE"
    echo "✅ Playback completed!"
elif command -v aplay >/dev/null 2>&1; then
    aplay "$FILE"
    echo "✅ Playback completed!"
else
    echo "Error: No audio player found. Please install ffmpeg (ffplay) or alsa-utils (aplay)"
    exit 1
fi
