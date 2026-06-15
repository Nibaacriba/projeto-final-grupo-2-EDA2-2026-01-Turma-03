"""
Manipulador de arquivos para entrada e saída de dados.

Fornece funcionalidades para:
- Ler documentos dos arquivos de texto
- Escrever documentos processados em formatos diversos
- Listar arquivos em diretórios
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any


class FileHandler:
    """
    Manipulador de arquivos para o projeto.

    Gerencia leitura de documentos brutos e escrita de dados processados.
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
            IOError: Se houver erro na leitura.
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
        Lista todos os arquivos com uma extensão específica em um diretório.

        Args:
            directory: Caminho do diretório.
            extension: Extensão dos arquivos a listar (padrão: ".txt").

        Returns:
            Lista com os nomes dos arquivos encontrados (sem caminho).

        Raises:
            FileNotFoundError: Se o diretório não existir.
        """
        directory_path = Path(directory)

        if not directory_path.exists():
            raise FileNotFoundError(f"Diretório não encontrado: {directory}")

        if not directory_path.is_dir():
            raise NotADirectoryError(f"{directory} não é um diretório")

        # Lista arquivos com a extensão especificada
        files = sorted([
            f.name for f in directory_path.glob(f"*{extension}")
        ])

        return files

    @staticmethod
    def get_file_path(directory: str, filename: str) -> str:
        """
        Constrói o caminho completo de um arquivo.

        Args:
            directory: Diretório base.
            filename: Nome do arquivo.

        Returns:
            Caminho completo do arquivo.
        """
        return os.path.join(directory, filename)

    @staticmethod
    def save_json(data: List[Dict[str, Any]], output_path: str, indent: int = 2) -> None:
        """
        Salva dados em formato JSON.

        Args:
            data: Dados a salvar (lista de dicionários).
            output_path: Caminho de saída do arquivo JSON.
            indent: Número de espaços para indentação (padrão: 2).

        Raises:
            IOError: Se houver erro na escrita.
        """
        try:
            # Converter sets para listas para serialização JSON
            json_data = []
            for item in data:
                json_item = item.copy()
                if isinstance(json_item.get("tokens"), set):
                    json_item["tokens"] = sorted(list(json_item["tokens"]))
                json_data.append(json_item)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=indent)

        except IOError as e:
            raise IOError(f"Erro ao salvar arquivo JSON {output_path}: {e}")

    @staticmethod
    def save_jsonl(data: List[Dict[str, Any]], output_path: str) -> None:
        """
        Salva dados em formato JSONL (JSON Lines).

        Cada documento é salvo em uma linha separada.
        Formato útil para processamento streaming.

        Args:
            data: Dados a salvar (lista de dicionários).
            output_path: Caminho de saída do arquivo JSONL.

        Raises:
            IOError: Se houver erro na escrita.
        """
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                for item in data:
                    json_item = item.copy()
                    if isinstance(json_item.get("tokens"), set):
                        json_item["tokens"] = sorted(list(json_item["tokens"]))
                    f.write(json.dumps(json_item, ensure_ascii=False) + "\n")

        except IOError as e:
            raise IOError(f"Erro ao salvar arquivo JSONL {output_path}: {e}")

    @staticmethod
    def save_python_pickle(data: List[Dict[str, Any]], output_path: str) -> None:
        """
        Salva dados em formato Python pickle.

        Mantém tipos nativos do Python (como sets) sem conversão.

        Args:
            data: Dados a salvar (lista de dicionários).
            output_path: Caminho de saída do arquivo pickle.

        Raises:
            IOError: Se houver erro na escrita.
        """
        try:
            import pickle
            with open(output_path, "wb") as f:
                pickle.dump(data, f)

        except IOError as e:
            raise IOError(f"Erro ao salvar arquivo pickle {output_path}: {e}")

    @staticmethod
    def load_python_pickle(input_path: str) -> List[Dict[str, Any]]:
        """
        Carrega dados do formato Python pickle.

        Args:
            input_path: Caminho do arquivo pickle a carregar.

        Returns:
            Dados carregados (lista de dicionários).

        Raises:
            FileNotFoundError: Se o arquivo não existir.
            IOError: Se houver erro na leitura.
        """
        try:
            import pickle
            with open(input_path, "rb") as f:
                return pickle.load(f)

        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")
        except IOError as e:
            raise IOError(f"Erro ao carregar arquivo pickle {input_path}: {e}")
