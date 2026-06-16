from communities import subtemas_fase3_finais

matriz_subtemas = subtemas_fase3_finais

LARGURA_ID = 6
LARGURA_QTD = 13

largura_coluna_palavras = 40

for subtema in matriz_subtemas:
    texto_palavras_unificadas = ", ".join(subtema)
    comprimento_texto = len(texto_palavras_unificadas)

    if comprimento_texto > largura_coluna_palavras:
        largura_coluna_palavras = comprimento_texto

largura_coluna_palavras += 4

linha_separadora = f"+{'-' * LARGURA_ID}+{'-' * LARGURA_QTD}+{'-' * largura_coluna_palavras}+\n"
tabela_terminal = ""

tabela_terminal += linha_separadora
tabela_terminal += f"| {'ID':^{LARGURA_ID-2}} | {'QTD TERMOS':^{LARGURA_QTD-2}} | {'PALAVRAS-CHAVE DO SUBTEMA':<{largura_coluna_palavras-2}} |\n"
tabela_terminal += linha_separadora.replace('-', '=')

for index, subtema in enumerate(matriz_subtemas):
    id_subtema = f"{index + 1:02d}"
    qtd_termos = str(len(subtema))
    palavras_chave = ", ".join(subtema)

    linha_dados = f"| {id_subtema:^{LARGURA_ID-2}} | {qtd_termos:^{LARGURA_QTD-2}} | {palavras_chave:<{largura_coluna_palavras-2}} |\n"

    tabela_terminal += linha_dados
    tabela_terminal += linha_separadora

print(tabela_terminal)

def exportar_impressao_terminal(tabela_finalizada):
    print("[SUCESSO] Tabela ASCII estruturada gerada e exibida no console.")
    return tabela_finalizada

tabela_fase5_concluida = exportar_impressao_terminal(tabela_terminal)