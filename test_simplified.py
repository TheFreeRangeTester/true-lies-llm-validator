#!/usr/bin/env python3
"""
Test simplificado para verificar que validate_llm_candidates funciona
"""

from llm_validator import create_scenario, validate_llm_candidates

def test_simple():
    """Test básico con validate_llm_candidates"""
    print("="*80)
    print("TEST SIMPLIFICADO - validate_llm_candidates")
    print("="*80)
    
    # Crear escenario simple
    scenario = create_scenario(
        facts={
            'precio': {'extractor': 'money', 'expected': '299'},
            'duracion': {'extractor': 'hours', 'expected': '40'},
            'curso': {'extractor': 'categorical', 'expected': 'python'}
        },
        semantic_reference='El curso de Python cuesta $299 y dura 40 horas.',
        semantic_mappings={
            'curso': ['programa', 'capacitación'],
            'cuesta': ['vale', 'precio'],
            'dura': ['duración', 'extensión']
        }
    )
    
    # Candidatos a validar
    candidates = [
        "El curso de Python cuesta $299 y dura 40 horas.",
        "El programa de Python vale $299 y tiene una duración de 40 horas.",
        "El curso de Python cuesta $299 y dura 30 horas.",  # ❌ Duración incorrecta
        "El curso de JavaScript cuesta $299 y dura 40 horas."  # ❌ Curso incorrecto
    ]
    
    # Validar
    results = validate_llm_candidates(
        scenario=scenario,
        candidates=candidates,
        threshold=0.7
    )
    
    print(f"\n📊 RESUMEN:")
    print(f"Total válidos: {results['fully_valid']}/{results['total_candidates']}")
    print(f"Precisión factual: {results['summary']['factual_accuracy']:.1%}")
    print(f"Precisión general: {results['summary']['overall_accuracy']:.1%}")
    
    return results

if __name__ == "__main__":
    test_simple()
