#!/usr/bin/env python3
"""
Ejemplo de Uso Simplificado - True Lies Validator
===============================================

Este ejemplo muestra cómo usar True Lies con reporting automático,
eliminando la necesidad de código manual de reporting.
"""

from true_lies import ConversationValidator


def test_support_chatbot_simplified():
    """Test simplificado para chatbot de soporte - SIN código manual de reporting"""
    print("🚀 TEST SIMPLIFICADO - SUPPORT CHATBOT")
    print("(Sin código manual de reporting - True Lies se encarga de todo)")
    print()
    
    # Crear validador
    conv = ConversationValidator()
    
    # Turn 1: Usuario reporta problema (con reporting automático)
    conv.add_turn_and_report(
        user_input="Mi app no funciona, soy usuario ID 12345",
        bot_response="Hola, voy a ayudarte. ¿Qué error ves?",
        expected_facts={'user_id': '12345', 'issue_type': 'app_no_funciona'},
        title="Turn 1: Usuario reporta problema"
    )
    
    # Turn 2: Usuario da detalles (con reporting automático)
    conv.add_turn_and_report(
        user_input="Error 500 en login, email juan@empresa.com",
        bot_response="Entiendo, error 500 en login. Revisando tu cuenta.",
        expected_facts={'error_code': '500', 'email': 'juan@empresa.com'},
        title="Turn 2: Usuario proporciona detalles"
    )
    
    # Mostrar resumen de conversación
    conv.print_conversation_summary("Resumen de Conversación")
    
    # Test de retención con reporting automático
    final_response = "Juan (ID 12345), tu error 500 será solucionado en 2 horas"
    retention = conv.validate_and_report(
        response=final_response,
        facts_to_check=['user_id', 'error_code', 'email'],
        title="Test de Retención de Contexto"
    )
    
    # Retornar resultado para tests automatizados
    return retention['retention_score'] >= 0.8


def test_ecommerce_simplified():
    """Test simplificado para e-commerce - SIN código manual de reporting"""
    print("🛒 TEST SIMPLIFICADO - E-COMMERCE")
    print("(Sin código manual de reporting - True Lies se encarga de todo)")
    print()
    
    # Crear validador
    conv = ConversationValidator()
    
    # Turn 1: Cliente se identifica
    conv.add_turn_and_report(
        user_input="Hola, soy María González, email maria@tienda.com, quiero comprar una laptop",
        bot_response="Hola María! Te ayudo con la laptop. Email registrado: maria@tienda.com",
        expected_facts={'customer_name': 'María González', 'email': 'maria@tienda.com', 'product_interest': 'laptop'},
        title="Turn 1: Cliente se identifica"
    )
    
    # Turn 2: Cliente especifica presupuesto
    conv.add_turn_and_report(
        user_input="Mi presupuesto es $1500, necesito para programar",
        bot_response="Perfecto María, tenemos laptops para programar en ese rango. Te envío opciones a maria@tienda.com",
        expected_facts={'budget': '1500', 'use_case': 'programar'},
        title="Turn 2: Cliente especifica presupuesto"
    )
    
    # Turn 3: Cliente pregunta por descuentos
    conv.add_turn_and_report(
        user_input="¿Tienen descuentos para estudiantes?",
        bot_response="Sí María, tienes 15% de descuento estudiante en la laptop",
        expected_facts={'discount_type': 'estudiante', 'discount_percentage': '15'},
        title="Turn 3: Cliente pregunta por descuentos"
    )
    
    # Mostrar resumen de conversación
    conv.print_conversation_summary("Resumen de Conversación E-commerce")
    
    # Test de retención con reporting automático
    final_response = "María, tu laptop de programación por $1500 con 15% descuento estudiante está lista. Te envío la factura a maria@tienda.com"
    retention = conv.validate_and_report(
        response=final_response,
        facts_to_check=['customer_name', 'email', 'budget', 'use_case', 'discount_percentage'],
        title="Test de Retención E-commerce"
    )
    
    # Retornar resultado para tests automatizados
    return retention['retention_score'] >= 0.9


