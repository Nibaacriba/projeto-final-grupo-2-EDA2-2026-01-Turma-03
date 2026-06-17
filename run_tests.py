#!/usr/bin/env python3
"""
Test Runner para o projeto BBC News.

Documentação completa: README.md - Seção "Executando Testes"
"""

import sys
import subprocess
from pathlib import Path


def print_header(title):
    """Imprime um cabeçalho formatado."""
    print("\n")
    print("╔" + "=" * 70 + "╗")
    print("║" + title.center(70) + "║")
    print("╚" + "=" * 70 + "╝")
    print()


def print_help():
    """Exibe mensagem de ajuda."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║              TEST RUNNER - BBC NEWS PROJECT                   ║
╚═══════════════════════════════════════════════════════════════╝

Uso:
    python3 run_tests.py              # Executa todos os testes
    python3 run_tests.py phase1       # Executa testes da Fase 1
    python3 run_tests.py phase2       # Executa testes da Fase 2
    python3 run_tests.py phase3       # Executa testes da Fase 3
    python3 run_tests.py --help       # Exibe esta mensagem

Testes Disponíveis:
    Phase 1: Validação de pré-processamento (JSON, JSONL, Pickle)
    Phase 2: Validação de grafo de coocorrência
    Phase 3: Validação de detecção de comunidades

Exemplos:
    python3 run_tests.py                    # Todos
    python3 run_tests.py phase1             # Só Fase 1
    python3 run_tests.py phase2 phase3      # Fase 2 + Fase 3
""")


def run_tests(phases):
    """Executa testes das fases especificadas."""
    project_root = Path(__file__).resolve().parent

    phase_mapping = {
        "phase1": "tests.test_phase1",
        "phase2": "tests.test_phase2",
        "phase3": "tests.test_phase3",
    }

    total_passed = 0
    total_failed = 0

    for phase in phases:
        if phase not in phase_mapping:
            print(f"❌ Fase desconhecida: {phase}")
            continue

        module = phase_mapping[phase]
        print_header(f"EXECUTANDO {phase.upper()}")

        try:
            result = subprocess.run(
                ["python3", "-m", module],
                cwd=str(project_root),
                capture_output=False,
                timeout=60
            )

            if result.returncode == 0:
                total_passed += 1
                print(f"\n✅ {phase.upper()} passou!\n")
            else:
                total_failed += 1
                print(f"\n❌ {phase.upper()} falhou!\n")

        except subprocess.TimeoutExpired:
            total_failed += 1
            print(f"\n❌ {phase.upper()} excedeu o tempo limite!\n")
        except Exception as e:
            total_failed += 1
            print(f"\n❌ Erro ao executar {phase}: {e}\n")

    # Resumo final
    print_header("RESUMO DOS TESTES")
    print(f"✅ Aprovados: {total_passed}")
    print(f"❌ Falhados:  {total_failed}")
    print(f"📊 Total:     {total_passed + total_failed}")

    return total_failed == 0


def main():
    """Função principal."""
    if len(sys.argv) < 2:
        # Se nenhum argumento, executar todos
        phases = ["phase1", "phase2", "phase3"]
    else:
        arg = sys.argv[1].lower().strip()

        if arg in {"--help", "-h", "help"}:
            print_help()
            return True

        if arg in {"all", "-a"}:
            phases = ["phase1", "phase2", "phase3"]
        else:
            phases = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

    if not phases:
        print("❌ Nenhuma fase especificada!")
        print_help()
        return False

    success = run_tests(phases)
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
