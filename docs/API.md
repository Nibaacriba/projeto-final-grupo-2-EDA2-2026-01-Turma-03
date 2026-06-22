# Documentação Técnica da API - Pipeline de Pré-processamento

Este documento detalha o funcionamento de baixo nível das classes, métodos e parâmetros do módulo de pré-processamento. Para uma visão arquitetural geral, consulte o `README.md`.

---

## 🔧 Módulo: `TextProcessor`

Classe responsável pela execução e configuração do pipeline de Processamento de Linguagem Natural.

### Inicialização

```python
from src.preprocessing import TextProcessor

processor = TextProcessor(min_token_length=2, remove_numbers=True)
```

### Parâmetros do Construtor

| Parâmetro         | Tipo | Padrão           | Descrição                                                |
| :---------------- | :--- | :--------------- | :------------------------------------------------------- |
| min_token_length  | int  | 2                | Comprimento mínimo de um token válido                    |
| remove_numbers    | bool | True             | Se True, remove tokens que contêm apenas números         |
| use_lemmatization | bool | True             | Se True, reduz as palavras ao seu radical/lema funcional |
| spacy_model       | str  | "en_core_web_sm" | Modelo do spaCy carregado sem os componentes pesados     |

### Métodos Principais

#### 1. `process_document(text: str) -> Set[str]`

Executa as 7 etapas do pipeline de limpeza em uma única string de texto bruto.

- **Retorno:** Um `set` contendo apenas tokens únicos, normalizados e sem stopwords.

#### 2. `process_batch(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]`

Processa em lote uma lista de dicionários contendo metadados e textos brutos.

- **Entrada esperada:** Uma lista de dicionários no formato `{"id": str, "category": str, "text": str}`.
- **Retorno:** Uma lista de dicionários estruturados no formato `{"id": str, "category": str, "tokens": set}`.

---

## 🛠️ Módulo: `FileHandler`

Classe utilitária para operações de entrada/saída de arquivos no sistema de arquivos.

### Métodos Estáticos

- **`read_text_file(file_path: str) -> str`**
  Lê e retorna o conteúdo textual de um arquivo `.txt` usando encoding UTF-8.

- **`list_files_in_directory(directory: str, extension: str = ".txt") -> List[str]`**
  Varre um diretório e retorna uma lista ordenada e reproduzível com os nomes dos arquivos.

- **`get_file_path(directory: str, filename: str) -> str`**
  Constrói caminhos de arquivos de forma segura e agnóstica ao Sistema Operacional.

- **`save_python_pickle(data: Any, output_path: str) -> None`**
  Serializa estruturas complexas em formato binário Pickle utilizando o protocolo de máxima velocidade (`HIGHEST_PROTOCOL`). **Garante autocriação de diretórios parentes** e mantém intacta a tipagem nativa de objetos como `set`.

- **`load_python_pickle(input_path: str) -> Any`**
  Carrega e desserializa um arquivo `.pkl` diretamente para a memória operacional, preservando as estruturas originais.

---

## 🚫 Módulo: `stopwords`

Gerenciador interno responsável por mitigar palavras funcionais de alta frequência que não agregam valor à identificação de tópicos. Suporta dicionários combinados de Inglês e Português (~150+ palavras).

### Funções Disponíveis

- **`get_stopwords() -> set`**: Retorna o conjunto completo de stopwords cadastradas no sistema.
- **`is_stopword(word: str) -> bool`**: Retorna um booleano avaliando se a palavra específica informada faz parte do conjunto de stopwords.

---

## ⏱️ Troubleshooting Técnico

### Erro: `ModuleNotFoundError: No module named 'src'`

- **Causa:** O script foi disparado de dentro de subpastas do projeto.
- **Solução:** O terminal deve estar situado obrigatoriamente na **raiz do projeto** ao executar qualquer comando.

### Por que usamos Pickle (.pkl) em vez de JSON?

- **Causa:** O formato JSON não suporta conjuntos (`set`). Ao converter um set para lista no JSON, a ordem se perde e o tempo de I/O aumenta drasticamente devido à serialização de strings textuais. O Pickle mantém a tipagem nativa em binário puro.

---

## 🔗 Módulo: `GraphBuilder` (Fase 2)

Classe responsável pela construção do grafo de coocorrência a partir dos documentos pré-processados.

### Inicialização

```python
from src.graph import GraphBuilder

# Grafo completo (todas as coocorrências, padrão)
builder = GraphBuilder(min_weight=1)

# Grafo filtrado (remove ruído: arestas com peso < 2)
builder_filtered = GraphBuilder(min_weight=2)
```

### Parâmetros do Construtor

