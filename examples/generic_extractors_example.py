#!/usr/bin/env python3
"""
EJEMPLO: Uso de Extractores Genéricos Reutilizables
==================================================

Este ejemplo demuestra cómo usar los nuevos extractores genéricos
para simplificar la configuración de campos en la librería llm-validator.
"""

from llm_validator.runner import run_validation_scenario
from llm_validator.utils import create_field_config_with_extractor, create_field_config

def normalize_coverage_type(value):
    """Normaliza el tipo de cobertura a valores estándar"""
    if not value:
        return None
    value_lower = str(value).lower().strip()
    coverage_mapping = {
        'automobile': 'auto insurance',
        'car': 'auto insurance',
        'auto': 'auto insurance',
        'vehicle': 'auto insurance',
        'auto insurance': 'auto insurance',
        'car insurance': 'auto insurance',
        'automobile insurance': 'auto insurance',
        'vehicle insurance': 'auto insurance'
    }
    return coverage_mapping.get(value_lower, value)

def main():
    print("="*80)
    print("EJEMPLO: Extractores Genéricos Reutilizables")
    print("="*80)
    
    print("\n🎯 COMPARACIÓN DE ENFOQUES:")
    print("1. Método Original: Patrones regex específicos")
    print("2. Método Nuevo: Extractores genéricos reutilizables")
    
    # ============================================================================
    # MÉTODO ORIGINAL: Patrones específicos
    # ============================================================================
    print("\n📝 MÉTODO ORIGINAL (Patrones Específicos):")
    print("-" * 50)
    
    original_field_configs = {
        "policy_number": create_field_config(
            "policy_number",
            [
                r'policy\s+#?([A-Z0-9\-]+)',
                r'#([A-Z0-9\-]+)',
                r'policy\s+([A-Z0-9\-]+)',
                r'([A-Z0-9\-]+)\s+policy'
            ]
        ),
        "premium": create_field_config(
            "premium",
            [
                r'premium\s+of\s+(\$\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'(\$\d+(?:,\d{3})*(?:\.\d{2})?)\s+per\s+month',
                r'(\$\d+(?:,\d{3})*(?:\.\d{2})?)\s+monthly'
            ]
        ),
        "coverage_type": create_field_config(
            "coverage_type",
            [
                r'([A-Za-z]+)\s+policy\s+#',
                r'([A-Za-z]+)\s+policy',
                r'covers?\s+your\s+([A-Za-z]+)'
            ],
            normalize_func=normalize_coverage_type
        )
    }
    
    print("Configuración original:")
    for field, config in original_field_configs.items():
        print(f"  {field}: {len(config['patterns'])} patrones regex")
    
    # ============================================================================
    # MÉTODO NUEVO: Extractores genéricos
    # ============================================================================
    print("\n🚀 MÉTODO NUEVO (Extractores Genéricos):")
    print("-" * 50)
    
    generic_field_configs = {
        "policy_number": create_field_config_with_extractor(
            "policy_number",
            "regex",
            expected_value="POL-2024-001",
            patterns=r'POL-\d{4}-\d{3}'
        ),
        "premium": create_field_config_with_extractor(
            "premium",
            "currency",
            expected_value="$850.00"
        ),
        "coverage_type": create_field_config_with_extractor(
            "coverage_type",
            "categorical",
            expected_value="auto insurance",
            patterns={
                "auto insurance": [
                    "auto policy", "car policy", "automobile policy",
                    "auto insurance", "car insurance", "automobile insurance",
                    "auto coverage", "car coverage", "automobile coverage",
                    "automobile", "car", "auto", "vehicle"
                ]
            },
            normalize_func=normalize_coverage_type
        ),
        "liability_limit": create_field_config_with_extractor(
            "liability_limit",
            "regex",
            expected_value="$100,000",
            patterns=r'(\$\d{1,3}(?:,\d{3})*)\s+liability'
        ),
        "expiry_date": create_field_config_with_extractor(
            "expiry_date",
            "date",
            expected_value="December 31, 2024"
        )
    }
    
    print("Configuración con extractores genéricos:")
    for field, config in generic_field_configs.items():
        print(f"  {field}: extractor='{config['extractor']}'")
    
    # ============================================================================
    # PRUEBA COMPARATIVA
    # ============================================================================
    print("\n🧪 PRUEBA COMPARATIVA:")
    print("-" * 50)
    
    # Texto de prueba
    test_text = "Auto policy #POL-2024-001 has a $850.00 monthly premium with $100,000 liability and comprehensive coverage. Valid until December 31, 2024."
    
    print(f"Texto de prueba: {test_text}")
    print()
    
    # Probar extracción con método original
    print("📊 RESULTADOS CON MÉTODO ORIGINAL:")
    from llm_validator.utils import extract_value_generic
    
    for field, config in original_field_configs.items():
        result = extract_value_generic(test_text, config)
        print(f"  {field}: {result}")
    
    print("\n📊 RESULTADOS CON MÉTODO NUEVO:")
    for field, config in generic_field_configs.items():
        result = extract_value_generic(test_text, config)
        print(f"  {field}: {result}")
    
    # ============================================================================
    # ESCENARIO COMPLETO CON EXTRACTORES GENÉRICOS
    # ============================================================================
    print("\n🎯 ESCENARIO COMPLETO CON EXTRACTORES GENÉRICOS:")
    print("-" * 50)
    
    insurance_reference = "Your auto insurance policy #POL-2024-001 has a premium of $850.00 per month. The coverage includes liability up to $100,000 and comprehensive protection. Your policy expires on December 31, 2024."
    insurance_reference_values = {
        "policy_number": "POL-2024-001",
        "premium": "$850.00",
        "coverage_type": "auto insurance",
        "liability_limit": "$100,000",
        "expiry_date": "December 31, 2024"
    }
    
    insurance_candidates = [
        "Policy POL-2024-001 covers your automobile with monthly payments of $850.00. You're protected with $100,000 liability coverage plus comprehensive insurance. This policy is valid until December 31, 2024.",
        "Your car insurance policy POL-2024-001 costs $850 monthly. It provides $100,000 liability protection and comprehensive coverage. Expires on December 31, 2024.",
        "Auto policy #POL-2024-001 has a $850.00 monthly premium with $100,000 liability and comprehensive coverage. Valid until December 31, 2024."
    ]
    
    print(f"Referencia: {insurance_reference}")
    print(f"Valores esperados: {insurance_reference_values}")
    print()
    
    results = run_validation_scenario(
        scenario_name="insurance_with_generic_extractors",
        reference_text=insurance_reference,
        reference_values=insurance_reference_values,
        candidates=insurance_candidates,
        threshold=0.7,
        domain="insurance",
        field_configs=generic_field_configs
    )
    
    print("📊 RESULTADOS FINALES:")
    for i, result in enumerate(results, 1):
        print(f"Candidato {i}: {'✅ VÁLIDO' if result.get('is_valid', False) else '❌ INVÁLIDO'}")
        if 'field_results' in result:
            for field, field_result in result['field_results'].items():
                status = "✅" if field_result.get('is_valid', False) else "❌"
                print(f"  {status} {field}: expected='{field_result.get('expected', 'N/A')}', found='{field_result.get('found', 'N/A')}'")
        print()
    
    # ============================================================================
    # VENTAJAS DE LOS EXTRACTORES GENÉRICOS
    # ============================================================================
    print("\n💡 VENTAJAS DE LOS EXTRACTORES GENÉRICOS:")
    print("-" * 50)
    print("✅ Reutilizables: Un extractor 'currency' funciona para cualquier dominio")
    print("✅ Simples: Menos configuración, más legible")
    print("✅ Mantenibles: Cambios en un extractor benefician a todos los usuarios")
    print("✅ Extensibles: Fácil agregar nuevos extractores genéricos")
    print("✅ Agnósticos: No dependen de dominios específicos")
    print("✅ Compatibles: Funcionan junto con el sistema original")

if __name__ == "__main__":
    main()
