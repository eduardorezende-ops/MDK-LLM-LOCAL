# MDK-LLM-LOCAL

Repositório para **estudo de LLMs rodando localmente com o [Ollama](https://ollama.com/)**, comparando **Llama 3**, **Qwen** e **Mistral**.

## O que vamos estudar
- Rodar modelos localmente (setup + comandos)
- Comparar qualidade (principalmente pt-BR) e usabilidade no dia a dia
- Registrar aprendizados e recomendações

## Modelos (via Ollama)
> Os nomes exatos podem variar no Ollama (ex.: `llama3.1:8b`, `qwen2.5:7b`, `mistral:7b`). Vamos padronizar durante o estudo.

## Começando (rápido)

1) Instale o Ollama: https://ollama.com/

2) Baixe e rode (exemplos):
```bash
ollama pull llama3
ollama run llama3

ollama pull qwen2.5:7b
ollama run qwen2.5:7b

ollama pull mistral:7b
ollama run mistral:7b
```

Úteis:
```bash
ollama list
ollama show llama3
```

## Próximos passos
- Definir quais variações/tamanhos vamos comparar
- Criar uma lista pequena de prompts padrão (pt-BR + código)
- Anotar resultados e conclusões aqui no repositório
