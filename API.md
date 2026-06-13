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

| Parâmetro          | Tipo   | Padrão | Descrição                                          |
| :----------------- | :----- | :----- | :------------------------------------------------- |
| `min_token_length` | `int`  | `2`    | Comprimento mínimo de um token válido              |
| `remove_numbers`   | `bool` | `True` | Se `True`, remove tokens que contêm apenas números |

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
  Lê e retorna o conteúdo textual completo de um arquivo `.txt`.

- **`list_files_in_directory(directory: str, extension: str = ".txt") -> List[str]`**
  Varre um diretório e retorna uma lista com os nomes dos arquivos filtrados pela extensão informada.

- **`save_json(data: List[Dict], output_path: str, indent: int = 2) -> None`**
  Serializa os dados no formato JSON tradicional. Nota: Converte estruturas `set` para `list` internamente durante a escrita.

- **`save_jsonl(data: List[Dict], output_path: str) -> None`**
  Salva os dados no formato JSON Lines (uma linha independente por registro de documento).

- **`save_python_pickle(data: List[Dict], output_path: str) -> None`**
  Serializa o objeto utilizando a biblioteca nativa `pickle` do Python. **Mantém a tipagem original de estruturas como `set` intactas**.

- **`load_python_pickle(input_path: str) -> List[Dict]`**
  Carrega e desserializa um arquivo `.pkl` gerado, trazendo a estrutura de dados de volta à memória operacional.

---

## 🚫 Módulo: `stopwords`

Gerenciador interno responsável por mitigar palavras funcionais de alta frequência que não agregam valor à identificação de tópicos. Suporta dicionários combinados de Inglês e Português (~150+ palavras).

### Funções Disponíveis

- **`get_stopwords() -> set`**: Retorna o conjunto completo de stopwords cadastradas no sistema.
- **`is_stopword(word: str) -> bool`**: Retorna um booleano avaliando se a palavra específica informada faz parte do conjunto de stopwords.

---

## 📚 Exemplos Avançados de Uso

### Exemplo 1: Instanciação Avançada e Restritiva

Caso queira aumentar o rigor do filtro limpando palavras com menos de 4 letras:

```python
from src.preprocessing import TextProcessor

# Filtro estrito: remove palavras curtas e ignora números
strict_processor = TextProcessor(min_token_length=4, remove_numbers=True)

text = "Python 3.12 is a core language for data structures."
tokens = strict_processor.process_document(text)
print(tokens)
# Saída esperada: {'python', 'core', 'language', 'data', 'structures'}
```

### Exemplo 2: Extração manual e geração de dicionário de frequências de coocorrência

Este exemplo serve para guiar o início do raciocínio da lógica que será implementada na **Fase 2**:

```python
from src.utils import FileHandler
from collections import defaultdict

# Carrega os sets limpos da Fase 1
documents = FileHandler.load_python_pickle("data/processed/documents.pkl")
cooccurrence_matrix = defaultdict(int)

for doc in documents:
    # Ordena os tokens para evitar registrar caminhos duplicados invertidos (ex: A-B e B-A)
    tokens = sorted(list(doc["tokens"]))

    # Gera combinações de pares de palavras dentro do mesmo documento
    for i in range(len(tokens)):
        for j in range(i + 1, len(tokens)):
            pair = (tokens[i], tokens[j])
            cooccurrence_matrix[pair] += 1

# Exibe as 5 coocorrências de palavras mais fortes do dataset
top_pairs = sorted(cooccurrence_matrix.items(), key=lambda x: x[1], reverse=True)[:5]
print("Top 5 conexões fortes para o Grafo:")
for (w1, w2), count in top_pairs:
    print(f"  {w1} <--> {w2}: {count} vezes juntas")
```

### Exemplo 3: Customizando a Lista de Stopwords em Tempo de Execução

Caso note que termos recorrentes do dataset da BBC como "news" ou "said" estão poluindo o grafo, você pode adicioná-los diretamente antes de processar os arquivos:

```python
from src.preprocessing.stopwords import get_stopwords
from src.preprocessing import TextProcessor

# Adicionar novos termos ao Set global de stopwords
stopwords_set = get_stopwords()
stopwords_set.update({"said", "news", "year"})

# O TextProcessor passará a respeitar a lista atualizada automaticamente
processor = TextProcessor()
```

---

## ⏱️ Troubleshooting Técnico

### Erro: `ModuleNotFoundError: No module named 'src'`

- **Causa:** O interpretador do Python foi chamado a partir de uma pasta interna (ex: de dentro da pasta `src/preprocessing/`).
- **Solução:** O terminal obrigatoriamente deve estar situado na **raiz do projeto** (`projeto-final-grupo-2-...`) ao disparar a execução de qualquer script.

### Diferença de contagem de tokens entre o JSON e o Pickle

- **Causa:** O formato JSON não possui suporte nativo à estrutura `set` (Conjunto). Por essa razão, ao salvar em JSON, o `FileHandler` converte os tokens em uma lista comum para manter o arquivo válido.
- **Solução:** Para qualquer processamento matemático posterior no grafo, priorize ler o arquivo `documents.pkl` via `FileHandler.load_python_pickle()`.

```

```
