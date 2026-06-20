import os
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
SRC_DIR = BASE_DIR / "src"

os.makedirs(SRC_DIR, exist_ok=True)

def atualizar_tabela(*args):
    for item in tree.get_children():
        tree.delete(item)
        
    tema = combo_tema.get()
    caminho_csv = DATA_DIR / f"comunidades_tabular_{tema}.csv"
    
    try:
        df = pd.read_csv(caminho_csv)
        for _, linha in df.head(20).iterrows():
            resumo = ", ".join([p.strip() for p in str(linha["palavras"]).split(",")][:10]) + "..."
            tree.insert("", tk.END, values=(linha["id_comunidade"], linha["quantidade_palavras"], resumo))
    except FileNotFoundError:
        tree.insert("", tk.END, values=("Aviso", "---", f"Arquivo CSV para '{tema}' não encontrado. Execute a Fase 4."))

def gerar_grafo():
    tema = combo_tema.get()
    caminho_csv = DATA_DIR / f"comunidades_tabular_{tema}.csv"
    caminho_pkl = DATA_DIR / "graph_edges.pkl"
    
    if not caminho_csv.exists() or not caminho_pkl.exists():
        messagebox.showerror(
            "Restrição de Dependência", 
            f"Os dados pré-processados para o tema '{tema}' não foram encontrados.\n\n"
            "O visual.py depende das etapas anteriores. Por favor, execute a pipeline na ordem:\n"
            "1. PLN e Limpeza de Textos\n"
            "2. Construção do Grafo\n"
            "3. Formação de Comunidades\n"
            "4. Exportação Tabular"
        )
        return

    try:
        print("⏳ Iniciando o gerador de visualização...")
        print(f"⏳ Passo 1: Lendo as comunidades do tema '{tema}'...")
        df = pd.read_csv(caminho_csv)
        
        print("⏳ Passo 2: Separando as top 15 palavras de cada grupo...")
        G = nx.Graph()
        paleta = ["#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231", 
                  "#911eb4", "#46f0f0", "#f032e6", "#bcf60c", "#fabebe"]
        
        mapa_comunidade = {}
        
        for _, linha in df.iterrows():
            id_com = int(linha["id_comunidade"])
            cor = paleta[id_com % len(paleta)]
            palavras = [p.strip() for p in str(linha["palavras"]).split(",")][:15]
            
            for p in palavras:
                mapa_comunidade[p] = (id_com, cor) 
                G.add_node(p, color=cor, title=f"Comunidade {id_com}")
        
        print("⏳ Passo 3: Carregando as conexões do grafo...")
        with open(caminho_pkl, "rb") as f:
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
        
        arquivo_html = str(SRC_DIR / f"grafo_interativo_{tema}.html")
        
        print(f"⏳ Passo 6: Salvando o arquivo em {arquivo_html}...")
        net.save_graph(arquivo_html)
        
        print(f"✅ SUCESSO! O arquivo foi gerado.")
        
        webbrowser.open(f"file://{arquivo_html}")
        
    except Exception as e:
        messagebox.showerror("Erro", f"Erro crítico ao gerar o grafo:\n{e}")

def montar_interface():
    global tree, combo_tema
    
    root = tk.Tk()
    root.title("Fase 5 - Renderização Visual de Comunidades")
    root.geometry("900x650") 
    
    lbl = tk.Label(root, text="Tabela de Comunidades Destiladas", font=("Arial", 16, "bold"))
    lbl.pack(pady=10)
    
    frame_tema = tk.Frame(root)
    frame_tema.pack(pady=5)
    
    lbl_tema = tk.Label(frame_tema, text="Selecione o Tema:", font=("Arial", 12))
    lbl_tema.pack(side=tk.LEFT, padx=5)
    
    combo_tema = ttk.Combobox(frame_tema, values=["business", "entertainment", "all"], font=("Arial", 12), state="readonly")
    combo_tema.current(0)
    combo_tema.pack(side=tk.LEFT, padx=5)
    
    combo_tema.bind("<<ComboboxSelected>>", atualizar_tabela)
    
    colunas = ("ID", "Qtd Termos", "Palavras Principais (Amostra)")
    tree = ttk.Treeview(root, columns=colunas, show="headings", height=15)
    
    tree.heading("ID", text="ID")
    tree.column("ID", width=50, anchor="center")
    
    tree.heading("Qtd Termos", text="Qtd Termos")
    tree.column("Qtd Termos", width=100, anchor="center")
    
    tree.heading("Palavras Principais (Amostra)", text="Palavras Principais (Amostra)")
    tree.column("Palavras Principais (Amostra)", width=700)
    
    tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
    
    atualizar_tabela()
    
    btn = tk.Button(root, text="🎨 Gerar Grafo Interativo", font=("Arial", 12, "bold"), 
                    bg="#4CAF50", fg="white", command=gerar_grafo)
    btn.pack(pady=15, ipadx=10, ipady=10)
    
    root.mainloop()

if __name__ == "__main__":
    montar_interface()