from pathlib import Path
from contextlib import redirect_stdout
from collections import defaultdict
import argparse
import io
import importlib.util
import os
import sys


# Script de entrada da raiz do projeto.
#
# Este arquivo fica na raiz para você rodar comandos como `python -u see.py ...`
# a partir da pasta `projeto-final-grupo-2-EDA2-2026-01-Turma-03`.
# Internamente ele carrega os módulos de `src/Part3-community-creation` por
# caminho explícito, então não depende do diretório atual além da raiz do projeto.
#
# Exemplos de uso (executar no terminal a partir da raiz do projeto):
#
# Entrar na pasta do projeto primeiro e depois executar o script:
#   cd \PARTE3-EDA2\projeto-final-grupo-2-EDA2-2026-01-Turma-03
#   python -u see.py --page 1 --per-page 10 --theme entertainment
#
# Mostrar página 2 (próxima página):
#   cd \PARTE3-EDA2\projeto-final-grupo-2-EDA2-2026-01-Turma-03
#   python -u see.py --page 2 --per-page 10
#
# Mostrar somente palavras de business ou entertainment:
#   cd \PARTE3-EDA2\projeto-final-grupo-2-EDA2-2026-01-Turma-03
#   python -u see.py --page 1 --per-page 10 --theme business
#   python -u see.py --page 1 --per-page 10 --theme entertainment
#
# Dar "zoom" em um subtema pelo ID mostrado na tabela (ex.: ID 3), mostrando 30 termos:
#   cd \PARTE3-EDA2\projeto-final-grupo-2-EDA2-2026-01-Turma-03
#   python -u see.py --zoom 3 --zoom-terms 30 --theme business
#
# Demo rápida (mostra página 1 e faz zoom no subtema 1 com 20 termos):
#   cd \PARTE3-EDA2\projeto-final-grupo-2-EDA2-2026-01-Turma-03
#   python -u see.py --demo
#
# Observações:
# - Os IDs dos subtemas aparecem na primeira coluna da tabela (coluna `ID`).
# - Os termos no zoom são ordenados por relevância (grau no MST) e mostram o valor de grau ao lado.
# - Se pedir mais termos do que o subtema tem, serão exibidos todos os termos disponíveis.
# - O parâmetro `--theme` seleciona qual grafo será carregado: `all`, `business` ou `entertainment`.
# - Esse tema é repassado para a Fase 2 e faz o script usar os arquivos separados de grafo gerados para cada tema.


ROOT_DIR = Path(__file__).resolve().parent
MODULE_DIR = ROOT_DIR / 'src' / 'Part3-community-creation'
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))


def _load_module(module_name, file_name):
    module_path = MODULE_DIR / file_name
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def carregar_contexto_tema(theme: str):
    os.environ['GRAPH_THEME'] = theme
    _buffer_saida = io.StringIO()
    with redirect_stdout(_buffer_saida):
        communities_mod = _load_module(f'communities_{theme}', 'communities.py')
        kruskal_mod = _load_module(f'kruskal_{theme}', 'kruskal.py')

    # Reordena por grau no MST
    grau = defaultdict(int)
    for a, b, _ in kruskal_mod.grafo_fase3_mst:
        grau[a] += 1
        grau[b] += 1
    matriz_base = [sorted(sub, key=lambda w: (-grau.get(w, 0), w)) for sub in communities_mod.subtemas_fase3_finais]
    matriz_base.sort(key=len, reverse=True)
    return matriz_base, grau


def render_page(subtemas, grau, theme, page: int, per_page: int, max_keyword_chars: int):
    total = len(subtemas)
    start = (page - 1) * per_page
    end = min(start + per_page, total)

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


def zoom_subtema(subtemas, grau, theme, subtema_id: int, termos: int):
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


def main():
    parser = argparse.ArgumentParser(description='Interface ASCII para visualizar subtemas')
    parser.add_argument('--page', type=int, default=1, help='Página a mostrar (1-based)')
    parser.add_argument('--per-page', type=int, default=10, help='Subtemas por página')
    parser.add_argument('--max-kw-chars', type=int, default=120, help='Max chars para lista de palavras por subtema')
    parser.add_argument('--zoom', type=int, help='ID do subtema para dar zoom')
    parser.add_argument('--zoom-terms', type=int, default=20, help='Quantos termos mostrar no zoom')
    parser.add_argument('--demo', action='store_true', help='Executa demonstração rápida')
    parser.add_argument('--theme', choices=['all', 'business', 'entertainment'], default='all', help='Filtrar palavras por tema (business|entertainment)')

    args = parser.parse_args()
    subtemas, grau = carregar_contexto_tema(args.theme)

    if args.demo:
        print(render_page(subtemas, grau, args.theme, 1, args.per_page, args.max_kw_chars))
        print(zoom_subtema(subtemas, grau, args.theme, 1, args.zoom_terms))
        return

    if args.zoom:
        print(zoom_subtema(subtemas, grau, args.theme, args.zoom, args.zoom_terms))
        return

    print(render_page(subtemas, grau, args.theme, args.page, args.per_page, args.max_kw_chars))


if __name__ == '__main__':
    main()