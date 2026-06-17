from collections import defaultdict
from itertools import combinations
from typing import Any, Dict, List, Tuple

# Tipos auxiliares para legibilidade das assinaturas
Aresta = List[Any]              # [palavra_A: str, palavra_B: str, peso: int]
ListaArestas = List[Aresta]     # [[A, B, peso], ...]  (lista plana de arestas)


class GraphBuilder:
    """
    Constrói o grafo de coocorrência de palavras a partir dos documentos
    pré-processados da Fase 1.

    Atributos:
        min_weight: Peso mínimo para uma aresta entrar no grafo final.
            - min_weight=1 (padrão) mantém o grafo COMPLETO (toda coocorrência,
              literal à especificação da Fase 2).
            - min_weight>=2 descarta arestas que ocorreram em um único documento
              (ruído), gerando um grafo muito menor e mais limpo para a MST.
    """

    def __init__(self, min_weight: int = 1):
        """
        Inicializa o construtor do grafo.

        Args:
            min_weight: Peso mínimo de uma aresta para ser mantida (padrão: 1).
        """
        if not isinstance(min_weight, int) or min_weight < 1:
            raise ValueError("min_weight deve ser um inteiro >= 1.")
        self.min_weight = min_weight

    def build(self, documents: List[Dict[str, Any]]) -> ListaArestas:
        """
        Constrói a lista plana de arestas de coocorrência.

        Args:
            documents: Lista de documentos da Fase 1. Cada documento é um dict
                no formato {"id": str, "category": str, "tokens": set[str]}.

        Returns:
            Lista plana de arestas [[palavra_A, palavra_B, peso], ...], ordenada
            de forma determinística (por peso decrescente e, em empate, ordem
            alfabética). O peso é sempre um `int` > 0.
        """
        # Dicionário usado APENAS internamente para acumular os pesos com acesso O(1).
        coocorrencias: Dict[Tuple[str, str], int] = defaultdict(int)

        for doc in documents:
            tokens = doc.get("tokens")

            # Validação protetiva: ignora documentos nulos ou que não tenham
            # pelo menos 2 palavras para formar um par.
            if not tokens or len(tokens) < 2:
                continue

            # Ordena os tokens para que cada par seja gerado em uma única
            # direção canônica (A, B) com A < B — evita arestas duplicadas
            # invertidas (A-B e B-A contam como a mesma aresta).
            tokens_ordenados = sorted(tokens)

            # Usa a biblioteca padrão do Python para gerar as combinações de
            # pares únicos de forma otimizada (executada internamente em C).
            for palavra_a, palavra_b in combinations(tokens_ordenados, 2):
                par = (palavra_a, palavra_b)
                coocorrencias[par] += 1

        # Converte o acumulador para a lista plana de arestas do contrato,
        # aplicando o filtro de peso mínimo.
        arestas: ListaArestas = [
            [palavra_a, palavra_b, peso]
            for (palavra_a, palavra_b), peso in coocorrencias.items()
            if peso >= self.min_weight
        ]

        # Ordenação determinística: arestas mais fortes primeiro.
        arestas.sort(key=lambda a: (-a[2], a[0], a[1]))

        return arestas

    @staticmethod
    def to_adjacency_list(
        arestas: ListaArestas,
    ) -> Dict[str, List[List[Any]]]:
        """
        (Opcional) Converte a lista plana de arestas em uma lista de adjacência.
        """
        adjacencia: Dict[str, List[List[Any]]] = defaultdict(list)
        for palavra_a, palavra_b, peso in arestas:
            adjacencia[palavra_a].append([palavra_b, peso])
            adjacencia[palavra_b].append([palavra_a, peso])
        return dict(adjacencia)

    @staticmethod
    def estatisticas(arestas: ListaArestas) -> Dict[str, Any]:
        """
        Calcula estatísticas descritivas do grafo gerado.
        """
        if not arestas:
            return {
                "vertices": 0,
                "arestas": 0,
                "peso_max": 0,
                "peso_medio": 0.0,
                "top_5": [],
            }

        vertices = set()
        soma_pesos = 0
        peso_max = 0
        for palavra_a, palavra_b, peso in arestas:
            vertices.add(palavra_a)
            vertices.add(palavra_b)
            soma_pesos += peso
            if peso > peso_max:
                peso_max = peso

        return {
            "vertices": len(vertices),
            "arestas": len(arestas),
            "peso_max": peso_max,
            "peso_medio": round(soma_pesos / len(arestas), 2),
            "top_5": arestas[:5],
        }
