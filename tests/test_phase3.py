"""
Testes e validação do Phase3Pipeline (Detecção de Comunidades - Fase 3)

Reúne validações da nova arquitetura refatorada:
- Validação de contrato
- Conversão de pesos
- Cálculo MST
- Particionamento de comunidades
- Integração completa
"""

from src.communities import Phase3Pipeline


def test_validation_contract():
    """
    Testa validação de contrato com as 5 regras auditadas.
    """
    print("=" * 70)
    print("TESTE 1: Validação de Contrato")
    print("=" * 70)

    pipeline = Phase3Pipeline(verbose=False)
    checks = []

    # Check 1: Arestas válidas passam
    try:
        edges = [
            ["word1", "word2", 5.0],
            ["word2", "word3", 3.0],
        ]
        validated = pipeline._validate_contract(edges)
        checks.append(("Arestas válidas aceitas", True, "2 arestas passaram"))
    except Exception as e:
        checks.append(("Arestas válidas aceitas", False, str(e)))

    # Check 2: Lista vazia rejeitada
    try:
        pipeline._validate_contract([])
        checks.append(("Lista vazia rejeitada", False, "Não lançou erro"))
    except ValueError:
        checks.append(("Lista vazia rejeitada", True, "ValueError levantado"))

    # Check 3: Não-lista rejeitada
    try:
        pipeline._validate_contract("not a list")
        checks.append(("Não-lista rejeitada", False, "Não lançou erro"))
    except TypeError:
        checks.append(("Não-lista rejeitada", True, "TypeError levantado"))

    # Check 4: Aresta malformada (2 elementos) rejeitada
    try:
        pipeline._validate_contract([["word1", "word2"]])
        checks.append(("Aresta com 2 elementos rejeitada", False, "Não lançou erro"))
    except ValueError:
        checks.append(("Aresta com 2 elementos rejeitada", True, "ValueError levantado"))

    # Check 5: Peso negativo rejeitado
    try:
        pipeline._validate_contract([["word1", "word2", -5.0]])
        checks.append(("Peso negativo rejeitado", False, "Não lançou erro"))
    except ValueError:
        checks.append(("Peso negativo rejeitado", True, "ValueError levantado"))

    # Check 6: Peso zero rejeitado
    try:
        pipeline._validate_contract([["word1", "word2", 0.0]])
        checks.append(("Peso zero rejeitado", False, "Não lançou erro"))
    except ValueError:
        checks.append(("Peso zero rejeitado", True, "ValueError levantado"))

    # Check 7: Palavras não-string rejeitadas
    try:
        pipeline._validate_contract([[1, 2, 5.0]])
        checks.append(("Palavras não-string rejeitadas", False, "Não lançou erro"))
    except TypeError:
        checks.append(("Palavras não-string rejeitadas", True, "TypeError levantado"))

    # Check 8: Peso não-numérico rejeitado
    try:
        pipeline._validate_contract([["word1", "word2", "cinco"]])
        checks.append(("Peso não-numérico rejeitado", False, "Não lançou erro"))
    except TypeError:
        checks.append(("Peso não-numérico rejeitado", True, "TypeError levantado"))

    # Exibir resultados
    all_passed = all(check[1] for check in checks)
    for check_name, passed, detail in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}: {detail}")

    if all_passed:
        print(f"\n✅ Todos os testes de validação passaram!")
    else:
        print(f"\n❌ Alguns testes falharam")
        raise AssertionError("Validação de contrato com falhas")


