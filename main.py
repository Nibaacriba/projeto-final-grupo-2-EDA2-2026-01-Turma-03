"""
Arquivo principal do projeto de PLN com Grafos.

Orquestra o pipeline completo: pré-processamento e construção do grafo.
Por padrão executa Fase 1 + Fase 2.

Uso: python main.py [OPÇÃO]

Opções:
    (nenhuma)   Executa Fase 1 + Fase 2 (padrão)
    phase1      Executa apenas Fase 1
    phase2      Executa apenas Fase 2
    --help      Mostra esta mensagem

Documentação completa em: README.md
"""

import os
import sys
import pickle
from pathlib import Path
from typing import List, Dict, Any

from src.preprocessing import TextProcessor
from src.graph import GraphBuilder
from src.utils import FileHandler


# Configurações do projeto
DATA_RAW_PATH = "data/raw"
DATA_PROCESSED_PATH = "data/processed"
CATEGORIES = ["business", "entertainment"]

# Configurações do processador (Fase 1)
MIN_TOKEN_LENGTH = 2
REMOVE_NUMBERS = True
USE_LEMMATIZATION = True

# Configurações da Fase 2 (Grafo)
BASE_DIR = Path(__file__).resolve().parent
DATA_PROCESSED_PATH_OBJ = BASE_DIR / "data" / "processed"
DOCUMENTS_PKL = DATA_PROCESSED_PATH_OBJ / "documents.pkl"
RAW_DATA_PATH_OBJ = BASE_DIR / "data" / "raw"
GRAPH_PKL = DATA_PROCESSED_PATH_OBJ / "graph_edges.pkl"

# Peso mínimo padrão para arestas (1 = grafo completo)
MIN_WEIGHT_DEFAULT = 1
CATEGORY_DEFAULT = "all"


def load_raw_documents(raw_path: str, categories: List[str]) -> List[Dict[str, Any]]:
    """Carrega documentos brutos dos diretórios de categorias."""
    documents = []

    for category in categories:
        category_path = FileHandler.get_file_path(raw_path, category)

        if not os.path.exists(category_path):
            print(f"⚠️  Categoria '{category}' não encontrada em {category_path}")
            continue

        try:
            files = FileHandler.list_files_in_directory(category_path)
            print(f"📁 Categoria '{category}': {len(files)} arquivos encontrados")

            for filename in files:
                file_path = FileHandler.get_file_path(category_path, filename)

                try:
                    text = FileHandler.read_text_file(file_path)
                    file_id = Path(filename).stem

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
    """Processa uma lista de documentos."""
    print("\n🔄 Iniciando processamento de documentos...")
    processed_documents = processor.process_batch(documents)
    print(f"✅ {len(processed_documents)} documentos processed com sucesso")
    return processed_documents


def save_processed_documents(
    documents: List[Dict[str, Any]],
    output_path: str
) -> None:
    """
    CORRIGIDO: Salva os documentos processados exclusivamente no formato Pickle (.pkl).
    Removidas as exportações redundantes e lixo para JSON e JSONL.
    """
    print("\n💾 Salvando documentos processados...")

    # Criar diretório de saída se não existir
    os.makedirs(output_path, exist_ok=True)

    # Salvar unicamente em pickle para preservar as estruturas nativas de 'set' do Python
    pickle_path = os.path.join(output_path, "documents.pkl")
    FileHandler.save_python_pickle(documents, pickle_path)
    print(f"  ✓ Salvo em pickle: {pickle_path}")


def print_statistics(documents: List[Dict[str, Any]]) -> None:
    """Imprime estatísticas sobre os documentos processados."""
    print("\n📊 Estatísticas dos Documentos Processados:")
    print("=" * 60)

    total_docs = len(documents)
    print(f"Total de documentos: {total_docs}")

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

    print(f"\nTokens:")
    print(f"  - Total: {total_tokens}")
    print(f"  - Média por documento: {total_tokens / total_docs:.1f}")
    print(f"  - Mínimo: {min_tokens}")
    print(f"  - Máximo: {max_tokens}")

    unique_tokens = set()
    for doc in documents:
        unique_tokens.update(doc["tokens"])
    print(f"  - Vocabulário único: {len(unique_tokens)} palavras")

    print("=" * 60)


