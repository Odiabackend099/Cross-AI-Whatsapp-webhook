#!/usr/bin/env bash
set -euo pipefail
echo "== ODIA TTS Linux bootstrap =="

# Python venv
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Try GPU wheels first; fall back to CPU if unavailable
if python3 -c "import torch,os; print('skip')" 2>/dev/null; then
  pip install --extra-index-url https://download.pytorch.org/whl/cu121 torch torchvision torchaudio || \
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
else
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
fi

pip install fastapi uvicorn[standard] TTS==0.22.0 soundfile numpy pydub

mkdir -p outputs

echo "Bootstrap complete. Test with:"
echo "source .venv/bin/activate && python3 scripts/test_synthesize_xtts.py --text 'How you dey? Today go sweet well-well.' --out outputs/sample.wav"
