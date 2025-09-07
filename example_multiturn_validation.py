#!/usr/bin/env python3
"""
Ejemplo Completo: Validación Multiturno - Préstamo Bancario
==========================================================

Este ejemplo demuestra el uso del ConversationValidator para validar
la memoria conversacional de un LLM en un escenario de préstamo bancario.
"""

from true_lies import ConversationValidator


def ejemplo_prestamo_bancario():
    """Ejemplo completo del escenario de préstamo bancario."""
    print("=== EJEMPLO: VALIDACIÓN MULTITURNO - PRÉSTAMO BANCARIO ===\n")
    
    # Crear validador de conversación
    loan_conv = ConversationValidator()
    
    print("🔹 Turn 1: Identificación del cliente")
    loan_conv.add_turn(
        user_input="Hi, I'm Sarah Johnson, SSN 987-65-4321. I'm interested in a mortgage",
        bot_response="Hello Sarah, I'll help with your mortgage application",
        expected_facts={
            'client_name': 'Sarah Johnson', 
            'ssn': '987-65-4321', 
            'loan_type': 'mortgage'
        }
    )
    
    print("🔹 Turn 2: Empleo e ingresos")
    loan_conv.add_turn(
        user_input="I work at TechCorp as Senior Developer, salary $95,000",
        bot_response="Thank you Sarah. Recorded TechCorp employment with $95,000 income",
        expected_facts={
            'employer': 'TechCorp', 
            'job_title': 'Senior Developer', 
            'annual_income': '95000'
        }
    )
    
    print("🔹 Turn 3: Propiedad y enganche")
    loan_conv.add_turn(
        user_input="House costs $450,000, I have $90,000 down payment",
        bot_response="Perfect Sarah. $450,000 property with $90,000 down = $360,000 mortgage needed",
        expected_facts={
            'property_value': '450000', 
            'down_payment': '90000', 
            'loan_amount': '360000'
        }
    )
    
    print("\n📊 Contexto conversacional acumulado:")
    summary = loan_conv.get_conversation_summary()
    for fact_name, fact_value in summary['facts'].items():
        print(f"   {fact_name}: {fact_value}")
    
    print(f"\n📈 Total de turnos: {summary['total_turns']}")
    print(f"📈 Total de facts: {summary['total_facts']}")
    
    # Test 1: Respuesta perfecta
    print("\n" + "="*60)
    print("🧪 TEST 1: RESPUESTA PERFECTA")
    print("="*60)
    
    perfect_response = "Sarah, your $360,000 mortgage at TechCorp with $95,000 income approved"
    retention_perfect = loan_conv.validate_retention(
        response=perfect_response,
        facts_to_check=['client_name', 'loan_amount', 'employer', 'annual_income']
    )
    
    print(f"Respuesta: '{perfect_response}'")
    print(f"Retention Score: {retention_perfect['retention_score']:.2f} ({retention_perfect['facts_retained']}/{retention_perfect['total_facts']})")
    print(f"All Retained: {retention_perfect['all_retained']}")
    
    print("\nDetalles por fact:")
    for fact_name in ['client_name', 'loan_amount', 'employer', 'annual_income']:
        retained = retention_perfect.get(f'{fact_name}_retained', False)
        detected = retention_perfect.get(f'{fact_name}_detected', 'N/A')
        expected = retention_perfect.get(f'{fact_name}_expected', 'N/A')
        status = "✅" if retained else "❌"
        print(f"   {status} {fact_name}: {detected} (esperado: {expected})")
    
    # Test 2: Respuesta que olvida el nombre
    print("\n" + "="*60)
    print("🧪 TEST 2: OLVIDA EL NOMBRE")
    print("="*60)
    
    forgets_name_response = "Your $360,000 mortgage at TechCorp with $95,000 income approved"
    retention_forgets = loan_conv.validate_retention(
        response=forgets_name_response,
        facts_to_check=['client_name', 'loan_amount', 'employer', 'annual_income']
    )
    
    print(f"Respuesta: '{forgets_name_response}'")
    print(f"Retention Score: {retention_forgets['retention_score']:.2f} ({retention_forgets['facts_retained']}/{retention_forgets['total_facts']})")
    print(f"All Retained: {retention_forgets['all_retained']}")
    
    print("\nDetalles por fact:")
    for fact_name in ['client_name', 'loan_amount', 'employer', 'annual_income']:
        retained = retention_forgets.get(f'{fact_name}_retained', False)
        detected = retention_forgets.get(f'{fact_name}_detected', 'N/A')
        expected = retention_forgets.get(f'{fact_name}_expected', 'N/A')
        status = "✅" if retained else "❌"
        print(f"   {status} {fact_name}: {detected} (esperado: {expected})")
    
    # Test 3: Respuesta con monto incorrecto
    print("\n" + "="*60)
    print("🧪 TEST 3: MONTO INCORRECTO")
    print("="*60)
    
    wrong_amount_response = "Sarah, your $450,000 mortgage at TechCorp with $95,000 income approved"
    retention_wrong = loan_conv.validate_retention(
        response=wrong_amount_response,
        facts_to_check=['client_name', 'loan_amount', 'employer', 'annual_income']
    )
    
    print(f"Respuesta: '{wrong_amount_response}'")
    print(f"Retention Score: {retention_wrong['retention_score']:.2f} ({retention_wrong['facts_retained']}/{retention_wrong['total_facts']})")
    print(f"All Retained: {retention_wrong['all_retained']}")
    
    print("\nDetalles por fact:")
    for fact_name in ['client_name', 'loan_amount', 'employer', 'annual_income']:
        retained = retention_wrong.get(f'{fact_name}_retained', False)
        detected = retention_wrong.get(f'{fact_name}_detected', 'N/A')
        expected = retention_wrong.get(f'{fact_name}_expected', 'N/A')
        status = "✅" if retained else "❌"
        print(f"   {status} {fact_name}: {detected} (esperado: {expected})")
    
    # Test 4: Validación completa (retención + validación core)
    print("\n" + "="*60)
    print("🧪 TEST 4: VALIDACIÓN COMPLETA")
    print("="*60)
    
    full_validation = loan_conv.validate_full_conversation(
        final_response=perfect_response,
        facts_to_check=['client_name', 'loan_amount', 'employer', 'annual_income'],
        similarity_threshold=0.8
    )
    
    print(f"Respuesta: '{perfect_response}'")
    print(f"Retention Score: {full_validation['retention_score']:.2f}")
    print(f"Core Validation - Valid: {full_validation['core_validation']['is_valid']}")
    print(f"Core Validation - Factual Accuracy: {full_validation['core_validation']['factual_accuracy']}")
    print(f"Turn Count: {full_validation['turn_count']}")


