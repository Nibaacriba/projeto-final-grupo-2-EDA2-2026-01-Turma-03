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
│   └── graph/                 # Módulo de grafos (Fase 2)
│       ├── graph_builder.py   # Classe GraphBuilder (lógica de coocorrência)
│       └── fase2_export.py    # Conector Fase 2 -> Fase 3 (importar_dados_fase2)
│
├── data/
│   ├── raw/                   # Dados brutos (business/ e entertainment/)
│   └── processed/             # Dados pré-processados (Saídas do pipeline)
│
├── main.py                    # Fase 1: pré-processamento (orquestrador)
├── build_graph.py             # Fase 2: construção do grafo de coocorrência
├── examples.py                # Exemplos de uso rápido
├── tests.py                   # Testes de validação (Fases 1 e 2)
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

## 🔗 Fase 2 — Construção do Grafo de Coocorrência

A Fase 2 transforma os tokens da Fase 1 em um **grafo de coocorrência de
palavras**, na forma de uma **lista plana de arestas** `[[palavra_A, palavra_B,
peso], ...]` — o formato consumido e validado pela Fase 3 (detecção de
comunidades via MST/Kruskal).

Para cada notícia, cruzam-se todos os pares de palavras que aparecem juntas; cada
reaparição do par em outro documento incrementa o peso da aresta.

```bash
# Pré-requisito: ter rodado a Fase 1 (python main.py)
python build_graph.py        # grafo completo (todas as coocorrências)
python build_graph.py 2      # opcional: descarta arestas de peso 1 (ruído)
python tests.py              # testes das Fases 1 e 2 (inclui o contrato da Fase 3)
```

### Formato de saída (contrato com a Fase 3)

Cada aresta é uma sublista de 3 elementos `[palavra_A, palavra_B, peso]`:

- índices `[0]` e `[1]`: palavras (`str`), sempre em ordem (par canônico, então
  A‑B e B‑A são a mesma aresta);
- índice `[2]`: peso de coocorrência (`int` > 0).

Internamente o acúmulo usa um `dict` (chave = par canônico) para incremento em
O(1); a entrega final é convertida para a **lista plana de arestas**, que é o
formato que a Fase 3 valida no Passo 0 do notebook.

O conector `src/graph/fase2_export.py` entrega essa lista pronta para a Fase 3:

```python
from src.graph.fase2_export import importar_dados_fase2
grafo_linear_bruto = importar_dados_fase2()
```

### Decisão importante: tamanho do grafo x limiar de peso

O grafo **completo** (`min_weight=1`) do dataset tem **~6 milhões de arestas**
(~93 MB em pickle, ~153 MB em JSON). Cerca de **78% delas têm peso 1** — pares de
palavras que apareceram juntos em um único documento (ruído).

- O **código** mantém o padrão fiel à especificação: `min_weight=1` = grafo
  completo, sem perder informação.
- O **arquivo já incluído** neste pacote (`graph_edges.pkl`/`.json`) foi gerado
  com **`min_weight=2`** (~1,34 M de arestas, ~21 MB). Isso remove apenas os pares
  de peso 1 e deixa o grafo leve o suficiente para o Kruskal em Python puro rodar
  bem no Colab, sem mudar as conexões realmente relevantes.

Para gerar a versão completa, basta rodar `python build_graph.py 1`. A escolha do
limiar fica a critério do grupo — o tradeoff está documentado aqui para a decisão
ser consciente. Termos como `there` e `time` ainda aparecem entre as conexões
mais fortes; se quiserem um grafo mais limpo, vale adicioná-los às stopwords da
Fase 1 (ver Exemplo 3 do [`API.md`](API.md)).

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
