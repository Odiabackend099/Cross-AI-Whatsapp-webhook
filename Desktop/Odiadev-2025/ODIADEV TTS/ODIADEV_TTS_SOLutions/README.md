# NaijaTTS - Nigerian English/Pidgin Text-to-Speech API

A high-quality, low-latency Text-to-Speech API specifically designed for Nigerian English and Pidgin using XTTS v2. Deploy locally or on Runpod with authentic Nigerian accent synthesis.

## 🎯 Features

- **Zero-shot voice cloning** with XTTS v2
- **Nigerian English/Pidgin optimization** with text normalization
- **Low latency**: p50 ≤ 600ms, p95 ≤ 1.5s for 10-15 words
- **High quality**: MOS ≥ 4.0 target for Nigerian accent
- **Batch processing** up to 50 items
- **GPU acceleration** with CPU fallback
- **Privacy-first**: No external calls during synthesis
- **Easy deployment** on Windows, Linux, and Runpod

## 🚀 Quick Start

### 🎵 One-Command Demo (30s Multilingual)

**Windows:**
```powershell
# Generate and play 30-second multilingual demo
py scripts/simple_demo.py && powershell -ExecutionPolicy Bypass -File scripts\play_demo.ps1
```

**Linux:**
```bash
# Generate and play 30-second multilingual demo
python scripts/simple_demo.py && ./scripts/play_demo.sh
```

**RunPod:**
```bash
# Generate and play 30-second multilingual demo
python scripts/simple_demo.py && ffplay -nodisp -autoexit outputs/demo_multilang_30s.wav
```

### Windows Setup

1. **Bootstrap the environment:**
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\bootstrap_windows.ps1
   ```

2. **Activate virtual environment:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. **Start the API server:**
   ```powershell
   python backend/app.py
   ```

4. **Test synthesis:**
   ```powershell
   python scripts/test_synthesize_xtts.py --text "How you dey? Today go sweet well-well!"
   ```

### Linux Setup

1. **Bootstrap the environment:**
   ```bash
   chmod +x bootstrap_linux.sh
   ./bootstrap_linux.sh
   ```

2. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

3. **Start the API server:**
   ```bash
   python backend/app.py
   ```

## 📡 API Usage

### Health Check
```bash
curl http://localhost:7860/health
```

### Single Speech Synthesis
```bash
curl -X POST "http://localhost:7860/speak" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "How you dey? Today go sweet well-well!",
    "language": "en",
    "seed": 42
  }' \
  --output naija_voice.wav
```

### Batch Synthesis
```bash
curl -X POST "http://localhost:7860/batch_speak" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"id": "greeting", "text": "How you dey?"},
      {"id": "weather", "text": "Today go sweet well-well!"},
      {"id": "question", "text": "Wetin dey happen?"}
    ],
    "return_format": "zip"
  }' \
  --output batch_audio.zip
```

## 🐍 Python SDK

```python
from adaqua_tts import NaijaTTSClient

# Initialize client
client = NaijaTTSClient("http://localhost:7860")

# Check health
health = client.health()
print(f"API Status: {health['status']}")

# Synthesize speech
audio_data = client.speak("How you dey? Today go sweet well-well!")
print(f"Generated {len(audio_data)} bytes of audio")

# Save to file
output_file = client.speak_to_file(
    "Wetin dey happen? Na so e be, sha o!",
    "output.wav"
)

# Batch synthesis
texts = ["How you dey?", "Today go sweet!", "Wetin dey happen?"]
output_files = client.batch_speak_to_files(texts, "outputs/")
```

## 🏗️ Project Structure

```
.
├── backend/
│   └── app.py                      # FastAPI service
├── engines/
│   └── xtts_engine.py              # XTTS wrapper with audio processing
├── utils/
│   └── textnorm.py                 # Nigerian English/Pidgin text normalization
├── scripts/
│   ├── test_synthesize_xtts.py     # One-shot synthesis test
│   └── bench.py                    # Latency and quality benchmarking
├── data/
│   └── voices/
│       └── lexi/                   # Reference voice files
├── outputs/                        # Generated audio files
├── bench/                          # Benchmark results
├── adaqua_tts.py                   # Python SDK
├── Dockerfile                      # Runpod deployment
├── requirements.txt                # Python dependencies
└── runpod_template.yaml           # Runpod configuration
```

## 🔧 Configuration

Edit `config/config.json` to customize:

```json
{
  "voice_glob": "data/voices/lexi/*.wav",
  "windows_voice_source_dir": "C:\\Users\\OD~IA\\Music\\LEXI VOICE\\wav",
  "default_language": "en",
  "api": {
    "host": "0.0.0.0",
    "port": 7860
  }
}
```

## 📊 Benchmarking

Run performance and quality benchmarks:

```bash
# Full benchmark suite
python scripts/bench.py --num-tests 50

