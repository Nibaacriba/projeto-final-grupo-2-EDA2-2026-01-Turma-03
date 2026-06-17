"""
Conector da Fase 2 -> Fase 3.

O notebook da Fase 3 espera uma função `importar_dados_fase2()` que devolve a
lista plana de arestas [[palavra_A, palavra_B, peso], ...]. No notebook essa
função está com dados de exemplo "chumbados". Para usar os dados REAIS gerados
por esta fase, basta substituir a função do notebook por esta — ou importar
daqui:

    from src.graph.exporter import importar_dados_fase2
    grafo_linear_bruto = importar_dados_fase2()

A saída respeita o contrato auditado no Passo 0 da Fase 3:
palavras como `str` e peso como `int` > 0.
"""

import os
import json
import pickle
from typing import Any, List, Tuple

# Este arquivo agora vive em src/graph/, então subimos dois níveis
# (src/graph -> src -> raiz) para localizar a pasta data/ na raiz do projeto.
_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _paths_for_theme(theme: str) -> Tuple[str, str]:
    """
    Retorna os caminhos para os arquivos de grafo de um tema específico.

    Args:
        theme: Tema ('business', 'entertainment', ou 'all')

    Returns:
        Tupla (caminho_pickle, caminho_json)
    """
    if theme in {"business", "entertainment"}:
        return (
            os.path.join(_BASE, "data", "processed", f"graph_edges_{theme}.pkl"),
            os.path.join(_BASE, "data", "processed", f"graph_edges_{theme}.json"),
        )

    return (
        os.path.join(_BASE, "data", "processed", "graph_edges.pkl"),
        os.path.join(_BASE, "data", "processed", "graph_edges.json"),
    )


def importar_dados_fase2() -> List[List[Any]]:
    """
    Carrega a lista plana de arestas gerada pela Fase 2.

    Tenta primeiro o pickle (preserva tipos nativos); se não existir, recorre
    ao JSON. Lança FileNotFoundError caso nenhum dos dois exista — nesse caso,
    rode antes: `python build_graph.py`.

    Returns:
        [[palavra_A, palavra_B, peso], ...]
    """
    theme = os.environ.get("GRAPH_THEME", "all").strip().lower()
    graph_pkl, graph_json = _paths_for_theme(theme)

    if os.path.exists(graph_pkl):
        with open(graph_pkl, "rb") as f:
            return pickle.load(f)

    if os.path.exists(graph_json):
        with open(graph_json, "r", encoding="utf-8") as f:
            return json.load(f)

    raise FileNotFoundError(
        "Grafo da Fase 2 não encontrado. Gere-o antes com: python build_graph.py"
    )


if __name__ == "__main__":
    arestas = importar_dados_fase2()
    print(f"Arestas carregadas: {len(arestas)}")
    print("Primeiras 5:", arestas[:5])
