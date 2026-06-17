# Projeto Final - EDA2: Detecção de Tópicos em Notícias usando Grafos

## 📋 Descrição

Pipeline completo de **Processamento de Linguagem Natural (PLN)** para detectar tópicos (comunidades) em notícias utilizando estruturas de grafos. Desenvolvido em Python 3.12+ com **Spacy** para processamento de texto.

**Dataset:** BBC News - 896 artigos (Business 510 + Entertainment 386)

---

## 🚀 Quick Start (30 Segundos)

```bash
# Entrar na pasta do projeto
cd projeto-final-grupo-2-EDA2-2026-01-Turma-03

# Executar pipeline de crição do grafo (Fase 1 + Fase 2)
python3 main.py

# Executar pipeline de detecção de comunidades (Fase 3)
python3 see.py

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
4. Tokenização          → Divide em lista de palavras através do spaCy
5. Filtro de Tokens     → Remove palavras < 2 chars e números puros
6. Lematização          → Reduz palavras ao radical funcional (ex: running -> run)
7. Remover Stopwords    → Filtra termos comuns comparando os lemas gerados
8. Deduplicação         → Converte para Set (garante unicidade dos lemas)
        ↓
SAÍDA: Set[str] (Lemas únicos por documento)
```

**Inputs:**

- Arquivos .txt em `data/raw/business/` e `data/raw/entertainment/`

**Outputs:**

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

### Executar Pipeline de criação do grafo (Padrão)

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

### Teste Específico

```bash
# Apenas Fase 1
python3 run_tests.py phase1

# Apenas Fase 2
python3 run_tests.py phase2

# Apenas Fase 3
python3 run_tests.py phase3
```

### Resultados de Testes

- **Phase 1:** 3 testes ( Pickle, Qualidade, Integração)
- **Phase 2:** 6 testes (Coocorrência, Peso, Canonicalidade, Filtro, Ordenação, Contrato)
- **Phase 3:** 7 testes (Validação, Conversão, Sorting, MST, Partição, Integração, Dados Reais)

**Total:** 18/18 testes passando ✅

---

## 📊 Visualização de Comunidades

Após executar o pipeline completo, visualize as comunidades com:

```bash
python3 see.py
```

- **--theme**: Filtra as conexões do grafo por categoria antes de computar as comunidades. Opções: all (padrão), business ou entertainment.

- **--page**: Número da página a ser exibida (padrão: 1).

- **--per-page**: Quantidade de subtemas exibidos por página (padrão: 10).

- **--max-kw-chars**: Limite máximo de caracteres de visualização da lista de palavras por linha na tabela (padrão: 120).

- **--zoom**: ID numérico de um subtema específico para inspecionar os termos de forma isolada e vertical.

- **--zoom-terms**: Quantidade de termos detalhados a serem exibidos dentro do modo zoom (padrão: 20).

- **--demo**: Executa um fluxo rápido mostrando a primeira página e aplicando zoom automático no primeiro subtema encontrado.

### Exemplos de Uso

```bash
# Navegar pelas páginas da tabela ASCII (10 subtemas por vez)
python3 see.py --page 2 --per-page 10

# Filtrar e recalcular as comunidades dinamicamente para um tema específico
python3 see.py --theme business
python3 see.py --theme entertainment

# Expandir um subtema específico para inspecionar o grau individual de seus termos
python3 see.py --zoom 1 --zoom-terms 15

# Ajustar a largura máxima da tabela de palavras-chave para telas menores
python3 see.py --max-kw-chars 80

# Demo rápido de verificação visual
python3 see.py --demo

# exemplo completo
python3 see.py --theme business --page 1 --per-page 5 --max-kw-chars 150 --zoom 2 --zoom-terms 10
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
