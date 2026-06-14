from verify import grafo_fase3_validado

lista_arestas_brutas = grafo_fase3_validado

lista_arestas_distancia = []

for aresta in lista_arestas_brutas:
    palavra_A = aresta[0]
    palavra_B = aresta[1]
    forca_coocorrencia = aresta[2]
    distancia_calculada = 1.0 / forca_coocorrencia
    lista_arestas_distancia.append([palavra_A, palavra_B, distancia_calculada])

print("[PROCESSAMENTO] Conversão matemática de pesos concluída com sucesso.")
print(f"[PROCESSAMENTO] {len(lista_arestas_distancia)} arestas convertidas para distância geométrica.\n")

def exportar_grafo_distancias(dados_convertidos):
    print("[SUCESSO] Script do Passo 1 finalizado. Dados de distância exportados.")
    return dados_convertidos

grafo_fase3_distancias = exportar_grafo_distancias(lista_arestas_distancia)