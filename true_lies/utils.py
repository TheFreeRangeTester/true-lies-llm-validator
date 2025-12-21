#!/usr/bin/env python3
"""
Utilidades para validación de LLM - Versión Limpia
==================================================

Solo contiene extractores genéricos y la función extract_fact como en la imagen.
"""

import re
from difflib import SequenceMatcher

# ============================================================================
# EXTRACTORES GENÉRICOS REUTILIZABLES
# ============================================================================

def extract_money(text, format='usd'):
    """
    Función unificada para extraer valores de moneda USD en cualquier formato
    
    Args:
        text: Texto a analizar
        format: Formato de salida ('usd', 'symbol', 'number', 'original')
            - 'usd': Devuelve "USD 27" (formato estándar)
            - 'symbol': Devuelve "$27" (con símbolo)
            - 'number': Devuelve "27" (solo número)
            - 'original': Devuelve en el formato original encontrado
    
    Returns:
        str: Valor extraído en el formato especificado
    """
    import re
    if not isinstance(text, str):
        return None
    
    # Patrones prioritarios para montos claramente asociados con moneda
    # 1. Números con símbolo $ (más específico)
    dollar_pattern = r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)'
    # 2. USD seguido de número
    usd_pattern = r'(?i)usd\s+(\d+(?:,\d{3})*(?:\.\d{2})?)'
    # 3. Número seguido de palabras de moneda
    currency_words_pattern = r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s+(?:dolares?|dólares?|dollar|dollars)'
    
    # Buscar en orden de prioridad
    patterns = [
        (dollar_pattern, 'symbol'),
        (usd_pattern, 'usd'),
        (currency_words_pattern, 'words')
    ]
    
    for pattern, pattern_type in patterns:
        match = re.search(pattern, text)
        if match:
            amount = match.group(1)
            
            if format == 'usd':
                return f"USD {amount}"
            elif format == 'symbol':
                return f"${amount}"
            elif format == 'number':
                return amount
            elif format == 'original':
                # Devolver en el formato original encontrado
                if pattern_type == 'symbol':
                    return f"${amount}"
                elif pattern_type == 'usd':
                    return f"USD {amount}"
                elif pattern_type == 'words':
                    return f"{amount} dólares"
            else:
                return f"USD {amount}"  # Default
    
    return None

# Funciones de compatibilidad (deprecated - usar extract_money)
def extract_currency(text):
    """DEPRECATED: Usar extract_money(text, format='symbol')"""
    return extract_money(text, format='symbol')

def extract_currency_all(text):
    """DEPRECATED: Usar extract_money con format='symbol'"""
    import re
    if not isinstance(text, str):
        return None
    
    # Buscar todos los patrones de moneda
    pattern = r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)'
    matches = re.findall(pattern, text)
    if matches:
        return [f"${match}" for match in matches]
    return None

def extract_usd_currency(text, include_prefix=True):
    """DEPRECATED: Usar extract_money(text, format='usd' o 'number')"""
    if include_prefix:
        return extract_money(text, format='usd')
    else:
        return extract_money(text, format='number')

def extract_percentage(text):
    """
    Extrae porcentajes (ej: 12.34%)
    """
    import re
    if not isinstance(text, str):
        return None
    
    pattern = r'(\d+(?:\.\d+)?)%'
    match = re.search(pattern, text)
    if match:
        return f"{match.group(1)}%"
    return None

