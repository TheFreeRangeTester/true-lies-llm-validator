"""
Ejemplo que demuestra cómo usar llm-validator de manera completamente agnóstica de dominio.
Cualquier usuario puede definir sus propios campos, patrones de extracción y sinónimos.
"""

from llm_validator.runner import run_validation_scenario
from llm_validator.utils import create_field_config
import re

def normalize_policy_number(value):
    """Normaliza el número de póliza removiendo caracteres extra"""
    if not value:
        return None
    # Remover espacios extra y caracteres especiales
    normalized = re.sub(r'[^\w\-]', '', str(value).strip())
    return normalized

def normalize_premium(value):
    """Normaliza el premium para formato consistente"""
    if not value:
        return None
    value_str = str(value).strip()
    # Asegurar formato de dólar
    if not value_str.startswith('$'):
        value_str = f"${value_str}"
    # Asegurar formato decimal si es un número entero
    if re.match(r'^\$\d+$', value_str):
        value_str = f"{value_str}.00"
    return value_str

def normalize_motorcycle_model(value):
    """Normaliza el modelo de motocicleta removiendo artículos"""
    if not value:
        return None
    normalized = re.sub(r'^The\s+', '', str(value).strip())
    return normalized

def normalize_warranty(value):
    """Normaliza la garantía para incluir '-month' si no está presente"""
    if not value:
        return None
    value_str = str(value).strip()
    if re.match(r'^\d+$', value_str):
        return f"{value_str}-month"
    return value_str

