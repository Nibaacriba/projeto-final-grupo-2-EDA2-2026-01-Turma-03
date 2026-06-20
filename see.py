from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Tuple, Set
import argparse
import os
import pickle

from src.communities import Phase3Pipeline
from src.graph.exporter import importar_dados_fase2
from src.utils.tabular_export import TabularExporter


def _mapear_vocabulario_por_tema(base_dir: Path) -> Dict[str, Set[str]]:
    """
    Carrega os documentos processados da Fase 1 (documents.pkl)
    e monta um mapa de palavras únicas por categoria.
    """
    vocab_por_tema = defaultdict(set)
    pkl_path = base_dir / "data" / "processed" / "documents.pkl"

    if not pkl_path.exists():
        return vocab_por_tema

    try:
        with open(pkl_path, "rb") as f:
            documentos = pickle.load(f)
            for doc in documentos:
                cat = doc.get("category")
                tokens = doc.get("tokens", [])
                if cat:
                    vocab_por_tema[cat].update(tokens)
    except Exception:
        pass  # Se falhar, retorna o dicionário incompleto/vazio de forma segura

    return vocab_por_tema


def carregar_contexto_tema(theme: str) -> Tuple[List[List[str]], Dict[str, int]]:
    """
    Carrega o grafo unificado e filtra as arestas dinamicamente
    mantendo apenas as conexões entre palavras da categoria selecionada.
    """
    # 1. Carrega todas as arestas do arquivo único 'graph_edges.pkl'
    all_edges = importar_dados_fase2()

    # Base do projeto para achar o documents.pkl
    base_dir = Path(__file__).resolve().parent

    # 2. Filtra o grafo se o usuário escolheu um tema específico
    if theme in {"business", "entertainment"}:
        vocab_map = _mapear_vocabulario_por_tema(base_dir)
        palavras_validas = vocab_map.get(theme, set())

        # Só mantém a aresta se AMBAS as palavras pertencerem ao vocabulário do tema
        edges_filtradas = [
            [u, v, w] for u, v, w in all_edges
            if u in palavras_validas and v in palavras_validas
        ]
    else:
        edges_filtradas = all_edges

    # 3. Executar Phase 3 Pipeline sobre as arestas filtradas
    pipeline = Phase3Pipeline(verbose=False)
    resultado = pipeline.run(edges_filtradas)

    comunidades = resultado["communities"]
    mst_edges = resultado["mst_edges"]

    # Calcular grau de cada palavra na MST
    grau = defaultdict(int)
    for a, b, _ in mst_edges:
        grau[a] += 1
        grau[b] += 1

    # Ordenar palavras dentro de cada comunidade por grau (decrescente)
    matriz_base = [
        sorted(com, key=lambda w: (-grau.get(w, 0), w))
        for com in comunidades
    ]
    matriz_base.sort(key=len, reverse=True)

    return matriz_base, grau


def render_page(
    subtemas: List[List[str]],
    grau: Dict[str, int],
    theme: str,
    page: int,
    per_page: int,
    max_keyword_chars: int
) -> str:
    total = len(subtemas)
    start = (page - 1) * per_page
    end = min(start + per_page, total)

    if total == 0:
        return f"Tema selecionado: {theme}\n[AVISO] Nenhuma comunidade encontrada com os critérios atuais.\n"

    header_top10 = ', '.join(
        f'{w}({grau.get(w, 0)})'
        for w in sorted({w for s in subtemas for w in s}, key=lambda w: (-grau.get(w, 0), w))[:10]
    )

    largura_id = 6
    largura_qtd = 13
    largura_coluna_palavras = max_keyword_chars + 4
    linha_separadora = f"+{'-' * largura_id}+{'-' * largura_qtd}+{'-' * largura_coluna_palavras}+\n"

    out = []
    out.append(f'Tema selecionado: {theme}\n')
    out.append(f'Top 10 termos (grau): {header_top10}\n')
    out.append(f'Mostrando subtemas {start + 1} a {end} de {total} (página {page})\n\n')
    out.append(linha_separadora)
    out.append(f"| {'ID':^{largura_id-2}} | {'QTD TERMOS':^{largura_qtd-2}} | {'PALAVRAS-CHAVE DO SUBTEMA':<{largura_coluna_palavras-2}} |\n")
    out.append(linha_separadora.replace('-', '='))

    for idx in range(start, end):
        subtema = subtemas[idx]
        id_subtema = f'{idx + 1:02d}'
        qtd_termos = str(len(subtema))
        palavras = ', '.join(subtema)
        if len(palavras) > max_keyword_chars:
            palavras = palavras[: max_keyword_chars - 3] + '...'
        out.append(f"| {id_subtema:^{largura_id-2}} | {qtd_termos:^{largura_qtd-2}} | {palavras:<{largura_coluna_palavras-2}} |\n")
        out.append(linha_separadora)

    return ''.join(out)


def zoom_subtema(
    subtemas: List[List[str]],
    grau: Dict[str, int],
    theme: str,
    subtema_id: int,
    termos: int
) -> str:
    if subtema_id < 1 or subtema_id > len(subtemas):
        return f'[ERRO] ID de subtema inválido: {subtema_id}\n'

    lista = subtemas[subtema_id - 1][:termos]
    linhas = [
        f'Tema selecionado: {theme}\n',
        f'Zoom no subtema {subtema_id} — mostrando {len(lista)} de {len(subtemas[subtema_id - 1])} termos:\n',
    ]
    for i, termo in enumerate(lista, 1):
        linhas.append(f' {i:02d}. {termo} (grau={grau.get(termo, 0)})\n')
    return ''.join(linhas)


def main() -> None:
    """Executa a interface ASCII para visualização de comunidades."""
    parser = argparse.ArgumentParser(description='Interface ASCII para visualizar subtemas do grafo.')
    parser.add_argument('--page', type=int, default=1, help='Página a mostrar (1-based)')
    parser.add_argument('--per-page', type=int, default=10, help='Subtemas por página')
    parser.add_argument('--max-kw-chars', type=int, default=120, help='Max chars para lista de palavras por subtema')
    parser.add_argument('--zoom', type=int, help='ID do subtema para dar zoom')
    parser.add_argument('--zoom-terms', type=int, default=20, help='Quantos termos mostrar no zoom')
    parser.add_argument('--demo', action='store_true', help='Executa demonstração rápida')
    parser.add_argument('--theme', choices=['all', 'business', 'entertainment'], default='all', help='Filtrar palavras por tema')

    args = parser.parse_args()

    try:
        subtemas, grau = carregar_contexto_tema(args.theme)
    except FileNotFoundError as e:
        print(e)
        return

    caminho_saida = f"data/processed/comunidades_tabular_{args.theme}.csv"
    TabularExporter.export_to_csv(subtemas, caminho_saida)

    if args.demo:
        print(render_page(subtemas, grau, args.theme, 1, args.per_page, args.max_kw_chars))
        if subtemas:
            print(zoom_subtema(subtemas, grau, args.theme, 1, args.zoom_terms))
        return

    if args.zoom:
        print(zoom_subtema(subtemas, grau, args.theme, args.zoom, args.zoom_terms))
        return

    print(render_page(subtemas, grau, args.theme, args.page, args.per_page, args.max_kw_chars))


if __name__ == '__main__':
    main()
