# Ollama Tray (Windows)

Um app pequeno em Python para **Windows** que coloca um **ícone na bandeja (system tray)** e:

- verifica se o Ollama está respondendo em `http://localhost:11434`
- se não estiver, inicia `ollama serve`
- mostra status (rodando / parado) e oferece **Iniciar / Parar / Configurações / Abrir logs / Sair**

## Requisitos

- Windows 10/11
- Python 3.10+ (recomendado 3.11)
- Ollama instalado
- Dependências Python: `pystray`, `pillow` e `pywin32` (no Windows)

## Tunnel (Cloudflare / trycloudflare)

O app agora consegue iniciar um **Cloudflare Tunnel (quick tunnel / trycloudflare)** para expor o Ollama/ELIS na internet e copiar a URL.

Pré-requisito: instalar o `cloudflared` (PowerShell 1 linha por comando):

```powershell
winget install --id Cloudflare.cloudflared -e
```

Opcional (se o app não encontrar o executável automaticamente): use **Configurações** no tray e aponte o caminho do `cloudflared.exe`.

## Rodar em modo dev (sem .exe)

```bat
cd ollama-tray
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src\main.py
```

No tray:
- **Iniciar Ollama**
- **Iniciar Tunnel**
- **Copiar URL do Tunnel** (aguarde alguns segundos até a URL ficar disponível)

## Gerar o executável (.exe) com PyInstaller

```bat
cd ollama-tray
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
build.bat
```

O executável será gerado em `dist\OllamaTray.exe`.

## Notas importantes

- O botão **Parar** só encerra o Ollama se ele tiver sido iniciado pelo próprio app.
- Configurações e logs ficam em `%APPDATA%\OllamaTray\`.

## Troubleshooting (rápido)

- Se você estiver usando **Python 3.13**, use uma versão mais nova do PyInstaller (o `requirements.txt` já permite isso).
- Se o status ficar “Parado” mesmo com o Ollama aberto, confira a URL em **Configurações**
  (o padrão é `http://localhost:11434`).
- Se o app não criar ícone no tray, confirme que o `pywin32` foi instalado via `pip install -r requirements.txt`.
