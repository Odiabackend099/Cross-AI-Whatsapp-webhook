# TASK-MANAGEMENT — NaijaTTS v0.1

**Method:** lightweight Kanban + short sprints (1 week).  
**Branching:** trunk‑based; feature branches → PR → squash merge.  
**CI (later):** lint/test/build docker on push; optional preview deploy.

---

## 1) Workstreams & Owners
- **Backend API** — endpoints, validation, error envelopes.
- **Engine/Audio** — XTTS wrapper, normalization, QA limits.
- **Data/Voices** — curate clean WAV references; naming; storage.
- **DevOps/RunPod** — image, cache volumes, healthcheck, template.
- **SDK/Client** — tiny Python client + examples (retry/backoff).
- **QA/Bench** — latency & audio checks, CSV reports.
- **Docs** — PRD, success metrics, runbooks.

---

## 2) Backlog → Doing → Done (Checklists)

### A) Backend API
- [ ] `/health` returns ok, engine, device, voice_dir_exists
- [ ] `/speak` (POST) validates input; returns audio/wav
- [ ] `/batch_speak` (POST) supports up to 50 items; returns ZIP
- [ ] Error envelope with clear messages
- [ ] CORS on (for dev); configurable origins (prod)

### B) Engine/Audio
- [ ] Auto‑detect device `cuda` vs `cpu`
- [ ] Soft limit to −1 dBFS (no clipping)
- [ ] Trim trailing silence ≤ 200ms
- [ ] Language hint param; default `"en"`
- [ ] Unit test for post‑processing

### C) Data/Voices
- [ ] Store under `data/voices/<name>/*.wav`
- [ ] Check sample rate (16–48 kHz ok), mono preferred
- [ ] Remove DC offset/noise clicks (basic filter if needed)
- [ ] Document consent & retention (NDPR basics)

### D) DevOps/RunPod
- [ ] Dockerfile (non‑root, healthcheck)
- [ ] Pin deps; param Torch wheel for CUDA
- [ ] Cache model dir as volume (faster cold start)
- [ ] RunPod template with port 8000
- [ ] Startup cmd with uvicorn workers tuned
- [ ] Logs to stdout; add request‑id header later

### E) SDK/Client
- [ ] `NaijaTTSClient` with timeouts and retry (3 tries: 250/500/1000ms)
- [ ] `speak()` and `batch_speak()` helpers
- [ ] Example scripts for Windows/Linux

### F) QA/Bench
- [ ] Script to run 20 sentences; export CSV with p50/p95/p99
- [ ] Verify peak ≤ −1 dBFS; trailing silence ≤ 200ms
- [ ] Save outputs to `/outputs/` with request‑id

### G) Docs
- [ ] PRD, Task‑Management, Success‑Metrics (this set)
- [ ] README (quick start)
- [ ] Runbook (ops: restart, scale, rotate logs)

---

## 3) Definition of Ready (DoR)
- Clear acceptance criteria & sample payloads.
- Dependencies identified; environment known (CPU or GPU).
- No secrets required or already provisioned via env.

## 4) Definition of Done (DoD)
- Code merged to main; tests pass locally.
- Manual smoke on Windows + Linux (CPU) and one GPU on RunPod.
- README/Docs updated; endpoints stable; version bumped.

---

## 5) Labels & Priority
- `area:api`, `area:engine`, `area:devops`, `area:data`, `area:docs`
- `prio:P0` (blocker), `prio:P1`, `prio:P2`
- `type:bug`, `type:feature`, `type:chore`

---

## 6) PR Template (paste in `.github/pull_request_template.md`)
```
## What & Why
-

## Screenshots/Audio (if relevant)
-

## How to Test
-

## Risk & Rollback
- Rollback: revert + deploy previous image

## Checklist
- [ ] Acceptance criteria met
- [ ] Works on Windows & Linux (CPU)
- [ ] Works on GPU (RunPod)
- [ ] Docs updated
```

