# SUCCESS-METRICS — NaijaTTS v0.1

This doc defines **what success looks like** for MVP and how we’ll measure it.

---

## 1) Product Outcomes
- **Time‑to‑First‑Voice (TTFV)**: < 10 minutes from clean clone → first WAV.
- **Developer Success**: 90% of integrators can call `/speak` in < 15 minutes.
- **Perceived Quality**: Mean Opinion Score (MOS) ≥ **4.0/5** for Nigerian English/Pidgin on a 10‑sentence blind test (≥ 5 raters).

---

## 2) Engineering SLOs (targets, MVP)
- **Latency** (10–15 words, 24GB GPU):
  - p50 ≤ **600ms**, p95 ≤ **1.5s** (server‑side measure; exclude network).
- **Availability**: **99.5%** monthly (single region).
- **Error rate** (5xx from `/speak`): ≤ **1%**.
- **Cold start** (first request after deploy): ≤ **30s** with cached model volume.
- **Throughput**: Sustain ≥ **10 RPS** single‑sentence on a 24GB GPU (goal; tune later).

---

## 3) Audio Quality KPIs
- **Peak level**: ≤ **−1.0 dBFS** (no clipping) — enforced by limiter.
- **Trailing silence**: ≤ **200 ms** — post‑trim step.
- **Sample rate**: **24 kHz** output.
- **Failures**: 0 files with NaN/Inf samples (guard rails in post).

**Validation method**
- Automated checks in bench script (peak, silence) + manual listening panel weekly.

---

## 4) Reliability & Ops
- **MTTR** (mean time to restore): < 20 minutes.
- **Alerting**: Health endpoint down > 2 minutes (page), p95 latency > SLO (warn).
- **Request‑ID**: present in responses ≥ 95% of time (after we add middleware).

---

## 5) Cost & Efficiency
> We do not hard‑code cloud prices in docs (they change). Instead we track **unit cost**.

- **Unit cost (voice)** = `GPU_hourly_rate * (wall_time_seconds / 3600)` per request.  
  Goal: **≤ target value** set each sprint (fill from current vendor pricing).
- **GPU utilization** target: 40–70% under steady load (no starvation/no idling).
- **Cache hit rate** for model weights: ≥ 95% after first boot on a node.

---

## 6) Security & Compliance
- **Secrets**: 0 secrets in repo (scan on CI later).
- **PII**: We do **not** store caller text or audio by default.
- **Voice consent**: Reference WAV owners consent recorded (checklist).

---

## 7) Measurement Plan
- Bench script emits CSV: `latency_ms`, `p50/p95/p99`, `peak_dbfs`, `silence_ms`.
- Weekly QA session: 10 sentences blind MOS; keep results in `/eval/mos/YYYY‑WW.md`.
- Ops dashboard (later): p95, error rate, GPU utilization, unit cost trend.

---

## 8) Go/No‑Go (Release Gate, MVP)
**Go** if all below are true:
- All endpoints pass acceptance tests on CPU + one GPU type.
- Latency SLO met on target GPU.
- Audio KPIs clean on 20‑utterance batch.
- Runbook updated; on‑call person assigned.

