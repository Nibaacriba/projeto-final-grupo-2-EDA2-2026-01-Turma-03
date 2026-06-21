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
        tree.insert("", tk.END, values=("Aviso", "---", f"Ficheiro para '{tema}' não encontrado."))

def gerar_grafo():
    tema = combo_tema.get()
    csv_path = DATA_DIR / f"comunidades_tabular_{tema}.csv"
    edges_path = DATA_DIR / f"mst_edges_{tema}.pkl"

    if not csv_path.exists() or not edges_path.exists():
        messagebox.showerror("Dados ausentes", f"Execute a pipeline para o tema '{tema}' primeiro.")
        return

    try:
        print("⏳ Gerando grafo com clusters mais compactos...")
        df = pd.read_csv(csv_path)

        G = nx.Graph()
        paleta = ["#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231",
                  "#911eb4", "#46f0f0", "#f032e6", "#bcf60c", "#fabebe"]

        mapa_comunidade = {}
        hub_comunidade = {}
        MAX_POR_COM = 100

        for _, row in df.iterrows():
            com_id = int(row["id_comunidade"])
            color = paleta[com_id % len(paleta)]
            words = [p.strip() for p in str(row["palavras"]).split(",")][:MAX_POR_COM]

            if words:
                hub_comunidade[com_id] = words[0]

            for word in words:
                mapa_comunidade[word] = (com_id, color)
                G.add_node(word, color=color, title=f"Comunidade {com_id}", size=14)

        with open(edges_path, "rb") as f:
            edges_per_com = pickle.load(f)

        for com_id, edges in edges_per_com.items():
            for u, v, weight in edges:
                if u in mapa_comunidade and v in mapa_comunidade:
                    G.add_edge(u, v, value=weight)

        # Conecta isolados
        for n in list(G.nodes()):
            if G.degree(n) == 0:
                com_id = mapa_comunidade[n][0]
                hub = hub_comunidade.get(com_id)
                if hub and n != hub:
                    G.add_edge(n, hub, value=1)

        net = Network(height="100vh", width="100%", bgcolor="#1a1a1a", font_color="white")

        for node, attrs in G.nodes(data=True):
            net.add_node(node,
                        color=attrs['color'],
                        title=attrs['title'],
                        size=attrs.get('size', 14),
                        label=node[:18])

        for u, v, data in G.edges(data=True):
            net.add_edge(u, v, value=data.get('value', 1), color="#444444")

        # Configuração forte para clusters compactos e redondos
        net.set_options("""
        {
          "physics": {
            "forceAtlas2Based": {
              "gravitationalConstant": -120,
              "centralGravity": 0.008,
              "springLength": 80,
              "springConstant": 0.12,
              "damping": 0.75,
              "avoidOverlap": 0.95
            },
            "solver": "forceAtlas2Based",
            "timestep": 0.4,
            "stabilization": {
              "enabled": true,
              "iterations": 2000,
              "updateInterval": 25,
              "fit": true
            }
          },
          "nodes": {
            "font": { "size": 13, "face": "Arial", "color": "#eeeeee" }
          },
          "edges": {
            "smooth": { "type": "continuous", "roundness": 0 },
            "color": { "inherit": false }
          }
        }
        """)

        html_path = SRC_DIR / f"grafo_interativo_{tema}.html"
        net.save_graph(str(html_path))

        try:
            with open(html_path, "r", encoding="utf-8") as f:
                conteudo = f.read()

            css_fix = """
            <style>
            #loadingBar {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                z-index: 1000;
                background-color: rgba(0,0,0,0);
            }
            #loadingBar .outerBorder {
                text-align: center;
                padding: 20px;
                background: rgba(0,0,0,0.7);
                border-radius: 8px;
            }
            #text {
                margin-bottom: 8px;
                font-family: Arial, sans-serif;
                color: white;
            }
            </style>
            """

            conteudo = conteudo.replace("</head>", f"{css_fix}\n</head>")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(conteudo)
        except Exception:
            pass

        webbrowser.open(f"file://{html_path}")
        print("✅ Grafo gerado com clusters mais compactos!")

    except Exception as e:
        messagebox.showerror("Erro", str(e))

def montar_interface():
    global tree, combo_tema
    root = tk.Tk()
    root.title("Fase 5 - Renderização Visual de Comunidades")
    root.geometry("1000x700")

    tk.Label(root, text="Tabela de Comunidades Destiladas", font=("Arial", 16, "bold")).pack(pady=10)

    frame = tk.Frame(root)
    frame.pack(pady=5)
    tk.Label(frame, text="Tema:").pack(side=tk.LEFT, padx=5)
    combo_tema = ttk.Combobox(frame, values=["business", "entertainment", "all"], state="readonly")
    combo_tema.current(2)
    combo_tema.pack(side=tk.LEFT, padx=5)
    combo_tema.bind("<<ComboboxSelected>>", atualizar_tabela)

    cols = ("ID", "Qtd Termos", "Palavras Principais")
    tree = ttk.Treeview(root, columns=cols, show="headings", height=18)
    for col, width in zip(cols, [60, 100, 750]):
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor="center" if col != "Palavras Principais" else "w")
    tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

    atualizar_tabela()

    tk.Button(root, text="🎨 Gerar Grafo Interativo", font=("Arial", 12, "bold"),
              bg="#4CAF50", fg="black", command=gerar_grafo).pack(pady=15, ipadx=20, ipady=8)

    root.mainloop()


if __name__ == "__main__":
    montar_interface()