# Health check only
python scripts/bench.py --health-only

# Quality benchmark only
python scripts/bench.py --quality-only

# Latency benchmark only
python scripts/bench.py --latency-only
```

Results are saved to `bench/` directory with timestamps.

## 🚀 Runpod Deployment

### Option 1: Using Runpod Template

1. Upload this repository to Runpod
2. Use the provided `runpod_template.yaml`
3. Deploy with RTX 4090 or A100 GPU (24GB+ VRAM recommended)

### Option 2: Manual Docker Deployment

```bash
# Build the image
docker build -t naija-tts .

# Run with GPU support
docker run --gpus all -p 7860:7860 naija-tts
```

## 📈 Performance Targets

- **Latency**: p50 ≤ 600ms, p95 ≤ 1.5s (10-15 words, 24GB GPU)
- **Quality**: MOS ≥ 4.0 (Nigerian English/Pidgin)
- **Throughput**: ≤ $0.60 per 1k seconds audio on Runpod
- **Uptime**: ≥ 99.5% availability
- **Error Rate**: < 0.5% (non-4xx errors)

## 🎵 Audio Quality Features

- **Soft limiting** at -1 dBFS to prevent clipping
- **Silence trimming** to ≤ 200ms trailing silence
- **Text normalization** for Nigerian English/Pidgin prosody
- **Punctuation optimization** for natural speech flow
- **Code-switch handling** for English/Pidgin mixing

## 🔍 API Endpoints

### `GET /health`
Health check endpoint with system status.

### `POST /speak`
Synthesize speech from text.

**Request:**
```json
{
  "text": "How you dey? Today go sweet well-well.",
  "language": "en",
  "speaker_wav": "path/to/speaker.wav",
  "seed": 42,
  "save": false
}
```

**Response:** WAV audio file

### `POST /batch_speak`
Batch synthesis for multiple texts.

**Request:**
```json
{
  "items": [
    {"id": "item1", "text": "Text 1", "language": "en"},
    {"id": "item2", "text": "Text 2", "speaker_wav": "path/to/speaker.wav"}
  ],
  "return_format": "zip",
  "save": false
}
```

**Response:** ZIP file or JSON with base64 audio

## 🛠️ Development

### Running Tests

```bash
# Test single synthesis
python scripts/test_synthesize_xtts.py --text "Test text" --out test.wav

# Run benchmarks
python scripts/bench.py --num-tests 10

# Test SDK
python adaqua_tts.py
```

### Adding New Voices

1. Place WAV files in `data/voices/lexi/`
2. Update `config/config.json` if needed
3. Restart the API server

## 📝 Text Normalization

The system includes specialized text normalization for Nigerian English/Pidgin:

- **Space collapsing** and punctuation optimization
- **Pidgin expression handling** (e.g., "well-well" → "well, well")
- **Code-switch punctuation** for natural prosody
- **Length validation** (max 3000 characters)
- **Repetition detection** to prevent spam

## 🔒 Privacy & Security

- **No external API calls** during synthesis
- **Local model processing** only
- **Optional audio saving** (disabled by default)
- **Request ID tracking** for debugging
- **Input validation** and sanitization

## 📊 Monitoring

The API provides comprehensive logging and metrics:

- Request ID tracking
- Synthesis timing
- Device usage (CPU/GPU)
- Error rates and types
- Audio quality metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review the logs for error messages
3. Run the health check endpoint
4. Check GPU availability and CUDA installation

## 🔧 Troubleshooting

### Common Issues

**CUDA not available:**
- Install CUDA 12.1 drivers
- Verify with `nvidia-smi`
- Service will fallback to CPU

**No voice files found:**
- Ensure WAV files are in `data/voices/lexi/`
- Check file permissions
- Run bootstrap script to copy reference voices

**High latency:**
- Use GPU acceleration
- Reduce text length
- Check system resources

**Audio quality issues:**
- Verify speaker reference audio quality
- Check text normalization
- Ensure proper punctuation

### Reset Environment

**Windows:**
```powershell
rmdir /s /q .venv
.\bootstrap_windows.ps1
```

**Linux:**
```bash
rm -rf .venv
./bootstrap_linux.sh
```

---

**Built with ❤️ for the Nigerian developer community**