from weight_inv import grafo_fase3_distancias

lista_arestas_distancia = grafo_fase3_distancias

lista_arestas_distancia.sort(key=lambda aresta: aresta[2])

print("[ORDENAÇÃO] Fila de prioridades gerada com sucesso via Timsort nativo.")
print(f"[ORDENAÇÃO] {len(lista_arestas_distancia)} arestas posicionadas por ordem crescente de distância.\n")

print("Amostra das conexões prioritárias na fila (Mais Fortes):")
for i in range(min(3, len(lista_arestas_distancia))):
    item = lista_arestas_distancia[i]
    print(f"  Posição {i}: {item[0]} ↔ {item[1]} | Distância: {item[2]:.2f}")

def exportar_grafo_ordenado(dados_ordenados):
    print("\n[SUCESSO] Script do Passo 2 finalizado. Fila de arestas exportada.")
    return dados_ordenados

grafo_fase3_ordenado = exportar_grafo_ordenado(lista_arestas_distancia)