"""
Testes de validação da Fase 2 (construção do grafo de coocorrência).

Executa testes unitários da lógica de coocorrência e verifica se a saída
respeita o CONTRATO da Fase 3 (as 5 regras auditadas no Passo 0 do notebook).

Uso:
    python tests_graph.py
"""

from src.graph import GraphBuilder


def _falhou(msg: str) -> None:
    raise AssertionError(msg)


def teste_coocorrencia_basica():
    """Pares dentro do mesmo documento devem ter peso 1 (uma ocorrência)."""
    docs = [{"id": "d1", "category": "x", "tokens": {"a", "b", "c"}}]
    arestas = GraphBuilder().build(docs)
    # 3 tokens -> C(3,2) = 3 arestas
    if len(arestas) != 3:
        _falhou(f"Esperava 3 arestas, obtive {len(arestas)}")
    for *_, peso in arestas:
        if peso != 1:
            _falhou(f"Peso esperado 1, obtido {peso}")
    print("✓ teste_coocorrencia_basica")


def teste_incremento_de_peso():
    """Par que reaparece em outro documento deve ter o peso incrementado."""
    docs = [
        {"id": "d1", "category": "x", "tokens": {"a", "b"}},
        {"id": "d2", "category": "y", "tokens": {"a", "b"}},
        {"id": "d3", "category": "y", "tokens": {"a", "c"}},
    ]
    arestas = GraphBuilder().build(docs)
    pesos = {(a, b): p for a, b, p in arestas}
    if pesos.get(("a", "b")) != 2:
        _falhou(f"Par a-b deveria ter peso 2, obtive {pesos.get(('a','b'))}")
    if pesos.get(("a", "c")) != 1:
        _falhou(f"Par a-c deveria ter peso 1, obtive {pesos.get(('a','c'))}")
    print("✓ teste_incremento_de_peso")


def teste_aresta_canonica_sem_duplicar_invertida():
    """A-B e B-A devem ser a MESMA aresta (par ordenado canônico)."""
    docs = [
        {"id": "d1", "category": "x", "tokens": {"b", "a"}},
        {"id": "d2", "category": "y", "tokens": {"a", "b"}},
    ]
    arestas = GraphBuilder().build(docs)
    if len(arestas) != 1:
        _falhou(f"Esperava 1 aresta única, obtive {len(arestas)}")
    a, b, p = arestas[0]
    if (a, b) != ("a", "b") or p != 2:
        _falhou(f"Aresta canônica incorreta: {arestas[0]}")
    print("✓ teste_aresta_canonica_sem_duplicar_invertida")


def teste_filtro_peso_minimo():
    """min_weight deve descartar arestas abaixo do limiar."""
    docs = [
        {"id": "d1", "category": "x", "tokens": {"a", "b"}},
        {"id": "d2", "category": "y", "tokens": {"a", "b"}},
        {"id": "d3", "category": "y", "tokens": {"c", "d"}},
    ]
    arestas = GraphBuilder(min_weight=2).build(docs)
    # Só a-b (peso 2) sobrevive; c-d (peso 1) é descartado.
    if len(arestas) != 1 or arestas[0][:2] != ["a", "b"]:
        _falhou(f"Filtro min_weight=2 falhou: {arestas}")
    print("✓ teste_filtro_peso_minimo")


def teste_ordenacao_por_peso():
    """A saída deve vir ordenada por peso decrescente."""
    docs = [
        {"id": "d1", "category": "x", "tokens": {"a", "b"}},
        {"id": "d2", "category": "y", "tokens": {"a", "b"}},
        {"id": "d3", "category": "y", "tokens": {"a", "c"}},
    ]
    arestas = GraphBuilder().build(docs)
    pesos = [p for *_, p in arestas]
    if pesos != sorted(pesos, reverse=True):
        _falhou(f"Arestas não ordenadas por peso desc: {pesos}")
    print("✓ teste_ordenacao_por_peso")


def teste_contrato_fase3():
    """
    Valida a saída contra as 5 regras do contrato da Fase 3 (Passo 0).
    """
    docs = [
        {"id": "d1", "category": "x", "tokens": {"banco", "selic", "juros"}},
        {"id": "d2", "category": "y", "tokens": {"banco", "selic"}},
    ]
    grafo = GraphBuilder().build(docs)

    # Regra 1: objeto raiz é uma lista
    if not isinstance(grafo, list):
        _falhou("Regra 1 violada: saída não é list")
    # Regra 2: não vazia
    if len(grafo) == 0:
        _falhou("Regra 2 violada: lista vazia")
    for i, aresta in enumerate(grafo):
        # Regra 3: sublista de exatamente 3 elementos
        if not isinstance(aresta, list) or len(aresta) != 3:
            _falhou(f"Regra 3 violada no índice {i}: {aresta}")
        a, b, peso = aresta
        # Regra 4: índices 0 e 1 são strings
        if not isinstance(a, str) or not isinstance(b, str):
            _falhou(f"Regra 4 violada no índice {i}: {aresta}")
        # Regra 5: peso é número > 0
        if not isinstance(peso, (int, float)) or peso <= 0:
            _falhou(f"Regra 5 violada no índice {i}: {aresta}")
    print("✓ teste_contrato_fase3 (5 regras do Passo 0)")


def main():
    print("🧪 Testes da Fase 2 (Grafo de Coocorrência)")
    print("=" * 60)
    teste_coocorrencia_basica()
    teste_incremento_de_peso()
    teste_aresta_canonica_sem_duplicar_invertida()
    teste_filtro_peso_minimo()
    teste_ordenacao_por_peso()
    teste_contrato_fase3()
    print("=" * 60)
    print("✅ Todos os testes passaram.")


if __name__ == "__main__":
    main()
