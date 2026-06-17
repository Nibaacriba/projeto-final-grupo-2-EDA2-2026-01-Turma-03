"""
Testes da Fase 2: Construção do grafo de coocorrência.

Validam a lógica de coocorrência do GraphBuilder e verificam se a saída
respeita o CONTRATO da Fase 3 (as 5 regras auditadas no Passo 0).
Seguindo o padrão de design visual e tratamento de logs da Fase 3.
"""

from src.graph import GraphBuilder


def test_graph_builder_logic():
    """
    Testa as regras lógicas e propriedades matemáticas do construtor de grafos.
    """
    print("=" * 70)
    print("TESTE 1: Propriedades e Lógica do Grafo (GraphBuilder)")
    print("=" * 70)

    try:
        builder = GraphBuilder()
        checks = []

        # Check 1: Coocorrência Básica e Contagem Combinatória Kn
        docs_1 = [{"id": "d1", "category": "x", "tokens": {"a", "b", "c"}}]
        edges_1 = builder.build(docs_1)
        check1 = len(edges_1) == 3 and all(p == 1 for *_, p in edges_1)
        checks.append(("Coocorrência básica e pesos unitários C(3,2)", check1, f"Geradas {len(edges_1)} arestas"))

        # Check 2: Incremento de peso cumulativo
        docs_2 = [
            {"id": "d1", "category": "x", "tokens": {"a", "b"}},
            {"id": "d2", "category": "y", "tokens": {"a", "b"}},
            {"id": "d3", "category": "y", "tokens": {"a", "c"}},
        ]
        edges_2 = builder.build(docs_2)
        weights = {(a, b): p for a, b, p in edges_2}
        check2 = weights.get(("a", "b")) == 2 and weights.get(("a", "c")) == 1
        checks.append(("Incremento de peso cumulativo inter-documentos", check2, f"a-b peso: {weights.get(('a', 'b'))}"))

        # Check 3: Aresta Canônica Lexicográfica (Sem duplicados reflexivos)
        docs_3 = [
            {"id": "d1", "category": "x", "tokens": {"b", "a"}},
            {"id": "d2", "category": "y", "tokens": {"a", "b"}},
        ]
        edges_3 = builder.build(docs_3)
        check3 = len(edges_3) == 1 and edges_3[0][0] == "a" and edges_3[0][1] == "b"
        checks.append(("Normalização canônica lexicográfica (palavra_a < palavra_b)", check3, f"Aresta gerada: {edges_3}"))

        # Check 4: Filtro de ruído por peso mínimo (min_weight)
        docs_4 = [
            {"id": "d1", "category": "x", "tokens": {"a", "b"}},
            {"id": "d2", "category": "y", "tokens": {"a", "b"}},
            {"id": "d3", "category": "y", "tokens": {"c", "d"}},
        ]
        edges_4 = GraphBuilder(min_weight=2).build(docs_4)
        check4 = len(edges_4) == 1 and edges_4[0][:2] == ["a", "b"]
        checks.append(("Filtro de ruído ativo (min_weight=2)", check4, f"Sobreviventes: {len(edges_4)} arestas"))

        # Check 5: Ordenação estável descendente por peso
        edges_sorted = builder.build(docs_2)
        weights_list = [p for *_, p in edges_sorted]
        check5 = weights_list == sorted(weights_list, reverse=True)
        checks.append(("Ordenação padrão por peso decrescente", check5, f"Pesos: {weights_list}"))

        # Exibir resultados no padrão Fase 3
        all_passed = all(check[1] for check in checks)
        for check_name, passed, detail in checks:
            status = "✅" if passed else "❌"
            print(f"{status} {check_name}: {detail}")

        if not all_passed:
            raise AssertionError("Falha nas propriedades matemáticas do GraphBuilder.")

    except Exception as e:
        print(f"❌ Erro na lógica do GraphBuilder: {e}")
        raise


def test_contrato_fase3():
    """
    Valida a saída contra o contrato de 5 regras exigido pela infraestrutura da Fase 3.
    """
    print("\n" + "=" * 70)
    print("TESTE 2: Validação Rígida de Contrato para a Fase 3")
    print("=" * 70)

    try:
        docs = [
            {"id": "d1", "category": "x", "tokens": {"banco", "selic", "juros"}},
            {"id": "d2", "category": "y", "tokens": {"banco", "selic"}},
        ]
        grafo = GraphBuilder().build(docs)
        checks = []

        # Regra 1: Objeto raiz é uma lista
        r1 = isinstance(grafo, list)
        checks.append(("Regra 1: Estrutura raiz é uma Lista", r1, type(grafo).__name__))

        # Regra 2: Lista não-vazia
        r2 = len(grafo) > 0
        checks.append(("Regra 2: Lista de arestas não está vazia", r2, f"Contém {len(grafo)} elementos"))

        if r1 and r2:
            r3, r4, r5 = True, True, True
            for aresta in grafo:
                # Regra 3: Sublista de exatamente tamanho 3
                if not isinstance(aresta, list) or len(aresta) != 3:
                    r3 = False
                else:
                    a, b, peso = aresta
                    # Regra 4: Vértices posicionado em 0 e 1 são Strings
                    if not isinstance(a, str) or not isinstance(b, str):
                        r4 = False
                    # Regra 5: Peso numérico estritamente maior que zero
                    if not isinstance(peso, (int, float)) or peso <= 0:
                        r5 = False

            checks.append(("Regra 3: Sublistas de tamanho exato igual a 3", r3, "Formato [u, v, w] mantido"))
            checks.append(("Regra 4: Vértices u e v mapeados como Strings", r4, "Tipagem str validada"))
            checks.append(("Regra 5: Pesos numéricos estritamente positivos (> 0)", r5, "Valores matemáticos consistentes"))

        # Exibir resultados
        all_passed = all(check[1] for check in checks)
        for check_name, passed, detail in checks:
            status = "✅" if passed else "❌"
            print(f"{status} {check_name}: {detail}")

        if not all_passed:
            raise AssertionError("A saída gerada quebrou o contrato de barramento da Fase 3.")

    except Exception as e:
        print(f"❌ Erro na validação do contrato da Fase 2: {e}")
        raise


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  FASE 2: TESTES DE CONSTRUÇÃO DO GRAFO (PADRONIZADO)".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    try:
        test_graph_builder_logic()
        test_contrato_fase3()
        print("\n" + "=" * 70)
        print("✅ TODOS OS TESTES DA FASE 2 PASSARAM!")
        print("=" * 70)
    except AssertionError as e:
        print(f"\n❌ Testes falharam: {e}")
        exit(1)
