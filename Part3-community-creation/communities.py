from kruskal import grafo_fase3_mst

lista_arestas_mst = grafo_fase3_mst

LIMIAR_CORTE = 0.7
arestas_fortes_sobreviventes = []

for aresta in lista_arestas_mst:
    distancia_link = aresta[2]
    if distancia_link <= LIMIAR_CORTE:
        arestas_fortes_sobreviventes.append(aresta)

pai_comunidades = {}

def encontrar_raiz_comunidade(palavra):
    if palavra not in pai_comunidades:
        pai_comunidades[palavra] = palavra
        return palavra
    if pai_comunidades[palavra] == palavra:
        return palavra
    pai_comunidades[palavra] = encontrar_raiz_comunidade(pai_comunidades[palavra])
    return pai_comunidades[palavra]

def unir_comunidades(palavra1, palavra2):
    raiz1 = encontrar_raiz_comunidade(palavra1)
    raiz2 = encontrar_raiz_comunidade(palavra2)
    if raiz1 != raiz2:
        pai_comunidades[raiz1] = raiz2

for link in arestas_fortes_sobreviventes:
    unir_comunidades(link[0], link[1])

comunidades_brutas = {}

for palavra in pai_comunidades.keys():
    raiz_grupo = encontrar_raiz_comunidade(palavra)
    if raiz_grupo not in comunidades_brutas:
        comunidades_brutas[raiz_grupo] = []
    comunidades_brutas[raiz_grupo].append(palavra)

lista_subtemas_finais = []

for raiz, membros in comunidades_brutas.items():
    if len(membros) >= 3:
        lista_subtemas_finais.append(membros)
    else:
        print(f"[PODA] Ruído detectado e eliminado: Grupo da raiz [{raiz}] com termos {membros}")

print("\n[PARTIÇÃO] Fragmentação da MST e limpeza de ruídos concluídas.")
print(f"[PARTIÇÃO] {len(lista_subtemas_finais)} subtemas puros isolados com sucesso.\n")

def exportar_subtemas_consolidados(dados_particionados):
    print("[SUCESSO] Script do Passo 4 finalizado. Matriz de subtemas exportada.")
    return dados_particionados

subtemas_fase3_finais = exportar_subtemas_consolidados(lista_subtemas_finais)