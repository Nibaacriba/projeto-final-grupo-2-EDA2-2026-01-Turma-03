"""
Módulo de construção de grafos (Fase 2 do pipeline).

Recebe os documentos pré-processados da Fase 1 (set de tokens por notícia) e
constrói o grafo de coocorrência de palavras na forma de uma LISTA PLANA DE
ARESTAS [[palavra_A, palavra_B, peso], ...], que é o formato consumido e
validado pela Fase 3 (detecção de comunidades via MST/Kruskal).

Exporta:
- GraphBuilder: construtor do grafo de coocorrência.
"""

from .graph_builder import GraphBuilder

__all__ = ["GraphBuilder"]