def normalize_condition(value):
    """Normaliza la condición a valores estándar"""
    if not value:
        return None
    value_lower = str(value).lower().strip()
    condition_mapping = {
        'excellent': 'excellent',
        'good': 'good',
        'fair': 'fair',
        'poor': 'poor',
        'mint': 'excellent',
        'like new': 'excellent',
        'new': 'excellent',
        'used': 'good'
    }
    return condition_mapping.get(value_lower, value)

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
    print("EJEMPLO: Librería Agnóstica de Dominio - Escenarios Robustos")
    print("="*80)
    
    # ============================================================================
    # CONFIGURACIONES PARA DIFERENTES DOMINIOS
    # ============================================================================
    
    # Configuración para seguros
    insurance_field_configs = {
        "policy_number": create_field_config(
            "policy_number",
            [
                r'policy\s+#?([A-Z0-9\-]+)',
                r'#([A-Z0-9\-]+)',
                r'policy\s+([A-Z0-9\-]+)',
                r'([A-Z0-9\-]+)\s+policy',
                r'policy\s+number:\s*([A-Z0-9\-]+)'
            ],
            normalize_func=normalize_policy_number
        ),
        "premium": create_field_config(
            "premium",
            [
                r'premium\s+of\s+(\$\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'(\$\d+(?:,\d{3})*(?:\.\d{2})?)\s+per\s+month',
                r'costs?\s+(\$\d+(?:,\d{3})*(?:\.\d{2})?)\s+monthly',
                r'monthly\s+payments?\s+of\s+(\$\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'(\$\d+(?:,\d{3})*(?:\.\d{2})?)\s+monthly',
                r'(\$\d+(?:,\d{3})*(?:\.\d{2})?)\s+monthly\s+premium',
                r'(\$\d+(?:,\d{3})*(?:\.\d{2})?)\s+monthly\s+payments?',
                r'(\$\d+(?:,\d{3})*(?:\.\d{2})?)\s+per\s+month'
            ],
            normalize_func=normalize_premium
        ),
        "coverage_type": create_field_config(
            "coverage_type",
            [
                r'covers?\s+your\s+([A-Za-z]+)',  # "covers your automobile"
                r'([A-Za-z]+)\s+insurance\s+policy\s+#',  # "auto insurance policy #"
                r'([A-Za-z]+)\s+policy\s+#',  # "auto policy #"
                r'([A-Za-z]+)\s+insurance\s+policy\s+has',  # "auto insurance policy has"
                r'([A-Za-z]+)\s+policy\s+has',  # "auto policy has"
                r'([A-Za-z]+)\s+insurance\s+policy\s+covers',  # "auto insurance policy covers"
                r'([A-Za-z]+)\s+policy\s+covers',  # "auto policy covers"
                r'([A-Za-z]+)\s+insurance\s+policy',  # "auto insurance policy"
                r'([A-Za-z]+)\s+policy',  # "auto policy"
                r'policy\s+([A-Za-z]+)',  # "policy auto"
            ],
            ["auto insurance", "car insurance", "automobile insurance", "vehicle insurance"],
            normalize_func=normalize_coverage_type
        ),
        "liability_limit": create_field_config(
            "liability_limit",
            [
                r'liability\s+up\s+to\s+(\$\d+(?:,\d{3})*)',
                r'(\$\d+(?:,\d{3})*)\s+liability',
                r'liability\s+(\$\d+(?:,\d{3})*)',
                r'(\$\d+(?:,\d{3})*)\s+liability\s+coverage'
            ]
        ),
        "expiry_date": create_field_config(
            "expiry_date",
            [
                r'expires?\s+on\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})',
                r'valid\s+until\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})',
                r'expiry\s+date:\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})',
                r'([A-Za-z]+\s+\d{1,2},\s+\d{4})',
                r'expires?\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})'
            ]
        )
    }
    
    # Configuración para motocicletas
    motorcycle_field_configs = {
        "motorcycle_model": create_field_config(
            "motorcycle_model",
            [
                r'([A-Za-z]+\s+[A-Za-z0-9\s]+)\s+is\s+available',
                r'([A-Za-z]+\s+[A-Za-z0-9\s]+)\s+for\s+\$',
                r'([A-Za-z]+\s+[A-Za-z0-9\s]+)\s+motorcycle',
                r'([A-Za-z]+\s+[A-Za-z0-9\s]+)\s+priced\s+at',
                r'Available:\s+([A-Za-z]+\s+[A-Za-z0-9\s]+)',
                r'([A-Za-z]+\s+[A-Za-z0-9\s]+)\s+for\s+\$'
            ],
            normalize_func=normalize_motorcycle_model
        ),
        "price": create_field_config(
            "price",
            [
                r'available\s+for\s+(\$\d+(?:,\d{3})*)',
                r'priced\s+at\s+(\$\d+(?:,\d{3})*)',
                r'for\s+(\$\d+(?:,\d{3})*)',
                r'(\$\d+(?:,\d{3})*)',
                r'costs?\s+(\$\d+(?:,\d{3})*)'
            ]
        ),
        "mileage": create_field_config(
            "mileage",
            [
                r'(\d+)\s+miles?\s+on\s+the\s+odometer',
                r'(\d+)\s+miles?\s+on\s+the\s+clock',
                r'Odometer\s+shows\s+(\d+)\s+miles',
                r'(\d+)\s+miles',
                r'mileage:\s*(\d+)'
            ]
        ),
        "warranty": create_field_config(
            "warranty",
            [
                r'(\d+)-month\s+warranty',
                r'(\d+)\s+month\s+warranty',
                r'(\d+)-month\s+warranty\s+included',
                r'(\d+)\s+months?\s+warranty',
                r'warranty:\s*(\d+)-month'
            ],
            normalize_func=normalize_warranty
        ),
        "condition": create_field_config(
            "condition",
            [
                r'bike\s+is\s+in\s+([A-Za-z]+)\s+condition',
                r'condition:\s*([A-Za-z]+)',
                r'([A-Za-z]+)\s+condition',
                r'in\s+([A-Za-z]+)\s+condition'
            ],
            ["excellent", "good", "fair", "poor", "mint", "like new", "used", "new"],
            normalize_func=normalize_condition
        )
    }
    
    # Configuración para productos retail
    retail_field_configs = {
        "product_name": create_field_config(
            "product_name",
            [
                r'([A-Za-z]+\s+\d+(?:\s+Pro)?(?:\s+Max)?(?:\s+Mini)?)',
                r'([A-Za-z]+\s+[A-Za-z0-9\s]+)\s+available',
                r'([A-Za-z]+\s+[A-Za-z0-9\s]+)\s+units?',
                r'([A-Za-z]+\s+[A-Za-z0-9\s]+)\s+in\s+stock',
                r'We\s+have\s+\d+\s+([A-Za-z]+\s+[A-Za-z0-9\s]+)\s+units',
                r'([A-Za-z]+\s+[A-Za-z0-9\s]+)\s+available:\s*\d+',
                r'([A-Za-z]+\s+[A-Za-z0-9\s]+)\s+units?\s+in\s+stock',
                r'(\d+)\s+([A-Za-z]+\s+[A-Za-z0-9\s]+)\s+units?\s+in\s+[A-Za-z\s]+',
                r'([A-Za-z]+\s+[A-Za-z0-9\s]+)\s+units?\s+in\s+[A-Za-z\s]+',
                r'([A-Za-z]+\s+[A-Za-z0-9\s]+)\s+units?\s+available'
            ]
        ),
        "stock": create_field_config(
            "stock",
            [
                r'(\d+)\s+units?\s+available',
                r'(\d+)\s+units?\s+in\s+stock',
                r'available:\s+(\d+)\s+units?',
                r'(\d+)\s+units?\s+available\s+for',
                r'We\s+have\s+(\d+)\s+[A-Za-z]+\s+units',
                r'(\d+)\s+units?\s+in\s+[A-Za-z\s]+',
                r'(\d+)\s+[A-Za-z]+\s+units?\s+in\s+[A-Za-z\s]+',
                r'(\d+)\s+[A-Za-z]+\s+units?\s+available',
                r'We\s+have\s+(\d+)\s+[A-Za-z]+\s+[A-Za-z0-9\s]+\s+units'
            ]
        ),
        "price": create_field_config(
            "price",
            [
                r'price\s+is\s+(\$\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'price:\s*(\$\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'(\$\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'available\s+for\s+(\$\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'(\$\d+(?:,\d{3})*(?:\.\d{2})?)\s+each'
            ]
        ),
        "color": create_field_config(
            "color",
            [
                r'comes?\s+in\s+([A-Za-z\s]+?)(?:\s+color)?',
                r'color:\s*([A-Za-z\s]+)',
                r'([A-Za-z\s]+?)\s+color',
                r'in\s+([A-Za-z\s]+?)\s+color',
                r'Color:\s*([A-Za-z\s]+)'
            ],
            ["Space Black", "Space Gray", "Silver", "Gold", "Blue", "Red", "Green", "Yellow", "White", "Black"]
        )
    }
    
    # ============================================================================
    # ESCENARIO 1: SEGUROS
    # ============================================================================
    print("\n🏛️ ESCENARIO 1: SEGUROS (Insurance Policy)")
    print("-" * 60)
    
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
    
    results1 = run_validation_scenario(
        scenario_name="insurance_policy",
        reference_text=insurance_reference,
        reference_values=insurance_reference_values,
        candidates=insurance_candidates,
        threshold=0.7,
        domain="insurance",
        field_configs=insurance_field_configs
    )
    
    # ============================================================================
    # ESCENARIO 2: MOTOCICLETAS
    # ============================================================================
    print("\n🏍️ ESCENARIO 2: MOTOCICLETAS (Motorcycle Inventory)")
    print("-" * 60)
    
    motorcycle_reference = "The Honda CBR 600RR is available for $12,500. It has 1500 miles on the odometer and comes with a 6-month warranty. The bike is in excellent condition."
    motorcycle_reference_values = {
        "motorcycle_model": "Honda CBR 600RR",
        "price": "$12,500",
        "mileage": "1500",
        "warranty": "6-month",
        "condition": "excellent"
    }
    
    motorcycle_candidates = [
        "The Honda CBR 600RR is available for $12,500. It has 1500 miles on the odometer and comes with a 6-month warranty. The bike is in excellent condition.",
        "Honda CBR 600RR motorcycle priced at $12,500. Odometer shows 1500 miles. Includes 6-month warranty. Condition: excellent.",
        "Available: Honda CBR 600RR for $12,500. 1500 miles on the clock. 6-month warranty included. Excellent condition."
    ]
    
    print(f"Referencia: {motorcycle_reference}")
    print(f"Valores esperados: {motorcycle_reference_values}")
    
    results2 = run_validation_scenario(
        scenario_name="motorcycle_inventory",
        reference_text=motorcycle_reference,
        reference_values=motorcycle_reference_values,
        candidates=motorcycle_candidates,
        threshold=0.7,
        domain="motorcycle_dealership",
        field_configs=motorcycle_field_configs
    )
    
    # ============================================================================
    # ESCENARIO 3: PRODUCTOS RETAIL
    # ============================================================================
    print("\n🛍️ ESCENARIO 3: PRODUCTOS RETAIL (Retail Product)")
    print("-" * 60)
    
    retail_reference = "The iPhone 15 Pro is currently in stock with 25 units available. The price is $999.99 and it comes in Space Black color."
    retail_reference_values = {
        "product_name": "iPhone 15 Pro",
        "stock": "25",
        "price": "$999.99",
        "color": "Space Black"
    }
    
    retail_candidates = [
        "The iPhone 15 Pro is currently in stock with 25 units available. The price is $999.99 and it comes in Space Black color.",
        "iPhone 15 Pro available: 25 units in stock. Price: $999.99. Color: Space Black.",
        "We have 25 iPhone 15 Pro units in Space Black color available for $999.99 each."
    ]
    
    print(f"Referencia: {retail_reference}")
    print(f"Valores esperados: {retail_reference_values}")
    
    results3 = run_validation_scenario(
        scenario_name="product_inventory",
        reference_text=retail_reference,
        reference_values=retail_reference_values,
        candidates=retail_candidates,
        threshold=0.7,
        domain="retail",
        field_configs=retail_field_configs
    )
    
    # ============================================================================
    # ANÁLISIS DE RESULTADOS
    # ============================================================================
    print("\n" + "="*80)
    print("ANÁLISIS DE RESULTADOS")
    print("="*80)
    
    all_results = [results1, results2, results3]
    scenario_names = ["Seguros", "Motocicletas", "Retail"]
    
    for i, (results, name) in enumerate(zip(all_results, scenario_names), 1):
        print(f"\n📊 ESCENARIO {i}: {name}")
        print("-" * 40)
        
        valid_candidates = [r for r in results if r["is_valid"]]
        factual_accurate = [r for r in results if r["factual"]["is_valid"]]
        
        print(f"Candidatos válidos: {len(valid_candidates)}/{len(results)}")
        print(f"Candidatos factualmente precisos: {len(factual_accurate)}/{len(results)}")
        
        for j, result in enumerate(results, 1):
            status = "✅ VÁLIDO" if result["is_valid"] else "❌ INVÁLIDO"
            print(f"\n  Candidato {j}: {status}")
            
            # Mostrar detalles de validación factual
            factual_details = result["factual"]["details"]
            for key, detail in factual_details.items():
                expected = detail.get("expected")
                found = detail.get("found")
                match = detail.get("match")
                status_icon = "✅" if match else "❌"
                print(f"    {status_icon} {key}: esperado='{expected}', encontrado='{found}'")
    
    print("\n" + "="*80)
    print("CONCLUSIÓN: Extracción Robusta y Confiable")
    print("="*80)
    print("✅ Configuraciones personalizadas para cada dominio")
    print("✅ Patrones de extracción específicos y robustos")
    print("✅ Funciones de normalización para valores consistentes")
    print("✅ Sinónimos configurables para cada campo")
    print("✅ La librería es completamente agnóstica de dominio")
    print("✅ Extracción confiable de reference values en candidatos")

if __name__ == "__main__":
    main()