def test_conversion_peso_distancia():
    """
    Testa conversão de pesos para distâncias (1/peso).
    """
    print("\n" + "=" * 70)
    print("TESTE 2: Conversão Peso → Distância")
    print("=" * 70)

    pipeline = Phase3Pipeline(verbose=False)
    checks = []

    # Check 1: Conversão básica
    edges = [
        ["word1", "word2", 2.0],
        ["word2", "word3", 5.0],
        ["word3", "word4", 10.0],
    ]
    distances = pipeline._convert_to_distances(edges)

    # Verificar valores
    expected_distances = [0.5, 0.2, 0.1]  # 1/2, 1/5, 1/10
    actual_distances = [d[2] for d in distances]

    for i, (expected, actual) in enumerate(zip(expected_distances, actual_distances)):
        tolerance = 1e-9
        match = abs(expected - actual) < tolerance
        checks.append((f"Aresta {i} convertida corretamente", match, f"{actual:.10f} ≈ {expected}"))

    # Check 2: Nomes de palavras preservados
    names_preserved = all(
        edges[i][0] == distances[i][0] and edges[i][1] == distances[i][1]
        for i in range(len(edges))
    )
    checks.append(("Nomes de palavras preservados", names_preserved, "Todos os pares mantidos"))

    # Exibir resultados
    all_passed = all(check[1] for check in checks)
    for check_name, passed, detail in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}: {detail}")

    if all_passed:
        print(f"\n✅ Conversão peso→distância validada!")
    else:
        print(f"\n❌ Alguns testes falharam")
        raise AssertionError("Conversão com falhas")


def test_ordenacao_distancia():
    """
    Testa ordenação por distância crescente.
    """
    print("\n" + "=" * 70)
    print("TESTE 3: Ordenação por Distância")
    print("=" * 70)

    pipeline = Phase3Pipeline(verbose=False)
    checks = []

    edges = [
        ["w1", "w2", 0.5],   # distância = 2.0
        ["w2", "w3", 0.1],   # distância = 10.0
        ["w3", "w4", 0.2],   # distância = 5.0
        ["w4", "w5", 1.0],   # distância = 1.0
    ]

    sorted_edges = pipeline._sort_by_distance(edges)

    # Extrair distâncias ordenadas
    distances_ordered = [e[2] for e in sorted_edges]
    expected_order = [0.1, 0.2, 0.5, 1.0]

    # Verificar que está em ordem crescente
    is_sorted = all(
        distances_ordered[i] <= distances_ordered[i + 1]
        for i in range(len(distances_ordered) - 1)
    )
    checks.append(("Arestas ordenadas crescente", is_sorted, f"Ordem: {distances_ordered}"))

    # Verificar valores
    tolerance = 1e-9
    values_match = all(
        abs(distances_ordered[i] - expected_order[i]) < tolerance
        for i in range(len(expected_order))
    )
    checks.append(("Valores de distância corretos", values_match, f"Obtido: {distances_ordered}"))

    # Exibir resultados
    all_passed = all(check[1] for check in checks)
    for check_name, passed, detail in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}: {detail}")

    if all_passed:
        print(f"\n✅ Ordenação validada!")
    else:
        print(f"\n❌ Alguns testes falharam")
        raise AssertionError("Ordenação com falhas")


