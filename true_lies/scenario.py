#!/usr/bin/env python3
"""
Factory Function para Crear Escenarios Dinámicos
===============================================

Funciones para crear y manejar escenarios de validación.
"""

def create_scenario(facts, semantic_reference, semantic_mappings=None):
    """
    Factory function para crear escenarios dinámicos.
    
    Args:
        facts: Diccionario con hechos configurados
        semantic_reference: Texto de referencia semántica
        semantic_mappings: Mapeos semánticos (opcional)
    
    Returns:
        dict: Escenario configurado
    """
    return {
        'facts': facts,
        'semantic_reference': semantic_reference,
        'semantic_mappings': semantic_mappings or {}
    }
