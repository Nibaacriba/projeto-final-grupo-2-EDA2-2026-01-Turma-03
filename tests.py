"""
Testes e validação do pipeline.

Reúne os testes das duas fases:
- Fase 1: qualidade dos dados pré-processados (JSON/JSONL/Pickle).
- Fase 2: lógica de coocorrência do grafo e validação do contrato da Fase 3.
"""

import json
from typing import List, Dict, Any

from src.utils import FileHandler
from src.graph import GraphBuilder


def test_json_output():
    """
    Testa o carregamento e validação do arquivo JSON.
    """
    print("=" * 70)
    print("TESTE 1: Validação do Arquivo JSON")
    print("=" * 70)

    try:
        with open("data/processed/documents.json", "r", encoding="utf-8") as f:
            documents = json.load(f)

        print(f"✅ Arquivo JSON carregado com sucesso")
        print(f"   Total de documentos: {len(documents)}")

        # Validar estrutura
        for i, doc in enumerate(documents[:3]):
            assert "id" in doc, "Campo 'id' não encontrado"
            assert "category" in doc, "Campo 'category' não encontrado"
            assert "tokens" in doc, "Campo 'tokens' não encontrado"
            assert isinstance(doc["tokens"], list), "Tokens deve ser lista"

        print(f"✅ Estrutura validada (primeiros 3 documentos OK)")

        # Estatísticas
        total_tokens = sum(len(doc["tokens"]) for doc in documents)
        unique_tokens = set()
        for doc in documents:
            unique_tokens.update(doc["tokens"])

        print(f"   Total de tokens: {total_tokens}")
        print(f"   Vocabulário único: {len(unique_tokens)}")

    except Exception as e:
        print(f"❌ Erro: {e}")


