# NaijaTTS MVP — Product Requirements Document (PRD)

**Doc version:** v1.0  
**Owner:** ODIADEV / Adaqua AI  
**Editors:** Engineering (Backend/ML), PM, QA  
**Last updated:** 2025-09-18

---

## 1) Summary
NaijaTTS is a **production‑grade Text‑to‑Speech (TTS) microservice** specialized for **Nigerian English + Pidgin** (and extendable to Igbo, Hausa, Yorùbá via additional voices).  
It exposes a small **HTTP API** (FastAPI) backed by **Coqui XTTS v2** for **zero‑shot voice cloning** from short WAV references. Deploys locally (Windows/Linux) and on **RunPod** (GPU).

**Core value:** low‑latency, natural Nigerian accent, simple API.

---

## 2) Goals & Non‑Goals

### Goals (v0.1 MVP)
- `/health`, `/speak`, `/batch_speak` endpoints (JSON in, WAV out).
- **Zero‑shot voice cloning** using one or more 5–30s reference WAVs.
- **Text normalization** tuned for Nigerian English/Pidgin prosody.
- **Audio QA controls**: peak limiting to ~−1 dBFS, trailing silence ≤ 200ms.
- **GPU if available, CPU fallback** without code changes.
- **Deterministic build**: pinned deps, reproducible Docker, env‑driven config.
- **Simple observability**: request logs with request‑id, timing, device info.

### Non‑Goals (for v0.1)
- Training new models from scratch (fine‑tune may come later).
- Mobile on‑device inference.
- Full product UX; we are backend‑first API.
- Speech‑to‑Text (STT) / diarization / alignment.

---

## 3) Target Users & Use Cases
- **Developers** adding realistic Nigerian voices to assistants, IVR, or learning apps.
- **Internal QA** for content preview and audio generation pipelines.
- **Ops** for batch generation (up to 50 items per call) before publishing.

---

## 4) Requirements

### Functional
- **/health**: returns {{ ok, engine, device, voice_dir_exists }}.
- **/speak (POST)**: body `{{ text, language?, speaker_files? }}` → `audio/wav`.
- **/batch_speak (POST)**: body `{{ items:[{{text, language?, speaker_files?}}], zip? }}` → ZIP (default) or NDJSON.
- **Text normalization** before synthesis.
- **Voice sources**: from `speaker_files` OR fallback to `NAIJA_VOICE_DIR/*.wav`.

### Non‑Functional (SLO targets, MVP)
- **Latency (single 10–15 word sentence)**: p50 ≤ **600ms**, p95 ≤ **1.5s** on a 24GB GPU.
- **Audio**: peak ≤ **−1 dBFS**; trailing silence ≤ **200ms**; sample rate **24 kHz**.
- **Availability**: 99.5% monthly (best‑effort, single region).
- **Security**: no secrets in code; env‑only; minimal logs (no PII).
- **Compliance**: NDPR basics—data minimization, opt‑in for voice samples; delete on request.
- **Cost control**: cache model weights; reuse GPU across requests; allow CPU fallback for dev.

### Nigeria‑Aware Requirements
- Default logs in **Africa/Lagos** time.
- Client examples include **retry with jitter** and **tight timeouts** (mobile data reality).
- Currency/NGN formatting in any future billing/ops dashboards.

---

## 5) API Spec (v0.1)

### POST `/speak`
**Request (JSON)**
```json
{
  "text": "How you dey? Today go sweet well-well!",
  "language": "en",
  "speaker_files": ["C:/Users/OD~IA/Music/LEXI VOICE/wav/1.wav"]
}
```

**Response**
- `200 audio/wav` — synthesized audio
- `400` — validation error (missing text or speaker)
- `500` — synthesis failure (engine/model)

**Limits**
- `text` ≤ 500 chars  
- `speaker_files` optional; fallback to `NAIJA_VOICE_DIR`

### POST `/batch_speak`
**Request (JSON)**
```json
{
  "items": [
    {"text": "Hello Kaduna!", "language": "en"},
    {"text": "Wetin dey sup?"}
  ],
  "zip": true
}
```

**Response**
- `200 application/zip` with `N.wav` files (or NDJSON if `zip=false`)
- `400/500` as above

---

## 6) System Design (MVP)
- **FastAPI** app → `XTTSEngine` wrapper (Coqui XTTS v2).
- Caching via standard model cache dirs (`XDG_CACHE_HOME` or library defaults).
- Audio post‑processing: soft limit to −1 dBFS; trim trailing silence.
- Optional GPU (`cuda`) auto‑detected; otherwise CPU.
- Config via env:
  - `NAIJA_VOICE_DIR` — directory of WAVs (default `data/voices/lexi`)
  - `NAIJA_DEFAULT_SPEAKER` — optional single path
  - `PORT` (default 8000)

---

## 7) Dependencies
- Python 3.10+
- `fastapi`, `uvicorn`, `TTS` (XTTS v2), `torch` (CPU or CUDA build), `numpy`, `soundfile`, `pydantic`.
- **CUDA wheels** must match the CUDA version on RunPod.

---

## 8) Constraints & Risks
- Model downloads are large; first run can be slow. Mitigate with cached volume.
- Voice cloning quality depends on **clean** reference audio (avoid reverb/noise).
- Heavy traffic can exhaust GPU VRAM → consider **queue** or **rate limiting** later.

---

## 9) Acceptance Criteria (v0.1)
- ✅ `uvicorn backend.app:app` starts without error on CPU and GPU.
- ✅ `/health` returns `ok:true` and correct device string.
- ✅ `/speak` returns playable WAV; peaks ≤ −1 dBFS; silence ≤ 200ms.
- ✅ Batch call with 10 items returns ZIP with 10 WAVs.
- ✅ Works on Windows (PowerShell env) and Linux; builds on RunPod.

---

## 10) Rollout
- **Phase 1**: Local dev (CPU), sample voice directory.
- **Phase 2**: RunPod single GPU (H100/L40/4090 class), private endpoint.
- **Phase 3**: Secure API gateway + basic rate limit, audit logs.
- **Phase 4**: Add Hausa/Igbo/Yorùbá voices; evaluate light fine‑tune if needed.

---

## 11) Open Questions
- Which **language hints** yield best accent with XTTS? (Keep `language="en"` for Nigerian English/Pidgin for now.)
- Batch ZIP vs NDJSON default for downstream? (MVP: ZIP default.)
- Future: API keys & billing?

---

## 12) References
- Internal: Truth‑First Accuracy Protocol; Debug Commander; Code Review Charter.
- Public: Coqui TTS (XTTS v2) docs; FastAPI docs.