def test_banking_simplified():
    """Test simplificado para banking - SIN código manual de reporting"""
    print("🏦 TEST SIMPLIFICADO - BANKING")
    print("(Sin código manual de reporting - True Lies se encarga de todo)")
    print()
    
    # Crear validador
    conv = ConversationValidator()
    
    # Turn 1: Cliente solicita préstamo
    conv.add_turn_and_report(
        user_input="Hola, soy Carlos Ruiz, email carlos@banco.com, quiero un préstamo hipotecario",
        bot_response="Hola Carlos! Te ayudo con tu préstamo hipotecario. Email registrado: carlos@banco.com",
        expected_facts={'customer_name': 'Carlos Ruiz', 'email': 'carlos@banco.com', 'loan_type': 'hipotecario'},
        title="Turn 1: Cliente solicita préstamo"
    )
    
    # Turn 2: Cliente proporciona ingresos
    conv.add_turn_and_report(
        user_input="Trabajo en TechCorp, gano $95,000 anuales",
        bot_response="Perfecto Carlos, registrado empleo en TechCorp con $95,000 anuales",
        expected_facts={'employer': 'TechCorp', 'annual_income': '95000'},
        title="Turn 2: Cliente proporciona ingresos"
    )
    
    # Turn 3: Cliente especifica propiedad
    conv.add_turn_and_report(
        user_input="La casa cuesta $450,000, tengo $90,000 de enganche",
        bot_response="Excelente Carlos, $450,000 de propiedad con $90,000 de enganche = $360,000 de préstamo",
        expected_facts={'property_value': '450000', 'down_payment': '90000', 'loan_amount': '360000'},
        title="Turn 3: Cliente especifica propiedad"
    )
    
    # Mostrar resumen de conversación
    conv.print_conversation_summary("Resumen de Conversación Banking")
    
    # Test de retención con reporting automático
    final_response = "Carlos, tu préstamo hipotecario de $360,000 con TechCorp está aprobado. Te envío la confirmación a carlos@banco.com"
    retention = conv.validate_and_report(
        response=final_response,
        facts_to_check=['customer_name', 'email', 'loan_amount', 'employer', 'annual_income'],
        title="Test de Retención Banking"
    )
    
    # Retornar resultado para tests automatizados
    return retention['retention_score'] >= 0.8


def test_multiple_scenarios():
    """Test de múltiples escenarios con reporting automático"""
    print("🎯 TEST DE MÚLTIPLES ESCENARIOS")
    print("(Comparación de diferentes casos de uso)")
    print()
    
    scenarios = [
        ("Support Chatbot", test_support_chatbot_simplified),
        ("E-commerce", test_ecommerce_simplified),
        ("Banking", test_banking_simplified)
    ]
    
    results = {}
    
    for scenario_name, test_func in scenarios:
        print(f"\n{'='*60}")
        print(f"🧪 EJECUTANDO: {scenario_name}")
        print(f"{'='*60}")
        
        try:
            result = test_func()
            results[scenario_name] = result
            print(f"\n✅ {scenario_name}: {'PASS' if result else 'FAIL'}")
        except Exception as e:
            results[scenario_name] = False
            print(f"\n❌ {scenario_name}: ERROR - {e}")
    
    # Resumen final
    print(f"\n{'='*60}")
    print("📊 RESUMEN FINAL")
    print(f"{'='*60}")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for scenario_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {scenario_name}: {status}")
    
    print(f"\n🎯 Resultado General: {passed}/{total} tests pasaron")
    print(f"📈 Tasa de éxito: {(passed/total)*100:.1f}%")
    
    return passed == total


if __name__ == "__main__":
    # Ejecutar test de múltiples escenarios
    all_passed = test_multiple_scenarios()
    
    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 TODOS LOS TESTS PASARON - True Lies funcionando perfectamente!")
    else:
        print("⚠️  ALGUNOS TESTS FALLARON - Revisar implementación")
    print(f"{'='*60}")