def extract_date(text):
    """
    Extrae fechas en múltiples formatos:
    - DD/MM/YYYY, DD/MM, MM/DD/YYYY, MM/DD
    - DD-MM-YYYY, DD-MM, YYYY-MM-DD
    - 25 de Diciembre, 25 de Diciembre de 2024
    - Diciembre 25, Diciembre 25, 2024
    - 25 Dec 2024, Dec 25, 2024
    - Y más variaciones en español e inglés
    """
    import re
    if not isinstance(text, str):
        return None
    
    # Diccionario de meses en español e inglés
    months_es = {
        'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
        'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
        'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
    }
    
    months_en = {
        'january': '01', 'february': '02', 'march': '03', 'april': '04',
        'may': '05', 'june': '06', 'july': '07', 'august': '08',
        'september': '09', 'october': '10', 'november': '11', 'december': '12',
        'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
        'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
        'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
    }
    
    # Patrones de fechas - ordenados por especificidad (más específicos primero)
    patterns = [
        # YYYY-MM-DD (formato ISO) - más específico primero
        (r'(\d{4}-\d{1,2}-\d{1,2})', 'numeric'),
        # DD/MM/YYYY o DD/MM
        (r'(\d{1,2}/\d{1,2}(?:/\d{4})?)', 'numeric'),
        # DD-MM-YYYY o DD-MM
        (r'(\d{1,2}-\d{1,2}(?:-\d{4})?)', 'numeric'),
        # Con ordinales: "25th December 2024" - más específico
        (r'(\d{1,2})(?:st|nd|rd|th)\s+([A-Za-z]+)\s+(\d{4})', 'ordinal_3'),
        # Con ordinales: "25th December" - solo con meses conocidos
        (r'(\d{1,2})(?:st|nd|rd|th)\s+(January|February|March|April|May|June|July|August|September|October|November|December|Enero|Febrero|Marzo|Abril|Mayo|Junio|Julio|Agosto|Septiembre|Octubre|Noviembre|Diciembre)', 'ordinal_2'),
        # Con ordinales: "October 10th" - orden inverso
        (r'(January|February|March|April|May|June|July|August|September|October|November|December|Enero|Febrero|Marzo|Abril|Mayo|Junio|Julio|Agosto|Septiembre|Octubre|Noviembre|Diciembre)\s+(\d{1,2})(?:st|nd|rd|th)', 'ordinal_2_rev'),
        # Con ordinales: "December 25th, 2024"
        (r'([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th),\s*(\d{4})', 'ordinal_3_rev'),
        # Con ordinales: "December 25th"
        (r'([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)', 'ordinal_2_rev'),
        # Mes en español: "25 de Diciembre de 2024"
        (r'(\d{1,2})\s+de\s+([A-Za-z]+)\s+de\s+(\d{4})', 'text_es_3'),
        # Mes en español: "25 de Diciembre"
        (r'(\d{1,2})\s+de\s+([A-Za-z]+)', 'text_es_2'),
        # Mes en español: "Diciembre 25, 2024"
        (r'([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})', 'text_es_3_rev'),
        # Mes en español: "Diciembre 25"
        (r'([A-Za-z]+)\s+(\d{1,2})', 'text_es_2_rev'),
        # Mes en inglés: "25 December 2024"
        (r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', 'text_en_3'),
        # Mes en inglés: "25 December"
        (r'(\d{1,2})\s+([A-Za-z]+)', 'text_en_2'),
        # Mes en inglés: "December 25, 2024"
        (r'([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})', 'text_en_3_rev'),
        # Mes en inglés: "December 25"
        (r'([A-Za-z]+)\s+(\d{1,2})', 'text_en_2_rev')
    ]
    
    for pattern, pattern_type in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if pattern_type == 'numeric':
                return match.group(1)
            else:
                return _normalize_text_date(match.groups(), pattern_type, months_es, months_en)
    
    return None

def _normalize_text_date(groups, pattern_type, months_es, months_en):
    """
    Normaliza fechas con meses en texto a formato estándar
    """
    import re
    
    # Filtrar grupos None
    groups = [g for g in groups if g is not None]
    
    # Determinar el formato basado en el tipo de patrón
    if pattern_type == 'text_es_3':
        # "25 de Diciembre de 2024"
        day, month, year = groups
    elif pattern_type == 'text_es_2':
        # "25 de Diciembre"
        day, month = groups
        year = None
    elif pattern_type == 'text_es_3_rev':
        # "Diciembre 25, 2024"
        month, day, year = groups
    elif pattern_type == 'text_es_2_rev':
        # "Diciembre 25"
        month, day = groups
        year = None
    elif pattern_type == 'text_en_3':
        # "25 December 2024"
        day, month, year = groups
    elif pattern_type == 'text_en_2':
        # "25 December"
        day, month = groups
        year = None
    elif pattern_type == 'text_en_3_rev':
        # "December 25, 2024"
        month, day, year = groups
    elif pattern_type == 'text_en_2_rev':
        # "December 25"
        month, day = groups
        year = None
    elif pattern_type == 'ordinal_3':
        # "25th December 2024"
        day, month, year = groups
    elif pattern_type == 'ordinal_2':
        # "25th December"
        day, month = groups
        year = None
    elif pattern_type == 'ordinal_3_rev':
        # "December 25th, 2024"
        month, day, year = groups
    elif pattern_type == 'ordinal_2_rev':
        # "December 25th"
        month, day = groups
        year = None
    else:
        return None
    
    # Normalizar mes
    month_lower = month.lower()
    if month_lower in months_es:
        month_num = months_es[month_lower]
    elif month_lower in months_en:
        month_num = months_en[month_lower]
    else:
        return None
    
    # Formatear resultado
    day_padded = day.zfill(2)
    if year:
        return f"{day_padded}/{month_num}/{year}"
    else:
        return f"{day_padded}/{month_num}"

def extract_categorical(text, patterns):
    """
    Extrae valores categóricos basado en patrones de sinónimos
    
    Args:
        text: Texto a analizar
        patterns: Diccionario {valor_esperado: [sinonimos]}
    
    Returns:
        str: El valor esperado si encuentra algún sinónimo, None si no
    """
    if not isinstance(text, str) or not patterns:
        return None
    
    text_lower = text.lower()
    
    # Buscar coincidencias exactas de palabras primero
    for expected_value, synonyms in patterns.items():
        for synonym in synonyms:
            if f" {synonym.lower()} " in f" {text_lower} ":
                return expected_value
    
    # Si no hay coincidencias exactas, buscar substrings
    for expected_value, synonyms in patterns.items():
        for synonym in synonyms:
            if synonym.lower() in text_lower:
                return expected_value
    
    return None

def extract_regex(text, pattern):
    """
    Extrae valores usando un patrón regex personalizado
    
    Args:
        text: Texto a analizar
        pattern: Patrón regex con grupo de captura
    
    Returns:
        str: Primer match encontrado, None si no hay match
    """
    if not isinstance(text, str) or not pattern:
        return None
    
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1) if match.groups() else match.group(0)
    return None

