"""
Configuração e fixtures compartilhadas para todos os testes com pytest.

Este arquivo permite que os testes sejam executados com:
- pytest tests/test_phase1.py
- pytest tests/test_phase2.py
- pytest tests/test_phase3.py
- pytest tests/ (todos os testes)
"""

import pytest
import sys
from pathlib import Path

# Adicionar o diretório raiz do projeto ao path para importações
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_documents():
    """Fixture com documentos de exemplo para testes."""
    return [
        {
            "id": "doc_001",
            "category": "business",
            "tokens": {"banco", "juros", "selic", "taxa"}
        },
        {
            "id": "doc_002",
            "category": "business",
            "tokens": {"banco", "cliente", "empréstimo"}
        },
        {
            "id": "doc_003",
            "category": "entertainment",
            "tokens": {"filme", "ator", "cinema"}
        },
    ]


@pytest.fixture
def sample_edges():
    """Fixture com arestas de grafo de exemplo para testes."""
    return [
        ["banco", "juros", 5],
        ["banco", "selic", 4],
        ["juros", "selic", 3],
        ["filme", "ator", 2],
        ["ator", "cinema", 1],
    ]
