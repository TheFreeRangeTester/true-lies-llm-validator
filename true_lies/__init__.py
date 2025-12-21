#!/usr/bin/env python3
"""
True Lies - Separating truth from AI fiction
===========================================

A powerful library for detecting LLM hallucinations and validating AI responses
against factual data, semantic similarity, and polarity analysis.

Uso básico:
    from llm_validator import create_scenario, validate_against_reference_dynamic
    
    # Crear escenario
    scenario = create_scenario(
        facts={
            'precio': {'extractor': 'usd_currency', 'expected': '27'},
            'duracion': {'extractor': 'hours', 'expected': '3'},
            'curso_nombre': {
                'extractor': 'categorical', 
                'expected': 'testing',
                'patterns': {
                    'testing': ['introduccion al testing', 'testing', 'programa de introduccion al testing'],
                    'python': ['python', 'programacion python'],
                    'javascript': ['javascript', 'js']
                }
            }
        },
        semantic_reference='Tenemos el curso de Introduccion al Testing que cuesta USD 27 y dura 3 horas.',
        semantic_mappings={
            'curso': ['programa', 'capacitacion', 'entrenamiento'],
            'cuesta': ['vale', 'precio', 'costo', 'inversion', 'tiene un costo de'],
            'usd': ['dolares', 'dolar'],
            'tenemos': ['ofrecemos', 'disponemos', 'manejamos']
        }
    )
    
    # Validar candidato
    result = validate_against_reference_dynamic(
        candidate_text="Ofrecemos el programa de Introduccion al Testing por 27 dolares durante 3 horas",
        reference_scenario=scenario,
        similarity_threshold=0.7
    )
    
    print(f"Valid: {result['is_valid']}")
    print(f"Factual accuracy: {result['factual_accuracy']}")
    print(f"Similarity: {result['similarity_score']:.3f}")
"""

# Importar funciones principales para la API pública
from .scenario import create_scenario
from .validation_core import validate_against_reference_dynamic
from .runner import validate_llm_candidates
from .extractors import EXTRACTORS
from .utils import extract_fact
from .polarity import POLARITY_PATTERNS, detect_polarity
from .semantic import apply_semantic_mappings, calculate_semantic_similarity
from .conversation import ConversationValidator
from .html_reporter import HTMLReporter

# API pública
__all__ = [
    # Funciones principales
    'create_scenario',
    'validate_against_reference_dynamic',
    'validate_llm_candidates',
    
    # Extractores
    'EXTRACTORS',
    'extract_fact',
    
    # Polaridad
    'POLARITY_PATTERNS',
    'detect_polarity',
    
    # Semántica
    'apply_semantic_mappings',
    'calculate_semantic_similarity',
    
    # Validación Multiturno
    'ConversationValidator',
    
    # Reportes HTML
    'HTMLReporter'
]

# Información del paquete
__version__ = "0.9.1"
__author__ = "True Lies Team"
__description__ = "Separating truth from AI fiction - A powerful library for detecting LLM hallucinations"