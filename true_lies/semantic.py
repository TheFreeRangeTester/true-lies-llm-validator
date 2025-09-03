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
    
    Args:
        text: Texto a normalizar
        mappings: Diccionario {valor_original: [sinonimos]}
    
    Returns:
        str: Texto normalizado
    """
    if not isinstance(text, str) or not mappings:
        return text
    
    text_lower = text.lower()
    
    for original, synonyms in mappings.items():
        for synonym in synonyms:
            text_lower = text_lower.replace(synonym.lower(), original.lower())
    
    return text_lower

def calculate_semantic_similarity(text1, text2):
    """
    Calcula la similitud semántica entre dos textos.
    
    Args:
        text1: Primer texto
        text2: Segundo texto
    
    Returns:
        float: Score de similitud entre 0 y 1
    """
    if not isinstance(text1, str) or not isinstance(text2, str):
        return 0.0
    
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