def test_mst_kruskal():
    """
    Testa cálculo de MST via algoritmo de Kruskal.
    """
    print("\n" + "=" * 70)
    print("TESTE 4: MST via Kruskal")
    print("=" * 70)

    pipeline = Phase3Pipeline(verbose=False)
    checks = []

    # Teste 1: 3 nós, 3 arestas (1 redundante)
    edges = [
        ["w1", "w2", 1.0],
        ["w2", "w3", 2.0],
        ["w1", "w3", 3.0],  # Redundante
    ]
    mst = pipeline._compute_mst_kruskal(edges)

    # MST de 3 nós deve ter 2 arestas
    check1 = len(mst) == 2
    checks.append(("MST(3 nós): 2 arestas", check1, f"Obtido {len(mst)} arestas"))

    # Teste 2: Nós conectados
    nodes_in_mst = set()
    for a, b, _ in mst:
        nodes_in_mst.add(a)
        nodes_in_mst.add(b)

    expected_nodes = {"w1", "w2", "w3"}
    check2 = nodes_in_mst == expected_nodes
    checks.append(("Todos os nós conectados", check2, f"Nós: {nodes_in_mst}"))

    # Teste 3: 4 nós com 2 componentes desconexas
    edges_disconnected = [
        ["w1", "w2", 1.0],
        ["w3", "w4", 2.0],
    ]
    mst_disconnected = pipeline._compute_mst_kruskal(edges_disconnected)

    check3 = len(mst_disconnected) == 2
    checks.append(("MST(2 componentes): 2 arestas", check3, f"Obtido {len(mst_disconnected)} arestas"))

    # Teste 4: Arestas redundantes não aparecem na MST
    edges_with_cycle = [
        ["w1", "w2", 1.0],
        ["w2", "w3", 1.0],
        ["w3", "w1", 1.0],  # Fecha ciclo
    ]
    mst_cycle = pipeline._compute_mst_kruskal(edges_with_cycle)

    # MST de 3 nós com ciclo ainda tem 2 arestas
    check4 = len(mst_cycle) == 2
    checks.append(("Ciclo removido da MST", check4, f"Obtido {len(mst_cycle)} arestas"))

    # Exibir resultados
    all_passed = all(check[1] for check in checks)
    for check_name, passed, detail in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}: {detail}")

    if all_passed:
        print(f"\n✅ MST (Kruskal) validada!")
    else:
        print(f"\n❌ Alguns testes falharam")
        raise AssertionError("MST com falhas")


def test_pipeline_completo():
    """
    Testa o pipeline completo com dados válidos.
    """
    print("\n" + "=" * 70)
    print("TESTE 5: Pipeline Completo (Integração)")
    print("=" * 70)

    pipeline = Phase3Pipeline(verbose=False)
    checks = []

    # Teste 1: Dados simples
    edges = [
        ["apple", "banana", 5.0],
        ["banana", "cherry", 3.0],
        ["cherry", "date", 4.0],
        ["date", "elderberry", 2.0],
    ]

    try:
        result = pipeline.run(edges)
        check1 = True
        detail1 = "Pipeline executado sem erros"
    except Exception as e:
        check1 = False
        detail1 = str(e)

    checks.append(("Pipeline executa sem erro", check1, detail1))

    if check1:
        # Verificar estrutura
        has_mst = "mst_edges" in result
        has_communities = "communities" in result
        has_stats = "statistics" in result

        checks.append(("Resultado tem 'mst_edges'", has_mst, "Chave presente"))
        checks.append(("Resultado tem 'communities'", has_communities, "Chave presente"))
        checks.append(("Resultado tem 'statistics'", has_stats, "Chave presente"))

        # Verificar MST
        mst_count = len(result["mst_edges"])
        check_mst = mst_count == (len(set(w for e in edges for w in [e[0], e[1]])) - 1)
        checks.append(("MST tem n-1 arestas", check_mst, f"{mst_count} arestas para {len(edges)} nós"))

        # Verificar estatísticas
        stats = result["statistics"]
        check_stats = (
            stats["input_edges"] == 4 and
            stats["validated_edges"] == 4
        )
        checks.append((
            "Estatísticas corretas",
            check_stats,
            f"input={stats['input_edges']}, validated={stats['validated_edges']}"
        ))

    # Exibir resultados
    all_passed = all(check[1] for check in checks)
    for check_name, passed, detail in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}: {detail}")

    if all_passed:
        print(f"\n✅ Pipeline completo validado!")
    else:
        print(f"\n❌ Alguns testes falharam")
        raise AssertionError("Pipeline com falhas")


