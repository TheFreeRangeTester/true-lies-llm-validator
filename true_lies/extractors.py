#!/usr/bin/env python3
"""
Extractores Genéricos Reutilizables
===================================

Diccionario de extractores genéricos como se muestra en las imágenes.
"""

import re

# Extractores genéricos reutilizables
EXTRACTORS = {
    'money': lambda text: (
        re.findall(r'\$\d+', text)[0] if re.findall(r'\$\d+', text) else
        re.findall(r'(?:USD|dollars?|dolares?)\s*(\d+)', text, re.IGNORECASE)[0] if re.findall(r'(?:USD|dollars?|dolares?)\s*(\d+)', text, re.IGNORECASE) else
        re.findall(r'(\d+)\s*(?:dollars?|dolares?)', text, re.IGNORECASE)[0] if re.findall(r'(\d+)\s*(?:dollars?|dolares?)', text, re.IGNORECASE) else
        None
    ),
    'percentage': lambda text: re.findall(r'\d+\.?\d*%', text)[0] if re.findall(r'\d+\.?\d*%', text) else None,
    'date': lambda text: re.findall(r'\d{1,2}/\d{1,2}/\d{4}', text)[0] if re.findall(r'\d{1,2}/\d{1,2}/\d{4}', text) else None,
    'categorical': lambda text, patterns: next((key for key, synonyms in patterns.items() if any(synonym.lower() in text.lower() for synonym in synonyms)), None),
    'regex': lambda text, pattern: re.findall(pattern, text)[0] if re.findall(pattern, text) else None,
    'number': lambda text: re.findall(r'\d+\.?\d*', text)[0] if re.findall(r'\d+\.?\d*', text) else None,
    'hours': lambda text: re.findall(r'(\d+)\s*horas?|hours?', text)[0] if re.findall(r'(\d+)\s*horas?|hours?', text) else None,
    'email': lambda text: re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)[0] if re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text) else None,
    'phone': lambda text: re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)[0] if re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text) else None,
}

# Esta función está obsoleta - usar la de utils.py
def extract_fact(text, fact_config):
    """
    DEPRECATED: Esta función está obsoleta. Usar la de utils.py
    """
    # Importar la función actualizada
    from .utils import extract_fact as updated_extract_fact
    return updated_extract_fact(text, fact_config)
