"""
XTTS v2 synthesis wrapper.
- Loads Coqui XTTS v2
- Supports speaker cloning via one or more WAV files
- Targets ~ -1 dBFS peak and trims trailing silence
"""
from __future__ import annotations
import os
import tempfile
from pathlib import Path
from typing import List, Optional

import numpy as np
import soundfile as sf

try:
    import torch  # type: ignore
except Exception:  # CPU fallback still OK to import
    torch = None  # pragma: no cover

from TTS.api import TTS  # type: ignore

TARGET_PEAK = 10 ** (-1.0 / 20.0)  # -1 dBFS


def _soft_limit(x: np.ndarray, target_peak: float = TARGET_PEAK) -> np.ndarray:
    if x.size == 0:
        return x
    max_abs = np.max(np.abs(x))
    if max_abs < 1e-9:
        return x
    scale = target_peak / max_abs if max_abs > target_peak else 1.0
    y = x * scale
    # simple soft clip to avoid >1.0 after fade-ins
    return np.tanh(y * 1.1)


def _trim_trailing_silence(x: np.ndarray, sr: int, thresh: float = 1e-3, max_ms: int = 200) -> np.ndarray:
    """Trim trailing silence but keep up to max_ms."""
    if x.size == 0:
        return x
    # find last index above threshold
    idx = np.where(np.abs(x) > thresh)[0]
    if idx.size == 0:
        return x[: int(sr * max_ms / 1000)]
    last = idx[-1]
    keep = min(x.size, last + int(sr * max_ms / 1000))
    return x[:keep]


class XTTSEngine:
    def __init__(
        self,
        model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2",
        device: Optional[str] = None,
        half: bool = True,
    ) -> None:
        self.model_name = model_name
        self.device = device or ("cuda" if (torch and torch.cuda.is_available()) else "cpu")
        self.half = half and (self.device.startswith("cuda"))
        self._model: Optional[TTS] = None

    @property
    def model(self) -> TTS:
        if self._model is None:
            # Fix PyTorch 2.6+ weights_only issue by setting environment variable
            import os
            os.environ["TORCH_WEIGHTS_ONLY"] = "0"
            # Coqui API automatically uses GPU if available
            self._model = TTS(model_name=self.model_name, progress_bar=False, gpu=self.device.startswith("cuda"))
        return self._model

    def synthesize_to_wav(
        self,
        text: str,
        speaker_wavs: List[Path],
        language: str = "en",
        out_path: Optional[Path] = None,
        sample_rate: int = 24000,
    ) -> Path:
        if not text or not text.strip():
            raise ValueError("text is required")
        if not speaker_wavs:
            raise ValueError("speaker_wavs must contain at least one WAV file")
        for p in speaker_wavs:
            if not Path(p).exists():
                raise FileNotFoundError(f"Speaker WAV not found: {p}")

        out_path = out_path or Path(tempfile.mkstemp(suffix=".wav")[1])
        out_path = Path(out_path)

        # Coqui will internally load, we export to a temp and then post-process
        self.model.tts_to_file(
            text=text,
            speaker_wav=str(speaker_wavs[0]),
            language=language,
            file_path=str(out_path),
            sample_rate=sample_rate,
        )

        audio, sr = sf.read(out_path, dtype="float32")
        if sr != sample_rate:
            # simple resample-free guard; Coqui already writes SR
            pass
        audio = _soft_limit(audio)
        audio = _trim_trailing_silence(audio, sr)
        sf.write(out_path, audio, sr)
        return out_path
