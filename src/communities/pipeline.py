"""
Phase 3: Community Detection via Minimum Spanning Tree (MST) + Partitioning

Fluxo:
  1. Validação de contrato
  2. Conversão peso → distância
  3. Ordenação por distância
  4. Cálculo MST via Kruskal
  5. Particionamento em comunidades
"""

from collections import defaultdict, deque
from typing import List, Dict, Set, Tuple, Optional


class Phase3Pipeline:
    """
    Pipeline de detecção de comunidades baseado em MST.

    Entrada esperada:
        [["palavra_a", "palavra_b", peso], ...]
        onde peso > 0 (força de coocorrência)

    Saída:
        {
            "mst_edges": [...],
            "communities": [...],
            "statistics": {...}
        }
    """

    def __init__(self, target_communities: int = 20, min_community_size: int = 150, verbose: bool = True):
        """
        Inicializa o pipeline.

        Args:
            target_communities: Número alvo de comunidades na partição
            min_community_size: Tamanho mínimo de uma comunidade válida
            verbose: Se True, imprime mensagens de progresso
        """
        self.target_communities = target_communities
        self.min_community_size = min_community_size
        self.verbose = verbose

    def run(self, edges: List[List]) -> Dict:
        """
        Executa o pipeline completo de Phase 3.

        Args:
            edges: Lista de arestas [palavra_a, palavra_b, peso]

        Returns:
            Dicionário com mst_edges, communities e statistics
        """
        # 1. VALIDAÇÃO RÍGIDA DE CONTRATO
        validated_edges = self._validate_contract(edges)
        if self.verbose:
            print(f"[VALIDAÇÃO] {len(validated_edges)} arestas aprovadas")

        # 2. CONVERSÃO: peso → distância
        distance_edges = self._convert_to_distances(validated_edges)
        if self.verbose:
            print(f"[CONVERSÃO] Pesos convertidos para distâncias")

        # 3. ORDENAÇÃO: por distância crescente
        sorted_edges = self._sort_by_distance(distance_edges)
        if self.verbose:
            print(f"[ORDENAÇÃO] Arestas ordenadas por distância crescente")

        # 4. MST: Algoritmo de Kruskal
        mst_edges = self._compute_mst_kruskal(sorted_edges)
        if self.verbose:
            print(f"[MST] {len(sorted_edges)} arestas reduzidas para {len(mst_edges)}")

        # 5. PARTICIONAMENTO: comunidades
        communities = self._partition_communities(mst_edges)
        if self.verbose:
            print(f"[PARTIÇÃO] {len(communities)} comunidades geradas")

        # Compilar resultados
        statistics = {
            "input_edges": len(edges),
            "validated_edges": len(validated_edges),
            "mst_edges": len(mst_edges),
            "communities_count": len(communities),
            "avg_community_size": sum(len(c) for c in communities) / len(communities) if communities else 0,
        }

        return {
            "mst_edges": mst_edges,
            "communities": communities,
            "statistics": statistics,
        }

    def _validate_contract(self, edges: List[List]) -> List[List]:
        """
        Valida estritamente o contrato de entrada exigindo apenas listas de listas.

        Raises:
            TypeError/ValueError se qualquer regra for violada
        """
        # Regra 1: Deve ser lista
        if not isinstance(edges, list):
            raise TypeError(f"Erro de Contrato: O grafo deve estar em formato List. Encontrado: {type(edges)}")

        # Regra 2: Não vazia
        if len(edges) == 0:
            raise ValueError("Erro de Consistência: A lista de arestas está vazia")

        # Regra 3-5: Validação de cada aresta
        for idx, edge in enumerate(edges):
            # Regra 3: Cada aresta deve ser estritamente uma sublista com exatamente 3 elementos
            if not isinstance(edge, list) or len(edge) != 3:
                raise ValueError(
                    f"Erro Estrutural na aresta [{idx}]: Esperado sublista no formato [Palavra_A, Palavra_B, Força]. "
                    f"Encontrado: {edge}"
                )

            palavra_a, palavra_b, forca = edge

            # Regra 4: Palavras devem ser strings
            if not isinstance(palavra_a, str) or not isinstance(palavra_b, str):
                raise TypeError(
                    f"Erro de Tipo na aresta [{idx}]: Palavras devem ser strings. "
                    f"Encontrado: {type(palavra_a).__name__}, {type(palavra_b).__name__}"
                )

            # Regra 5: Força deve ser numérica e positiva
            if not isinstance(forca, (int, float)):
                raise TypeError(
                    f"Erro de Tipo na aresta [{idx}]: Força deve ser numérica. "
                    f"Encontrado: {type(forca).__name__}"
                )

            if forca <= 0:
                raise ValueError(
                    f"Erro Lógico na aresta [{idx}]: Força deve ser > 0. "
                    f"Encontrado: {forca}"
                )

        return edges

    def _convert_to_distances(self, edges: List[List]) -> List[List]:
        """Converte peso (força de coocorrência) → distância geométrica (1/peso)"""
        distances = []
        for palavra_a, palavra_b, forca in edges:
            distancia = 1.0 / forca
            distances.append([palavra_a, palavra_b, distancia])
        return distances

    def _sort_by_distance(self, edges: List[List]) -> List[List]:
        """Ordena arestas por distância crescente (arestas mais fortes primeiro na MST)"""
        return sorted(edges, key=lambda e: e[2])

    def _compute_mst_kruskal(self, sorted_edges: List[List]) -> List[List]:
        """Calcula MST usando algoritmo de Kruskal com Union-Find."""
        parent = {}

        def encontrar_raiz(palavra: str) -> str:
            """Find com path compression"""
            if palavra not in parent:
                parent[palavra] = palavra
                return palavra
            if parent[palavra] == palavra:
                return palavra
            parent[palavra] = encontrar_raiz(parent[palavra])
            return parent[palavra]

        def unir_componentes(palavra_a: str, palavra_b: str):
            """Union heurística: une por raiz"""
            raiz_a = encontrar_raiz(palavra_a)
            raiz_b = encontrar_raiz(palavra_b)
            if raiz_a != raiz_b:
                parent[raiz_a] = raiz_b

        mst_edges = []
        for palavra_a, palavra_b, distancia in sorted_edges:
            raiz_a = encontrar_raiz(palavra_a)
            raiz_b = encontrar_raiz(palavra_b)

            if raiz_a != raiz_b:
                mst_edges.append([palavra_a, palavra_b, distancia])
                unir_componentes(palavra_a, palavra_b)

        return mst_edges

    def _partition_communities(self, mst_edges: List[List]) -> List[List[str]]:
        """Particiona MST em comunidades via divisão recursiva balanceada."""
        adjacencia = defaultdict(list)
        for palavra_a, palavra_b, distancia in mst_edges:
            adjacencia[palavra_a].append((palavra_b, distancia))
            adjacencia[palavra_b].append((palavra_a, distancia))

        componentes = self._find_initial_components(adjacencia)
        comunidades = self._recursive_partition(componentes, adjacencia)

        comunidades_validas = [
            sorted(com) for com in comunidades
            if len(com) >= self.min_community_size
        ]
        comunidades_validas.sort(key=len, reverse=True)

        return comunidades_validas

    def _find_initial_components(self, adjacencia: Dict) -> List[Set[str]]:
        """Encontra componentes conexas usando BFS"""
        visitados = set()
        componentes = []

        for nodo_inicial in adjacencia:
            if nodo_inicial in visitados:
                continue

            fila = deque([nodo_inicial])
            visitados.add(nodo_inicial)
            componente = set()

            while fila:
                atual = fila.popleft()
                componente.add(atual)

                for vizinho, _ in adjacencia[atual]:
                    if vizinho not in visitados:
                        visitados.add(vizinho)
                        fila.append(vizinho)

            componentes.append(componente)

        return componentes

    def _recursive_partition(self, componentes: List[Set[str]], adjacencia: Dict) -> List[Set[str]]:
        """Divide componentes recursivamente até atingir target de comunidades."""
        componentes = [set(c) for c in componentes]

        while len(componentes) < self.target_communities:
            componentes.sort(key=len, reverse=True)
            foi_dividida = False

            for idx, componente in enumerate(componentes):
                corte = self._find_best_cut(componente, adjacencia)
                if corte is None:
                    continue

                subcomp_a, subcomp_b = corte
                componentes.pop(idx)
                componentes.extend([subcomp_a, subcomp_b])
                foi_dividida = True
                break

            if not foi_dividida:
                break

        return componentes

    def _find_best_cut(self, nodos: Set[str], adjacencia: Dict) -> Optional[Tuple[Set[str], Set[str]]]:
        """Encontra o melhor ponto de corte em uma componente baseado em balanceamento topológico."""
        nodos = set(nodos)
        qtd = len(nodos)

        if qtd < self.min_community_size * 2:
            return None

        raiz = next(iter(nodos))
        pai = {raiz: None}
        ordem = [raiz]
        pilha = [raiz]

        while pilha:
            atual = pilha.pop()
            for vizinho, _ in adjacencia[atual]:
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
        alvo = qtd / 2.0

        for nodo in ordem[1:]:
            tamanho_a = tamanho_subarvore[nodo]
            tamanho_b = qtd - tamanho_a

            if tamanho_a < self.min_community_size or tamanho_b < self.min_community_size:
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
            for child in filhos.get(atual, []):
                pilha.append(child)

        complemento = nodos - subarvore

        if not subarvore or not complemento:
            return None

        return subarvore, complemento
