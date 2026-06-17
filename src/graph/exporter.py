from pathlib import Path
import os
import pickle
from typing import Any, List

# Definição do diretório base do projeto para garantir caminhos absolutos robustos
_BASE = Path(__file__).resolve().parent.parent.parent


def _get_pkl_path(theme: str) -> str:
    """
    Retorna o caminho do arquivo Pickle (.pkl) baseado estritamente no mapeamento de temas.

    Conforme a arquitetura:
    - 'business' -> graph_edges_business.pkl
    - 'entertainment' -> graph_edges_entertainment.pkl
    - 'all' (Padrão) -> graph_edges.pkl
    """
    if theme == "business":
        return os.path.join(_BASE, "data", "processed", "graph_edges_business.pkl")
    elif theme == "entertainment":
        return os.path.join(_BASE, "data", "processed", "graph_edges_entertainment.pkl")

    # Caso padrão mapeado na arquitetura para o dataset global
    return os.path.join(_BASE, "data", "processed", "graph_edges.pkl")


def importar_dados_fase2() -> List[List[Any]]:
    """
    Carrega e importa os dados de arestas do grafo gerados na Fase 2.
    O formato exclusivo utilizado para leitura é o Pickle (.pkl).

    Returns:
        List[List]: Uma lista plana de arestas no formato [[palavra1, palavra2, peso], ...].

    Raises:
        FileNotFoundError: Caso o arquivo .pkl correspondente ao tema não seja encontrado.
    """
    # Recupera o tema atual configurado no ambiente (default: 'all')
    theme = os.environ.get("GRAPH_THEME", "all").strip().lower()
    graph_pkl = _get_pkl_path(theme)

    if os.path.exists(graph_pkl):
        with open(graph_pkl, "rb") as f:
            dados = pickle.load(f)
            # Garantia absoluta de contrato: força a conversão interna de cada aresta para lista
            return [list(aresta) for aresta in dados]

    raise FileNotFoundError(
        f"[ERRO] O arquivo de dados principal da Fase 2 não foi encontrado em: {graph_pkl}\n"
        f"Certifique-se de que a Fase 2 foi executada e gerou os arquivos .pkl para o tema '{theme}'."
    )
