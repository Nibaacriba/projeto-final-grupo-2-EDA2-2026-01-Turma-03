"""
Manipulador de arquivos para entrada e saída de dados.

Fornece funcionalidades otimizadas para:
- Ler documentos dos arquivos de texto brutos
- Listar arquivos em diretórios do dataset
- Salvar e carregar dados processados no formato binário Pickle (.pkl)
"""

import os
import pickle
from pathlib import Path
from typing import List, Any


class FileHandler:
    """
    Manipulador de arquivos centralizado do projeto.

    Gerencia com alta performance a leitura de documentos brutos e
    a persistência binária do pipeline.
    """

    @staticmethod
    def read_text_file(file_path: str) -> str:
        """
        Lê o conteúdo de um arquivo de texto.

        Args:
            file_path: Caminho do arquivo a ler.

        Returns:
            Conteúdo do arquivo como string.

        Raises:
            FileNotFoundError: Se o arquivo não existir.
            IOError: Se houver erro na leitura do arquivo.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        except IOError as e:
            raise IOError(f"Erro ao ler arquivo {file_path}: {e}")

    @staticmethod
    def list_files_in_directory(directory: str, extension: str = ".txt") -> List[str]:
        """
        Lista e ordena de forma determinística todos os arquivos com uma extensão
        específica dentro de um diretório.

        Args:
            directory: Caminho do diretório base.
            extension: Extensão dos arquivos a filtrar (padrão: ".txt").

        Returns:
            Lista com os nomes dos arquivos encontrados (apenas o nome + extensão).

        Raises:
            FileNotFoundError: Se o diretório não existir.
            NotADirectoryError: Se o caminho informado não for um diretório válido.
        """
        directory_path = Path(directory)

        if not directory_path.exists():
            raise FileNotFoundError(f"Diretório não encontrado: {directory}")

        if not directory_path.is_dir():
            raise NotADirectoryError(f"O caminho informado não é um diretório: {directory}")

        # Busca e ordena os arquivos para garantir reprodutibilidade nos lotes
        files = sorted([
            f.name for f in directory_path.glob(f"*{extension}")
        ])

        return files

    @staticmethod
    def get_file_path(directory: str, filename: str) -> str:
        """
        Constrói o caminho completo de um arquivo de forma segura para o SO.

        Args:
            directory: Diretório base.
            filename: Nome do arquivo com extensão.

        Returns:
            Caminho completo do arquivo como string.
        """
        return os.path.join(directory, filename)

    @staticmethod
    def save_python_pickle(data: Any, output_path: str) -> None:
        """
        Salva dados complexos em formato binário Pickle (.pkl).

        Mantém intactos os tipos nativos do Python (como sets, tuplas e grafos)
        sem a necessidade de conversões pesadas de strings, garantindo máxima performance.

        Args:
            data: Dados a serem serializados (listas, dicionários, sets, etc).
            output_path: Caminho completo de saída do arquivo pkl.

        Raises:
            IOError: Se houver erro na escrita do arquivo binário.
        """
        try:
            # Cria os diretórios pais automaticamente se eles não existirem
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "wb") as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

        except IOError as e:
            raise IOError(f"Erro crítico ao salvar arquivo pickle binário em {output_path}: {e}")

    @staticmethod
    def load_python_pickle(input_path: str) -> Any:
        """
        Carrega dados serializados do formato Python pickle.

        Args:
            input_path: Caminho do arquivo pickle a carregar.

        Returns:
            Os dados originais reconstruídos com seus tipos nativos preservados.

        Raises:
            FileNotFoundError: Se o arquivo binário não existir.
            IOError: Se houver erro na leitura ou desserialização do arquivo.
        """
        try:
            with open(input_path, "rb") as f:
                return pickle.load(f)

        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo de dados binários não encontrado: {input_path}")
        except (IOError, pickle.UnpicklingError) as e:
            raise IOError(f"Erro ao ler/desserializar o arquivo pickle em {input_path}: {e}")
