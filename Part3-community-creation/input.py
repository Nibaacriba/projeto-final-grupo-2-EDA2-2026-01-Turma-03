import json

def importar_dados_fase2():
    grafo_linear_entrada = [
    ['banco', 'selic', 3],
    ['inflação', 'selic', 3],
    ['banco', 'inflação', 2],
    ['banco', 'juros', 3],
    ['juros', 'selic', 3],
    ['mercado', 'ações', 3],
    ['ações', 'investimento', 3],
    ['mercado', 'investimento', 3],
    ['mercado', 'dólar', 2],
    ['banco', 'mercado', 1],
    ['brasil', 'copa', 3],
    ['brasil', 'futebol', 3],
    ['brasil', 'neymar', 2],
    ['copa', 'futebol', 3],
    ['futebol', 'seleção', 3],
    ['neymar', 'seleção', 3],
    ['copa', 'estádio', 2],
    ['futebol', 'gol', 3],
    ['brasil', 'banco', 1],
    ['ia', 'python', 3],
    ['python', 'código', 3],
    ['código', 'algoritmo', 3],
    ['ia', 'algoritmo', 3],
    ['software', 'código', 3],
    ['python', 'software', 2],
    ['terminal', 'codigo', 2],
    ['dados', 'ia', 3],
    ['mercado', 'ia', 1],
    ['receita', 'cozinha', 3],
    ['cozinha', 'chefe', 3],
    ['chefe', 'prato', 3],
    ['sabor', 'prato', 3],
    ['receita', 'sabor', 2],
    ['restaurante', 'chefe', 3],
    ['tempero', 'cozinha', 3],
    ['chuva', 'tempo', 3],
    ['clima', 'tempo', 3],
    ['chuva', 'clima', 2],
    ['sol', 'tempo', 3],
    ['nuvem', 'chuva', 3],
    ['floresta', 'ecologia', 3],
    ['rio', 'floresta', 2],
    ['python', 'clima', 1]
]
    return grafo_linear_entrada

grafo_linear_bruto = importar_dados_fase2()

lista_arestas_processadas = []

for aresta in grafo_linear_bruto:
    palavra_A = aresta[0]
    palavra_B = aresta[1]
    forca_peso = aresta[2]
    distancia_calculada = 1.0 / forca_peso
    lista_arestas_processadas.append([palavra_A, palavra_B, distancia_calculada])

lista_arestas_processadas.sort(key=lambda x: x[2])

def exportar_dados_fase3(dados_finais):
    with open("grafo_ordenado.json", "w", encoding="utf-8") as arquivo:
        json.dump(dados_finais, arquivo, indent=4, ensure_ascii=False)
    print("[SUCESSO] Arquivo 'grafo_ordenado.json' gerado e salvo fisicamente em disco.")
    return dados_finais

grafo_fase3_pronto = exportar_dados_fase3(lista_arestas_processadas)