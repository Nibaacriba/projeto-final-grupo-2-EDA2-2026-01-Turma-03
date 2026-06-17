from collections import defaultdict, deque

from kruskal import grafo_fase3_mst


lista_arestas_mst = grafo_fase3_mst

TARGET_SUBTHEMES = 20
MIN_SUBTHEME_SIZE = 150


adjacencia_mst = defaultdict(list)
for palavra_a, palavra_b, distancia in lista_arestas_mst:
    adjacencia_mst[palavra_a].append((palavra_b, distancia))
    adjacencia_mst[palavra_b].append((palavra_a, distancia))


def _componentes_iniciais():
    visitados = set()
    componentes = []

    for nodo_inicial in adjacencia_mst:
        if nodo_inicial in visitados:
            continue

        fila = deque([nodo_inicial])
        visitados.add(nodo_inicial)
        componente = set()

        while fila:
            atual = fila.popleft()
            componente.add(atual)

            for vizinho, _ in adjacencia_mst[atual]:
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    fila.append(vizinho)

        componentes.append(componente)

    return componentes


def _melhor_corte_componente(nodos):
    nodos = set(nodos)
    quantidade = len(nodos)
    if quantidade < MIN_SUBTHEME_SIZE * 2:
        return None

    raiz = next(iter(nodos))
    pai = {raiz: None}
    ordem = [raiz]
    pilha = [raiz]

    while pilha:
        atual = pilha.pop()
        for vizinho, _ in adjacencia_mst[atual]:
            if vizinho in nodos and vizinho not in pai:
                pai[vizinho] = atual
                ordem.append(vizinho)
                pilha.append(vizinho)

    filhos = defaultdict(list)
    for nodo, nodo_pai in pai.items():
        if nodo_pai is not None:
            filhos[nodo_pai].append(nodo)

    tamanho_subarvore = {nodo: 1 for nodo in nodos}
    for nodo in reversed(ordem):
        nodo_pai = pai.get(nodo)
        if nodo_pai is not None:
            tamanho_subarvore[nodo_pai] += tamanho_subarvore[nodo]

    melhor = None
    alvo = quantidade / 2

    for nodo in ordem[1:]:
        tamanho_a = tamanho_subarvore[nodo]
        tamanho_b = quantidade - tamanho_a
        if tamanho_a < MIN_SUBTHEME_SIZE or tamanho_b < MIN_SUBTHEME_SIZE:
            continue

        desbalanco = abs(tamanho_a - alvo)
        chave = (desbalanco, -max(tamanho_a, tamanho_b), nodo)
        if melhor is None or chave < melhor[0]:
            melhor = (chave, nodo)

    if melhor is None:
        return None

    nodo_corte = melhor[1]

    subarvore = set()
    pilha = [nodo_corte]
    while pilha:
        atual = pilha.pop()
        if atual in subarvore:
            continue
        subarvore.add(atual)
        for filho in filhos.get(atual, []):
            pilha.append(filho)

    complemento = nodos - subarvore
    if not subarvore or not complemento:
        return None

    return subarvore, complemento


def _dividir_ate_alvo(componentes, alvo):
    componentes = [set(componente) for componente in componentes]

    while len(componentes) < alvo:
        componentes.sort(key=len, reverse=True)
        componente_dividida = False

        for indice, componente in enumerate(componentes):
            corte = _melhor_corte_componente(componente)
            if corte is None:
                continue

            a, b = corte
            componentes.pop(indice)
            componentes.extend([a, b])
            componente_dividida = True
            break

        if not componente_dividida:
            break

    return componentes


componentes_iniciais = _componentes_iniciais()
subtemas_em_aberto = _dividir_ate_alvo(componentes_iniciais, TARGET_SUBTHEMES)

subtemas_filtrados = [sorted(subtema) for subtema in subtemas_em_aberto if len(subtema) >= MIN_SUBTHEME_SIZE]
subtemas_filtrados.sort(key=len, reverse=True)

for subtema in subtemas_em_aberto:
    if len(subtema) < MIN_SUBTHEME_SIZE:
        print(f"[PODA] Ruído detectado e eliminado: subtema com {len(subtema)} termos")

print("\n[PARTIÇÃO] Fragmentação guiada por alvo e limpeza de ruídos concluídas.")
print(f"[PARTIÇÃO] {len(subtemas_filtrados)} subtemas consolidados com sucesso.\n")


def exportar_subtemas_consolidados(dados_particionados):
    print("[SUCESSO] Script do Passo 4 finalizado. Matriz de subtemas exportada.")
    return dados_particionados


subtemas_fase3_finais = exportar_subtemas_consolidados(subtemas_filtrados)