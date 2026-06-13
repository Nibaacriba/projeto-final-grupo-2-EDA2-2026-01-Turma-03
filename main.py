"""
Arquivo principal do projeto de PLN com Grafos.

Orquestra o pipeline de extração e pré-processamento de textos.

Uso:
    python main.py

O script:
1. Lê os arquivos de texto dos diretórios data/raw/
2. Processa cada documento através do pipeline
3. Salva os resultados em data/processed/
"""

import os
from pathlib import Path
from typing import List, Dict, Any

from src.preprocessing import TextProcessor
from src.utils import FileHandler


# Configurações do projeto
DATA_RAW_PATH = "data/raw"
DATA_PROCESSED_PATH = "data/processed"
CATEGORIES = ["business", "entertainment"]

# Configurações do processador
MIN_TOKEN_LENGTH = 2
REMOVE_NUMBERS = True


def load_raw_documents(raw_path: str, categories: List[str]) -> List[Dict[str, Any]]:
    """
    Carrega documentos brutos dos diretórios de categorias.

    Args:
        raw_path: Caminho do diretório raw.
        categories: Lista de categorias a processar.

    Returns:
        Lista de documentos com estrutura:
        {
            "id": str,
            "category": str,
            "text": str
        }
    """
    documents = []

    for category in categories:
        category_path = FileHandler.get_file_path(raw_path, category)

        if not os.path.exists(category_path):
            print(f"⚠️  Categoria '{category}' não encontrada em {category_path}")
            continue

        try:
            # Listar arquivos da categoria
            files = FileHandler.list_files_in_directory(category_path)
            print(f"📁 Categoria '{category}': {len(files)} arquivos encontrados")

            for filename in files:
                file_path = FileHandler.get_file_path(category_path, filename)

                try:
                    # Ler arquivo
                    text = FileHandler.read_text_file(file_path)

                    # Extrair ID do nome do arquivo (ex: "001.txt" -> "001")
                    file_id = Path(filename).stem

                    # Criar documento
                    document = {
                        "id": f"{category}_{file_id}",
                        "category": category,
                        "text": text
                    }
                    documents.append(document)

                except Exception as e:
                    print(f"❌ Erro ao processar {filename}: {e}")
                    continue

        except Exception as e:
            print(f"❌ Erro ao processar categoria '{category}': {e}")
            continue

    return documents


def process_documents(
    documents: List[Dict[str, Any]],
    processor: TextProcessor
) -> List[Dict[str, Any]]:
    """
    Processa uma lista de documentos.

    Args:
        documents: Lista de documentos brutos.
        processor: Instância de TextProcessor.

    Returns:
        Lista de documentos processados com tokens.
    """
    print("\n🔄 Iniciando processamento de documentos...")

    processed_documents = processor.process_batch(documents)

    print(f"✅ {len(processed_documents)} documentos processados com sucesso")

    return processed_documents


def save_processed_documents(
    documents: List[Dict[str, Any]],
    output_path: str
) -> None:
    """
    Salva documentos processados em múltiplos formatos.

    Args:
        documents: Lista de documentos processados.
        output_path: Diretório de saída.
    """
    print("\n💾 Salvando documentos processados...")

    # Criar diretório de saída se não existir
    os.makedirs(output_path, exist_ok=True)

    # Salvar em JSON
    json_path = os.path.join(output_path, "documents.json")
    FileHandler.save_json(documents, json_path)
    print(f"  ✓ Salvo em JSON: {json_path}")

    # Salvar em JSONL
    jsonl_path = os.path.join(output_path, "documents.jsonl")
    FileHandler.save_jsonl(documents, jsonl_path)
    print(f"  ✓ Salvo em JSONL: {jsonl_path}")

    # Salvar em pickle (preserva estruturas Python nativas)
    pickle_path = os.path.join(output_path, "documents.pkl")
    FileHandler.save_python_pickle(documents, pickle_path)
    print(f"  ✓ Salvo em pickle: {pickle_path}")


def print_statistics(documents: List[Dict[str, Any]]) -> None:
    """
    Imprime estatísticas sobre os documentos processados.

    Args:
        documents: Lista de documentos processados.
    """
    print("\n📊 Estatísticas dos Documentos Processados:")
    print("=" * 60)

    # Estatísticas gerais
    total_docs = len(documents)
    print(f"Total de documentos: {total_docs}")

    # Estatísticas por categoria
    categories_count = {}
    total_tokens = 0
    min_tokens = float('inf')
    max_tokens = 0

    for doc in documents:
        category = doc["category"]
        num_tokens = len(doc["tokens"])

        categories_count[category] = categories_count.get(category, 0) + 1
        total_tokens += num_tokens
        min_tokens = min(min_tokens, num_tokens)
        max_tokens = max(max_tokens, num_tokens)

    print("\nDocumentos por categoria:")
    for category, count in sorted(categories_count.items()):
        percentage = (count / total_docs) * 100
        print(f"  - {category}: {count} ({percentage:.1f}%)")

    # Estatísticas de tokens
    print(f"\nTokens:")
    print(f"  - Total: {total_tokens}")
    print(f"  - Média por documento: {total_tokens / total_docs:.1f}")
    print(f"  - Mínimo: {min_tokens}")
    print(f"  - Máximo: {max_tokens}")

    # Vocabulário único
    unique_tokens = set()
    for doc in documents:
        unique_tokens.update(doc["tokens"])
    print(f"  - Vocabulário único: {len(unique_tokens)} palavras")

    print("=" * 60)


def main():
    """
    Função principal que orquestra o pipeline completo.
    """
    print("🚀 Iniciando pipeline de pré-processamento de textos")
    print("=" * 60)

    # Etapa 1: Carregar documentos brutos
    print("\n📖 Etapa 1: Carregando documentos brutos...")
    documents = load_raw_documents(DATA_RAW_PATH, CATEGORIES)

    if not documents:
        print("❌ Nenhum documento foi carregado. Verifique os caminhos e categorias.")
        return

    print(f"✅ {len(documents)} documentos carregados")

    # Etapa 2: Inicializar processador
    print("\n⚙️  Etapa 2: Inicializando processador de textos...")
    processor = TextProcessor(
        min_token_length=MIN_TOKEN_LENGTH,
        remove_numbers=REMOVE_NUMBERS
    )
    print("✅ Processador inicializado")

    # Etapa 3: Processar documentos
    processed_docs = process_documents(documents, processor)

    # Etapa 4: Salvar resultados
    save_processed_documents(processed_docs, DATA_PROCESSED_PATH)

    # Etapa 5: Exibir estatísticas
    print_statistics(processed_docs)

    print("\n✨ Pipeline concluído com sucesso!")
    print(f"Resultados salvos em: {DATA_PROCESSED_PATH}/")


if __name__ == "__main__":
    main()
