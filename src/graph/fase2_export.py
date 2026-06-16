"""
Conector da Fase 2 -> Fase 3.

O notebook da Fase 3 espera uma função `importar_dados_fase2()` que devolve a
lista plana de arestas [[palavra_A, palavra_B, peso], ...]. No notebook essa
função está com dados de exemplo "chumbados". Para usar os dados REAIS gerados
por esta fase, basta substituir a função do notebook por esta — ou importar
daqui:

    from src.graph.fase2_export import importar_dados_fase2
    grafo_linear_bruto = importar_dados_fase2()

A saída respeita o contrato auditado no Passo 0 da Fase 3:
palavras como `str` e peso como `int` > 0.
"""

import os
import json
import pickle
from typing import Any, List

# Este arquivo agora vive em src/graph/, então subimos dois níveis
# (src/graph -> src -> raiz) para localizar a pasta data/ na raiz do projeto.
_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_GRAPH_PKL = os.path.join(_BASE, "data", "processed", "graph_edges.pkl")
_GRAPH_JSON = os.path.join(_BASE, "data", "processed", "graph_edges.json")


def importar_dados_fase2() -> List[List[Any]]:
    """
    Carrega a lista plana de arestas gerada pela Fase 2.

    Tenta primeiro o pickle (preserva tipos nativos); se não existir, recorre
    ao JSON. Lança FileNotFoundError caso nenhum dos dois exista — nesse caso,
    rode antes: `python build_graph.py`.

    Returns:
        [[palavra_A, palavra_B, peso], ...]
    """
    if os.path.exists(_GRAPH_PKL):
        with open(_GRAPH_PKL, "rb") as f:
            return pickle.load(f)

    if os.path.exists(_GRAPH_JSON):
        with open(_GRAPH_JSON, "r", encoding="utf-8") as f:
            return json.load(f)

    raise FileNotFoundError(
        "Grafo da Fase 2 não encontrado. Gere-o antes com: python build_graph.py"
    )


if __name__ == "__main__":
    arestas = importar_dados_fase2()
    print(f"Arestas carregadas: {len(arestas)}")
    print("Primeiras 5:", arestas[:5])
