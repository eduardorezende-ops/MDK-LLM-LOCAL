# Ollama (local) — passo a passo do estudo

Este documento registra o **passo a passo do que estamos fazendo** para rodar LLMs **localmente** com o **Ollama**, começando com **Mistral** no **Windows**, e depois evoluindo para comparação com **Llama 3** e **Qwen**.

> Nota de padrão: **comandos PowerShell sempre em 1 linha**.

---

## 1) Pré-requisitos

- Ollama instalado no Windows
- Acesso ao PowerShell

---

## 2) Confirmar o que está rodando na máquina

### 2.1 Confirmar executável e versão

```powershell
where.exe ollama; ollama --version
```

### 2.2 Confirmar que a API local está no ar (porta 11434)

```powershell
curl http://localhost:11434/api/tags
```

✅ Esperado: `StatusCode 200` e um JSON listando os modelos (ex.: `mistral:latest`).

### 2.3 Listar modelos instalados

```powershell
ollama list
```

### 2.4 Ver detalhes do modelo (ex.: Mistral)

```powershell
ollama show mistral:latest
```

### 2.5 Confirmar processo no Windows (opcional)

```powershell
Get-Process ollama -ErrorAction SilentlyContinue
```

---

## 3) Baixar e rodar o Mistral (CLI)

```powershell
ollama pull mistral; ollama run mistral
```

Sugestão de testes no chat:
- “Responda em pt-BR: explique em 5 linhas o que é Ollama.”
- “Gere um JSON válido com: nome, idade, tags (array).”

---

## 4) Testar o modelo via API (sem chat interativo)

### 4.1 `/api/generate` (prompt simples)

```powershell
curl.exe http://localhost:11434/api/generate -H "Content-Type: application/json" -d "{\"model\":\"mistral:latest\",\"prompt\":\"Responda em pt-BR: em 3 linhas, o que é Ollama?\",\"stream\":false}"
```

✅ Esperado: retorno JSON com o campo `response`.

### 4.2 `/api/chat` (com system message)

```powershell
curl.exe http://localhost:11434/api/chat -H "Content-Type: application/json" -d "{\"model\":\"mistral:latest\",\"stream\":false,\"messages\":[{\"role\":\"system\",\"content\":\"Você é um assistente. Responda sempre em português do Brasil (pt-BR), a menos que o usuário peça outra língua.\"},{\"role\":\"user\",\"content\":\"Me explique o que é Ollama em 3 linhas.\"}]}"
```

---

## 5) “Sempre responder em pt-BR”

O jeito mais confiável é **fixar isso no `system`** (quando usar API) ou colocar um **prefixo padrão** nos prompts.

- **Via API (recomendado)**: sempre inclua um `system` pedindo pt-BR.
- **Via CLI**: comece as mensagens com “Responda em pt-BR: …”.

---

## 6) Próximos passos do estudo (roadmap)

1. Rodar os mesmos prompts no **Mistral** e registrar observações.
2. Repetir com **Llama 3** e **Qwen** (mesmos prompts) para comparar.
3. Definir uma tabelinha de comparação (qualidade pt-BR, utilidade, consistência, velocidade).
4. (Opcional) Criar um “modelo” custom no Ollama com **system pt-BR fixo** (ex.: `mistral-ptbr`) para facilitar os testes.
