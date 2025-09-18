param(
  [string]$Python = "python",
  [switch]$CpuOnly
)

Write-Host "== ODIA TTS Windows bootstrap ==" -ForegroundColor Cyan

# 1) Create venv
if (-Not (Test-Path ".\.venv")) {
  & $Python -m venv .venv
}
$py = ".\.venv\Scripts\python.exe"
$pip = ".\.venv\Scripts\pip.exe"

# 2) Upgrade pip
& $py -m pip install --upgrade pip

# 3) Try to install PyTorch with CUDA 12.1 first, then fall back to CPU
if (-not $CpuOnly) {
  Write-Host "Installing PyTorch (CUDA 12.1 wheel index)..." -ForegroundColor Yellow
  & $pip install --extra-index-url https://download.pytorch.org/whl/cu121 torch torchvision torchaudio
  if ($LASTEXITCODE -ne 0) {
    Write-Warning "CUDA install failed, falling back to CPU wheels."
    & $pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
  }
} else {
  & $pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
}

# 4) Core deps
& $pip install fastapi uvicorn[standard] TTS==0.22.0 soundfile numpy pydub

# 5) Prepare folders
if (-Not (Test-Path ".\outputs")) { New-Item -ItemType Directory -Path ".\outputs" | Out-Null }

# 6) Optionally copy your voice WAVs into project (non-destructive)
$configPath = "config\config.json"
$config = Get-Content $configPath | ConvertFrom-Json
$src = $config.windows_voice_source_dir
$dst = "data\voices\lexi"
if (Test-Path $src) {
  Write-Host "Copying reference WAVs from: $src" -ForegroundColor Cyan
  Copy-Item -Path (Join-Path $src "*.wav") -Destination $dst -Force -ErrorAction SilentlyContinue
} else {
  Write-Warning "Voice source folder not found: $src — skipping copy. Put WAVs under data\voices\lexi"
}

Write-Host "`nBootstrap complete. Try:" -ForegroundColor Green
Write-Host ".\.venv\Scripts\python.exe scripts\test_synthesize_xtts.py --text `"Naija Pidgin dey flow well-well.`" --out outputs\sample.wav"
