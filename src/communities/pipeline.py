"""
Phase 3: Community Detection via Minimum Spanning Tree (MST) + Partitioning
"""

from collections import defaultdict, deque
from typing import List, Dict, Set, Tuple, Optional


class Phase3Pipeline:
    def __init__(self, target_communities: int = 20, min_community_size: int = 150, verbose: bool = True):
        self.target_communities = target_communities
        self.min_community_size = min_community_size
        self.verbose = verbose

    def run(self, edges: List[List]) -> Dict:
        validated_edges = self._validate_contract(edges)
        if self.verbose:
            print(f"[VALIDAÇÃO] {len(validated_edges)} arestas aprovadas")

        distance_edges = self._convert_to_distances(validated_edges)
        sorted_edges = self._sort_by_distance(distance_edges)
        if self.verbose:
            print(f"[ORDENAÇÃO] Arestas ordenadas por distância")

        mst_edges = self._compute_mst_kruskal(sorted_edges)
        if self.verbose:
            print(f"[MST] {len(mst_edges)} arestas geradas")

        communities = self._partition_communities(mst_edges)
        if self.verbose:
            print(f"[PARTIÇÃO] {len(communities)} comunidades geradas")

        edges_per_community = self._build_edges_per_community(mst_edges, communities)

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
            "edges_per_community": edges_per_community,
            "statistics": statistics,
        }

    def _validate_contract(self, edges: List[List]) -> List[List]:
        if not isinstance(edges, list):
            raise TypeError(f"Esperado List, recebido {type(edges)}")
        if len(edges) == 0:
            raise ValueError("Lista de arestas vazia")

        for idx, edge in enumerate(edges):
            if not isinstance(edge, list) or len(edge) != 3:
                raise ValueError(f"Aresta inválida no índice {idx}")
            a, b, w = edge
            if not isinstance(a, str) or not isinstance(b, str):
                raise TypeError(f"Palavras devem ser strings na aresta {idx}")
            if not isinstance(w, (int, float)) or w <= 0:
                raise ValueError(f"Peso inválido na aresta {idx}: {w}")
        return edges

    def _convert_to_distances(self, edges: List[List]) -> List[List]:
        return [[a, b, 1.0 / w] for a, b, w in edges]

    def _sort_by_distance(self, edges: List[List]) -> List[List]:
        return sorted(edges, key=lambda e: e[2])

    def _compute_mst_kruskal(self, sorted_edges: List[List]) -> List[List]:
        parent = {}

        def find(x):
            if x not in parent:
                parent[x] = x
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py

        mst = []
        for a, b, dist in sorted_edges:
            if find(a) != find(b):
                union(a, b)
                mst.append([a, b, dist])
        return mst

    def _partition_communities(self, mst_edges: List[List]) -> List[List[str]]:
        adj = defaultdict(list)
        for a, b, d in mst_edges:
            adj[a].append((b, d))
            adj[b].append((a, d))

        components = self._find_initial_components(adj)
        communities = self._recursive_partition(components, adj)

        valid = [sorted(c) for c in communities if len(c) >= self.min_community_size]
        valid.sort(key=len, reverse=True)
        return valid

    def _find_initial_components(self, adj: Dict) -> List[Set[str]]:
        visited = set()
        components = []
        for node in list(adj.keys()):
            if node in visited:
                continue
            component = set()
            queue = deque([node])
            visited.add(node)
            while queue:
                curr = queue.popleft()
                component.add(curr)
                for neigh, _ in adj[curr]:
                    if neigh not in visited:
                        visited.add(neigh)
                        queue.append(neigh)
            components.append(component)
        return components

    def _recursive_partition(self, components: List[Set[str]], adj: Dict) -> List[Set[str]]:
        components = [set(c) for c in components]
        while len(components) < self.target_communities:
            components.sort(key=len, reverse=True)
            split = False
            for i in range(len(components)):
                cut = self._find_best_cut(components[i], adj)
                if cut:
                    components.pop(i)
                    components.extend(cut)
                    split = True
                    break
            if not split:
                break
        return components

    def _find_best_cut(self, nodes: Set[str], adj: Dict) -> Optional[Tuple[Set[str], Set[str]]]:
        """Sua implementação original completa"""
        if len(nodes) < self.min_community_size * 2:
            return None

        nodos = set(nodes)
        qtd = len(nodos)
        raiz = next(iter(nodos))
        pai = {raiz: None}
        ordem = [raiz]
        pilha = [raiz]

        while pilha:
            atual = pilha.pop()
            for vizinho, _ in adj[atual]:
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

    def _build_edges_per_community(self, mst_edges: List[List], communities: List[List[str]]) -> Dict[int, List]:
        node_to_com = {}
        for com_id, comm in enumerate(communities):
            for word in comm:
                node_to_com[word] = com_id

        edges_per_com = defaultdict(list)
        for u, v, dist in mst_edges:
            cu = node_to_com.get(u)
            cv = node_to_com.get(v)
            if cu is not None and cv is not None and cu == cv:
                peso = 1.0 / dist if dist > 0 else 1.0
                edges_per_com[cu].append((u, v, peso))
        return dict(edges_per_com)
