#!/usr/bin/env python3
"""
Funciones Semánticas
===================

Funciones para manejo de mapeos semánticos y similitud.
"""

def apply_semantic_mappings(text, mappings):
    """
    Aplica mapeos semánticos para normalizar sinónimos en el texto.
    Versión mejorada que usa regex para coincidencias de palabras completas.
    
    Args:
        text: Texto a normalizar
        mappings: Diccionario {valor_original: [sinonimos]}
    
    Returns:
        str: Texto normalizado
    """
    import re
    
    if not isinstance(text, str) or not mappings:
        return text
    
    text_lower = text.lower()
    
    for original, synonyms in mappings.items():
        for synonym in synonyms:
            # Usar regex para coincidencias de palabras completas
            pattern = r'\b' + re.escape(synonym.lower()) + r'\b'
            text_lower = re.sub(pattern, original.lower(), text_lower)
    
    return text_lower


def _semantic_similarity_core(text1, text2, fact_weights=None):
    """
    Núcleo de cálculo de similitud semántica.
    
    Devuelve un diccionario con métricas intermedias y el score final.
    """
    import re
    from difflib import SequenceMatcher
    
    if not isinstance(text1, str) or not isinstance(text2, str):
        return {
            "precision": 0.0,
            "recall": 0.0,
            "token_f1": 0.0,
            "sequence_score": 0.0,
            "weighted_f1": 0.0,
            "final_score": 0.0,
        }
    
    # Normalizar textos (remover puntuación, convertir a minúsculas)
    text1_norm = re.sub(r"[^\w\s]", " ", text1.lower())
    text2_norm = re.sub(r"[^\w\s]", " ", text2.lower())
    
    # Stopwords básicas en inglés y español (para reducir ruido)
    stopwords = {
        # Inglés
        "the", "a", "an", "and", "or", "but", "if", "then", "else", "when", "while",
        "for", "to", "from", "in", "on", "at", "of", "by", "with", "about", "as",
        "this", "that", "these", "those", "it", "its", "is", "are", "was", "were",
        "be", "been", "being", "do", "does", "did", "doing", "have", "has", "had",
        "i", "you", "he", "she", "we", "they", "them", "him", "her", "my", "your",
        "our", "their", "me", "us",
        "please", "thanks", "thank", "sorry",
        # Español
        "el", "la", "los", "las", "un", "una", "unos", "unas",
        "y", "o", "pero", "si", "entonces", "cuando", "mientras",
        "para", "por", "con", "sin", "de", "del", "al", "en", "sobre",
        "este", "esta", "estos", "estas", "eso", "esa", "esos", "esas", "esto",
        "es", "son", "fue", "fueron", "ser", "estar", "está", "están", "estaba",
        "tengo", "tiene", "tienes", "tenemos", "tienen",
        "yo", "tu", "tú", "él", "ella", "nosotros", "nosotras", "ellos", "ellas",
        "mi", "mis", "tu", "tus", "su", "sus", "nuestro", "nuestra", "nuestros", "nuestras",
        "porfavor", "por", "favor", "gracias", "disculpa", "perdón",
    }
    
    def content_tokens(text_norm: str):
        """Obtiene tokens de contenido (sin stopwords, solo palabras significativas)."""
        tokens = text_norm.split()
        return [t for t in tokens if len(t) > 2 and t not in stopwords]
    
    # Tokens de contenido
    tokens1_list = content_tokens(text1_norm)
    tokens2_list = content_tokens(text2_norm)
    tokens1 = set(tokens1_list)
    tokens2 = set(tokens2_list)
    
    if not tokens1 and not tokens2:
        # Fallback: si todo son stopwords / vacío, usar solo SequenceMatcher
        sequence_score_only = SequenceMatcher(None, text1_norm, text2_norm).ratio()
        return {
            "precision": 0.0,
            "recall": 0.0,
            "token_f1": 0.0,
            "sequence_score": float(sequence_score_only),
            "weighted_f1": 0.0,
            "final_score": float(sequence_score_only),
        }
    
    # Calcular precision, recall y F1 sobre tokens de contenido
    common_tokens = tokens1.intersection(tokens2)
    precision = len(common_tokens) / len(tokens2) if tokens2 else 0.0
    recall = len(common_tokens) / len(tokens1) if tokens1 else 0.0
    
    if precision + recall > 0:
        token_f1 = 2 * precision * recall / (precision + recall)
    else:
        token_f1 = 0.0
    
    # Score de secuencia (menos peso), usando texto normalizado completo
    sequence_score = SequenceMatcher(None, text1_norm, text2_norm).ratio()
    
    # Aplicar pesos a tokens importantes si se proporcionan
    weighted_f1 = token_f1
    if fact_weights:
        # Pequeño bonus por cada token clave que está en el overlap
        # Limitamos el bonus total para no inflar artificialmente el score
        bonus = 0.0
        for token, weight in fact_weights.items():
            token_norm = token.lower()
            if token_norm in common_tokens:
                # Cada token clave aporta un bonus acotado
                bonus += min(0.05 * weight, 0.15)
        # Limitar bonus total
        bonus = min(bonus, 0.25)
        weighted_f1 = min(1.0, weighted_f1 + bonus)
    
    # Combinar scores (70% F1 ponderado, 30% secuencia)
    final_score = (weighted_f1 * 0.7) + (sequence_score * 0.3)
    final_score = float(min(max(final_score, 0.0), 1.0))
    
    return {
        "precision": float(precision),
        "recall": float(recall),
        "token_f1": float(token_f1),
        "sequence_score": float(sequence_score),
        "weighted_f1": float(weighted_f1),
        "final_score": final_score,
    }

def calculate_semantic_similarity(text1, text2, fact_weights=None):
    """
    Calcula la similitud semántica entre dos textos.
    
    Versión mejorada:
    - Usa una métrica tipo F1 (precision/recall) sobre tokens de contenido
    - Reduce el impacto de stopwords y frases de cortesía
    - Sigue aprovechando SequenceMatcher como componente secundario
    - Usa fact_weights para reforzar tokens clave sin inflar artificialmente el score
    
    Args:
        text1: Primer texto (referencia)
        text2: Segundo texto (candidato)
        fact_weights: Diccionario con pesos para tokens importantes (opcional)
    
    Returns:
        float: Score de similitud entre 0 y 1
    """
    metrics = _semantic_similarity_core(text1, text2, fact_weights)
    return metrics["final_score"]


def calculate_semantic_similarity_metrics(text1, text2, fact_weights=None):
    """
    Calcula la similitud semántica y devuelve todas las métricas intermedias.
    
    Útil para depuración y visualización avanzada en reportes.
    """
    return _semantic_similarity_core(text1, text2, fact_weights)
