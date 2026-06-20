import os
import pickle
import pandas as pd
import networkx as nx
from pyvis.network import Network
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

def carregar_dados(tema: str):
    caminho_pkl = DATA_DIR / "graph_edges.pkl"
    with open(caminho_pkl, "rb") as f:
        arestas = pickle.load(f)

    caminho_csv = DATA_DIR / f"comunidades_tabular_{tema}.csv"
    
    if not caminho_csv.exists():
        raise FileNotFoundError(f"Arquivo CSV não encontrado: {caminho_csv}. Rode o see.py antes para gerar!")
        
    df_comunidades = pd.read_csv(caminho_csv)
    
    return arestas, df_comunidades

def construir_e_renderizar_grafo(arestas, df_comunidades, tema):
    print("🎨 Construindo a visualização gráfica...")
    
    G = nx.Graph()

    paleta = ["#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231", 
              "#911eb4", "#46f0f0", "#f032e6", "#bcf60c", "#fabebe"]
    
    mapa_cores = {}
    
    for _, linha in df_comunidades.iterrows():
        id_com = int(linha["id_comunidade"])
        cor = paleta[id_com % len(paleta)] 
        
        palavras = [p.strip() for p in linha["palavras"].split(",")]
        
        for palavra in palavras:
            mapa_cores[palavra] = cor
            G.add_node(palavra, color=cor, title=f"Comunidade {id_com}")

    for u, v, peso in arestas:
        if u in G.nodes and v in G.nodes:
            G.add_edge(u, v, value=peso)

    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
    net.from_nx(G)
    
    net.repulsion(node_distance=100, central_gravity=0.2, spring_length=200)

    arquivo_saida = f"grafo_interativo_{tema}.html"
    net.show(arquivo_saida, notebook=False)
    print(f"✅ Sucesso! O grafo foi renderizado no arquivo: {arquivo_saida}")

if __name__ == "__main__":
    TEMA_TESTE = "business" 
    
    try:
        arestas, df = carregar_dados(TEMA_TESTE)
        construir_e_renderizar_grafo(arestas, df, TEMA_TESTE)
    except Exception as e:
        print(f"❌ Erro: {e}")