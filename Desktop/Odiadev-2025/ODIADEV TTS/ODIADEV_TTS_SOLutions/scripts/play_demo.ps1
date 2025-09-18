# Windows PowerShell script to play the demo audio
Param(
    [string]$Path = "outputs/demo_multilang_30s.wav"
)

$ErrorActionPreference = "Stop"

Write-Host "🎵 Playing Naija TTS Demo..." -ForegroundColor Green

if (-not (Test-Path $Path)) {
    Write-Error "File not found: $Path"
    exit 1
}

try {
    Add-Type -AssemblyName presentationCore
    $player = New-Object System.Media.SoundPlayer($Path)
    $player.PlaySync()
    Write-Host "✅ Playback completed!" -ForegroundColor Green
} catch {
    Write-Error "Failed to play audio: $_"
    exit 1
}
