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
    """Exibe mensagem de ajuda em português."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║              EXECUTOR DE TESTES - PROJETO BBC NEWS            ║
╚═══════════════════════════════════════════════════════════════╝

Uso:
    python3 run_tests.py              # Executa todos os testes
    python3 run_tests.py fase1        # Executa testes da Fase 1
    python3 run_tests.py fase2        # Executa testes da Fase 2
    python3 run_tests.py fase3        # Executa testes da Fase 3
    python3 run_tests.py --help       # Exibe esta mensagem

Testes Disponíveis:
    Fase 1: Validação de pré-processamento e persistência em Pickle (.pkl)
    Fase 2: Validação de construção do grafo de coocorrência
    Fase 3: Validação de detecção de comunidades (MST/Kruskal)

Exemplos:
    python3 run_tests.py                    # Todos os testes
    python3 run_tests.py fase1              # Apenas Fase 1
    python3 run_tests.py fase2 fase3        # Fase 2 + Fase 3
""")


def run_tests(phases):
    """Executa testes das fases especificadas sem repetir mensagens de sucesso individuais."""
    project_root = Path(__file__).resolve().parent

    # Mapeamento para aceitar "faseX" em português
    phase_mapping = {
        "fase1": "tests.test_phase1",
        "fase2": "tests.test_phase2",
        "fase3": "tests.test_phase3",
    }

    # Nomes amigáveis para exibição de logs
    phase_names = {
        "fase1": "FASE 1",
        "fase2": "FASE 2",
        "fase3": "FASE 3"
    }

    total_passed = 0
    total_failed = 0

    for phase in phases:
        if phase not in phase_mapping:
            print(f"❌ Fase desconhecida: {phase}")
            continue

        module = phase_mapping[phase]
        nome_exibicao = phase_names[phase]

        print_header(f"EXECUTANDO {nome_exibicao}")

        try:
            result = subprocess.run(
                ["python3", "-m", module],
                cwd=str(project_root),
                capture_output=False,
                timeout=60
            )

            if result.returncode == 0:
                total_passed += 1
                # O print redundante que aparecia aqui foi removido!
            else:
                total_failed += 1
                print(f"\n❌ {nome_exibicao} falhou no processo geral!\n")

        except subprocess.TimeoutExpired:
            total_failed += 1
            print(f"\n❌ {nome_exibicao} excedeu o tempo limite!\n")
        except Exception as e:
            total_failed += 1
            print(f"\n❌ Erro ao executar {nome_exibicao}: {e}\n")

    # Resumo final padronizado
    print_header("RESUMO DOS TESTES")
    print(f"✅ Aprovados: {total_passed}")
    print(f"❌ Falhados:  {total_failed}")
    print(f"📊 Total:     {total_passed + total_failed}")

    return total_failed == 0


def main():
    """Função principal."""
    if len(sys.argv) < 2:
        # Se nenhum argumento, executar todos
        phases = ["fase1", "fase2", "fase3"]
    else:
        arg = sys.argv[1].lower().strip()

        # Normalizar caso o usuário digite "phase1" em vez de "fase1"
        arg = arg.replace("phase", "fase")

        if arg in {"--help", "-h", "help"}:
            print_help()
            return True

        if arg in {"all", "-a"}:
            phases = ["fase1", "fase2", "fase3"]
        else:
            # Captura todos os argumentos passados e converte "phase" para "fase"
            phases = [a.lower().strip().replace("phase", "fase") for a in sys.argv[1:] if not a.startswith("-")]

    if not phases:
        print("❌ Nenhuma fase especificada!")
        print_help()
        return False

    success = run_tests(phases)
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
