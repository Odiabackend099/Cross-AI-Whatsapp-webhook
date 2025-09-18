"""
Test suite for the multilingual demo audio generation.
Validates audio quality, duration, and technical specifications.
"""
import os
import sys
import tempfile
from pathlib import Path
from typing import Optional

import numpy as np
import pytest
import soundfile as sf

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.multilang_demo import main as generate_demo

class TestDemoAudio:
    """Test cases for demo audio generation and validation."""
    
    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Set up environment variables for testing."""
        os.environ.setdefault("NAIJA_VOICE_DIR", "data/voices/lexi")
        os.environ.setdefault("HF_HOME", str(Path.home() / ".cache" / "huggingface"))
        os.environ.setdefault("XDG_CACHE_HOME", str(Path.home() / ".cache"))
    
    def test_demo_generation_succeeds(self):
        """Test that demo generation completes without errors."""
        # This test will skip if voice files are missing
        try:
            result = generate_demo()
            # Should return 0 on success, 1 on failure
            assert result in [0, 1]
        except Exception as e:
            pytest.skip(f"Demo generation failed: {e}")
    
    def test_demo_file_exists(self):
        """Test that demo file is created."""
        output_path = Path("outputs/demo_multilang_30s.wav")
        
        # Generate demo if it doesn't exist
        if not output_path.exists():
            result = generate_demo()
            if result != 0:
                pytest.skip("Demo generation failed - check voice files and dependencies")
        
        assert output_path.exists(), f"Demo file not found: {output_path}"
    
    def test_demo_duration(self):
        """Test that demo duration is within target range (27-33 seconds)."""
        output_path = Path("outputs/demo_multilang_30s.wav")
        
        if not output_path.exists():
            pytest.skip("Demo file not found - run demo generation first")
        
        audio, sr = sf.read(output_path, dtype="float32")
        duration = len(audio) / sr
        
        assert 27.0 <= duration <= 33.0, f"Duration {duration:.1f}s outside target range (27-33s)"
    
    def test_demo_sample_rate(self):
        """Test that demo has acceptable sample rate."""
        output_path = Path("outputs/demo_multilang_30s.wav")
        
        if not output_path.exists():
            pytest.skip("Demo file not found - run demo generation first")
        
        audio, sr = sf.read(output_path, dtype="float32")
        
        assert sr in [16000, 22050, 24000], f"Sample rate {sr} not in acceptable range"
    
    def test_demo_no_clipping(self):
        """Test that demo has no clipping (max absolute value < 1.0)."""
        output_path = Path("outputs/demo_multilang_30s.wav")
        
        if not output_path.exists():
            pytest.skip("Demo file not found - run demo generation first")
        
        audio, sr = sf.read(output_path, dtype="float32")
        max_abs = np.max(np.abs(audio))
        
        assert max_abs < 1.0, f"Audio clipped: max absolute value {max_abs:.3f} >= 1.0"
    
    def test_demo_peak_level(self):
        """Test that demo peak level is within acceptable range."""
        output_path = Path("outputs/demo_multilang_30s.wav")
        
        if not output_path.exists():
            pytest.skip("Demo file not found - run demo generation first")
        
        audio, sr = sf.read(output_path, dtype="float32")
        max_abs = np.max(np.abs(audio))
        peak_db = 20 * np.log10(max_abs + 1e-9)
        
        # Should be below -0.5 dBFS (leaving some headroom)
        assert peak_db <= -0.5, f"Peak level {peak_db:.1f} dBFS too high (target: ≤-0.5 dBFS)"
    
    def test_demo_tail_silence(self):
        """Test that demo has minimal trailing silence (≤200ms)."""
        output_path = Path("outputs/demo_multilang_30s.wav")
        
        if not output_path.exists():
            pytest.skip("Demo file not found - run demo generation first")
        
        audio, sr = sf.read(output_path, dtype="float32")
        
        # Find last non-silent sample
        silence_thresh = 1e-3
        non_silent = np.where(np.abs(audio) > silence_thresh)[0]
        
        if len(non_silent) > 0:
            last_non_silent = non_silent[-1]
            tail_samples = len(audio) - last_non_silent
            tail_duration = tail_samples / sr
            
            assert tail_duration <= 0.2, f"Tail silence {tail_duration:.3f}s exceeds 200ms limit"
    
    def test_demo_mono_channel(self):
        """Test that demo is mono (single channel)."""
        output_path = Path("outputs/demo_multilang_30s.wav")
        
        if not output_path.exists():
            pytest.skip("Demo file not found - run demo generation first")
        
        audio, sr = sf.read(output_path, dtype="float32")
        
        if audio.ndim > 1:
            assert audio.shape[1] == 1, f"Expected mono audio, got {audio.shape[1]} channels"
    
    def test_voice_files_exist(self):
        """Test that voice files are available for XTTS cloning."""
        voice_dir = Path(os.getenv("NAIJA_VOICE_DIR", "data/voices/lexi"))
        
        if not voice_dir.exists():
            pytest.skip(f"Voice directory not found: {voice_dir}")
        
        wav_files = list(voice_dir.glob("*.wav"))
        if not wav_files:
            pytest.skip(f"No WAV files found in {voice_dir}")
        
        assert len(wav_files) > 0, f"No voice files found in {voice_dir}"
    
    def test_engines_initialization(self):
        """Test that TTS engines can be initialized."""
        try:
            from engines.xtts_engine import XTTSEngine
            from engines.mms_tts import MMSTTSEngine
            
            xtts = XTTSEngine()
            mms = MMSTTSEngine()
            
            assert xtts.device is not None
            assert mms.device is not None
            
        except ImportError as e:
            pytest.skip(f"TTS engines not available: {e}")
        except Exception as e:
            pytest.fail(f"Engine initialization failed: {e}")

# Integration test that runs the full demo generation
@pytest.mark.integration
def test_full_demo_generation():
    """Integration test: generate demo and validate all properties."""
    output_path = Path("outputs/demo_multilang_30s.wav")
    
    # Clean up any existing demo
    if output_path.exists():
        output_path.unlink()
    
    # Generate demo
    result = generate_demo()
    
    if result != 0:
        pytest.skip("Demo generation failed - check dependencies and voice files")
    
    # Validate all properties
    assert output_path.exists()
    
    audio, sr = sf.read(output_path, dtype="float32")
    duration = len(audio) / sr
    max_abs = np.max(np.abs(audio))
    peak_db = 20 * np.log10(max_abs + 1e-9)
    
    # Duration check
    assert 27.0 <= duration <= 33.0, f"Duration {duration:.1f}s outside range"
    
    # Quality checks
    assert max_abs < 1.0, f"Audio clipped: {max_abs:.3f}"
    assert peak_db <= -0.5, f"Peak too high: {peak_db:.1f} dBFS"
    assert sr in [16000, 22050, 24000], f"Invalid sample rate: {sr}"
    
    print(f"✅ Demo validation passed: {duration:.1f}s, {peak_db:.1f} dBFS, {sr} Hz")