def test_contrato_violado():
    """
    Testa que o pipeline rejeita dados que violam o contrato.
    """
    print("\n" + "=" * 70)
    print("TESTE 6: Rejeição de Contrato Violado")
    print("=" * 70)

    pipeline = Phase3Pipeline(verbose=False)
    checks = []

    # Violação 1: Falta peso
    try:
        pipeline.run([["word1", "word2"]])
        checks.append(("Rejeita aresta com 2 elementos", False, "Não lançou erro"))
    except ValueError:
        checks.append(("Rejeita aresta com 2 elementos", True, "ValueError levantado"))

    # Violação 2: Peso inválido
    try:
        pipeline.run([["word1", "word2", "abc"]])
        checks.append(("Rejeita peso não-numérico", False, "Não lançou erro"))
    except TypeError:
        checks.append(("Rejeita peso não-numérico", True, "TypeError levantado"))

    # Violação 3: Peso negativo
    try:
        pipeline.run([["word1", "word2", -5.0]])
        checks.append(("Rejeita peso negativo", False, "Não lançou erro"))
    except ValueError:
        checks.append(("Rejeita peso negativo", True, "ValueError levantado"))

    # Exibir resultados
    all_passed = all(check[1] for check in checks)
    for check_name, passed, detail in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}: {detail}")

    if all_passed:
        print(f"\n✅ Rejeição de contrato violado validada!")
    else:
        print(f"\n❌ Alguns testes falharam")
        raise AssertionError("Rejeição com falhas")


def test_casos_extremos():
    """
    Testa casos extremos e edge cases.
    """
    print("\n" + "=" * 70)
    print("TESTE 7: Casos Extremos")
    print("=" * 70)

    pipeline = Phase3Pipeline(verbose=False)
    checks = []

    # Check 1: Uma única aresta
    try:
        result = pipeline.run([["w1", "w2", 1.0]])
        check1 = len(result["mst_edges"]) == 1
        checks.append(("Uma única aresta", check1, f"{len(result['mst_edges'])} arestas na MST"))
    except Exception as e:
        checks.append(("Uma única aresta", False, str(e)))

    # Check 2: Pesos muito grandes
    try:
        result = pipeline.run([
            ["w1", "w2", 1e10],
            ["w2", "w3", 1e11],
        ])
        check2 = "mst_edges" in result
        checks.append(("Pesos muito grandes (1e10+)", check2, "Pipeline executou"))
    except Exception as e:
        checks.append(("Pesos muito grandes (1e10+)", False, str(e)))

    # Check 3: Pesos muito pequenos
    try:
        result = pipeline.run([
            ["w1", "w2", 1e-10],
            ["w2", "w3", 1e-9],
        ])
        check3 = "mst_edges" in result
        checks.append(("Pesos muito pequenos (1e-10)", check3, "Pipeline executou"))
    except Exception as e:
        checks.append(("Pesos muito pequenos (1e-10)", False, str(e)))

    # Check 4: Palavras com caracteres especiais
    try:
        result = pipeline.run([
            ["café", "naïve", 1.0],
            ["naïve", "résumé", 2.0],
        ])
        check4 = len(result["mst_edges"]) == 2
        checks.append(("Caracteres especiais Unicode", check4, "Pipeline executou"))
    except Exception as e:
        checks.append(("Caracteres especiais Unicode", False, str(e)))

    # Exibir resultados
    all_passed = all(check[1] for check in checks)
    for check_name, passed, detail in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}: {detail}")

    if all_passed:
        print(f"\n✅ Casos extremos validados!")
    else:
        print(f"\n❌ Alguns testes falharam")
        raise AssertionError("Casos extremos com falhas")


# ======================================================================
# Execução dos testes
# ======================================================================

if __name__ == "__main__":
    try:
        test_validation_contract()
        test_conversion_peso_distancia()
        test_ordenacao_distancia()
        test_mst_kruskal()
        test_pipeline_completo()
        test_contrato_violado()
        test_casos_extremos()

        print("\n" + "=" * 70)
        print("✅ TODOS OS TESTES DE PHASE3 PASSARAM!")
        print("=" * 70)

    except AssertionError as e:
        print(f"\n❌ Testes falharam: {e}")
        exit(1)
