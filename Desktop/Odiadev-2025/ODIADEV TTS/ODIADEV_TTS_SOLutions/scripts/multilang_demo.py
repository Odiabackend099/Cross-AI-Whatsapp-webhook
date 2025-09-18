#!/usr/bin/env python3
"""
30-second multilingual Naija TTS demo.
- Uses XTTS for English with voice cloning
- Uses MMS-TTS for Nigerian languages (Yoruba, Hausa, Pidgin, Igbo)
- Produces ~30s demo with language switching
"""
import os
import sys
from pathlib import Path
from typing import List, Tuple

import numpy as np
import soundfile as sf

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from engines.xtts_engine import XTTSEngine
from engines.mms_tts import MMSTTSEngine

# Demo text lines (targeting ~5-7 seconds each for ~30s total)
LINES = [
    ("en",  "Hi, I'm Lexi from Adaqua AI. Listen as I switch languages for all Naija."),
    ("pcm", "How you dey? Today go sweet well well."),
    ("yor", "Ẹ káàbọ̀. A ń kọ́ ohun tuntun fún gbogbo Naijiria."),
    ("ibo", "Ụtụtụ ọma. Anyị na-arụ ọrụ maka Naịjiria niile."),
    ("hau", "Sannu! Muna aiki don Najeriya gaba ɗaya."),
    ("en",  "Thanks for listening. Adaqua AI—built for Naija, by Naija."),
]

def find_voice_files() -> List[Path]:
    """Find voice files for XTTS cloning."""
    voice_dir = Path(os.getenv("NAIJA_VOICE_DIR", "data/voices/lexi"))
    
    if not voice_dir.exists():
        print(f"Warning: Voice directory not found: {voice_dir}")
        return []
    
    # Look for WAV files
    wav_files = list(voice_dir.glob("*.wav"))
    if not wav_files:
        print(f"Warning: No WAV files found in {voice_dir}")
        return []
    
    print(f"Found {len(wav_files)} voice files in {voice_dir}")
    return wav_files

def synthesize_segment(text: str, language: str, xtts_engine: XTTSEngine, 
                      mms_engine: MMSTTSEngine, voice_files: List[Path]) -> np.ndarray:
    """Synthesize a single text segment."""
    print(f"Synthesizing {language}: {text[:50]}...")
    
    if language == "en":
        # Use XTTS for English with voice cloning
        if not voice_files:
            raise ValueError("No voice files available for XTTS cloning")
        
        temp_path = xtts_engine.synthesize_to_wav(
            text=text,
            speaker_wavs=voice_files,
            language="en",
            sample_rate=22050
        )
        audio, sr = sf.read(temp_path, dtype="float32")
        temp_path.unlink()  # Clean up temp file
        return audio, sr
    
    else:
        # Use MMS-TTS for Nigerian languages
        if not mms_engine.is_language_supported(language):
            print(f"Warning: MMS-TTS not available for {language}, falling back to English")
            return synthesize_segment(text, "en", xtts_engine, mms_engine, voice_files)
        
        temp_path = mms_engine.synthesize_to_wav(
            text=text,
            language=language,
            sample_rate=22050
        )
        audio, sr = sf.read(temp_path, dtype="float32")
        temp_path.unlink()  # Clean up temp file
        return audio, sr

def main():
    """Generate the 30-second multilingual demo."""
    print("🎤 Starting Naija TTS Multilingual Demo Generation")
    print("=" * 60)
    
    # Initialize engines
    print("Initializing TTS engines...")
    xtts_engine = XTTSEngine()
    mms_engine = MMSTTSEngine()
    
    print(f"XTTS device: {xtts_engine.device}")
    print(f"MMS device: {mms_engine.device}")
    print(f"Available MMS languages: {sorted(mms_engine._available_languages)}")
    
    # Find voice files
    voice_files = find_voice_files()
    if not voice_files:
        print("Error: No voice files found for XTTS cloning")
        return 1
    
    # Create output directory
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "demo_multilang_30s.wav"
    
    print(f"\nSynthesizing {len(LINES)} segments...")
    print("-" * 40)
    
    # Synthesize all segments
    segments = []
    total_duration = 0.0
    
    for i, (lang, text) in enumerate(LINES, 1):
        try:
            audio, sr = synthesize_segment(text, lang, xtts_engine, mms_engine, voice_files)
            duration = len(audio) / sr
            total_duration += duration
            
            print(f"  {i}/{len(LINES)} {lang}: {duration:.1f}s")
            segments.append((audio, sr))
            
        except Exception as e:
            print(f"  Error synthesizing {lang}: {e}")
            return 1
    
    print(f"\nConcatenating segments...")
    
    # Concatenate all segments
    if not segments:
        print("Error: No segments to concatenate")
        return 1
    
    # Ensure all segments have the same sample rate
    target_sr = segments[0][1]
    concatenated = []
    
    for audio, sr in segments:
        if sr != target_sr:
            print(f"Warning: Resampling from {sr} to {target_sr}")
            # Simple resampling (in production, use librosa or scipy)
            ratio = target_sr / sr
            new_length = int(len(audio) * ratio)
            audio = np.interp(np.linspace(0, len(audio), new_length), 
                            np.arange(len(audio)), audio)
        concatenated.append(audio)
    
    final_audio = np.concatenate(concatenated)
    
    # Final post-processing
    print("Applying final post-processing...")
    
    # Peak limiting
    max_val = np.max(np.abs(final_audio))
    if max_val > 0.0:
        final_audio = final_audio * (0.9 / max_val)  # Leave some headroom
    
    # Trim trailing silence
    silence_thresh = 1e-3
    last_non_silent = np.where(np.abs(final_audio) > silence_thresh)[0]
    if len(last_non_silent) > 0:
        final_audio = final_audio[:last_non_silent[-1] + int(0.2 * target_sr)]  # Keep 200ms tail
    
    # Write final file
    sf.write(output_path, final_audio, target_sr)
    
    # Validation
    final_duration = len(final_audio) / target_sr
    peak_db = 20 * np.log10(np.max(np.abs(final_audio)) + 1e-9)
    
    print(f"\n✅ Demo generated successfully!")
    print(f"📁 Output: {output_path}")
    print(f"⏱️  Duration: {final_duration:.1f}s")
    print(f"📊 Peak level: {peak_db:.1f} dBFS")
    print(f"🎵 Sample rate: {target_sr} Hz")
    
    # Validate duration
    if not (27.0 <= final_duration <= 33.0):
        print(f"❌ WARNING: Duration {final_duration:.1f}s is outside target range (27-33s)")
        return 1
    
    if peak_db > -0.5:
        print(f"❌ WARNING: Peak level {peak_db:.1f} dBFS is too high (target: ≤-1.0 dBFS)")
        return 1
    
    print(f"\n🎉 Demo ready for playback!")
    print(f"   Windows: scripts\\play_demo.ps1")
    print(f"   Linux:   ./scripts/play_demo.sh")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
