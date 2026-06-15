"""
Processador de textos para pipeline de pré-processamento.

Implementa todas as etapas necessárias para transformar texto bruto
em uma representação limpa e organizada de tokens relevantes.

Etapas do pipeline:
1. Normalização do texto
2. Conversão para minúsculas
3. Remoção de pontuação
4. Tokenização
5. Remoção de stopwords
6. Remoção de tokens inválidos
7. Remoção de palavras repetidas
8. Produção da representação final
"""

import string
from typing import List, Set, Dict, Any
from .stopwords import is_stopword


class TextProcessor:
    """
    Processador de textos que implementa o pipeline completo de pré-processamento.

    Atributos:
        min_token_length: Comprimento mínimo de um token para ser considerado válido.
        remove_numbers: Se True, remove tokens que contêm apenas números.
    """

    def __init__(self, min_token_length: int = 2, remove_numbers: bool = True):
        """
        Inicializa o processador de textos.

        Args:
            min_token_length: Comprimento mínimo de um token (padrão: 2).
            remove_numbers: Se True, remove tokens numéricos (padrão: True).
        """
        self.min_token_length = min_token_length
        self.remove_numbers = remove_numbers

    def process_document(self, text: str) -> Set[str]:
        """
        Processa um documento através do pipeline completo.

        Args:
            text: Texto bruto a processar.

        Returns:
            Set contendo os tokens relevantes (sem repetições).

        Pipeline executado:
            1. Normalização
            2. Minúsculas
            3. Remoção de pontuação
            4. Tokenização
            5. Validação de tokens
            6. Remoção de stopwords
            7. Remoção de repetições (automaticamente via set)
        """
        # Etapa 1: Normalizar
        text = self._normalize(text)

        # Etapa 2: Converter para minúsculas
        text = text.lower()

        # Etapa 3: Remover pontuação
        text = self._remove_punctuation(text)

        # Etapa 4: Tokenizar
        tokens = self._tokenize(text)

        # Etapa 5: Validar e filtrar
        tokens = self._filter_invalid_tokens(tokens)

        # Etapa 6: Remover stopwords
        tokens = self._remove_stopwords(tokens)

        # Etapa 7 e 8: Remover repetições e retornar como set
        # (set já elimina automaticamente palavras repetidas)
        return set(tokens)

    def _normalize(self, text: str) -> str:
        """
        Normaliza o texto removendo espaços em branco extras.

        Args:
            text: Texto a normalizar.

        Returns:
            Texto normalizado.
        """
        # Remove espaços múltiplos
        text = " ".join(text.split())
        return text

    def _remove_punctuation(self, text: str) -> str:
        """
        Remove pontuação do texto.

        Args:
            text: Texto a processar.

        Returns:
            Texto sem pontuação.
        """
        # Remove todos os caracteres de pontuação
        translator = str.maketrans("", "", string.punctuation)
        text = text.translate(translator)
        return text

    def _tokenize(self, text: str) -> List[str]:
        """
        Tokeniza o texto dividindo por espaços em branco.

        Args:
            text: Texto a tokenizar.

        Returns:
            Lista de tokens.
        """
        return text.split()

    def _filter_invalid_tokens(self, tokens: List[str]) -> List[str]:
        """
        Filtra tokens inválidos.

        Um token é considerado inválido se:
        - Tem comprimento menor que min_token_length
        - É composto apenas de números (se remove_numbers=True)
        - Está vazio

        Args:
            tokens: Lista de tokens a filtrar.

        Returns:
            Lista de tokens válidos.
        """
        valid_tokens = []

        for token in tokens:
            # Verificar comprimento
            if len(token) < self.min_token_length:
                continue

            # Verificar se é vazio
            if not token:
                continue

            # Verificar se é apenas números
            if self.remove_numbers and token.isdigit():
                continue

            valid_tokens.append(token)

        return valid_tokens

    def _remove_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Remove stopwords da lista de tokens.

        Args:
            tokens: Lista de tokens a processar.

        Returns:
            Lista de tokens sem stopwords.
        """
        return [token for token in tokens if not is_stopword(token)]

    def process_batch(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processa um lote de documentos.

        Cada documento deve ter a estrutura:
        {
            "id": str,
            "category": str,
            "text": str
        }

        Args:
            documents: Lista de documentos a processar.

        Returns:
            Lista de documentos processados com tokens.

        Exemplo:
            >>> processor = TextProcessor()
            >>> docs = [
            ...     {"id": "001", "category": "business", "text": "..."},
            ...     {"id": "002", "category": "entertainment", "text": "..."}
            ... ]
            >>> result = processor.process_batch(docs)
        """
        processed_documents = []

        for document in documents:
            processed_doc = {
                "id": document["id"],
                "category": document["category"],
                "tokens": self.process_document(document["text"])
            }
            processed_documents.append(processed_doc)

        return processed_documents
