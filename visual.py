import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import networkx as nx
from pyvis.network import Network
import pickle
import webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

def gerar_grafo():
    try:
        print("⏳ Iniciando o gerador de visualização...")
        print("⏳ Passo 1: Lendo as comunidades...")
        df = pd.read_csv(DATA_DIR / "comunidades_tabular_business.csv")
        
        print("⏳ Passo 2: Separando as top 15 palavras de cada grupo...")
        G = nx.Graph()
        paleta = ["#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231", 
                  "#911eb4", "#46f0f0", "#f032e6", "#bcf60c", "#fabebe"]
        
        mapa_comunidade = {}
        
        for _, linha in df.iterrows():
            id_com = int(linha["id_comunidade"])
            cor = paleta[id_com % len(paleta)]
            palavras = [p.strip() for p in linha["palavras"].split(",")][:15]
            
            for p in palavras:
                mapa_comunidade[p] = (id_com, cor) 
                G.add_node(p, color=cor, title=f"Comunidade {id_com}")
        
        print("⏳ Passo 3: Carregando as conexões do grafo...")
        with open(DATA_DIR / "graph_edges.pkl", "rb") as f:
            arestas = pickle.load(f)

        print("⏳ Passo 4: Cruzando conexões VIPs...")
        for u, v, peso in arestas:
            if u in mapa_comunidade and v in mapa_comunidade:
                id_com_u = mapa_comunidade[u][0]
                id_com_v = mapa_comunidade[v][0]
                
                if id_com_u == id_com_v:
                    G.add_edge(u, v, value=peso)
        
        print("⏳ Passo 5: Desenhando o gráfico com física de agrupamento...")
        net = Network(height="100vh", width="100%", bgcolor="#222222", font_color="white")
        net.from_nx(G)
        net.force_atlas_2based(gravity=-50, central_gravity=0.01, spring_length=100, damping=0.4, overlap=0)
        
        arquivo_html = str(BASE_DIR / "grafo_interativo_business.html")
        
        print("⏳ Passo 6: Salvando o arquivo no computador...")
        net.save_graph(arquivo_html)
        
        print(f"✅ SUCESSO! O arquivo 'grafo_interativo_business.html' foi gerado.")
        
        webbrowser.open(f"file://{arquivo_html}")
        
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao gerar o grafo:\n{e}")

def montar_interface():
    root = tk.Tk()
    root.title("Fase 5 - Renderização Visual de Comunidades")
    root.geometry("900x600") 
    
    lbl = tk.Label(root, text="Tabela de Comunidades Destiladas (Business)", font=("Arial", 16, "bold"))
    lbl.pack(pady=15)
    
    colunas = ("ID", "Qtd Termos", "Palavras Principais (Amostra)")
    tree = ttk.Treeview(root, columns=colunas, show="headings", height=15)
    
    tree.heading("ID", text="ID")
    tree.column("ID", width=50, anchor="center")
    
    tree.heading("Qtd Termos", text="Qtd Termos")
    tree.column("Qtd Termos", width=100, anchor="center")
    
    tree.heading("Palavras Principais (Amostra)", text="Palavras Principais (Amostra)")
    tree.column("Palavras Principais (Amostra)", width=700)
    
    try:
        df = pd.read_csv(DATA_DIR / "comunidades_tabular_business.csv")
        for _, linha in df.head(20).iterrows():
            resumo = ", ".join([p.strip() for p in linha["palavras"].split(",")][:10]) + "..."
            tree.insert("", tk.END, values=(linha["id_comunidade"], linha["quantidade_palavras"], resumo))
    except Exception:
        tree.insert("", tk.END, values=("Erro", "---", "Arquivo CSV não encontrado."))
        
    tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
    
    btn = tk.Button(root, text="🎨 Gerar Grafo Interativo", font=("Arial", 12, "bold"), 
                    bg="#4CAF50", fg="white", command=gerar_grafo)
    btn.pack(pady=20, ipadx=10, ipady=10)
    
    root.mainloop()

if __name__ == "__main__":
    montar_interface()