| Parâmetro    | Tipo  | Padrão | Descrição                                         |
| ------------ | ----- | ------ | ------------------------------------------------- |
| `min_weight` | `int` | `1`    | Peso mínimo para uma aresta entrar no grafo final |

**Nota sobre `min_weight`:**

- `min_weight=1`: Grafo COMPLETO (respeta especificação literal da Fase 2)
- `min_weight≥2`: Grafo FILTRADO (remove arestas que ocorrem em apenas 1 documento = ruído)

### Métodos Principais

#### 1. `build(documents: List[Dict]) -> List[List]`

Constrói a lista plana de arestas de coocorrência.

**Parâmetros:**

- `documents`: Lista de documentos da Fase 1. Cada documento é um `dict` no formato:
  ```python
  {
      "id": "doc_001",
      "category": "business",
      "tokens": {"market", "stock", "trade", ...}  # ← Set de tokens únicos
  }
  ```

**Retorno:** Lista plana de arestas ordenada por peso decrescente:

```python
[
    ["market", "stock", 125],     # Peso 125 (coocorrência forte)
    ["market", "trade", 98],      # Peso 98
    ["stock", "exchange", 45],    # Peso 45
    ...
]
```

**Propriedades da saída:**

1. Cada aresta é `[palavra_a: str, palavra_b: str, peso: int/float > 0]`
2. Aresta canônica: sempre `palavra_a < palavra_b` (não repete invertidas)
3. Determinística: mesma entrada = mesma saída (ordenada por peso)

#### 2. `to_adjacency_list(arestas: List[List]) -> Dict[str, List]`

**(Método estático)** Converte lista plana em lista de adjacência (opcional).

**Entrada:**

```python
arestas = [["market", "stock", 125], ["stock", "trade", 45], ...]
```

**Saída:**

```python
{
    "market": [["stock", 125], ["trade", 35], ...],
    "stock": [["market", 125], ["trade", 45], ...],
    "trade": [["stock", 45], ["market", 35], ...],
    ...
}
```

**Uso:** Apenas se consumidor preferir visão por vértice. Fase 3 usa lista plana.

#### 3. `estatisticas(arestas: List[List]) -> Dict[str, Any]`

**(Método estático)** Retorna estatísticas do grafo.

**Saída:**

```python
{
    "num_arestas": 2500000,
    "num_vertices": 5000,
    "peso_total": 1250000,
    "peso_media": 500.0,
    "peso_min": 1,
    "peso_max": 150,
    "densidade": 0.0002  # (2 * arestas) / (vertices * (vertices-1))
}
```

### Exemplos de Uso

```python
from src.utils import FileHandler
from src.graph import GraphBuilder

# Carregar documentos da Fase 1
documents = FileHandler.load_python_pickle("data/processed/documents.pkl")

# Construir grafo (padrão: todas as coocorrências)
builder = GraphBuilder(min_weight=1)
arestas = builder.build(documents)

print(f"Grafo construído: {len(arestas)} arestas")

# Opcionalmente: converter para lista de adjacência
adjacencia = GraphBuilder.to_adjacency_list(arestas)
print(f"Vizinhos de 'market': {adjacencia.get('market', [])}")

# Estatísticas
stats = GraphBuilder.estatisticas(arestas)
print(f"Peso máximo de aresta: {stats['peso_max']}")
print(f"Densidade do grafo: {stats['densidade']:.6f}")
```

---

## 🌳 Módulo: `Phase3Pipeline` (Fase 3)

Classe responsável pela detecção de comunidades via Minimum Spanning Tree (MST) + particionamento recursivo.

### Inicialização

```python
from src.communities.pipeline import Phase3Pipeline

# Configuração padrão: 20 comunidades, mínimo 150 palavras/comunidade
pipeline = Phase3Pipeline(
    target_communities=20,
    min_community_size=150,
    verbose=True
)
```

### Parâmetros do Construtor

| Parâmetro            | Tipo   | Padrão | Descrição                               |
| -------------------- | ------ | ------ | --------------------------------------- |
| `target_communities` | `int`  | `20`   | Número alvo de comunidades a gerar      |
| `min_community_size` | `int`  | `150`  | Tamanho mínimo de uma comunidade válida |
| `verbose`            | `bool` | `True` | Se True, imprime mensagens de progresso |

### Métodos Principais

#### 1. `run(edges: List[List]) -> Dict`

Executa o pipeline completo: validação → MST → particionamento.

**Parâmetros:**

- `edges`: Lista de arestas da Fase 2:
  ```python
  [["palavra_a", "palavra_b", peso], ...]
  ```

**Retorno:** Dicionário com resultado completo:

