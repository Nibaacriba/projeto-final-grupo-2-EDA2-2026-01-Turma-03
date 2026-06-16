"""
Interface da Fase 3 com os dados reais da Fase 2.

Este módulo expõe `grafo_linear_bruto`, que é consumido por `verify.py`.
A carga é delegada ao conector oficial em `src.graph.fase2_export`.
"""

from pathlib import Path
import sys


_BASE_DIR = Path(__file__).resolve().parents[2]
if str(_BASE_DIR) not in sys.path:
    sys.path.insert(0, str(_BASE_DIR))

from src.graph.fase2_export import importar_dados_fase2


grafo_linear_bruto = importar_dados_fase2()