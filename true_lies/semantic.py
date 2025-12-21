#!/usr/bin/env python3
"""
Funciones Semánticas
===================

Funciones para manejo de mapeos semánticos y similitud.
"""

from difflib import SequenceMatcher

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

def calculate_semantic_similarity(text1, text2, fact_weights=None):
    """
    Calcula la similitud semántica entre dos textos usando un algoritmo mejorado
    que penaliza las adiciones no deseadas (posibles alucinaciones).
    
    Args:
        text1: Primer texto (referencia)
        text2: Segundo texto (candidato)
        fact_weights: Diccionario con pesos para tokens importantes (opcional)
    
    Returns:
        float: Score de similitud entre 0 y 1
    """
    import re
    from difflib import SequenceMatcher
    
    if not isinstance(text1, str) or not isinstance(text2, str):
        return 0.0
    
    # Normalizar textos (remover puntuación, convertir a minúsculas)
    text1_norm = re.sub(r'[^\w\s]', ' ', text1.lower())
    text2_norm = re.sub(r'[^\w\s]', ' ', text2.lower())
    
    # Dividir en tokens
    tokens1 = set(text1_norm.split())
    tokens2 = set(text2_norm.split())
    
    # Calcular overlap de tokens
    common_tokens = tokens1.intersection(tokens2)
    total_tokens = tokens1.union(tokens2)
    
    # Score base de overlap de tokens
    token_score = len(common_tokens) / len(total_tokens) if total_tokens else 0
    
    # PENALIZACIÓN POR ADICIONES: Detectar posibles alucinaciones
    tokens_only_in_candidate = tokens2 - tokens1
    tokens_only_in_reference = tokens1 - tokens2
    
    # Calcular penalización por adiciones excesivas
    addition_penalty = 0.0
    if len(tokens1) > 0:
        addition_ratio = len(tokens_only_in_candidate) / len(tokens1)
        
        # Aplicar penalización progresiva:
        # - 0-10% adicionales: sin penalización
        # - 10-30% adicionales: penalización moderada
        # - >30% adicionales: penalización fuerte
        if addition_ratio > 0.1:
            if addition_ratio <= 0.3:
                # Penalización moderada: 10-30% adicionales
                addition_penalty = (addition_ratio - 0.1) * 0.5
            else:
                # Penalización fuerte: >30% adicionales
                addition_penalty = 0.1 + (addition_ratio - 0.3) * 1.5
    
    # Aplicar penalización al score de tokens
    token_score = max(token_score - addition_penalty, 0.0)
    
    # Score de secuencia (menos peso)
    sequence_score = SequenceMatcher(None, text1_norm, text2_norm).ratio()
    
    # Aplicar pesos a tokens importantes si se proporcionan
    weighted_score = token_score
    if fact_weights:
        for token, weight in fact_weights.items():
            if token in common_tokens:
                weighted_score += weight * 0.1  # Bonus por tokens importantes
    
    # Combinar scores (70% tokens ponderados, 30% secuencia)
    final_score = (weighted_score * 0.7) + (sequence_score * 0.3)
    
    return min(final_score, 1.0)  # Cap at 1.0
