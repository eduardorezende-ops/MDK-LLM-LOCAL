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
