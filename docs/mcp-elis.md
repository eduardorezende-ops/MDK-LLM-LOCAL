# MCP da ELIS (Ollama) — guia rápido

> Padrão: comandos PowerShell sempre em **1 linha**.

## O que é isso

Um **MCP server (HTTP)** com uma tool: **`ask_elis`**.

Essa tool envia um prompt para a ELIS (Ollama) via:
- `POST /api/chat` em `ELIS_BASE_URL`

## Pré-requisitos

- Node.js **>= 18**
- ELIS acessível (local ou internet)

## Configuração (env vars)

- `ELIS_BASE_URL` (default: `http://localhost:11434`)
- `ELIS_MODEL` (default: `elis:latest`)
- `PORT` (default: `3333`)

## Rodar localmente

Instalar deps (1 linha):
```powershell
npm i
```

Subir o servidor (1 linha):
```powershell
npm run dev
```

Vai imprimir:
- `http://localhost:3333/mcp`
- `http://localhost:3333/health`

## Teste direto (antes do MCP)

Teste se a ELIS responde via internet (exemplo com Cloudflare):
```powershell
curl.exe https://SUA_URL.trycloudflare.com/api/tags
```

## Testar no MCP Inspector

Rodar o Inspector (1 linha):
```powershell
npx -y @modelcontextprotocol/inspector
```

Conectar em:
- Transport: **Streamable HTTP**
- URL: `http://localhost:3333/mcp`

Depois, chamar a tool:
- `ask_elis`
- prompt: `Responda em pt-BR: diga oi.`
