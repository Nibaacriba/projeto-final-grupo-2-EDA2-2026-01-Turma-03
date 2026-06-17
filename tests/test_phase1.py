"""
Testes da Fase 1: Pré-processamento de textos.

Testa a qualidade dos dados pré-processados salvos exclusivamente no formato Pickle (.pkl).
Seguindo o padrão de design visual e tratamento de logs da Fase 3.
"""

from typing import List, Dict, Any
from src.utils import FileHandler


def test_pickle_output() -> List[Dict[str, Any]]:
    """
    Testa o carregamento e validação de contrato e estrutura do arquivo Pickle.
    """
    print("=" * 70)
    print("TESTE 1: Validação do Arquivo Pickle (.pkl)")
    print("=" * 70)

    try:
        documents = FileHandler.load_python_pickle("data/processed/documents.pkl")
        checks = []

        # Check 1: Carregamento do arquivo
        check1 = isinstance(documents, list) and len(documents) > 0
        checks.append(("Arquivo carregado e não vazio", check1, f"Total: {len(documents)} docs"))

        if check1:
            # Check 2: Chaves obrigatórias e estrutura
            structure_ok = True
            type_ok = True
            for doc in documents[:5]:  # Amostragem de segurança
                if not ("id" in doc and "category" in doc and "tokens" in doc):
                    structure_ok = False
                if not isinstance(doc["tokens"], set):
                    type_ok = False

            checks.append(("Chaves obrigatórias nos dicionários", structure_ok, "id, category, tokens presentes"))
            checks.append(("Tipagem de tokens como Set nativo", type_ok, "Garante busca em tempo O(1)"))

            # Check 3: Presença equilibrada de categorias bbc
            categories = {doc["category"] for doc in documents}
            check3 = "business" in categories and "entertainment" in categories
            checks.append(("Presença de categorias obrigatórias", check3, f"Detectadas: {list(categories)}"))

        # Exibir resultados no padrão Fase 3
        all_passed = all(check[1] for check in checks)
        for check_name, passed, detail in checks:
            status = "✅" if passed else "❌"
            print(f"{status} {check_name}: {detail}")

        if all_passed:
            print(f"\n✅ Validação do arquivo Pickle concluída com sucesso!")
            return documents
        else:
            raise AssertionError("O arquivo serializado viola a integridade da Fase 1.")

    except Exception as e:
        print(f"❌ Erro no Teste do Pickle: {e}")
        raise


def test_data_quality(documents: List[Dict[str, Any]]) -> None:
    """
    Testa os critérios de qualidade do texto limpo gerado pelo TextProcessor.
    """
    print("\n" + "=" * 70)
    print("TESTE 2: Critérios de Qualidade de Dados (PLN)")
    print("=" * 70)

    try:
        checks = []

        # Check 1: IDs únicos
        ids = [doc["id"] for doc in documents]
        unique_ids = len(set(ids))
        check1 = unique_ids == len(documents)
        checks.append(("IDs únicos no corpus", check1, f"{unique_ids}/{len(documents)}"))

        # Check 2: Categorias válidas
        valid_categories = {"business", "entertainment"}
        categories = {doc["category"] for doc in documents}
        check2 = categories == valid_categories
        checks.append(("Categorias válidas mapeadas", check2, str(categories)))

        # Check 3: Tokens não vazios
        empty_token_docs = [d for d in documents if len(d["tokens"]) == 0]
        check3 = len(empty_token_docs) == 0
        checks.append(("Ausência de documentos sem palavras", check3, f"{len(empty_token_docs)} vazios"))

        # Check 4: Tokens contêm strings válidas (Filtro e Lematização)
        invalid_tokens = 0
        for doc in documents:
            for token in doc["tokens"]:
                if not isinstance(token, str) or len(token) < 2:
                    invalid_tokens += 1
        check4 = invalid_tokens == 0
        checks.append(("Tokens válidos (letras e len >= 2)", check4, f"{invalid_tokens} inválidos"))

        # Check 5: Não contém nenhuma stopword residual
        common_stopwords = {"the", "a", "an", "and", "or", "is", "are"}
        stopword_violations = 0
        for doc in documents:
            for token in doc["tokens"]:
                if token in common_stopwords:
                    stopword_violations += 1
        check5 = stopword_violations == 0
        checks.append(("Exclusão total de stopwords", check5, f"{stopword_violations} violações"))

        # Exibir resultados
        all_passed = all(check[1] for check in checks)
        for check_name, passed, detail in checks:
            status = "✅" if passed else "❌"
            print(f"{status} {check_name}: {detail}")

        if all_passed:
            print(f"\n✅ Todos os testes de qualidade de PLN passaram!")
        else:
            print(f"\n❌ Alguns testes de consistência falharam")
            raise AssertionError("Os dados processados violam as restrições da Fase 1.")

    except Exception as e:
        print(f"❌ Erro no Teste de Qualidade: {e}")
        raise


def test_integration_pipeline(documents: List[Dict[str, Any]]) -> None:
    """
    Testa a integração da Fase 1 com os requisitos de entrada para a Fase 2.
    """
    print("\n" + "=" * 70)
    print("TESTE 3: Integração e Prontidão de Contrato para Grafo")
    print("=" * 70)

    try:
        checks = []

        # Check 1: Tipagem do objeto para barramento
        check1 = isinstance(documents, list)
        checks.append(("Objeto de barramento é uma lista", check1, type(documents).__name__))

        # Check 2: Volume mínimo de dados para gerar coocorrência estável
        check2 = len(documents) >= 500
        checks.append(("Volume de corpus suficiente para a Fase 2", check2, f"{len(documents)} documentos"))

        # Check 3: Avaliar densidade de tokens únicos por documento (evita underfitting)
        avg_tokens = sum(len(d["tokens"]) for d in documents) / len(documents)
        check3 = avg_tokens >= 10
        checks.append(("Densidade léxica média por artigo", check3, f"{avg_tokens:.2f} tokens/doc"))

        # Exibir resultados
        all_passed = all(check[1] for check in checks)
        for check_name, passed, detail in checks:
            status = "✅" if passed else "❌"
            print(f"{status} {check_name}: {detail}")

        if all_passed:
            print(f"\n✅ Contrato de barramento e integração validado para a Fase 2!")
        else:
            raise AssertionError("Os dados da Fase 1 não estão prontos para integração.")

    except Exception as e:
        print(f"❌ Erro no Teste de Integração: {e}")
        raise


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  FASE 1: TESTES DE PRÉ-PROCESSAMENTO (PADRONIZADO)".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    try:
        docs = test_pickle_output()
        test_data_quality(docs)
        test_integration_pipeline(docs)
        print("\n" + "=" * 70)
        print("✅ TODOS OS TESTES DA FASE 1 PASSARAM!")
        print("=" * 70)
    except AssertionError as e:
        print(f"\n❌ Testes falharam: {e}")
        exit(1)
