# Como a gente trabalha (regras rápidas)

Este arquivo define **como vamos trabalhar daqui pra frente** neste repo.

## 1) PowerShell

- **Todos os comandos de PowerShell** que eu te passar serão **sempre em 1 linha** (sem multiline).
- Se precisar criar arquivo (ex.: `Modelfile`), eu vou preferir comandos 1‑linha ou orientar a criar via editor.

## 2) Git (commit + push)

- Quando você pedir **“faz commit”** (ou equivalente), eu vou:
  1) checar `git status`
  2) stage dos arquivos relevantes
  3) fazer o **commit**
  4) fazer o **push**

### Observações importantes

- Eu **só consigo dar push** se:
  - o repo tiver **remote** configurado (ex.: `origin`)
  - houver **permissão/autenticação** disponível no ambiente (token/SSH).  
Se não der push, eu vou te avisar o motivo e o que falta.

## 3) Identidade do commit (name/email)

Vamos usar esta identidade **localmente no repo** (não global):

- `user.name`: `eduardorezende-ops`
- `user.email`: `eduardo.rezende@lopesecia.com.br`

Comando (1 linha):

```bash
git config user.name "eduardorezende-ops" && git config user.email "eduardo.rezende@lopesecia.com.br"
```

## 4) Arquivos do estudo (ELIS)

- ELIS = seu Ollama local.
- Documentação principal:
  - `README.md`
  - `ollama-estudo.md`
  - `plano-mcp-ollama.md`