def extract_number(text):
    """
    Extrae números generales (enteros o decimales)
    """
    import re
    if not isinstance(text, str):
        return None
    
    matches = re.findall(r'\d+(?:\.\d+)?', text)
    if matches:
        return matches[0]
    return None

def extract_hours(text):
    """
    Extrae valores de horas (ej: 3 horas, 12 hours)
    """
    import re
    if not isinstance(text, str):
        return None
    
    patterns = [
        r'(\d+)\s+horas?',
        r'(\d+)\s+hours?',
        r'(\d+)\s+h'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

def extract_email(text):
    """
    Extrae direcciones de email
    """
    import re
    if not isinstance(text, str):
        return None
    
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    return None

def extract_phone(text):
    """
    Extrae números de teléfono
    """
    import re
    if not isinstance(text, str):
        return None
    
    patterns = [
        r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
        r'(\+?\d{1,3}[-.\s]?)?\d{2,4}[-.\s]?\d{2,4}[-.\s]?\d{2,4}',  # International
        r'\(\d{3}\)\s?\d{3}-\d{4}'  # (123) 456-7890
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None

def extract_id(text, pattern=None):
    """
    Extrae IDs genéricos (puede ser configurado con patrón)
    """
    import re
    if not isinstance(text, str):
        return None
    
    if pattern:
        match = re.search(pattern, text)
        if match:
            return match.group(1) if match.groups() else match.group(0)
    else:
        # Patrones genéricos para IDs
        patterns = [
            r'([A-Z]{2,}-\d{4}-\d{3})',  # XX-YYYY-ZZZ
            r'([A-Z]{3,}\d{3,})',  # XXX123
            r'(\d{4,})',  # Solo números
            r'([A-Z0-9]{6,})'  # Alfanumérico
        ]
        
        for p in patterns:
            match = re.search(p, text)
            if match:
                return match.group(1)
    return None



# Diccionario de extractores genéricos
# Funciones wrapper para mantener compatibilidad
def extract_usd_amount(text):
    """Wrapper que devuelve solo el monto sin prefijo USD"""
    return extract_money(text, format='number')

def extract_person(text):
    """
    Extrae nombres de personas del texto.
    """
    import re
    
    # Patrones para nombres de personas
    patterns = [
        r'Dr\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # Dr. Garcia, Dr Garcia
        r'Mr\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',   # Mr. Smith
        r'Ms\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',   # Ms. Johnson
        r'Mrs\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # Mrs. Brown
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',           # Nombre simple
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            return matches[0]
    
    return None

def extract_time(text):
    """
    Extrae horas del texto.
    """
    import re
    
    # Patrones para horas
    patterns = [
        r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))',  # 2:30 PM
        r'(\d{1,2}\s*(?:AM|PM|am|pm))',         # 2 PM
        r'(\d{1,2}:\d{2})',                     # 14:30
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            return matches[0]
    
    return None

def extract_location(text):
    """
    Extrae ubicaciones del texto.
    """
    import re
    
    # Patrones para ubicaciones
    patterns = [
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Clinic|Hospital|Center|Office|Building))',  # Green Valley Clinic
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|Avenue|Road|Boulevard))',           # Main Street
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',                                            # Nombre de lugar simple
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            return matches[0]
    
    return None

