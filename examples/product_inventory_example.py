"""
Ejemplo de uso de llm-validator para validación de inventario de productos
"""

from llm_validator.runner import run_validation_scenario

def main():
    print("="*80)
    print("EJEMPLO: Validación de Inventario de Productos")
    print("="*80)
    
    # Definir el escenario de referencia
    reference_text = "The iPhone 15 Pro is currently in stock with 25 units available. The price is $999.99 and it comes in Space Black color."
    reference_values = {
        "product_name": "iPhone 15 Pro",
        "stock": "25", 
        "price": "$999.99",
        "color": "Space Black"
    }
    
    # Diferentes candidatos para probar
    candidates = [
        # Candidato correcto
        "The iPhone 15 Pro is currently in stock with 25 units available. The price is $999.99 and it comes in Space Black color.",
        
        # Candidato con formato diferente pero correcto
        "iPhone 15 Pro - 25 units in stock. Price: $999.99. Available in Space Black.",
        
        # Candidato incorrecto (valores diferentes)
        "The iPhone 15 is currently in stock with 20 units available. The price is $899.99 and it comes in Blue color.",
        
        # Candidato con producto diferente
        "Samsung Galaxy S24 is available with 15 units in stock. The cost is $899.99 and it comes in Silver color."
    ]
    
    print(f"Texto de referencia: {reference_text}")
    print(f"Valores esperados: {reference_values}")
    print(f"Número de candidatos: {len(candidates)}")
    print("-" * 80)
    
    # Ejecutar validación
    results = run_validation_scenario(
        scenario_name="product_inventory_validation",
        reference_text=reference_text,
        reference_values=reference_values,
        candidates=candidates,
        threshold=0.7,
        domain="retail"
    )
    
    print("\n" + "="*80)
    print("ANÁLISIS DE RESULTADOS")
    print("="*80)
    
    # Analizar resultados
    valid_candidates = [r for r in results if r["is_valid"]]
    factual_accurate = [r for r in results if r["factual"]["is_valid"]]
    
    print(f"Candidatos válidos: {len(valid_candidates)}/{len(candidates)}")
    print(f"Candidatos factualmente precisos: {len(factual_accurate)}/{len(candidates)}")
    
    print("\nDetalles por candidato:")
    for i, result in enumerate(results, 1):
        status = "✅ VÁLIDO" if result["is_valid"] else "❌ INVÁLIDO"
        print(f"\nCandidato {i}: {status}")
        
        # Mostrar detalles de validación factual
        factual_details = result["factual"]["details"]
        for key, detail in factual_details.items():
            expected = detail.get("expected")
            found = detail.get("found")
            match = detail.get("match")
            status_icon = "✅" if match else "❌"
            print(f"  {status_icon} {key}: esperado='{expected}', encontrado='{found}'")
        
        # Mostrar similitud semántica
        similarity = result["semantic"]["similarity_score"]
        print(f"  📊 Similitud semántica: {similarity:.3f}")

if __name__ == "__main__":
    main()
