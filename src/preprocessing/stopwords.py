"""
Gerenciador de stopwords para o pipeline de pré-processamento.

Stopwords são palavras muito comuns que geralmente não agregam valor
semântico (artigos, preposições, etc.) e podem ser removidas para
melhorar a qualidade da análise.
"""

# Stopwords em inglês
# Fonte: lista comum de stopwords em inglês
ENGLISH_STOPWORDS = {
    # Artigos
    "a", "an", "the",

    # Preposições
    "at", "by", "for", "from", "in", "of", "on", "to", "with",
    "about", "above", "after", "before", "between", "down", "during",
    "into", "out", "over", "through", "under", "up", "below", "above",

    # Conjunções
    "and", "or", "but", "nor", "yet", "so", "because", "if", "unless",
    "while", "when", "where", "why", "how",

    # Verbos auxiliares
    "am", "are", "as", "be", "been", "being", "do", "does", "did",
    "doing", "have", "has", "had", "having", "is", "was", "were",
    "being", "will", "would", "shall", "should", "can", "could",
    "may", "might", "must", "ought",

    # Pronomes
    "i", "you", "he", "she", "it", "we", "they", "me", "him", "her",
    "us", "them", "mine", "yours", "his", "hers", "ours", "theirs",
    "this", "that", "these", "those", "who", "whom", "whose", "which",
    "what", "my", "your", "his", "her", "its", "our", "their",
    "myself", "yourself", "himself", "herself", "itself", "ourselves",
    "yourselves", "themselves",

    # Outras palavras comuns
    "all", "another", "any", "each", "each", "every", "few", "both",
    "no", "not", "only", "some", "such", "than", "too", "very",
    "just", "most", "also", "even", "much", "own", "same", "so",
    "then", "now", "more", "less", "all", "few", "some", "any",
    "other", "such", "no", "nor", "through", "throughout",
}

BBC_STOPWORDS = {
    "said",
    "says",
    "say",

    "mr",
    "mrs",
    "ms",

    "year",
    "years",

    "new",

    "one",
    "two",
    "three",

    "first",
    "second",

    "last",

    "also",

    "could",
    "would",
    "should",

    "may",
    "might",

    "made",
    "make",

    "get",
    "gets",
    "got",

    "go",
    "goes",
    "went",

    "come",
    "comes",
    "came",

    "take",
    "takes",
    "took",

    "many",
    "much",

    "well",

    "still",

    "back",

    "like",

    "according",

    "however",

    "including",

    "among",

    "around",

    "across",

    "since",

    "yet",

    "even",

    "another",

    "already",

    "former",

    "current"
}

ENGLISH_STOPWORDS.update(BBC_STOPWORDS)



def get_stopwords() -> set:
    """
    Retorna o conjunto de stopwords em português.

    Returns:
        set: Conjunto contendo stopwords em português.
    """
    return ENGLISH_STOPWORDS.copy()


def is_stopword(word: str) -> bool:
    """
    Verifica se uma palavra é um stopword.

    Args:
        word: Palavra a verificar.

    Returns:
        bool: True se a palavra é um stopword, False caso contrário.
    """
    return word.lower() in ENGLISH_STOPWORDS
