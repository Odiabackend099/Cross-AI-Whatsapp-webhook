import argparse, glob, json
from pathlib import Path
import torch
from TTS.api import TTS

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT/"config/config.json").read_text())

parser = argparse.ArgumentParser()
parser.add_argument("--text", required=True, help="Text to speak")
parser.add_argument("--out", default=str(ROOT/"outputs/sample.wav"))
parser.add_argument("--language", default=CFG.get("default_language","en"))
parser.add_argument("--speaker_wav", default=None, help="Path to reference WAV")
args = parser.parse_args()

device = "cuda" if torch.cuda.is_available() else "cpu"
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

speaker = args.speaker_wav
if not speaker:
    wavs = sorted(glob.glob(str(ROOT/"data/voices/lexi/*.wav")))
    if not wavs:
        raise SystemExit("No reference WAVs. Put files under data/voices/lexi or pass --speaker_wav")
    speaker = wavs[0]

print(f"[XTTS] device={device} lang={args.language} ref={speaker}")
tts.tts_to_file(text=args.text, file_path=args.out, speaker_wav=speaker, language=args.language)
print(f"Saved: {args.out}")
