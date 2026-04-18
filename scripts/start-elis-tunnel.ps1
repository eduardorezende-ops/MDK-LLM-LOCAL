$ErrorActionPreference = "Stop"

# Script: start-elis-tunnel.ps1
# Objetivo: garantir que o Ollama (ELIS) está respondendo localmente e, em seguida,
# abrir um Cloudflare Tunnel (trycloudflare) para expor a ELIS na internet.
#
# Uso (1 linha):
# powershell -ExecutionPolicy Bypass -File .\scripts\start-elis-tunnel.ps1
#
# Observação: o tunnel fica rodando no terminal. Para parar: CTRL+C.

param(
  [string]$OllamaBaseUrl = "http://localhost:11434",
  [string]$CloudflaredArgs = "--url http://localhost:11434"
)

function Resolve-CommandPath {
  param(
    [Parameter(Mandatory = $true)][string]$CommandName,
    [Parameter(Mandatory = $false)][string]$FallbackPath
  )

  $cmd = Get-Command $CommandName -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  if ($FallbackPath -and (Test-Path $FallbackPath)) { return $FallbackPath }
  throw "Não encontrei '$CommandName'. Instale ou adicione no PATH. Fallback testado: $FallbackPath"
}

function Test-Ollama {
  param([Parameter(Mandatory = $true)][string]$BaseUrl)
  try {
    Invoke-WebRequest -Uri "$BaseUrl/api/tags" -UseBasicParsing -TimeoutSec 3 | Out-Null
    return $true
  } catch {
    return $false
  }
}

$ollamaExe = Resolve-CommandPath -CommandName "ollama" -FallbackPath "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
$cloudflaredExe = Resolve-CommandPath -CommandName "cloudflared"

Write-Host "Ollama exe: $ollamaExe"
Write-Host "Cloudflared exe: $cloudflaredExe"
Write-Host "Ollama Base URL (ELIS): $OllamaBaseUrl"

if (-not (Test-Ollama -BaseUrl $OllamaBaseUrl)) {
  Write-Host "Ollama não respondeu. Tentando iniciar 'ollama serve'..."
  Start-Process -FilePath $ollamaExe -ArgumentList "serve" -WindowStyle Hidden
  Start-Sleep -Seconds 2

  $maxTries = 30
  for ($i = 1; $i -le $maxTries; $i++) {
    if (Test-Ollama -BaseUrl $OllamaBaseUrl) { break }
    Start-Sleep -Seconds 1
    if ($i -eq $maxTries) { throw "Ollama não subiu em tempo. Verifique o serviço/porta 11434 e tente novamente." }
  }
}

Write-Host "ELIS (Ollama) OK. Abrindo Cloudflare Tunnel..."

# Rodar em foreground pra você ver a URL trycloudflare e manter o tunnel aberto.
& $cloudflaredExe tunnel $CloudflaredArgs
