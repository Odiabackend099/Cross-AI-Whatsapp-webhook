"""
MMS-TTS synthesis wrapper for Facebook's Multilingual Speech models.
- Supports Yoruba, Hausa, Nigerian Pidgin, and Igbo
- Uses Hugging Face transformers pipeline
- Targets ~ -1 dBFS peak and trims trailing silence
"""
from __future__ import annotations
import os
import tempfile
from pathlib import Path
from typing import Optional

import numpy as np
import soundfile as sf

try:
    from transformers import pipeline
    import torch
except ImportError:
    pipeline = None
    torch = None

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


class MMSTTSEngine:
    """Facebook MMS-TTS engine for Nigerian languages."""
    
    # Model mapping for Nigerian languages
    MODEL_MAP = {
        "yor": "facebook/mms-tts-yor",  # Yoruba
        "hau": "facebook/mms-tts-hau",  # Hausa
        "pcm": "facebook/mms-tts-pcm",  # Nigerian Pidgin
        "ibo": "facebook/mms-tts-ibo",  # Igbo (try both variants)
        "igb": "facebook/mms-tts-ibo",  # Igbo alternative
    }
    
    def __init__(self, device: Optional[str] = None):
        self.device = device or ("cuda" if (torch and torch.cuda.is_available()) else "cpu")
        self._models = {}
        self._available_languages = self._detect_available_models()
    
    def _detect_available_models(self) -> set[str]:
        """Detect which MMS models are available in the HF cache."""
        available = set()
        
        if not pipeline or not torch:
            print("Warning: transformers or torch not available, MMS-TTS disabled")
            return available
        
        for lang, model_name in self.MODEL_MAP.items():
            try:
                # Try to load the model to check if it exists
                pipe = pipeline("text-to-speech", model=model_name, device=self.device)
                available.add(lang)
                print(f"✓ MMS-TTS model available: {model_name} ({lang})")
            except Exception as e:
                print(f"✗ MMS-TTS model not available: {model_name} ({lang}) - {e}")
        
        return available
    
    def is_language_supported(self, language: str) -> bool:
        """Check if a language is supported by available MMS models."""
        return language in self._available_languages
    
    def get_model(self, language: str):
        """Get or load the model for the specified language."""
        if language not in self._available_languages:
            raise ValueError(f"Language '{language}' not supported by available MMS models")
        
        if language not in self._models:
            model_name = self.MODEL_MAP[language]
            self._models[language] = pipeline(
                "text-to-speech", 
                model=model_name, 
                device=self.device
            )
        
        return self._models[language]
    
    def synthesize_to_wav(
        self,
        text: str,
        language: str,
        out_path: Optional[Path] = None,
        sample_rate: int = 22050,
    ) -> Path:
        """Synthesize text to WAV using MMS-TTS."""
        import tempfile
        
        if not text or not text.strip():
            raise ValueError("text is required")
        
        if not self.is_language_supported(language):
            raise ValueError(f"Language '{language}' not supported by MMS-TTS")
        
        out_path = out_path or Path(tempfile.mkstemp(suffix=".wav")[1])
        out_path = Path(out_path)
        
        # Get the model for this language
        model = self.get_model(language)
        
        # Synthesize
        result = model(text)
        
        # Extract audio data
        if isinstance(result, dict) and "audio" in result:
            audio = result["audio"]
            sr = result.get("sampling_rate", sample_rate)
        else:
            # Fallback if result format is different
            audio = result
            sr = sample_rate
        
        # Convert to numpy array if needed
        if hasattr(audio, 'numpy'):
            audio = audio.numpy()
        elif hasattr(audio, 'cpu'):
            audio = audio.cpu().numpy()
        
        # Ensure it's 1D
        if audio.ndim > 1:
            audio = audio.squeeze()
        
        # Post-process
        audio = _soft_limit(audio)
        audio = _trim_trailing_silence(audio, sr)
        
        # Write to file
        try:
            sf.write(out_path, audio, sr)
        except Exception as e:
            # If file is locked, try a different name
            new_path = Path(tempfile.mkstemp(suffix=".wav")[1])
            sf.write(new_path, audio, sr)
            out_path = new_path
        return out_path
