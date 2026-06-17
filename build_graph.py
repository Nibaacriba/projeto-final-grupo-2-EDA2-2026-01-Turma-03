"""
Orquestrador da Fase 2: construção do grafo de coocorrência.

O script:
1. Carrega os documentos pré-processados da Fase 1 (data/processed/documents.pkl).
    O `.pkl` é preferido porque preserva o tipo nativo `set` dos tokens, sem
    necessidade de tratamento extra.
2. Constrói a lista plana de arestas de coocorrência via GraphBuilder.
3. Salva o grafo em data/processed/ nos formatos:
     - graph_edges.pkl   (lista de listas nativa, ideal para a Fase 3)
     - graph_edges.json  (mesma lista, legível por humanos)
4. Imprime estatísticas e as conexões mais fortes.

Opcionalmente, é possível filtrar por categoria (ex.: business ou
entertainment) para gerar grafos separados por tema.
"""

import os
import sys
import json
import pickle
from pathlib import Path

from src.graph import GraphBuilder
from src.preprocessing import TextProcessor


# Configurações
BASE_DIR = Path(__file__).resolve().parent
DATA_PROCESSED_PATH = BASE_DIR / "data" / "processed"
DOCUMENTS_PKL = DATA_PROCESSED_PATH / "documents.pkl"
RAW_DATA_PATH = BASE_DIR / "data" / "raw"
GRAPH_PKL = DATA_PROCESSED_PATH / "graph_edges.pkl"
GRAPH_JSON = DATA_PROCESSED_PATH / "graph_edges.json"

# Peso mínimo padrão de uma aresta (1 = grafo completo, literal à Fase 2).
# Pode ser sobrescrito pelo primeiro argumento de linha de comando.
MIN_WEIGHT_DEFAULT = 1
CATEGORY_DEFAULT = "all"


def carregar_documentos(caminho_pkl: str):
    """Carrega os documentos pré-processados a partir do pickle da Fase 1."""
    if not os.path.exists(caminho_pkl):
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho_pkl}\n"
            f"Rode primeiro a Fase 1 com: python main.py"
        )
    with open(caminho_pkl, "rb") as f:
        return pickle.load(f)


def carregar_documentos_raw(categoria: str):
    """Carrega documentos diretamente da pasta raw quando o pickle não existe."""
    pasta = str(RAW_DATA_PATH)
    categorias = [categoria] if categoria != CATEGORY_DEFAULT else ["business", "entertainment"]
    processor = TextProcessor()
    documentos = []

    for cat in categorias:
        cat_dir = os.path.join(pasta, cat)
        if not os.path.isdir(cat_dir):
            continue

        for nome_arquivo in sorted(os.listdir(cat_dir)):
            if not nome_arquivo.lower().endswith(".txt"):
                continue

            caminho = os.path.join(cat_dir, nome_arquivo)
            with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
                texto = f.read()

            documentos.append(
                {
                    "id": os.path.splitext(nome_arquivo)[0],
                    "category": cat,
                    "tokens": processor.process_document(texto),
                }
            )

    if not documentos:
        raise FileNotFoundError(
            f"Nenhum documento encontrado em {RAW_DATA_PATH} para a categoria '{categoria}'."
        )

    return documentos


def salvar_grafo(arestas, caminho_pkl: str, caminho_json: str) -> None:
    """Salva a lista plana de arestas em pickle e em JSON (lista de listas)."""
    os.makedirs(os.path.dirname(str(caminho_pkl)), exist_ok=True)

    with open(caminho_pkl, "wb") as f:
        pickle.dump(arestas, f)

    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(arestas, f, ensure_ascii=False)


def filtrar_documentos_por_categoria(documentos, categoria: str):
    """Filtra documentos por categoria; 'all' mantém o corpus inteiro."""
    if categoria == CATEGORY_DEFAULT:
        return documentos

    return [doc for doc in documentos if doc.get("category") == categoria]


def main():
    # Lê o peso mínimo do argumento de linha de comando, se fornecido.
    min_weight = MIN_WEIGHT_DEFAULT
    categoria = CATEGORY_DEFAULT
    if len(sys.argv) > 1:
        try:
            min_weight = int(sys.argv[1])
        except ValueError:
            categoria = sys.argv[1].strip().lower()
            if categoria not in {"all", "business", "entertainment"}:
                print(
                    f"⚠️  Argumento inválido '{sys.argv[1]}'. "
                    f"Usando categoria={categoria} apenas se ela existir nos documentos."
                )

    print("🚀 Fase 2: Construção do grafo de coocorrência")
    print("=" * 60)
    print(f"Peso mínimo das arestas (min_weight): {min_weight}")
    print(f"Categoria selecionada: {categoria}")

    # Etapa 1: Carregar documentos da Fase 1
    print("\n📖 Carregando documentos pré-processados...")
    documentos = None
    if categoria == CATEGORY_DEFAULT and DOCUMENTS_PKL.exists():
        documentos = carregar_documentos(str(DOCUMENTS_PKL))
        print(f"✅ {len(documentos)} documentos carregados de {DOCUMENTS_PKL}")
    else:
        documentos = carregar_documentos_raw(categoria)
        print(f"✅ {len(documentos)} documentos carregados de {RAW_DATA_PATH}")

    documentos = filtrar_documentos_por_categoria(documentos, categoria)
    print(f"✅ {len(documentos)} documentos após filtro por categoria")

    # Etapa 2: Construir o grafo
    print("\n🔗 Construindo arestas de coocorrência...")
    builder = GraphBuilder(min_weight=min_weight)
    arestas = builder.build(documentos)
    print(f"✅ Grafo construído: {len(arestas)} arestas")

    # Etapa 3: Salvar
    print("\n💾 Salvando grafo...")
    if categoria == CATEGORY_DEFAULT:
        caminho_pkl = GRAPH_PKL
        caminho_json = GRAPH_JSON
    else:
        caminho_pkl = DATA_PROCESSED_PATH / f"graph_edges_{categoria}.pkl"
        caminho_json = DATA_PROCESSED_PATH / f"graph_edges_{categoria}.json"

    salvar_grafo(arestas, caminho_pkl, caminho_json)
    print(f"  ✓ Pickle: {caminho_pkl}")
    print(f"  ✓ JSON:   {caminho_json}")

    # Etapa 4: Estatísticas
    stats = GraphBuilder.estatisticas(arestas)
    print("\n📊 Estatísticas do Grafo:")
    print("=" * 60)
    print(f"Vértices (palavras únicas): {stats['vertices']}")
    print(f"Arestas (conexões):         {stats['arestas']}")
    print(f"Peso máximo:                {stats['peso_max']}")
    print(f"Peso médio:                 {stats['peso_medio']}")
    print("\nTop 5 conexões mais fortes:")
    for palavra_a, palavra_b, peso in stats["top_5"]:
        print(f"  {palavra_a} <--> {palavra_b}: {peso}")
    print("=" * 60)

    print("\n✨ Fase 2 concluída! A lista plana de arestas está pronta para a Fase 3.")


if __name__ == "__main__":
    main()
