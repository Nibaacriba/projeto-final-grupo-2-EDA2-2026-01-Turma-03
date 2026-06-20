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
        tree.insert("", tk.END, values=("Aviso", "---", f"Ficheiro CSV para o tema '{tema}' não foi encontrado. Por favor, execute a Fase 4."))

def gerar_grafo():
    tema = combo_tema.get()
    caminho_csv = DATA_DIR / f"comunidades_tabular_{tema}.csv"
    caminho_pkl = DATA_DIR / "graph_edges.pkl"
    
    if not caminho_csv.exists() or not caminho_pkl.exists():
        messagebox.showerror(
            "Restrição de Dependência", 
            f"Os dados pré-processados para o tema '{tema}' não foram encontrados.\n\n"
            "O programa visual.py depende das etapas anteriores. Por favor, execute o pipeline na ordem:\n"
            "1. Processamento de Linguagem Natural (PLN)\n"
            "2. Construção do Grafo Ponderado\n"
            "3. Formação e Particionamento de Comunidades\n"
            "4. Exportação Tabular dos Dados"
        )
        return

    try:
        print("⏳ Iniciando o gerador de visualização...")
        print(f"⏳ Passo 1: A ler as comunidades do tema '{tema}'...")
        df = pd.read_csv(caminho_csv)
        
        print("⏳ Passo 2: A extrair as 15 principais palavras de cada grupo...")
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
        
        print("⏳ Passo 3: A carregar as conexões do grafo...")
        with open(caminho_pkl, "rb") as f:
            arestas = pickle.load(f)

        print("⏳ Passo 4: A cruzar conexões VIP...")
        for u, v, peso in arestas:
            if u in mapa_comunidade and v in mapa_comunidade:
                id_com_u = mapa_comunidade[u][0]
                id_com_v = mapa_comunidade[v][0]
                
                if id_com_u == id_com_v and peso >= 4:
                    G.add_edge(u, v, value=peso)

        nos_isolados = [n for n, d in G.degree() if d == 0]
        if nos_isolados:
            print(f"⏳ A ligar {len(nos_isolados)} nós isolados às respetivas comunidades...")
            for u in nos_isolados:
                if u in mapa_comunidade:
                    id_com_u, cor_u = mapa_comunidade[u]
                    melhor_peso = -1
                    melhor_vizinho = None
                    
                    for edge_u, edge_v, peso in arestas:
                        vizinho = None
                        if edge_u == u:
                            vizinho = edge_v
                        elif edge_v == u:
                            vizinho = edge_u
                        
                        if vizinho and vizinho in mapa_comunidade:
                            id_com_vizinho = mapa_comunidade[vizinho][0]
                            if id_com_vizinho == id_com_u:
                                if peso > melhor_peso:
                                    melhor_peso = peso
                                    melhor_vizinho = vizinho
                    
                    if melhor_vizinho:
                        G.add_edge(u, melhor_vizinho, value=melhor_peso)
        
        print("⏳ Passo 5: A desenhar o gráfico com física de agrupamento...")
        net = Network(height="100vh", width="100%", bgcolor="#222222", font_color="white")
        net.from_nx(G)
        net.force_atlas_2based(gravity=-50, central_gravity=0.01, spring_length=100, damping=0.4, overlap=0)
        
        arquivo_html = str(SRC_DIR / f"grafo_interativo_{tema}.html")
        
        print(f"⏳ Passo 6: A guardar o ficheiro em {arquivo_html}...")
        net.save_graph(arquivo_html)

        try:
            with open(arquivo_html, "r", encoding="utf-8") as f:
                conteudo_html = f.read()

            css_loading_fix = """
            <style>
            #loadingBar {
                position: absolute !important;
                top: 0 !important;
                left: 0 !important;
                width: 100% !important;
                height: 100% !important;
                background-color: rgba(34, 34, 34, 0.95) !important;
                transition: all 0.5s ease !important;
                opacity: 1 !important;
                z-index: 9999 !important;
                display: flex !important;
                justify-content: center !important;
                align-items: center !important;
                flex-direction: column !important;
            }
            #loadingBar .outerBorder {
                display: flex !important;
                align-items: center !important;
                gap: 15px !important;
                background: #2d2d2d !important;
                padding: 20px 30px !important;
                border-radius: 12px !important;
                box-shadow: 0 4px 20px rgba(0,0,0,0.5) !important;
                border: 1px solid #444 !important;
                width: auto !important;
                height: auto !important;
                position: relative !important;
            }
            #text {
                position: static !important;
                font-size: 18px !important;
                color: #ffffff !important;
                font-family: Arial, sans-serif !important;
                font-weight: bold !important;
                width: auto !important;
                height: auto !important;
                margin: 0 !important;
            }
            #border {
                position: static !important;
                width: 250px !important;
                height: 16px !important;
                border: 1px solid #555 !important;
                background: #111 !important;
                border-radius: 8px !important;
                overflow: hidden !important;
                margin: 0 !important;
            }
            #bar {
                position: static !important;
                height: 100% !important;
                background: #4CAF50 !important;
                border: none !important;
                border-radius: 0 !important;
                transition: width 0.2s ease !important;
                margin: 0 !important;
            }
            </style>
            """
            conteudo_html = conteudo_html.replace("</head>", f"{css_loading_fix}\n</head>")
            
            with open(arquivo_html, "w", encoding="utf-8") as f:
                f.write(conteudo_html)
            print("🎨 CSS de correção do carregamento aplicado com sucesso!")
        except Exception as e:
            print(f"⚠️ Aviso: Não foi possível aplicar as correções de CSS: {e}")
        
        print(f"✅ SUCESSO! O ficheiro foi gerado com sucesso.")
        
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
    combo_tema.current(2)
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
                    bg="#4CAF50", fg="#000000", activebackground="#45a049", activeforeground="#000000",
                    relief=tk.RAISED, bd=2, command=gerar_grafo)
    btn.pack(pady=15, ipadx=10, ipady=10)
    
    root.mainloop()

if __name__ == "__main__":
    montar_interface()