GENERIC_EXTRACTORS = {
    'money': extract_money,  # Función unificada para dinero
    'percentage': extract_percentage,
    'date': extract_date,
    'categorical': extract_categorical,
    'regex': extract_regex,
    'number': extract_number,
    'hours': extract_hours,
    'email': extract_email,
    'phone': extract_phone,
    'id': extract_id,
    'person': extract_person,    # Nuevo extractor para personas
    'time': extract_time,        # Nuevo extractor para horas
    'location': extract_location # Nuevo extractor para ubicaciones
}

# ============================================================================
# FUNCIÓN PRINCIPAL DE EXTRACCIÓN
# ============================================================================

def extract_fact(text, fact_config):
    """
    Extrae un hecho específico del texto usando un extractor configurado.
    
    Args:
        text: Texto a analizar
        fact_config: Configuración del hecho con extractor
    
    Returns:
        Valor extraído o None
    """
    if 'extractor' not in fact_config:
        return None
    
    extractor_name = fact_config['extractor']
    if extractor_name not in GENERIC_EXTRACTORS:
        return None
    
    extractor_func = GENERIC_EXTRACTORS[extractor_name]
    
    # Manejar extractores que requieren parámetros adicionales
    if extractor_name == 'money':
        # Detectar automáticamente el formato basándose en el expected
        expected = fact_config.get('expected', '')
        if expected.startswith('USD '):
            format_type = 'usd'
        elif expected.startswith('$'):
            format_type = 'symbol'
        elif expected.endswith(' dólares') or expected.endswith(' dolares'):
            format_type = 'original'
        else:
            format_type = 'number'  # Por defecto, solo número
        return extractor_func(text, format=format_type)
    elif extractor_name == 'categorical':
        patterns = fact_config.get('patterns')
        if not patterns:
            return None
        return extractor_func(text, patterns)
    elif extractor_name == 'regex':
        pattern = fact_config.get('pattern')
        if not pattern:
            return None
        return extractor_func(text, pattern)
    elif extractor_name == 'id':
        pattern = fact_config.get('pattern')
        return extractor_func(text, pattern)
    else:
        return extractor_func(text)

# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def create_field_config_with_extractor(field_name, extractor_name, expected_value=None, patterns=None, normalize_func=None, validation_func=None):
    """
    Crea configuración de campo usando extractores genéricos
    
    Args:
        field_name: Nombre del campo
        extractor_name: Nombre del extractor genérico
        expected_value: Valor esperado
        patterns: Patrones para extractores que los requieren
        normalize_func: Función de normalización
        validation_func: Función de validación
    
    Returns:
        dict: Configuración del campo
    """
    config = {
        "field_name": field_name,
        "extractor": extractor_name,
        "expected": expected_value
    }
    
    if patterns:
        config["patterns"] = patterns
    
    if validation_func and callable(validation_func):
        config["validate"] = validation_func
    
    if normalize_func and callable(normalize_func):
        config["normalize"] = normalize_func
    
    return config

def create_dynamic_extractor(extractor_type, **kwargs):
    """
    Crea un extractor dinámico basado en el tipo
    
    Args:
        extractor_type: Tipo de extractor ('currency', 'date', 'categorical', etc.)
        **kwargs: Parámetros específicos del extractor
    
    Returns:
        Función extractora configurada
    """
    if extractor_type not in GENERIC_EXTRACTORS:
        raise ValueError(f"Extractor type '{extractor_type}' not found")
    
    base_extractor = GENERIC_EXTRACTORS[extractor_type]
    
    if extractor_type == 'categorical':
        patterns = kwargs.get('patterns', {})
        return lambda text: base_extractor(text, patterns)
    elif extractor_type == 'regex':
        pattern = kwargs.get('pattern', '')
        return lambda text: base_extractor(text, pattern)
    elif extractor_type == 'id':
        pattern = kwargs.get('pattern')
        return lambda text: base_extractor(text, pattern)
    else:
        return base_extractor

def apply_semantic_mappings(text, mappings):
    """
    Aplica mapeos semánticos para normalizar sinónimos en el texto
    
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

def load_semantic_mapping(domain, path=None):
    """
    Carga mapeo semántico desde archivo JSON
    
    Args:
        domain: Dominio del mapeo (ej: 'insurance', 'banking')
        path: Ruta personalizada al archivo (opcional)
    
    Returns:
        dict: Mapeo semántico o None si no se encuentra
    """
    import json
    import os
    
    if path:
        mapping_path = path
    else:
        # Ruta por defecto
        current_dir = os.path.dirname(os.path.abspath(__file__))
        mapping_path = os.path.join(current_dir, 'semantic_data', f'{domain}.json')
    
    try:
        with open(mapping_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def replace_synonyms(text, mapping):
    """
    Reemplaza sinónimos en el texto usando el mapeo
    
    Args:
        text: Texto a procesar
        mapping: Diccionario de mapeo de sinónimos
    
    Returns:
        str: Texto con sinónimos reemplazados
    """
    if not mapping:
        return text
    
    return apply_semantic_mappings(text, mapping)

def normalize_text_advanced(text):
    """
    Normalización avanzada de texto
    
    Args:
        text: Texto a normalizar
    
    Returns:
        str: Texto normalizado
    """
    if not isinstance(text, str):
        return ""
    
    # Normalización básica
    text = text.lower().strip()
    
    # Remover caracteres especiales excesivos
    text = re.sub(r'\s+', ' ', text)
    
    return text

# Función validate_against_reference_dynamic movida a validation_core.py
# para evitar duplicación y mantener consistencia en la API
