#!/usr/bin/env python3
"""
Herramienta de diagnóstico para identificar problemas con scores de similitud
y extracción en true_lies validator

Uso:
    python diagnostic_tool.py
"""

from true_lies import create_scenario, validate_llm_candidates
from true_lies.utils import extract_fact
from true_lies.semantic import calculate_semantic_similarity

def test_extraction_diagnosis(text, fact_configs):
    """
    Diagnostica problemas de extracción para un texto y configuraciones específicas
    
    Args:
        text: Texto a analizar
        fact_configs: Diccionario con configuraciones de hechos
    """
    print("="*80)
    print("DIAGNÓSTICO DE EXTRACCIÓN")
    print("="*80)
    
    print(f"Texto de prueba: '{text}'")
    print()
    
    for fact_name, config in fact_configs.items():
        print(f"🔍 EXTRACTOR '{config['extractor']}' para {fact_name}:")
        result = extract_fact(text, config)
        print(f"   Resultado: {result}")
        print(f"   Esperado:  {config.get('expected', 'N/A')}")
        print(f"   {'✅ CORRECTO' if result == config.get('expected') else '❌ INCORRECTO'}")
        print()

def test_similarity_diagnosis(reference, candidates, fact_weights=None):
    """
    Diagnostica problemas de similitud entre referencia y candidatos
    
    Args:
        reference: Texto de referencia
        candidates: Lista de textos candidatos
        fact_weights: Pesos opcionales para hechos importantes
    """
    print("="*80)
    print("DIAGNÓSTICO DE SIMILITUD")
    print("="*80)
    
    print(f"Referencia: '{reference}'")
    print()
    
    for i, candidate in enumerate(candidates, 1):
        # Test sin pesos
        score_no_weights = calculate_semantic_similarity(reference, candidate)
        
        # Test con pesos si se proporcionan
        score_with_weights = score_no_weights
        if fact_weights:
            score_with_weights = calculate_semantic_similarity(reference, candidate, fact_weights)
        
        print(f"Candidato {i}: '{candidate}'")
        print(f"   Sin pesos:  {score_no_weights:.3f}")
        if fact_weights:
            print(f"   Con pesos:  {score_with_weights:.3f}")
            print(f"   Mejora:     {score_with_weights - score_no_weights:+.3f}")
        print(f"   {'✅ VÁLIDO' if score_with_weights >= 0.6 else '❌ INVÁLIDO'} (threshold: 0.6)")
        print()

def test_scenario_comparison(scenarios, candidates, threshold=0.6):
    """
    Compara diferentes configuraciones de escenario
    
    Args:
        scenarios: Diccionario con diferentes configuraciones de escenario
        candidates: Lista de textos candidatos
        threshold: Umbral de similitud
    """
    print("="*80)
    print("COMPARACIÓN DE ESCENARIOS")
    print("="*80)
    
    for scenario_name, scenario in scenarios.items():
        print(f"\n{scenario_name}:")
        print("-" * 40)
        
        try:
            results = validate_llm_candidates(
                scenario=scenario, 
                candidates=candidates, 
                threshold=threshold
            )
            print(f"   Válidos: {results['fully_valid']}/{results['total_candidates']}")
            print(f"   Precisión factual: {results['summary']['factual_accuracy']:.1%}")
            print(f"   Precisión general: {results['summary']['overall_accuracy']:.1%}")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
        print()

def run_banking_diagnosis():
    """
    Ejecuta diagnóstico completo para escenario bancario
    """
    print("🏦 DIAGNÓSTICO BANCARIO COMPLETO 🏦")
    print("="*80)
    
    # Texto de prueba
    test_text = "The balance of your Term Deposit account 2992 is $3,000.60"
    
    # Configuraciones de hechos para probar
    fact_configs = {
        'term_deposit': {
            'extractor': 'categorical',
            'expected': 'term_deposit',
            'patterns': {
                'term_deposit': ['term deposit', 'depósito a plazo', 'depósito a término', 'depósito fijo', 'certificado de depósito', 'CD', 'cuenta de depósito'],
                'other_account': ['savings', 'checking', 'current', 'ahorros', 'corriente'],
                'no_account': ['no account', 'sin cuenta']
            }
        },
        'account_number_number': {
            'extractor': 'number',
            'expected': '2992'
        },
        'account_number_categorical': {
            'extractor': 'categorical',
            'expected': 'account_number',
            'patterns': {
                'account_number': ['account', 'cuenta', 'número de cuenta', 'account number', 'número', 'ID de cuenta', 'código de cuenta'],
                'other_info': ['balance', 'amount', 'saldo', 'monto'],
                'no_number': ['no number', 'sin número']
            }
        },
        'balance_amount': {
            'extractor': 'money',
            'expected': '3,000.60'
        }
    }
    
    # Diagnóstico de extracción
    test_extraction_diagnosis(test_text, fact_configs)
    
    # Textos candidatos
    reference = test_text
    candidates = [
        "The balance of your Term Deposit account 2992 is $3,000.60",
        "Your Term Deposit account number 2992 has a current balance of $3,000.60",
        "Account 2992 (Term Deposit) shows a balance of $3,000.60",
        "The balance in your Term Deposit account 2992 is $3,000.60",
        "Your Term Deposit account 2992 currently has $3,000.60 available"
    ]
    
    # Pesos para hechos importantes
    fact_weights = {
        '2992': 2.0,
        '3,000.60': 2.0,
        'term deposit': 1.5,
        'account': 1.0,
        'balance': 1.0
    }
    
    # Diagnóstico de similitud
    test_similarity_diagnosis(reference, candidates, fact_weights)
    
    # Escenarios para comparar
    scenarios = {
        "Escenario con extractor 'number'": create_scenario(
            facts={
                'term_deposit': fact_configs['term_deposit'],
                'account_number': fact_configs['account_number_number'],
                'balance_amount': fact_configs['balance_amount']
            },
            semantic_reference=reference,
            semantic_mappings={}
        ),
        "Escenario con extractor 'categorical'": create_scenario(
            facts={
                'term_deposit': fact_configs['term_deposit'],
                'account_number': fact_configs['account_number_categorical'],
                'balance_amount': fact_configs['balance_amount']
            },
            semantic_reference=reference,
            semantic_mappings={}
        )
    }
    
    # Comparación de escenarios
    test_scenario_comparison(scenarios, candidates[:3])  # Solo primeros 3 para brevedad

def run_custom_diagnosis(text, fact_configs, candidates, fact_weights=None):
    """
    Ejecuta diagnóstico personalizado
    
    Args:
        text: Texto a analizar
        fact_configs: Configuraciones de hechos
        candidates: Lista de candidatos
        fact_weights: Pesos opcionales
    """
    print("🔧 DIAGNÓSTICO PERSONALIZADO 🔧")
    print("="*80)
    
    # Diagnóstico de extracción
    test_extraction_diagnosis(text, fact_configs)
    
    # Diagnóstico de similitud
    test_similarity_diagnosis(text, candidates, fact_weights)

if __name__ == "__main__":
    # Ejecutar diagnóstico bancario por defecto
    run_banking_diagnosis()
    
    print("\n" + "="*80)
    print("💡 RECOMENDACIONES:")
    print("="*80)
    print("1. Para extraer números específicos (como 2992), usa extractor: 'number'")
    print("2. Para extraer categorías (como 'account_number'), usa extractor: 'categorical'")
    print("3. Los pesos de hechos mejoran significativamente los scores de similitud")
    print("4. El extractor 'money' funciona bien para montos con símbolos de moneda")
    print("5. Usa semantic_mappings para mejorar la similitud con sinónimos")
    print("="*80)
