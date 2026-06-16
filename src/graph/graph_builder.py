"""
Construtor do grafo de coocorrência (Fase 2 do pipeline).

Esta é a etapa que liga a Fase 1 (pré-processamento de textos, que entrega um
`set` de tokens únicos por documento) à Fase 3 (detecção de comunidades via
MST/Kruskal, implementada no notebook).

Contrato de saída exigido pela Fase 3
-------------------------------------
A Fase 3 valida e consome uma **lista plana de arestas** no formato:

    [[palavra_A, palavra_B, peso], ...]

Regras do contrato (auditadas no "Passo 0" do notebook):
    1. O objeto raiz é uma `list`.
    2. A lista não é vazia.
    3. Cada aresta é uma sublista com exatamente 3 elementos.
    4. Os índices [0] e [1] (as palavras) são `str`.
    5. O índice [2] (o peso/força de coocorrência) é um número > 0.

Por isso a representação interna aqui é a **lista plana de arestas**, e não um
dicionário aninhado de adjacência: é o formato direto que o próximo módulo lê.

Lógica de construção
--------------------
Para cada documento (notícia), gera-se todas as combinações de pares de
palavras distintas que aparecem juntas naquele documento. Cada vez que um par
(A, B) reaparece em um novo documento, o peso da aresta é incrementado.

Para evitar registrar a mesma aresta nos dois sentidos (A-B e B-A), as palavras
de cada par são ordenadas, gerando uma chave canônica única (palavra menor,
palavra maior) — exatamente como sugerido no exemplo da documentação (API.md).

Sem dependências externas: apenas tipos nativos do Python.
"""

from collections import defaultdict
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
                (Use o `.pkl` da Fase 1: ele preserva o tipo `set` nativo.)

        Returns:
            Lista plana de arestas [[palavra_A, palavra_B, peso], ...], ordenada
            de forma determinística (por peso decrescente e, em empate, ordem
            alfabética). O peso é sempre um `int` > 0.
        """
        # Dicionário usado APENAS internamente para acumular os pesos com acesso
        # O(1). A "lista de adjacência" mencionada no enunciado é representada
        # aqui pela chave canônica do par; a saída é convertida para lista plana.
        coocorrencias: Dict[Tuple[str, str], int] = defaultdict(int)

        for doc in documents:
            tokens = doc.get("tokens")
            if tokens is None:
                continue

            # Ordena os tokens para que cada par seja gerado em uma única
            # direção canônica (A, B) com A < B — evita arestas duplicadas
            # invertidas (A-B e B-A contam como a mesma aresta).
            tokens_ordenados = sorted(tokens)
            n = len(tokens_ordenados)

            # Gera todas as combinações de pares dentro do mesmo documento.
            for i in range(n):
                palavra_a = tokens_ordenados[i]
                for j in range(i + 1, n):
                    palavra_b = tokens_ordenados[j]
                    par = (palavra_a, palavra_b)

                    # "Se não tiver aresta, cria; se já existir, incrementa o
                    # peso." defaultdict(int) faz exatamente isso: ausente == 0.
                    coocorrencias[par] += 1

        # Converte o acumulador para a lista plana de arestas do contrato,
        # aplicando o filtro de peso mínimo.
        arestas: ListaArestas = [
            [palavra_a, palavra_b, peso]
            for (palavra_a, palavra_b), peso in coocorrencias.items()
            if peso >= self.min_weight
        ]

        # Ordenação determinística: arestas mais fortes primeiro. Facilita
        # inspeção e torna a saída reprodutível entre execuções.
        arestas.sort(key=lambda a: (-a[2], a[0], a[1]))

        return arestas

    @staticmethod
    def to_adjacency_list(
        arestas: ListaArestas,
    ) -> Dict[str, List[List[Any]]]:
        """
        (Opcional) Converte a lista plana de arestas em uma lista de adjacência.

        Útil apenas se algum consumidor preferir a visão por vértice. A Fase 3
        do projeto NÃO usa este formato — ela espera a lista plana de arestas.

        Args:
            arestas: Lista plana [[A, B, peso], ...].

        Returns:
            Dicionário {palavra: [[vizinho, peso], ...]} (grafo não-direcionado,
            cada aresta aparece nos dois vértices).
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

        Args:
            arestas: Lista plana [[A, B, peso], ...].

        Returns:
            Dicionário com número de vértices, arestas, peso máximo/médio e
            as 5 conexões mais fortes.
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
            # A lista já vem ordenada por peso desc, então o topo é o início.
            "top_5": arestas[:5],
        }
