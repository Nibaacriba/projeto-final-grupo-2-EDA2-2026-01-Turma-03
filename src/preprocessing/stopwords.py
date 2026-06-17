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

    "current",
}

# Stopwords e termos genéricos identificados na análise de data/processed
# (tokens de alta frequência, vazamento de stopwords do spaCy e lémas
# divergentes após lematização, ex.: including -> include)
CORPUS_STOPWORDS = {
    # Lémas que escapavam de stopwords já cadastradas
    "accord",
    "include",

    # Pronomes / referências vagas
    "here",
    "there",
    "thing",

    # spaCy stopwords ainda presentes após lematização
    "alone",
    "amount",
    "anywhere",
    "become",
    "bottom",
    "call",
    "due",
    "eight",
    "eleven",
    "else",
    "empty",
    "enough",
    "front",
    "full",
    "further",
    "give",
    "hundred",
    "keep",
    "latter",
    "least",
    "move",
    "name",
    "next",
    "none",
    "off",
    "part",
    "per",
    "put",
    "rather",
    "re",
    "see",
    "seem",
    "serious",
    "several",
    "show",
    "side",
    "ten",
    "third",
    "top",
    "twelve",
    "twenty",
    "used",
    "various",
    "whole",

    # Tempo / calendário
    "afternoon",
    "annual",
    "april",
    "august",
    "day",
    "december",
    "evening",
    "friday",
    "january",
    "july",
    "june",
    "march",
    "moment",
    "monday",
    "month",
    "morning",
    "night",
    "november",
    "october",
    "period",
    "quarter",
    "saturday",
    "september",
    "sunday",
    "thursday",
    "time",
    "today",
    "tomorrow",
    "tuesday",
    "wednesday",
    "week",
    "yesterday",

    # Quantidades e unidades comuns em notícias
    "billion",
    "million",
    "percent",
    "percentage",
    "thousand",

    # Verbos genéricos de reportagem
    "add",
    "believe",
    "buy",
    "continue",
    "cut",
    "expect",
    "face",
    "fall",
    "find",
    "follow",
    "give",
    "grow",
    "help",
    "hit",
    "hold",
    "know",
    "lead",
    "look",
    "lose",
    "need",
    "offer",
    "pay",
    "play",
    "receive",
    "release",
    "remain",
    "report",
    "rise",
    "run",
    "see",
    "sell",
    "set",
    "start",
    "tell",
    "think",
    "use",
    "want",
    "win",
    "work",

    # Adjetivos genéricos
    "big",
    "good",
    "high",
    "large",
    "late",
    "long",
    "low",
    "recent",
    "strong",

    # Substantivos genéricos / boilerplate jornalístico
    "analyst",
    "award",
    "base",
    "business",
    "chief",
    "comment",
    "company",
    "cost",
    "country",
    "deal",
    "demand",
    "director",
    "dollar",
    "end",
    "executive",
    "figure",
    "film",
    "financial",
    "firm",
    "group",
    "growth",
    "interest",
    "life",
    "market",
    "money",
    "news",
    "number",
    "office",
    "official",
    "people",
    "place",
    "plan",
    "president",
    "price",
    "public",
    "rate",
    "record",
    "sale",
    "share",
    "source",
    "spokesman",
    "spokesperson",
    "spokeswoman",
    "star",
    "state",
    "statement",
    "trade",
    "way",
    "world",

    # Domínio econômico/jornalístico muito frequente e pouco discriminativo
    "bank",
    "bbc",
    "british",
    "economic",
    "economy",
    "government",
    "increase",
    "industry",
    "international",
    "investment",
    "london",
    "music",
    "production",
    "tv",
    "uk",

    # Entretenimento genérico (aparece em quase todo artigo da categoria)
    "actor",
    "producer",
    "singer",

    # Genéricos adicionais (>= 10% dos documentos em data/processed)
    "agree",
    "announce",
    "begin",
    "boost",
    "bring",
    "change",
    "claim",
    "close",
    "create",
    "decision",
    "euro",
    "europe",
    "european",
    "february",
    "force",
    "foreign",
    "fund",
    "future",
    "giant",
    "global",
    "great",
    "head",
    "hop",
    "investor",
    "issue",
    "job",
    "leave",
    "level",
    "likely",
    "main",
    "man",
    "meet",
    "member",
    "oil",
    "old",
    "open",
    "performance",
    "point",
    "problem",
    "profit",
    "raise",
    "reach",
    "result",
    "return",
    "role",
    "series",
    "sign",
    "stock",
    "support",
    "term",
    "total",
    "try",
    "turn",
    "value",
    "york",
}

ENGLISH_STOPWORDS.update(BBC_STOPWORDS)
ENGLISH_STOPWORDS.update(CORPUS_STOPWORDS)


def get_stopwords() -> set:
    """
    Retorna o conjunto de stopwords em inglês.

    Returns:
        set: Conjunto contendo stopwords em inglês.
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