# ======================================================================
# FASE 2: Funções de construção do grafo de coocorrência
# ======================================================================

def load_preprocessed_documents(pkl_path: str) -> List[Dict[str, Any]]:
    """Carrega os documentos pré-processados a partir do pickle da Fase 1."""
    if not os.path.exists(pkl_path):
        raise FileNotFoundError(
            f"Arquivo não encontrado: {pkl_path}\n"
            f"Execute primeiro a Fase 1 com: python main.py"
        )
    with open(pkl_path, "rb") as f:
        return pickle.load(f)


def load_raw_documents_for_graph(categoria: str) -> List[Dict[str, Any]]:
    """Carrega documentos diretamente da pasta raw quando o pickle não existe."""
    pasta = str(RAW_DATA_PATH_OBJ)
    categorias = [categoria] if categoria != CATEGORY_DEFAULT else ["business", "entertainment"]
    processor = TextProcessor()
    documentos = []

    for cat in categorias:
        cat_dir = os.path.join(pasta, cat)
        if not os.path.isdir(cat_dir):
            continue

        for nome_arquivo in sorted(os.listdir(cat_dir)):
            if not nome_arquivo.lower().endswith(".txt"):
                continue

            caminho = os.path.join(cat_dir, nome_arquivo)
            with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
                texto = f.read()

            documentos.append(
                {
                    "id": os.path.splitext(nome_arquivo)[0],
                    "category": cat,
                    "tokens": processor.process_document(texto),
                }
            )

    if not documentos:
        raise FileNotFoundError(
            f"Nenhum documento encontrado em {RAW_DATA_PATH_OBJ} para a categoria '{categoria}'."
        )

    return documentos


def filter_documents_by_category(
    documents: List[Dict[str, Any]],
    categoria: str
) -> List[Dict[str, Any]]:
    """Filtra documentos por categoria; 'all' mantém o corpus inteiro."""
    if categoria == CATEGORY_DEFAULT:
        return documents

    return [doc for doc in documents if doc.get("category") == categoria]


def save_graph_edges(arestas: List[List[Any]], caminho_pkl: Path) -> None:
    """CORRIGIDO: Salva a lista plana de arestas exclusivamente em formato binário Pickle."""
    os.makedirs(os.path.dirname(str(caminho_pkl)), exist_ok=True)

    with open(caminho_pkl, "wb") as f:
        pickle.dump(arestas, f)


def build_graph_phase2(
    min_weight: int = MIN_WEIGHT_DEFAULT,
    categoria: str = CATEGORY_DEFAULT
) -> None:
    """Orquestra a Fase 2: Construção do grafo de coocorrência."""
    print("\n" + "=" * 70)
    print("🚀 FASE 2: Construção do Grafo de Coocorrência")
    print("=" * 70)
    print(f"Peso mínimo das arestas: {min_weight}")
    print(f"Categoria selecionada: {categoria}")

    # Etapa 1: Carregar documentos da Fase 1
    print("\n📖 Etapa 1: Carregando documentos pré-processados...")
    try:
        if categoria == CATEGORY_DEFAULT and DOCUMENTS_PKL.exists():
            documentos = load_preprocessed_documents(str(DOCUMENTS_PKL))
            print(f"✅ {len(documentos)} documentos carregados de {DOCUMENTS_PKL}")
        else:
            documentos = load_raw_documents_for_graph(categoria)
            print(f"✅ {len(documentos)} documentos carregados de {RAW_DATA_PATH_OBJ}")

        documentos = filter_documents_by_category(documentos, categoria)
        print(f"✅ {len(documentos)} documentos após filtro por categoria")
    except FileNotFoundError as e:
        print(f"❌ Erro: {e}")
        return

    # Etapa 2: Construir o grafo
    print("\n🔗 Etapa 2: Construindo arestas de coocorrência...")
    builder = GraphBuilder(min_weight=min_weight)
    arestas = builder.build(documentos)
    print(f"✅ Grafo construído: {len(arestas)} arestas")

    # Etapa 3: Salvar (CORRIGIDO: Removida completamente a rota e variáveis do JSON)
    print("\n💾 Etapa 3: Salvando grafo...")
    if categoria == CATEGORY_DEFAULT:
        caminho_pkl = GRAPH_PKL
    else:
        caminho_pkl = DATA_PROCESSED_PATH_OBJ / f"graph_edges_{categoria}.pkl"

    save_graph_edges(arestas, caminho_pkl)
    print(f"  ✓ Pickle: {caminho_pkl}")

    # Etapa 4: Estatísticas
    print("\n📊 Etapa 4: Estatísticas do Grafo")
    stats = GraphBuilder.estatisticas(arestas)
    print("=" * 70)
    print(f"Vértices (palavras únicas): {stats['vertices']}")
    print(f"Arestas (conexões):         {stats['arestas']}")
    print(f"Peso máximo:                {stats['peso_max']}")
    print(f"Peso médio:                 {stats['peso_medio']:.2f}")
    print("\nTop 5 conexões mais fortes:")
    for palavra_a, palavra_b, peso in stats["top_5"]:
        print(f"  {palavra_a} <--> {palavra_b}: {peso}")
    print("=" * 70)

    print("\n✨ Fase 2 concluída! Grafo pronto para a Fase 3.")


