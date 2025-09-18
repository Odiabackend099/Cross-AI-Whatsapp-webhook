from __future__ import annotations
import os
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from engines.xtts_engine import XTTSEngine
from utils.textnorm import normalize

app = FastAPI(title="NaijaTTS", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

VOICE_DIR = Path(os.getenv("NAIJA_VOICE_DIR", "data/voices/lexi")).resolve()
DEFAULT_SPEAKER = os.getenv("NAIJA_DEFAULT_SPEAKER", None)
ENGINE = XTTSEngine()


class SpeakIn(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    language: str = Field("en", description="XTTS language code (use 'en' for Nigerian English)")
    speaker_files: Optional[List[str]] = Field(None, description="Paths to local WAV(s)")


@app.get("/health")
def health():
    return {
        "ok": True,
        "engine": ENGINE.model_name,
        "device": ENGINE.device,
        "voice_dir_exists": VOICE_DIR.exists(),
    }


@app.post("/speak", response_class=Response)
def speak(body: SpeakIn):
    rid = str(uuid.uuid4())
    text = normalize(body.text)
    # choose speaker files
    speaker_files = body.speaker_files or []
    if not speaker_files and DEFAULT_SPEAKER:
        speaker_files = [DEFAULT_SPEAKER]
    if not speaker_files:
        # fall back to any wav in voice dir
        candidates = sorted([str(p) for p in VOICE_DIR.glob("*.wav")])
        if not candidates:
            raise HTTPException(status_code=400, detail="No speaker WAVs provided and none found in VOICE_DIR")
        speaker_files = [candidates[0]]

    try:
        out_path = ENGINE.synthesize_to_wav(
            text=text,
            speaker_wavs=[Path(p) for p in speaker_files],
            language=body.language,
        )
        data = Path(out_path).read_bytes()
        headers = {
            "Content-Disposition": f'inline; filename="tts_{rid}.wav"'
        }
        return Response(content=data, media_type="audio/wav", headers=headers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000)