```python
{
    "mst_edges": [...],           # Arestas da MST (~5000)
    "communities": [...],         # 20 listas de palavras
    "statistics": {
        "input_edges": 2500000,
        "validated_edges": 2500000,
        "mst_edges": 5000,
        "communities_count": 20,
        "avg_community_size": 250.0
    }
}
```

**Fluxo interno:**

1. **Validação** (5 regras contrato): verifica tipos e estrutura
2. **Conversão**: peso → distância (1/peso)
3. **Ordenação**: por distância crescente
4. **Kruskal**: computa MST (reduz de 2.5M para ~5k arestas)
5. **Particionamento**: divide recursivamente até 20 comunidades

**Exceções:**

- `TypeError`: Se contrato de entrada violado (tipo incorreto)
- `ValueError`: Se dados inconsistentes (peso ≤ 0, lista vazia, etc)

### Exemplo de Uso

```python
from src.utils import FileHandler
from src.communities.pipeline import Phase3Pipeline

# Carregar grafo da Fase 2
with open("data/processed/graph_edges.pkl", "rb") as f:
    import pickle
    arestas = pickle.load(f)

# Detectar comunidades
pipeline = Phase3Pipeline(target_communities=20, min_community_size=150)
resultado = pipeline.run(arestas)

# Acessar comunidades
comunidades = resultado["communities"]
print(f"Comunidades geradas: {len(comunidades)}")

# Examinar primeira comunidade
primeira = comunidades[0]
print(f"Comunidade 1: {len(primeira)} palavras")
print(f"Termos: {sorted(primeira)[:20]}")

# Estatísticas
stats = resultado["statistics"]
print(f"Arestas reduzidas de {stats['input_edges']} para {stats['mst_edges']}")
```

---

## 🔌 Módulo: `exporter` (Auxiliar)

Conector da Fase 2 → Fase 3. Fornece função para importar dados processados.

### Funções Disponíveis

#### 1. `importar_dados_fase2(theme: str = "all") -> List[List]`

Carrega e retorna a lista plana de arestas da Fase 2.

**Parâmetros:**

- `theme`: Tema de documentos a carregar
  - `"all"`: Todas as categorias combinadas (padrão)
  - `"business"`: Apenas artigos de negócios
  - `"entertainment"`: Apenas artigos de entretenimento

**Retorno:** Lista plana de arestas:

```python
[
    ["market", "stock", 125],
    ["business", "trade", 98],
    ...
]
```

**Exemplo:**

```python
from src.graph.exporter import importar_dados_fase2

# Carregar grafo completo
arestas = importar_dados_fase2()
print(f"Carregadas {len(arestas)} arestas")

# Carregar apenas tema 'business'
arestas_business = importar_dados_fase2(theme="business")
print(f"Arestas de negócios: {len(arestas_business)}")
```

**Nota:** Se os arquivos `.pkl` não existirem, a função levanta `FileNotFoundError` com mensagem descritiva indicando qual arquivo está faltando.

---

## 📊 Resumo da Arquitetura (Fases 1-3)

```
Fase 1 (TextProcessor)
  ├─ Entrada: Arquivos .txt brutos
  ├─ Saída: documents.pkl com sets de tokens
  └─ Documentação: Seção "TextProcessor" acima

Fase 2 (GraphBuilder)
  ├─ Entrada: documents.pkl (Fase 1)
  ├─ Saída: graph_edges.pkl com lista de arestas
  └─ Documentação: Seção "GraphBuilder" acima

Fase 3 (Phase3Pipeline)
  ├─ Entrada: graph_edges.pkl (Fase 2)
  ├─ Saída: 20 comunidades de palavras relacionadas
  └─ Documentação: Seção "Phase3Pipeline" acima

Auxiliares:
  ├─ FileHandler: I/O genérico
  ├─ exporter: Conexão Fase 2 → Fase 3
  └─ stopwords: Gerenciador de palavras comuns
```

---

## ⚡ Referência Rápida

| Classe           | Método                   | Entrada                | Saída                        |
| ---------------- | ------------------------ | ---------------------- | ---------------------------- |
| `TextProcessor`  | `process_document()`     | `str` (texto)          | `Set[str]` (tokens)          |
| `GraphBuilder`   | `build()`                | `List[Dict]` (docs)    | `List[List]` (arestas)       |
| `Phase3Pipeline` | `run()`                  | `List[List]` (arestas) | `Dict` (comunidades)         |
| `FileHandler`    | `load_python_pickle()`   | `str` (caminho)        | `List[Dict]` ou `List[List]` |
| `exporter`       | `importar_dados_fase2()` | `str` (tema)           | `List[List]` (arestas)       |
