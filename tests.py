"""
Testes e validação do pipeline de pré-processamento.

Este módulo fornece testes básicos para validar a qualidade
dos dados processados e demonstra como consumi-los.
"""

import json
from typing import List, Dict, Any

from src.utils import FileHandler


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

    print("\n" + "=" * 70)
    print("✨ Testes concluídos!")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
