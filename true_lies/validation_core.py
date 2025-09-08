#!/usr/bin/env python3
"""
Validación Dinámica Basada en Hechos Configurados, Semántica y Polaridad
========================================================================

Función principal de validación como se muestra en las imágenes.
"""

from .utils import extract_fact
from .semantic import apply_semantic_mappings, calculate_semantic_similarity
from .polarity import detect_polarity

def validate_against_reference_dynamic(candidate_text, reference_scenario, similarity_threshold=0.8):
    """
    Validación dinámica basada en hechos configurados, semántica y polaridad.
    
    Args:
        candidate_text: Texto candidato a validar
        reference_scenario: Escenario de referencia con hechos y mapeos
        similarity_threshold: Umbral de similitud (default: 0.8)
    
    Returns:
        dict: Resultados de la validación
    """
    facts = reference_scenario['facts']
    fact_results = {}
    
    # Validar cada hecho configurado
    for fact_name, fact_config in facts.items():
        extracted = extract_fact(candidate_text, fact_config)
        expected = fact_config['expected']
        
        # Calcular precisión
        if isinstance(extracted, list):
            accuracy = expected in extracted
        else:
            accuracy = extracted == expected
        
        fact_results[f'{fact_name}_accuracy'] = accuracy
        fact_results[f'extracted_{fact_name}'] = extracted
    
    # Precisión factual general
    factual_accuracy = all(fact_results.get(f'{name}_accuracy', False) for name in facts.keys())
    
    # Similitud semántica con mapeos y pesos de hechos
    reference_text = reference_scenario['semantic_reference'].lower()
    candidate_mapped = apply_semantic_mappings(
        candidate_text, 
        reference_scenario.get('semantic_mappings', {})
    )
    
    # Crear pesos de hechos basados en los valores extraídos
    fact_weights = {}
    for fact_name, fact_config in facts.items():
        expected_value = fact_config.get('expected', '')
        if expected_value:
            # Agregar el valor esperado con peso alto
            fact_weights[expected_value.lower()] = 2.0
            # Agregar variaciones del valor esperado
            if isinstance(expected_value, str):
                # Dividir en palabras para valores compuestos
                for word in expected_value.lower().split():
                    if len(word) > 2:  # Solo palabras significativas
                        fact_weights[word] = 1.5
    
    similarity_score = calculate_semantic_similarity(reference_text, candidate_mapped, fact_weights)
    
    # Validación de polaridad con lógica personalizada
    reference_polarity = detect_polarity(reference_scenario['semantic_reference'])
    candidate_polarity = detect_polarity(candidate_text)
    
    # Lógica de polaridad personalizada:
    # Falla cuando:
    # 1. Se esperaba positivo y se encuentra negativo
    # 2. Se esperaba negativo y se encuentra positivo  
    # 3. Se esperaba negativo y se encuentra neutral
    # 4. Se esperaba neutral y se encuentra negativo
    # 
    # Pasa cuando:
    # - Se esperaba positivo y da neutral (permisivo)
    # - Se esperaba neutral y da positivo (permisivo)
    # - Cualquier coincidencia exacta
    
    polarity_match = True  # Por defecto pasa
    
    if reference_polarity == 'positive' and candidate_polarity == 'negative':
        polarity_match = False  # Falla: positivo → negativo
    elif reference_polarity == 'negative' and candidate_polarity == 'positive':
        polarity_match = False  # Falla: negativo → positivo
    elif reference_polarity == 'negative' and candidate_polarity == 'neutral':
        polarity_match = False  # Falla: negativo → neutral
    elif reference_polarity == 'neutral' and candidate_polarity == 'negative':
        polarity_match = False  # Falla: neutral → negativo
    # Todos los demás casos pasan (incluyendo positivo → neutral y neutral → positivo)
    
    # Determinar si es válido y la razón de falla
    is_valid = factual_accuracy and similarity_score >= similarity_threshold and polarity_match
    failure_reason = None
    
    if not is_valid:
        if similarity_score < similarity_threshold:
            failure_reason = "Possible hallucination found in the candidate"
        elif not factual_accuracy:
            failure_reason = "Factual accuracy issues detected"
        elif not polarity_match:
            failure_reason = "Polarity mismatch detected"
    
    return {
        'factual_accuracy': factual_accuracy,
        'similarity_score': similarity_score,
        'polarity_match': polarity_match,
        'reference_polarity': reference_polarity,
        'candidate_polarity': candidate_polarity,
        'is_valid': is_valid,
        'failure_reason': failure_reason,
        **fact_results
    }