def ejemplo_ecommerce():
    """Ejemplo de validación multiturno para e-commerce."""
    print("\n\n=== EJEMPLO: VALIDACIÓN MULTITURNO - E-COMMERCE ===\n")
    
    # Crear validador de conversación para e-commerce
    ecommerce_conv = ConversationValidator()
    
    print("🔹 Turn 1: Cliente se identifica")
    ecommerce_conv.add_turn(
        user_input="Hi, I'm Maria Rodriguez, email maria@email.com",
        bot_response="Hello Maria! Welcome to our store",
        expected_facts={
            'customer_name': 'Maria Rodriguez',
            'email': 'maria@email.com'
        }
    )
    
    print("🔹 Turn 2: Agrega productos al carrito")
    ecommerce_conv.add_turn(
        user_input="I want to buy a laptop for $1200 and a mouse for $25",
        bot_response="Added laptop ($1200) and mouse ($25) to your cart. Total: $1225",
        expected_facts={
            'laptop_price': '1200',
            'mouse_price': '25',
            'cart_total': '1225'
        }
    )
    
    print("🔹 Turn 3: Aplica descuento")
    ecommerce_conv.add_turn(
        user_input="I have a 10% discount code SAVE10",
        bot_response="Applied 10% discount! New total: $1102.50",
        expected_facts={
            'discount_code': 'SAVE10',
            'discount_percentage': '10',
            'final_total': '1102.50'
        }
    )
    
    # Test de retención
    print("\n🧪 TEST: Validar retención en checkout")
    checkout_response = "Maria, your order total is $1102.50 with SAVE10 discount applied"
    retention = ecommerce_conv.validate_retention(
        response=checkout_response,
        facts_to_check=['customer_name', 'final_total', 'discount_code']
    )
    
    print(f"Respuesta: '{checkout_response}'")
    print(f"Retention Score: {retention['retention_score']:.2f} ({retention['facts_retained']}/{retention['total_facts']})")
    
    print("\nDetalles por fact:")
    for fact_name in ['customer_name', 'final_total', 'discount_code']:
        retained = retention.get(f'{fact_name}_retained', False)
        detected = retention.get(f'{fact_name}_detected', 'N/A')
        expected = retention.get(f'{fact_name}_expected', 'N/A')
        status = "✅" if retained else "❌"
        print(f"   {status} {fact_name}: {detected} (esperado: {expected})")


if __name__ == "__main__":
    # Ejecutar ejemplos
    ejemplo_prestamo_bancario()
    ejemplo_ecommerce()
    
    print("\n" + "="*60)
    print("✅ EJEMPLOS COMPLETADOS")
    print("="*60)
    print("\nLa validación multiturno permite:")
    print("• Acumular contexto conversacional a través de múltiples turnos")
    print("• Detectar automáticamente facts por tipo (nombres, montos, IDs, etc.)")
    print("• Validar retención de memoria en respuestas finales")
    print("• Proporcionar métricas detalladas de qué facts se retuvieron")
    print("• Identificar exactamente qué información se perdió en la conversación")
