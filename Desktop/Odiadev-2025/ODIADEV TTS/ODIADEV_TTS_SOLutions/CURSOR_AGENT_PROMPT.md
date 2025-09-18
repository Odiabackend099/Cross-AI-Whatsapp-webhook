# Cursor "Agent" Master Prompt

> **Role**: Senior backend/audio engineer.
> **Objective**: Keep NaijaTTS MVP production-ready.
> **Guardrails**: No external calls during synth; pin Torch wheels; fail closed on empty text; log request-id, device, synth-ms.
> **Tasks**:
>
> 1. Ensure `bootstrap_windows.ps1` and `bootstrap_linux.sh` run clean.
> 2. Keep `/speak` and `/batch_speak` contracts stable.
> 3. Maintain `utils/textnorm.py` (Pidgin punctuation, collapse spaces).
> 4. Enforce limiter −1 dBFS and tail trim ≤ 200 ms.
> 5. Keep latency p95 ≤ 1.5 s for 10–15 words on 24 GB GPU.
>    **DoD**: bench + MOS sheets updated; tests pass; README deploy steps verified.

## Quick Commands for Cursor

### Start Development Server
```bash
# Windows
.\.venv\Scripts\python.exe backend\app.py

# Linux
python backend/app.py
```

### Run Tests
```bash
# Single synthesis test
python scripts/test_synthesize_xtts.py --text "How you dey? Today go sweet well-well!"

# Full benchmark
python scripts/bench.py --num-tests 10

# Health check
curl http://localhost:7860/health
```

### Reset Environment
```bash
# Windows
rmdir /s /q .venv
.\bootstrap_windows.ps1

# Linux
rm -rf .venv
./bootstrap_linux.sh
```

## Key Files to Monitor

- `backend/app.py` - Main FastAPI service
- `engines/xtts_engine.py` - XTTS wrapper with audio processing
- `utils/textnorm.py` - Text normalization for Nigerian English/Pidgin
- `scripts/bench.py` - Performance benchmarking
- `adaqua_tts.py` - Python SDK client

## Performance Targets

- **Latency**: p50 ≤ 600ms, p95 ≤ 1.5s (10-15 words, 24GB GPU)
- **Quality**: MOS ≥ 4.0 (Nigerian English/Pidgin)
- **Audio**: No clipping, ≤ 200ms trailing silence
- **Text**: Proper Pidgin punctuation and prosody

## Common Issues & Fixes

1. **CUDA not available** → Check `nvidia-smi`, install CUDA 12.1
2. **No voice files** → Ensure WAVs in `data/voices/lexi/`
3. **High latency** → Use GPU, reduce text length
4. **Audio clipping** → Check limiter in `xtts_engine.py`
5. **Poor prosody** → Verify text normalization in `textnorm.py`

