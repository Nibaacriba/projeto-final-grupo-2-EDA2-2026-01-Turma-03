"""
Processador de textos para pipeline de pré-processamento.

Implementa todas as etapas necessárias para transformar texto bruto
em uma representação limpa e organizada de tokens relevantes.

Etapas do pipeline:
1. Normalização do texto
2. Conversão para minúsculas
3. Remoção de pontuação (modo básico) ou tokenização via spaCy (modo PLN)
4. Tokenização
5. Lematização (spaCy) — unifica flexões como playing/played/plays -> play
6. Remoção de stopwords
7. Remoção de tokens inválidos
8. Remoção de palavras repetidas
9. Produção da representação final
"""

import re
import string
from typing import List, Set, Dict, Any, Optional

from .stopwords import is_stopword

CONTENT_POS = frozenset({"NOUN", "PROPN", "VERB", "ADJ"})
_POSSESSIVE_PATTERN = re.compile(r"(\w)'s\b", re.IGNORECASE)
_NUMERIC_PATTERN = re.compile(r"^[\d$£€]+[\d.,]*[a-z%]*$", re.IGNORECASE)


class TextProcessor:
    """
    Processador de textos que implementa o pipeline completo de pré-processamento.

    Atributos:
        min_token_length: Comprimento mínimo de um token para ser considerado válido.
        remove_numbers: Se True, remove tokens que contêm apenas números.
        use_lemmatization: Se True, usa spaCy para tokenização e lematização.
    """

    def __init__(
        self,
        min_token_length: int = 2,
        remove_numbers: bool = True,
        use_lemmatization: bool = True,
        spacy_model: str = "en_core_web_sm",
    ):
        """
        Inicializa o processador de textos.

        Args:
            min_token_length: Comprimento mínimo de um token (padrão: 2).
            remove_numbers: Se True, remove tokens numéricos (padrão: True).
            use_lemmatization: Se True, aplica lematização com spaCy (padrão: True).
            spacy_model: Nome do modelo spaCy a carregar.
        """
        self.min_token_length = min_token_length
        self.remove_numbers = remove_numbers
        self.use_lemmatization = use_lemmatization
        self.spacy_model = spacy_model
        self._nlp = None

    def _get_nlp(self):
        """Carrega o modelo spaCy sob demanda."""
        if self._nlp is None:
            import spacy

            try:
                self._nlp = spacy.load(self.spacy_model, disable=["ner", "parser"])
            except OSError as exc:
                raise OSError(
                    f"Modelo spaCy '{self.spacy_model}' não encontrado. "
                    f"Instale com: python -m spacy download {self.spacy_model}"
                ) from exc
        return self._nlp

    def process_document(self, text: str) -> Set[str]:
        """
        Processa um documento através do pipeline completo.

        Args:
            text: Texto bruto a processar.

        Returns:
            Set contendo os tokens relevantes (sem repetições).
        """
        text = self._normalize(text)
        text = text.lower()

        if self.use_lemmatization:
            tokens = self._tokenize_and_lemmatize(text)
        else:
            text = self._remove_punctuation(text)
            tokens = self._tokenize(text)

        tokens = self._filter_invalid_tokens(tokens)
        tokens = self._remove_stopwords(tokens)
        return set(tokens)

    def _normalize(self, text: str) -> str:
        """
        Normaliza o texto removendo espaços extras e artefatos comuns.

        - Remove espaços múltiplos
        - Converte possessivos (AOL's -> AOL) antes da tokenização
        - Substitui hífens por espaço para evitar palavras coladas (box-office -> box office)
        """
        text = " ".join(text.split())
        text = _POSSESSIVE_PATTERN.sub(r"\1", text)
        text = text.replace("-", " ")
        return text

    def _remove_punctuation(self, text: str) -> str:
        """Remove pontuação do texto (modo básico, sem spaCy)."""
        translator = str.maketrans("", "", string.punctuation)
        return text.translate(translator)

    def _tokenize(self, text: str) -> List[str]:
        """Tokeniza o texto dividindo por espaços em branco."""
        return text.split()

    def _tokenize_and_lemmatize(self, text: str) -> List[str]:
        """
        Tokeniza e lematiza com spaCy.

        Usa lematização (não stemming) para preservar palavras inteiras
        e unificar apenas flexões morfológicas.
        """
        doc = self._get_nlp()(text)
        lemmas: List[str] = []

        for token in doc:
            if token.is_space or token.is_punct or token.pos_ not in CONTENT_POS:
                continue

            lemma = token.lemma_.lower().strip()
            if lemma and lemma != "-":
                lemmas.append(lemma)

        return lemmas

    def _is_numeric_token(self, token: str) -> bool:
        """Verifica se o token representa número ou valor monetário."""
        if not token:
            return True
        if token.isdigit():
            return True
        return bool(_NUMERIC_PATTERN.match(token))

    def _filter_invalid_tokens(self, tokens: List[str]) -> List[str]:
        """
        Filtra tokens inválidos.

        Um token é considerado inválido se:
        - Tem comprimento menor que min_token_length
        - É composto apenas de números ou valores monetários (se remove_numbers=True)
        - Contém dígitos misturados a letras (ex.: 109bn, 600m)
        - Não é composto apenas por letras
        - Está vazio
        """
        valid_tokens = []

        for token in tokens:
            if len(token) < self.min_token_length:
                continue

            if not token:
                continue

            if self.remove_numbers and self._is_numeric_token(token):
                continue

            if not token.isalpha():
                continue

            valid_tokens.append(token)

        return valid_tokens

    def _remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove stopwords da lista de tokens."""
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
        """
        processed_documents = []

        for document in documents:
            processed_doc = {
                "id": document["id"],
                "category": document["category"],
                "tokens": self.process_document(document["text"]),
            }
            processed_documents.append(processed_doc)

        return processed_documents