def print_help():
    """Exibe mensagem de ajuda sobre como usar o script."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║         PIPELINE DE PLN COM GRAFOS - USAGE                   ║
╚═══════════════════════════════════════════════════════════════╝

Uso:
    python main.py              # Executa Fase 1 + Fase 2 (PADRÃO)
    python main.py phase1       # Executa apenas Fase 1
    python main.py phase2       # Executa apenas Fase 2
    python main.py --help       # Exibe esta mensagem

Fase 1 - Pré-processamento de Textos:
    - Lê arquivos de data/raw/[categoria]/
    - Processa tokens, stopwords, etc
    - Salva unicamente em data/processed/documents.pkl

Fase 2 - Construção do Grafo de Coocorrência:
    - Carrega documentos processados da Fase 1
    - Constrói grafo ponderado de coocorrência
    - Salva arestas exclusivamente em arquivos binários (.pkl)
""")


def main():
    """Função principal que orquestra o pipeline completo."""
    phase = "all"

    if len(sys.argv) > 1:
        arg = sys.argv[1].lower().strip()

        if arg in {"--help", "-h", "help"}:
            print_help()
            return

        if arg in {"phase2", "--phase2", "-p2"}:
            phase = "phase2"
        elif arg == "phase1":
            phase = "phase1"
        elif arg in {"all", "--all", "-a"}:
            phase = "all"
        else:
            print(f"❌ Argumento não reconhecido: {arg}")
            print_help()
            return

    # Executar fases conforme solicitado
    if phase in {"phase1", "all"}:
        print("🚀 Iniciando FASE 1: Pré-processamento de Textos")
        print("=" * 70)

        print("\n📖 Etapa 1: Carregando documentos brutos...")
        documents = load_raw_documents(DATA_RAW_PATH, CATEGORIES)

        if not documents:
            print("❌ Nenhum documento foi carregado. Verifique os caminhos e categorias.")
            return

        print(f"✅ {len(documents)} documentos carregados")

        print("\n⚙️  Etapa 2: Inicializando processador de textos...")
        processor = TextProcessor(
            min_token_length=MIN_TOKEN_LENGTH,
            remove_numbers=REMOVE_NUMBERS,
            use_lemmatization=USE_LEMMATIZATION,
        )
        print("✅ Processador inicializado")

        processed_docs = process_documents(documents, processor)
        save_processed_documents(processed_docs, DATA_PROCESSED_PATH)
        print_statistics(processed_docs)

        print("\n✨ Fase 1 concluída com sucesso!")
        print(f"Resultados salvos em: {DATA_PROCESSED_PATH}/")

    if phase in {"phase2", "all"}:
        build_graph_phase2(min_weight=MIN_WEIGHT_DEFAULT, categoria=CATEGORY_DEFAULT)


if __name__ == "__main__":
    main()
