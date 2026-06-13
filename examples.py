"""
Exemplos de uso da biblioteca de pré-processamento.

Este módulo demonstra como utilizar as classes e funções
do pipeline de pré-processamento de forma independente.
"""

from src.preprocessing import TextProcessor
from src.utils import FileHandler
from typing import List, Dict, Any


def example_1_process_single_document():
    """
    Exemplo 1: Processar um único documento.
    """
    print("=" * 70)
    print("EXEMPLO 1: Processar um Único Documento")
    print("=" * 70)

    # Criar processador
    processor = TextProcessor(min_token_length=2, remove_numbers=True)

    # Texto de exemplo
    text = """
    Apple Inc. is planning to launch new products in 2024.
    The company has invested heavily in research and development.
    Apple's stock prices have been rising steadily this year.
    """

    # Processar
    tokens = processor.process_document(text)

    # Exibir resultado
    print(f"\nTexto original:\n{text}")
    print(f"\nTokens extraídos ({len(tokens)} palavras):")
    print(f"{sorted(tokens)}")
    print()


def example_2_process_batch():
    """
    Exemplo 2: Processar um lote de documentos.
    """
    print("=" * 70)
    print("EXEMPLO 2: Processar um Lote de Documentos")
    print("=" * 70)

    # Criar processador
    processor = TextProcessor(min_token_length=2, remove_numbers=True)

    # Documentos de exemplo
    documents = [
        {
            "id": "doc_001",
            "category": "business",
            "text": "The stock market had a strong performance this quarter. Investors were pleased with the earnings reports from major companies."
        },
        {
            "id": "doc_002",
            "category": "entertainment",
            "text": "The new movie received excellent reviews from critics and audiences. The lead actor's performance was outstanding and memorable."
        },
        {
            "id": "doc_003",
            "category": "business",
            "text": "Government announces new economic policies aimed at supporting small businesses and startups in the technology sector."
        }
    ]

    # Processar lote
    processed = processor.process_batch(documents)

    # Exibir resultado
    print(f"\nDocumentos processados: {len(processed)}\n")
    for doc in processed:
        print(f"ID: {doc['id']}")
        print(f"Categoria: {doc['category']}")
        print(f"Tokens ({len(doc['tokens'])}): {sorted(doc['tokens'])}")
        print()


def example_3_filter_stopwords():
    """
    Exemplo 3: Demonstrar remoção de stopwords.
    """
    print("=" * 70)
    print("EXEMPLO 3: Filtro de Stopwords")
    print("=" * 70)

    from src.preprocessing.stopwords import get_stopwords, is_stopword

    # Texto de exemplo
    text = "The quick brown fox jumps over the lazy dog. This is a test sentence."

    # Criar processador
    processor = TextProcessor()

    # Processar
    tokens = processor.process_document(text)

    print(f"\nTexto original:\n{text}")
    print(f"\nTokens após processamento:")
    print(f"Stopwords removidos: a, the, is, over, etc.")
    print(f"Tokens restantes ({len(tokens)}): {sorted(tokens)}")

    # Demonstrar função de verificação
    test_words = ["quick", "the", "fox", "is", "lazy"]
    print(f"\nVerificação de stopwords:")
    for word in test_words:
        result = "SIM" if is_stopword(word) else "NÃO"
        print(f"  '{word}' é stopword? {result}")

    print()


def example_4_save_load_formats():
    """
    Exemplo 4: Salvar e carregar em diferentes formatos.
    """
    print("=" * 70)
    print("EXEMPLO 4: Salvar e Carregar em Diferentes Formatos")
    print("=" * 70)

    # Criar dados de exemplo
    documents = [
        {
            "id": "ex_001",
            "category": "business",
            "tokens": {"market", "stock", "economy", "profit"}
        },
        {
            "id": "ex_002",
            "category": "entertainment",
            "tokens": {"movie", "actor", "film", "award"}
        }
    ]

    print("\nFormatos suportados:")
    print("  1. JSON: Legível e compatível com outras linguagens")
    print("  2. JSONL (JSON Lines): Ideal para processamento em stream")
    print("  3. Pickle: Preserva tipos nativos do Python (sets, etc.)")

    print("\nExemplo de estrutura:")
    print("  JSON/JSONL: tokens convertidos para listas ordenadas")
    print("  Pickle: tokens mantidos como sets (melhor performance)")

    print(f"\nDocumentos de exemplo: {len(documents)}")
    for doc in documents:
        print(f"  - {doc['id']}: {len(doc['tokens'])} tokens únicos")

    print()


def example_5_text_preprocessing_pipeline():
    """
    Exemplo 5: Demonstrar cada etapa do pipeline de pré-processamento.
    """
    print("=" * 70)
    print("EXEMPLO 5: Etapas do Pipeline de Pré-processamento")
    print("=" * 70)

    # Texto original
    original_text = """
    Banking Regulations and Financial Markets!!!
    The central bank announced new regulations...
    Interest rates dropped by 0.5% to 2.5%.
    """

    print(f"Texto original:\n{original_text}\n")
    print("Etapas do processamento:\n")

    processor = TextProcessor(min_token_length=2)

    # Etapa 1: Normalização
    step1 = " ".join(original_text.split())
    print(f"1. Normalização (remove espaços extras):\n   '{step1}'\n")

    # Etapa 2: Minúsculas
    step2 = step1.lower()
    print(f"2. Converter para minúsculas:\n   '{step2}'\n")

    # Etapa 3: Remover pontuação
    import string
    translator = str.maketrans("", "", string.punctuation)
    step3 = step2.translate(translator)
    print(f"3. Remover pontuação:\n   '{step3}'\n")

    # Etapa 4: Tokenizar
    step4 = step3.split()
    print(f"4. Tokenizar:\n   {step4}\n")

    # Etapa 5: Filtrar inválidos
    step5 = [t for t in step4 if len(t) >= 2 and not t.isdigit()]
    print(f"5. Filtrar tokens inválidos (comprimento < 2 ou apenas números):\n   {step5}\n")

    # Etapa 6: Remover stopwords
    final = processor.process_document(original_text)
    print(f"6. Remover stopwords e gerar set final:\n   {sorted(final)}\n")


def main():
    """
    Executa todos os exemplos.
    """
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  EXEMPLOS DE USO - PIPELINE DE PRÉ-PROCESSAMENTO DE TEXTOS".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    # Executar exemplos
    example_1_process_single_document()
    print()

    example_2_process_batch()
    print()

    example_3_filter_stopwords()
    print()

    example_4_save_load_formats()
    print()

    example_5_text_preprocessing_pipeline()
    print()

    print("=" * 70)
    print("✨ Exemplos concluídos!")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
