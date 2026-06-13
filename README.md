# Projeto Final - EDA2: Detecção de Tópicos em Notícias usando Grafos

## 📋 Descrição

Este projeto implementa um pipeline completo de **Processamento de Linguagem Natural (PLN)** com o objetivo de detectar tópicos (comunidades) em notícias utilizando estruturas de grafos. O projeto é desenvolvido em Python 3.12+ e conta com **zero dependências externas**.

### Dataset

**BBC News Dataset** com foco em 896 artigos das categorias:

- 🏢 Business (510 notícias)
- 🎬 Entertainment (386 notícias)

---

## 🚀 Guia de Início Rápido (30 Segundos)

```bash
# 1. Entrar na pasta do projeto
cd projeto-final-grupo-2-EDA2-2026-01-Turma-03

# 2. Executar o pipeline de pré-processamento
python3 main.py

# ✅ Pronto! Seus dados limpos estão gerados em data/processed/
```

### Outros comandos úteis:

- **Ver exemplos práticos:** `python3 examples.py`
- **Validar os dados com testes:** `python3 tests.py`

---

## 🏗️ Estrutura do Projeto

```
pln-grafos/
│
├── src/                       # Código-fonte principal
│   ├── __init__.py
│   ├── preprocessing/         # Módulo de pré-processamento (TextProcessor, Stopwords)
│   ├── utils/                 # Utilitários de I/O (FileHandler)
│   └── graph/                 # Módulo de grafos
│
├── data/
│   ├── raw/                   # Dados brutos (business/ e entertainment/)
│   └── processed/             # Dados pré-processados (Saídas do pipeline)
│
├── main.py                    # Script principal (orquestrador)
├── examples.py                # Exemplos de uso rápido
├── tests.py                   # Testes de validação
├── pyproject.toml             # Configuração do projeto
├── README.md                  # Este arquivo (Visão geral e arquitetura)
└── API.md                     # Documentação detalhada de classes e métodos
```

---

## 🧠 Pipeline de Pré-processamento

Cada documento de texto bruto passa pelas seguintes etapas sequenciais dentro do orquestrador:

```
ENTRADA (Texto Bruto)
        ↓
┌─────────────────────────────────┐
│ 1. NORMALIZAÇÃO                 │ -> Remove espaços em branco extras
└─────────────────────────────────┘
        ↓
┌─────────────────────────────────┐
│ 2. MINÚSCULAS                   │ -> Converte todo o texto para lowercase
└─────────────────────────────────┘
        ↓
┌─────────────────────────────────┐
│ 3. REMOVER PONTUAÇÃO            │ -> Remove caracteres como !, @, #, $, etc.
└─────────────────────────────────┘
        ↓
┌─────────────────────────────────┐
│ 4. TOKENIZAÇÃO                  │ -> Divide a string de texto em uma lista de palavras
└─────────────────────────────────┘
        ↓
┌─────────────────────────────────┐
│ 5. FILTRO DE TOKENS             │ -> Remove palavras menores que 2 caracteres e números puros
└─────────────────────────────────┘
        ↓
┌─────────────────────────────────┐
│ 6. REMOVER STOPWORDS            │ -> Filtra palavras comuns sem valor semântico (the, and, a)
└─────────────────────────────────┘
        ↓
┌─────────────────────────────────┐
│ 7. DEDUPLICAÇÃO                 │ -> Converte o resultado para Set (garante palavras únicas)
└─────────────────────────────────┘
        ↓
SAÍDA: Set[str] (Tokens únicos prontos para o grafo)
```

---

## 📊 Formatos de Saída Disponíveis

Após rodar o comando principal, a Fase 1 salva os dados em três formatos dentro de `data/processed/` para garantir flexibilidade nas próximas fases:

| Formato    | Arquivo           | Melhor Caso de Uso                                     |
| :--------- | :---------------- | :----------------------------------------------------- |
| **JSON**   | `documents.json`  | Legível por humanos, altamente compatível.             |
| **JSONL**  | `documents.jsonl` | Processamento em linha (Streaming), economiza memória. |
| **Pickle** | `documents.pkl`   | Preserva o tipo nativo `set` do Python.                |

---

## 📈 Estruturas de Dados Utilizadas & Desempenho

Visando a eficiência exigida na disciplina de Estrutura de Dados 2, foram escolhidas as seguintes estruturas nativas:

- **`set` (Conjuntos):** Utilizado para os tokens de cada documento e armazenamento de stopwords. Garante remoção automática de duplicatas e busca com complexidade de tempo média estável de $O(1)$.
- **`list` (Listas):** Utilizada para armazenar o lote de documentos, preservando a ordem de leitura e permitindo iteração linear eficiente.
- **`dict` (Dicionários):** Utilizado para mapear as propriedades estruturadas de cada documento (`id`, `category`, `tokens`), garantindo acesso direto e semântico às propriedades.

---

## 👥 Integrantes

- Gabriel da Cunha Barbaceli

## 📄 Licença

Projeto acadêmico - Universidade de Brasília (UnB).
