# Projeto Final - EDA2: Detecção de Tópicos em Notícias usando Grafos

## 📋 Descrição

Pipeline completo de **Processamento de Linguagem Natural (PLN)** para detectar tópicos (comunidades) em notícias utilizando estruturas de grafos. Desenvolvido em Python 3.12+ com **Spacy** para processamento de texto.

**Dataset:** BBC News - 896 artigos (Business 510 + Entertainment 386)

---

## 🚀 Quick Start (30 Segundos)

```bash
# Entrar na pasta do projeto
cd projeto-final-grupo-2-EDA2-2026-01-Turma-03

# Executar pipeline completo (Fase 1 + Fase 2)
python3 main.py

# ✅ Pronto! Dados gerados em data/processed/
```

---

## 📖 Documentação

- **README.md** (este arquivo) - Uso, arquitetura e guia rápido
- **API.md** - Documentação técnica detalhada de classes e métodos
- **Docstrings** nos arquivos - Apenas o essencial, não repetir README

---

## 🏗️ Estrutura do Projeto

```
projeto-final-grupo-2-EDA2-2026-01-Turma-03/
├── main.py                        # Pipeline: Fase 1 + Fase 2
├── see.py                         # Visualização interativa de comunidades
├── run_tests.py                   # Test runner
├── README.md                       # Este arquivo
├── API.md                         # Documentação técnica detalhada
│
├── src/                           # Código-fonte
│   ├── preprocessing/             # Fase 1: Pré-processamento
│   │   ├── text_processor.py     # TextProcessor class
│   │   └── stopwords.py          # Gerenciador de stopwords
│   ├── graph/                    # Fase 2: Construção de grafo
│   │   ├── graph_builder.py      # GraphBuilder class
│   │   └── exporter.py           # Conector Fase 2 → Fase 3
│   ├── communities/              # Fase 3: Detecção de comunidades
│   │   ├── pipeline.py           # Phase3Pipeline class
│   │   └── __init__.py
│   └── utils/
│       └── file_handler.py       # FileHandler class (I/O)
│
├── tests/                         # Testes separados por fase
│   ├── test_phase1.py            # 5 testes de pré-processamento
│   ├── test_phase2.py            # 6 testes de grafo
│   ├── test_phase3.py            # 7 testes de comunidades
│   ├── __init__.py
│   └── conftest.py               # pytest fixtures
│
├── data/
│   ├── raw/                       # Dados brutos (input)
│   │   ├── business/             # 510 artigos
│   │   └── entertainment/        # 386 artigos
│   └── processed/                 # Dados processados (output)
│
└── pyproject.toml                 # Configuração do projeto
```

---

## 🧠 Pipeline de 3 Fases

### 🔄 Fase 1: Pré-processamento de Textos

Cada documento passa por 7 etapas sequenciais:

```
ENTRADA (Texto Bruto)
        ↓
1. Normalização          → Remove espaços em branco extras
2. Minúsculas           → Converte para lowercase
3. Remover Pontuação    → Remove !, @, #, $, etc.
4. Tokenização          → Divide em lista de palavras
5. Filtro de Tokens     → Remove palavras < 2 chars e números puros
6. Remover Stopwords    → Filtra palavras comuns (the, and, a, etc.)
7. Deduplicação         → Converte para Set (garante unicidade)
        ↓
SAÍDA: Set[str] (Tokens únicos por documento)
```

**Inputs:**

- Arquivos .txt em `data/raw/business/` e `data/raw/entertainment/`

**Outputs:**

- `data/processed/documents.json` - Formato legível
- `data/processed/documents.jsonl` - Formato JSON Lines
- `data/processed/documents.pkl` - Pickle (preserva tipos nativos)

### 🔗 Fase 2: Construção do Grafo de Coocorrência

Cria um grafo ponderado onde:

- **Nós:** palavras (tokens)
- **Arestas:** pares de palavras que aparecem juntas
- **Peso:** frequência de coocorrência

**Inputs:**

- `data/processed/documents.pkl` (Fase 1)

**Outputs:**

- `data/processed/graph_edges.pkl` - Formato nativo Python
- `data/processed/graph_edges.json` - Formato legível

**Contrato da Fase 2 (validado em testes):**

1. Output é uma `list`
2. Não está vazia
3. Cada elemento é uma `list` de exatamente 3 elementos: `[palavra1, palavra2, peso]`
4. `palavra1` e `palavra2` são `str`
5. `peso` é `int` ou `float` > 0

### 🌳 Fase 3: Detecção de Comunidades

Particiona o grafo em 20 comunidades balanceadas usando:

1. Conversão peso → distância
2. Minimum Spanning Tree (Kruskal)
3. Particionamento recursivo

**Inputs:**

- `data/processed/graph_edges.pkl` (Fase 2)

**Outputs:**

- 20 comunidades ordenadas por relevância
- Cada comunidade contém palavras relacionadas (tópicos)

---

## 🎯 Como Usar

### Executar Pipeline Completo (Padrão)

```bash
python3 main.py
```

Executa Fase 1 + Fase 2 sequencialmente.

### Executar Apenas Fase 1

```bash
python3 main.py phase1
```

Pré-processa documentos, salva em `data/processed/`.

### Executar Apenas Fase 2

```bash
python3 main.py phase2
```

Constrói grafo. Requer Fase 1 já executada.

### Ver Ajuda

```bash
python3 main.py --help
```

---

## 🧪 Executando Testes

### Todos os Testes

```bash
python3 run_tests.py
```

Ou com pytest:

```bash
pytest tests/ -v
```

### Teste Específico

```bash
# Apenas Fase 1
python3 run_tests.py phase1
python3 -m tests.test_phase1

# Apenas Fase 2
python3 run_tests.py phase2
python3 -m tests.test_phase2

# Apenas Fase 3
python3 run_tests.py phase3
python3 -m tests.test_phase3
```

### Resultados de Testes

- **Phase 1:** 5 testes (JSON, JSONL, Pickle, Qualidade, Integração)
- **Phase 2:** 6 testes (Coocorrência, Peso, Canonicalidade, Filtro, Ordenação, Contrato)
- **Phase 3:** 7 testes (Validação, Conversão, Sorting, MST, Partição, Integração, Dados Reais)

**Total:** 18/18 testes passando ✅

---

## 📊 Visualização de Comunidades

Após executar o pipeline completo, visualize as comunidades com:

```bash
python3 see.py
```

### Exemplos de Uso

```bash
# Mostrar página 1 (10 comunidades por página)
python3 see.py --page 1 --per-page 10

# Filtrar por tema
python3 see.py --theme business
python3 see.py --theme entertainment

# Zoom em comunidade específica (mostra termos mais relevantes)
python3 see.py --zoom 3 --zoom-terms 30

# Demo rápido
python3 see.py --demo
```

---

## ⚙️ Requisitos

- **Python:** 3.12+
- **Dependências:** Spacy 3.8+ (PLN) + modelo en-core-web-sm
- **Disco:** ~100MB (datasets inclusos)

---

## Dúvidas?

1. **Como usar o Script:** `python3 main.py --help`
2. **Detalhes Técnicos:** Ver `API.md`
3. **Executar Testes:** `python3 run_tests.py --help`
4. **Ver Comunidades:** `python3 see.py --help`

---

**Última atualização:** 17 de junho de 2026
