from pathlib import Path
from collections import defaultdict
import argparse
import pickle

# Imports
from src.communities import Phase3Pipeline
from src.graph.exporter import importar_dados_fase2
from src.utils.tabular_export import TabularExporter


def _mapear_vocabulario_por_tema(base_dir: Path):
    """Mapeia vocabulário por tema a partir dos documentos processados"""
    vocab_por_tema = defaultdict(set)
    pkl_path = base_dir / "data" / "processed" / "documents.pkl"

    if not pkl_path.exists():
        print(f"[AVISO] Arquivo {pkl_path} não encontrado.")
        return vocab_por_tema

    try:
        with open(pkl_path, "rb") as f:
            documentos = pickle.load(f)
            for doc in documentos:
                cat = doc.get("category")
                tokens = doc.get("tokens", [])
                if cat and tokens:
                    vocab_por_tema[cat].update(tokens)
    except Exception as e:
        print(f"[ERRO] Falha ao carregar documents.pkl: {e}")

    return vocab_por_tema


def carregar_contexto_tema(theme: str):
    """Carrega dados e executa pipeline de comunidades"""
    print(f"[INFO] Carregando dados para tema: {theme}")
    all_edges = importar_dados_fase2()

    base_dir = Path(__file__).resolve().parent

    # Filtragem por tema
    if theme in {"business", "entertainment"}:
        vocab_map = _mapear_vocabulario_por_tema(base_dir)
        palavras_validas = vocab_map.get(theme, set())
        edges_filtradas = [
            [u, v, w] for u, v, w in all_edges
            if u in palavras_validas and v in palavras_validas
        ]
        print(f"[FILTRO] {len(edges_filtradas)} arestas mantidas para tema {theme}")
    else:
        edges_filtradas = all_edges

    # Executa Phase 3
    pipeline = Phase3Pipeline(verbose=True)
    resultado = pipeline.run(edges_filtradas)

    comunidades = resultado["communities"]
    mst_edges = resultado["mst_edges"]

    # Calcula grau
    grau = defaultdict(int)
    for a, b, _ in mst_edges:
        grau[a] += 1
        grau[b] += 1

    # Ordena comunidades
    matriz_base = [
        sorted(com, key=lambda w: (-grau.get(w, 0), w))
        for com in comunidades
    ]
    matriz_base.sort(key=len, reverse=True)

    data_dir = base_dir / "data" / "processed"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Exporta arestas por comunidade (essencial para GUI rápida)
    edges_path = data_dir / f"mst_edges_{theme}.pkl"
    with open(edges_path, "wb") as f:
        pickle.dump(resultado["edges_per_community"], f)
    print(f"[EXPORT] Arestas por comunidade → {edges_path}")

    # Exporta CSV tabular
    csv_path = data_dir / f"comunidades_tabular_{theme}.csv"
    TabularExporter.export_to_csv(matriz_base, str(csv_path))
    print(f"[EXPORT] Tabela → {csv_path}")

    return matriz_base, grau


def render_page(subtemas, grau, theme, page=1, per_page=10, max_keyword_chars=120):
    total = len(subtemas)
    start = (page - 1) * per_page
    end = min(start + per_page, total)

    if total == 0:
        return f"Tema selecionado: {theme}\n[AVISO] Nenhuma comunidade encontrada.\n"

    header_top10 = ', '.join(
        f'{w}({grau.get(w, 0)})'
        for w in sorted({w for s in subtemas for w in s}, key=lambda w: (-grau.get(w, 0), w))[:10]
    )

    largura_id = 6
    largura_qtd = 13
    largura_coluna = max_keyword_chars + 4
    linha = f"+{'-' * largura_id}+{'-' * largura_qtd}+{'-' * largura_coluna}+\n"

    out = [
        f'Tema selecionado: {theme}\n',
        f'Top 10 termos (grau): {header_top10}\n',
        f'Mostrando subtemas {start + 1} a {end} de {total} (página {page})\n\n',
        linha,
        f"| {'ID':^{largura_id-2}} | {'QTD TERMOS':^{largura_qtd-2}} | {'PALAVRAS-CHAVE':<{largura_coluna-2}} |\n",
        linha.replace('-', '=')
    ]

    for idx in range(start, end):
        subtema = subtemas[idx]
        id_sub = f'{idx + 1:02d}'
        qtd = str(len(subtema))
        palavras = ', '.join(subtema)
        if len(palavras) > max_keyword_chars:
            palavras = palavras[:max_keyword_chars - 3] + '...'
        out.append(f"| {id_sub:^{largura_id-2}} | {qtd:^{largura_qtd-2}} | {palavras:<{largura_coluna-2}} |\n")
        out.append(linha)

    return ''.join(out)


def zoom_subtema(subtemas, grau, theme, subtema_id, termos=20):
    if subtema_id < 1 or subtema_id > len(subtemas):
        return f'[ERRO] ID inválido: {subtema_id}\n'

    lista = subtemas[subtema_id - 1][:termos]
    linhas = [
        f'Tema: {theme}\n',
        f'Zoom no subtema {subtema_id} — {len(lista)} de {len(subtemas[subtema_id-1])} termos:\n'
    ]
    for i, termo in enumerate(lista, 1):
        linhas.append(f' {i:02d}. {termo} (grau={grau.get(termo, 0)})\n')
    return ''.join(linhas)


def main():
    parser = argparse.ArgumentParser(description='Visualizador de Comunidades')
    parser.add_argument('--theme', choices=['all', 'business', 'entertainment'], default='all')
    parser.add_argument('--page', type=int, default=1)
    parser.add_argument('--per-page', type=int, default=10)
    parser.add_argument('--max-kw-chars', type=int, default=120)
    parser.add_argument('--zoom', type=int, help='ID do subtema para zoom')
    parser.add_argument('--zoom-terms', type=int, default=25)
    parser.add_argument('--demo', action='store_true')

    args = parser.parse_args()

    try:
        subtemas, grau = carregar_contexto_tema(args.theme)
    except FileNotFoundError as e:
        print(e)
        return
    except Exception as e:
        print(f"Erro durante processamento: {e}")
        return

    if args.demo:
        print(render_page(subtemas, grau, args.theme, 1, args.per_page, args.max_kw_chars))
        if subtemas:
            print("\n" + zoom_subtema(subtemas, grau, args.theme, 1, args.zoom_terms))
        return

    if args.zoom:
        print(zoom_subtema(subtemas, grau, args.theme, args.zoom, args.zoom_terms))
        return

    print(render_page(subtemas, grau, args.theme, args.page, args.per_page, args.max_kw_chars))


if __name__ == '__main__':
    main()
