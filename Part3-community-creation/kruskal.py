from fila_prioridades import grafo_fase3_ordenado

lista_arestas_prioridade = grafo_fase3_ordenado

tabela_pai = {}

def encontrar_raiz(palavra):
    if palavra not in tabela_pai:
        tabela_pai[palavra] = palavra
        return palavra
    if tabela_pai[palavra] == palavra:
        return palavra
    tabela_pai[palavra] = encontrar_raiz(tabela_pai[palavra])
    return tabela_pai[palavra]

def unir_componentes(palavra_1, palavra_2):
    raiz_A = encontrar_raiz(palavra_1)
    raiz_B = encontrar_raiz(palavra_2)
    if raiz_A != raiz_B:
        tabela_pai[raiz_A] = raiz_B

lista_arestas_mst = []

for aresta in lista_arestas_prioridade:
    vertice_A = aresta[0]
    vertice_B = aresta[1]
    distancia_geometrica = aresta[2]

    lider_A = encontrar_raiz(vertice_A)
    lider_B = encontrar_raiz(vertice_B)

    if lider_A != lider_B:
        lista_arestas_mst.append([vertice_A, vertice_B, distancia_geometrica])
        unir_componentes(vertice_A, vertice_B)

print("[ALGORITMO] Execução do motor de Kruskal finalizada com sucesso.")
print(f"[ALGORITMO] Conexões originais: {len(lista_arestas_prioridade)} | Reduzidas na MST: {len(lista_arestas_mst)}")

def exportar_esqueleto_mst(mst_consolidada):
    print("\n[SUCESSO] Script do Passo 3 finalizado. Esqueleto da MST exportado.")
    return mst_consolidada

grafo_fase3_mst = exportar_esqueleto_mst(lista_arestas_mst)