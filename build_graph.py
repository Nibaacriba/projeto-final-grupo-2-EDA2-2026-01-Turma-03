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
"""

import os
import sys
import json
import pickle

from src.graph import GraphBuilder


# Configurações
DATA_PROCESSED_PATH = "data/processed"
DOCUMENTS_PKL = os.path.join(DATA_PROCESSED_PATH, "documents.pkl")
GRAPH_PKL = os.path.join(DATA_PROCESSED_PATH, "graph_edges.pkl")
GRAPH_JSON = os.path.join(DATA_PROCESSED_PATH, "graph_edges.json")

# Peso mínimo padrão de uma aresta (1 = grafo completo, literal à Fase 2).
# Pode ser sobrescrito pelo primeiro argumento de linha de comando.
MIN_WEIGHT_DEFAULT = 1


def carregar_documentos(caminho_pkl: str):
    """Carrega os documentos pré-processados a partir do pickle da Fase 1."""
    if not os.path.exists(caminho_pkl):
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho_pkl}\n"
            f"Rode primeiro a Fase 1 com: python main.py"
        )
    with open(caminho_pkl, "rb") as f:
        return pickle.load(f)


def salvar_grafo(arestas, caminho_pkl: str, caminho_json: str) -> None:
    """Salva a lista plana de arestas em pickle e em JSON (lista de listas)."""
    os.makedirs(os.path.dirname(caminho_pkl), exist_ok=True)

    with open(caminho_pkl, "wb") as f:
        pickle.dump(arestas, f)

    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(arestas, f, ensure_ascii=False)


def main():
    # Lê o peso mínimo do argumento de linha de comando, se fornecido.
    min_weight = MIN_WEIGHT_DEFAULT
    if len(sys.argv) > 1:
        try:
            min_weight = int(sys.argv[1])
        except ValueError:
            print(f"⚠️  Argumento inválido '{sys.argv[1]}'. Usando min_weight={min_weight}.")

    print("🚀 Fase 2: Construção do grafo de coocorrência")
    print("=" * 60)
    print(f"Peso mínimo das arestas (min_weight): {min_weight}")

    # Etapa 1: Carregar documentos da Fase 1
    print("\n📖 Carregando documentos pré-processados...")
    documentos = carregar_documentos(DOCUMENTS_PKL)
    print(f"✅ {len(documentos)} documentos carregados de {DOCUMENTS_PKL}")

    # Etapa 2: Construir o grafo
    print("\n🔗 Construindo arestas de coocorrência...")
    builder = GraphBuilder(min_weight=min_weight)
    arestas = builder.build(documentos)
    print(f"✅ Grafo construído: {len(arestas)} arestas")

    # Etapa 3: Salvar
    print("\n💾 Salvando grafo...")
    salvar_grafo(arestas, GRAPH_PKL, GRAPH_JSON)
    print(f"  ✓ Pickle: {GRAPH_PKL}")
    print(f"  ✓ JSON:   {GRAPH_JSON}")

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
