import csv
import os
from typing import List

class TabularExporter:
    """
    Classe responsável pela Fase 4: Documento Tabular.
    Exporta as comunidades geradas pelo grafo para um arquivo CSV legível.
    """
    
    @staticmethod
    def export_to_csv(communities: List[List[str]], output_path: str) -> None:
        """
        Transforma a lista de comunidades em um arquivo CSV.
        
        Args:
            communities: Lista de listas, onde cada sublista contém as palavras de uma comunidade.
            output_path: Caminho completo onde o arquivo .csv será salvo.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        print(f"\n📝 Iniciando Fase 4: Exportação Tabular...")
        print(f"Gerando documento para {len(communities)} comunidades...")

        # Abre o arquivo para escrita
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Cabeçalho 
            writer.writerow(["id_comunidade", "quantidade_palavras", "palavras"])

            for idx, comunidade in enumerate(communities):
                id_comunidade = idx + 1 # Começa o ID no 1 em vez de 0 para ficar mais legível
                tamanho = len(comunidade)
                
                palavras_str = ", ".join(comunidade) 
                
                writer.writerow([id_comunidade, tamanho, palavras_str])

        print(f"✅ Sucesso! Arquivo tabular exportado para: {output_path}")