def test_jsonl_output():
    """
    Testa o carregamento e validação do arquivo JSONL.
    """
    print("\n" + "=" * 70)
    print("TESTE 2: Validação do Arquivo JSONL")
    print("=" * 70)

    try:
        documents = []
        with open("data/processed/documents.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                documents.append(json.loads(line))

        print(f"✅ Arquivo JSONL carregado com sucesso")
        print(f"   Total de documentos: {len(documents)}")
        print(f"   Cada linha é um documento JSON válido")

        # Verificar primeiros documentos
        categories_count = {}
        for doc in documents:
            category = doc["category"]
            categories_count[category] = categories_count.get(category, 0) + 1

        print(f"   Documentos por categoria:")
        for category, count in sorted(categories_count.items()):
            print(f"     - {category}: {count}")

    except Exception as e:
        print(f"❌ Erro: {e}")


def test_pickle_output():
    """
    Testa o carregamento e validação do arquivo pickle.
    """
    print("\n" + "=" * 70)
    print("TESTE 3: Validação do Arquivo Pickle")
    print("=" * 70)

    try:
        documents = FileHandler.load_python_pickle("data/processed/documents.pkl")

        print(f"✅ Arquivo pickle carregado com sucesso")
        print(f"   Total de documentos: {len(documents)}")

        # Verificar estrutura (sets em vez de listas)
        for doc in documents[:3]:
            assert isinstance(doc["tokens"], set), "Tokens devem ser sets no pickle"

        print(f"✅ Estrutura validada (tokens como sets)")

        # Mostrar exemplo
        print(f"\nExemplo de documento com tokens como set:")
        print(f"   ID: {documents[0]['id']}")
        print(f"   Categoria: {documents[0]['category']}")
        print(f"   Tokens ({len(documents[0]['tokens'])}): {sorted(list(documents[0]['tokens']))[:10]}...")

    except Exception as e:
        print(f"❌ Erro: {e}")


def test_data_quality():
    """
    Testa a qualidade dos dados processados.
    """
    print("\n" + "=" * 70)
    print("TESTE 4: Qualidade dos Dados")
    print("=" * 70)

    try:
        with open("data/processed/documents.json", "r", encoding="utf-8") as f:
            documents = json.load(f)

        # Verificações
        checks = []

        # Check 1: IDs únicos
        ids = [doc["id"] for doc in documents]
        unique_ids = len(set(ids))
        check1 = unique_ids == len(documents)
        checks.append(("IDs únicos", check1, f"{unique_ids}/{len(documents)}"))

        # Check 2: Categorias válidas
        valid_categories = {"business", "entertainment"}
        categories = {doc["category"] for doc in documents}
        check2 = categories == valid_categories
        checks.append(("Categorias válidas", check2, str(categories)))

        # Check 3: Tokens não vazios
        empty_token_docs = [d for d in documents if len(d["tokens"]) == 0]
        check3 = len(empty_token_docs) == 0
        checks.append(("Documentos sem tokens vazios", check3, f"{len(empty_token_docs)} vazios"))

        # Check 4: Tokens contêm strings
        invalid_tokens = 0
        for doc in documents:
            for token in doc["tokens"]:
                if not isinstance(token, str) or len(token) < 2:
                    invalid_tokens += 1
        check4 = invalid_tokens == 0
        checks.append(("Tokens válidos (strings com len >= 2)", check4, f"{invalid_tokens} inválidos"))

        # Check 5: Não contém stopwords comuns
        common_stopwords = {"the", "a", "an", "and", "or", "is", "are"}
        stopword_violations = 0
        for doc in documents:
            for token in doc["tokens"]:
                if token in common_stopwords:
                    stopword_violations += 1
        check5 = stopword_violations == 0
        checks.append(("Sem stopwords comuns", check5, f"{stopword_violations} violações"))

        # Exibir resultados
        all_passed = all(check[1] for check in checks)

        for check_name, passed, detail in checks:
            status = "✅" if passed else "❌"
            print(f"{status} {check_name}: {detail}")

        if all_passed:
            print(f"\n✅ Todos os testes de qualidade passaram!")
        else:
            print(f"\n⚠️  Alguns testes falharam")

    except Exception as e:
        print(f"❌ Erro: {e}")


def test_integration_for_graph_building():
    """
    Simula como a próxima etapa (construção de grafo) consumirá os dados.
    """
    print("\n" + "=" * 70)
    print("TESTE 5: Integração com Construção de Grafo")
    print("=" * 70)

    try:
        # Carregar usando pickle (melhor para próxima etapa)
        documents = FileHandler.load_python_pickle("data/processed/documents.pkl")

        print(f"✅ Dados carregados para construção de grafo")
        print(f"   Total de documentos: {len(documents)}")

        # Simular construção de grafo
        word_cooccurrence = {}
        total_pairs = 0

        for doc in documents:
            tokens = sorted(list(doc["tokens"]))

            # Criar pares de coocorrência
            for i in range(len(tokens)):
                for j in range(i + 1, len(tokens)):
                    pair = (tokens[i], tokens[j])
                    word_cooccurrence[pair] = word_cooccurrence.get(pair, 0) + 1
                    total_pairs += 1

        print(f"✅ Simulação de grafo de coocorrência:")
        print(f"   Total de pares únicos: {len(word_cooccurrence)}")
        print(f"   Total de ocorrências de pares: {total_pairs}")

        # Top 10 coocorrências
        top_pairs = sorted(
            word_cooccurrence.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        print(f"\n   Top 10 coocorrências mais frequentes:")
        for (word1, word2), count in top_pairs:
            print(f"     - ({word1}, {word2}): {count}")

        print(f"\n✅ Dados prontos para construção de grafo!")

    except Exception as e:
        print(f"❌ Erro: {e}")


# ======================================================================
# Fase 2 — Testes do grafo de coocorrência (movidos de tests_graph.py)
#
# Validam a lógica de coocorrência do GraphBuilder e verificam se a saída
# respeita o CONTRATO da Fase 3 (as 5 regras auditadas no Passo 0 do notebook).
# Diferente dos testes acima, estes levantam AssertionError em caso de falha.
# ======================================================================

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


def test_graph_fase2():
    """
    Executa todos os testes da Fase 2 (grafo de coocorrência).
    """
    print("\n" + "=" * 70)
    print("TESTE 6: Fase 2 — Grafo de Coocorrência")
    print("=" * 70)

    try:
        teste_coocorrencia_basica()
        teste_incremento_de_peso()
        teste_aresta_canonica_sem_duplicar_invertida()
        teste_filtro_peso_minimo()
        teste_ordenacao_por_peso()
        teste_contrato_fase3()
        print("\n✅ Todos os testes da Fase 2 passaram (contrato da Fase 3 respeitado)!")
    except AssertionError as e:
        print(f"❌ Falha em teste da Fase 2: {e}")


def main():
    """
    Executa todos os testes.
    """
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  TESTES E VALIDAÇÃO DO PIPELINE".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    test_json_output()
    test_jsonl_output()
    test_pickle_output()
    test_data_quality()
    test_integration_for_graph_building()
    test_graph_fase2()

    print("\n" + "=" * 70)
    print("✨ Testes concluídos!")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
