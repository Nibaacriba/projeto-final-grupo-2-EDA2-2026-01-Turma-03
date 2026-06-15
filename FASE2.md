# Fase 2 — Construção do Grafo de Coocorrência

Esta é a etapa que liga a **Fase 1** (pré-processamento, feita pelo Gabriel) à
**Fase 3** (detecção de comunidades via MST/Kruskal, no notebook).

## O que esta fase faz

Recebe os documentos pré-processados da Fase 1 — onde cada notícia já virou um
`set` de tokens únicos com sua categoria — e cruza, **dentro de cada documento**,
todos os pares de palavras. Cada vez que um par (A, B) reaparece em uma nova
notícia, o peso da aresta é incrementado.

> "pega as ocorrências entre duas palavras num mesmo documento/notícia; se não
> tiver aresta, cria; se tiver, incrementa o peso."

## Formato de saída (o contrato com a Fase 3)

A saída é uma **lista plana de arestas**, exatamente o formato que o Passo 0 do
notebook valida e que os passos seguintes consomem:

```python
[
  ['company', 'firm', 128],
  ['chief', 'executive', 111],
  ...
]
```

- índices `[0]` e `[1]`: palavras (`str`), sempre ordenadas (par canônico, então
  A‑B e B‑A são a mesma aresta);
- índice `[2]`: peso de coocorrência (`int` > 0).

Internamente o acúmulo usa um `dict` (chave = par canônico) para incremento em
O(1) — a ideia de "lista de adjacência" do enunciado. A entrega final, porém, é
convertida para a **lista plana de arestas**, porque é isso que a Fase 3 espera
(o notebook diz explicitamente: *"Lista Plana de Arestas em vez de dicionários
aninhados"*).

## Arquivos desta fase

| Arquivo | Papel |
| :-- | :-- |
| `src/graph/graph_builder.py` | Classe `GraphBuilder`: a lógica de coocorrência. |
| `build_graph.py` | Orquestrador: carrega a Fase 1, constrói e salva o grafo. |
| `fase2_export.py` | `importar_dados_fase2()` — conector que entrega a lista para o notebook da Fase 3. |
| `tests_graph.py` | Testes da lógica + validação das 5 regras do contrato da Fase 3. |
| `data/processed/graph_edges.pkl` | Grafo pronto (pickle, formato preferido). |
| `data/processed/graph_edges.json` | Mesmo grafo, legível por humanos. |

## Como rodar

```bash
# 1. (Pré-requisito) Gerar os dados da Fase 1, se ainda não existirem:
python main.py

# 2. Construir o grafo (grafo COMPLETO, todas as coocorrências):
python build_graph.py

# Variações de limiar de peso mínimo:
python build_graph.py 2   # descarta arestas de peso 1 (pares que só apareceram juntos 1x)
python build_graph.py 3   # mantém só arestas com peso >= 3

# 3. Rodar os testes desta fase:
python tests_graph.py
```

No notebook da Fase 3, basta trocar a função de exemplo por:

```python
from fase2_export import importar_dados_fase2
grafo_linear_bruto = importar_dados_fase2()
```

## ⚠️ Decisão importante: tamanho do grafo x limiar de peso

O grafo **completo** (`min_weight=1`) do dataset tem **~6 milhões de arestas**
(~93 MB em pickle, ~153 MB em JSON). Cerca de **78% delas têm peso 1** — ou seja,
o par de palavras apareceu junto em um único documento (ruído).

- O **código** mantém o padrão fiel à especificação: `min_weight=1` = grafo
  completo, sem perder informação.
- O **arquivo já incluído** neste pacote (`graph_edges.pkl`/`.json`) foi gerado
  com **`min_weight=2`** (1,34 M de arestas, ~21 MB). Isso remove apenas os pares
  hapax (peso 1) e deixa o grafo leve o suficiente para o Kruskal em Python puro
  rodar bem no Colab — sem mudar as conexões realmente relevantes.

Para gerar a versão completa, é só rodar `python build_graph.py 1`. A escolha do
limiar é do grupo; documentei o tradeoff para a decisão ser consciente.

> Observação adicional: termos como `there` e `time` ainda aparecem entre as
> conexões mais fortes. Se quiserem um grafo mais limpo para a detecção de
> tópicos, vale adicioná-los às stopwords da Fase 1 (o `README.md` do projeto
> mostra como, no Exemplo 3 do `API.md`).
