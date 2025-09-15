param(
  [string]$VerifyToken = "",
  [string]$ProjectName = "crossai-whatsapp-webhook"
)
function Info($m){ Write-Host " [i] $m" -ForegroundColor Cyan }
function Good($m){ Write-Host " [+] $m" -ForegroundColor Green }
if ([string]::IsNullOrWhiteSpace($VerifyToken)) {
  $chars = @(); $chars += [char[]](97..122); $chars += [char[]](65..90); $chars += [char[]](48..57)
  1..32 | % { $VerifyToken += ($chars | Get-Random) }
}
Info "VERIFY_TOKEN: $($VerifyToken.Substring(0,4))***$($VerifyToken.Substring($VerifyToken.Length-4))"
Copy-Item ".env.example" ".env" -Force
(Get-Content ".env") -replace "CHANGE_ME_32_CHAR_RANDOM", $VerifyToken | Set-Content ".env"
npm install
Good "Run: npm run dev"
