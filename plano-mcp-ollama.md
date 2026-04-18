# Plano — ELIS (LLM local via Ollama)

> Padrão: comandos PowerShell sempre em **1 linha**.

## O que é a ELIS

**ELIS** é o nome que vamos usar para nos referirmos ao seu **LLM local**, rodando via **Ollama** na sua máquina (Windows).

Em termos práticos:
- a ELIS “mora” no Ollama
- a ELIS responde por uma API local em `http://localhost:11434`

## Como configuramos a ELIS para responder em pt-BR por padrão

A forma mais estável é criar um **modelo custom** no Ollama com um `SYSTEM` fixo em pt-BR.

### 1) Garantir que o Mistral está instalado

```powershell
ollama pull mistral
```

### 2) Criar um Modelfile da ELIS com SYSTEM pt-BR

```powershell
Set-Content -Path .\Modelfile-elis -Encoding utf8 -Value "FROM mistral:latest`nSYSTEM Você é a ELIS. Responda sempre em português do Brasil (pt-BR), a menos que o usuário peça explicitamente outra língua.`n"
```

### 3) Criar o modelo `elis`

```powershell
ollama create elis -f .\Modelfile-elis
```

### 4) Testar

```powershell
ollama run elis "Qual idioma você vai usar por padrão? Responda em 1 frase."
```

## Próximo passo — disponibilizar a ELIS na internet (pra eu/um app usar)

Como a ELIS roda **na sua máquina**, “disponibilizar na internet” significa gerar uma **URL pública** que encaminha para:
- `http://localhost:11434` (Ollama/ELIS)

O caminho mais direto pro estudo é usar um **túnel**.

### Opção A (recomendada) — Cloudflare Tunnel (URL pública)

1) Rodar o túnel apontando pro Ollama local (1 linha):
```powershell
cloudflared tunnel --url http://localhost:11434
```

2) Ele vai imprimir uma URL `https://...trycloudflare.com`. Teste (1 linha):
```powershell
curl.exe https://SUA_URL_PUBLICA.trycloudflare.com/api/tags
```

### Opção B — ngrok (URL pública rápida)

1) Rodar (1 linha):
```powershell
ngrok http 11434
```

2) Pegar a URL `https://...ngrok-free.app` e testar (1 linha):
```powershell
curl.exe https://SUA_URL_PUBLICA.ngrok-free.app/api/tags
```

### Como isso vira “ELIS pra eu usar”

- Você me manda a `SUA_URL_PUBLICA` (só a URL, sem token/segredo).
- No MCP/app, a gente configura:
  - `ELIS_BASE_URL=https://SUA_URL_PUBLICA`
  - `ELIS_MODEL=elis`

---

## Status atual (já feito)

- ELIS criada como modelo custom no Ollama (`elis:latest`) com `SYSTEM` pt-BR
- ELIS exposta na internet via Cloudflare Tunnel (trycloudflare)

URL atual (exemplo do estudo):
- `https://urw-inbox-matter-desire.trycloudflare.com`

Validar (1 linha):
```powershell
curl.exe https://urw-inbox-matter-desire.trycloudflare.com/api/tags
```

---

## Próximo passo — criar um MCP que conversa com a ELIS (via internet)

Objetivo: ter um **MCP server** com uma tool simples (ex.: `ask_elis`) que chama a ELIS via HTTP e devolve a resposta.

### Plano (alto nível)

1) Criar um projeto MCP (Node.js + TypeScript) dentro do repo  
2) Implementar um MCP server com 1 tool: `ask_elis`  
3) A tool chama a ELIS em `ELIS_BASE_URL` usando o modelo `elis:latest`  
4) Rodar o MCP localmente  
5) Testar a tool com uma pergunta simples e confirmar que respondeu em pt-BR

### Variáveis (pra gente padronizar)

- `ELIS_BASE_URL=https://urw-inbox-matter-desire.trycloudflare.com`
- `ELIS_MODEL=elis:latest`

### Teste HTTP direto (antes do MCP)

```powershell
curl.exe https://urw-inbox-matter-desire.trycloudflare.com/api/chat -H "Content-Type: application/json" -d "{\"model\":\"elis:latest\",\"stream\":false,\"messages\":[{\"role\":\"user\",\"content\":\"Responda em pt-BR: diga oi.\"}]}"
```
