#!/usr/bin/env python3
"""
Ejemplo de uso del HTML Reporter - True Lies Validator
====================================================

Este ejemplo muestra cómo usar el sistema de reportes HTML para generar
reportes profesionales de validaciones de chatbots.
"""

from true_lies import ConversationValidator, HTMLReporter
from datetime import datetime


def run_chatbot_tests():
    """Ejecuta una serie de pruebas de chatbot y genera reporte HTML."""
    
    # Crear validador
    validator = ConversationValidator()
    
    # Lista para almacenar resultados
    test_results = []
    
    # Test 1: Soporte técnico básico
    print("🧪 Running Test 1: Basic technical support...")
    validator.add_turn_and_report(
        user_input="Hola, soy Juan Pérez, mi ID es 12345 y tengo un problema",
        bot_response="Hola Juan, te ayudo con tu problema. ¿Qué error específico ves?",
        expected_facts={'nombre': 'Juan Pérez', 'user_id': '12345', 'issue_type': 'problem'},
        title="Test 1 - Turn 1"
    )
    
    final_response_1 = "Juan Pérez (ID 12345), tu problema ha sido solucionado"
    result_1 = validator.validate_and_report(
        response=final_response_1,
        facts_to_check=['nombre', 'user_id'],
        title="Test 1 - Final validation"
    )
    result_1['test_name'] = "Soporte Técnico Básico"
    result_1['timestamp'] = datetime.now().isoformat()
    test_results.append(result_1)
    
    # Test 2: E-commerce
    print("🧪 Running Test 2: E-commerce...")
    validator2 = ConversationValidator()  # Nuevo validador para test independiente
    
    validator2.add_turn_and_report(
        user_input="Hola, soy María González, email maria@store.com, quiero comprar una laptop",
        bot_response="Hola María! Te ayudo con la laptop. Enviaré opciones a maria@store.com",
        expected_facts={'nombre': 'María González', 'email': 'maria@store.com', 'producto': 'laptop'},
        title="Test 2 - Turn 1"
    )
    
    validator2.add_turn_and_report(
        user_input="Mi presupuesto es $1500 y la necesito para programar",
        bot_response="Perfecto María, tenemos laptops para programar en ese rango. Enviaré opciones.",
        expected_facts={'presupuesto': '1500', 'uso': 'programar'},
        title="Test 2 - Turn 2"
    )
    
    final_response_2 = "María González, tu laptop para programar de $1500 está lista. Factura enviada a maria@store.com"
    result_2 = validator2.validate_and_report(
        response=final_response_2,
        facts_to_check=['nombre', 'email', 'presupuesto', 'uso'],
        title="Test 2 - Final validation"
    )
    result_2['test_name'] = "E-commerce Completo"
    result_2['timestamp'] = datetime.now().isoformat()
    test_results.append(result_2)
    
    # Test 3: Banca (fallo intencional)
    print("🧪 Running Test 3: Banking (with failure)...")
    validator3 = ConversationValidator()
    
    validator3.add_turn_and_report(
        user_input="Soy Carlos López, trabajo en TechCorp, gano $95,000, quiero un préstamo",
        bot_response="Hola Carlos, te ayudo con tu préstamo. Email: carlos@bank.com",
        expected_facts={'nombre': 'Carlos López', 'empleador': 'TechCorp', 'ingreso': '95000'},
        title="Test 3 - Turn 1"
    )
    
    # Respuesta que NO incluye todos los datos (fallo intencional)
    final_response_3 = "Carlos, tu préstamo está aprobado"  # Falta empleador e ingreso
    result_3 = validator3.validate_and_report(
        response=final_response_3,
        facts_to_check=['nombre', 'empleador', 'ingreso'],
        title="Test 3 - Final validation (with failure)"
    )
    result_3['test_name'] = "Banca con Fallo"
    result_3['timestamp'] = datetime.now().isoformat()
    test_results.append(result_3)
    
    # Test 4: Seguros
    print("🧪 Running Test 4: Insurance...")
    validator4 = ConversationValidator()
    
    validator4.add_turn_and_report(
        user_input="Necesito seguro para mi auto, póliza POL-2024-001, prima $850",
        bot_response="Procesando tu seguro POL-2024-001 con prima de $850",
        expected_facts={'tipo_seguro': 'auto', 'poliza': 'POL-2024-001', 'prima': '850'},
        title="Test 4 - Turn 1"
    )
    
    final_response_4 = "Tu seguro de auto POL-2024-001 con prima de $850 está activo"
    result_4 = validator4.validate_and_report(
        response=final_response_4,
        facts_to_check=['tipo_seguro', 'poliza', 'prima'],
        title="Test 4 - Final validation"
    )
    result_4['test_name'] = "Seguros"
    result_4['timestamp'] = datetime.now().isoformat()
    test_results.append(result_4)
    
    # Test 5: Caso extremo - muy malo
    print("🧪 Running Test 5: Extreme case...")
    validator5 = ConversationValidator()
    
    validator5.add_turn_and_report(
        user_input="Soy Ana García, mi email es ana@test.com, quiero información sobre productos",
        bot_response="Hola Ana, te ayudo con información de productos",
        expected_facts={'nombre': 'Ana García', 'email': 'ana@test.com', 'consulta': 'productos'},
        title="Test 5 - Turn 1"
    )
    
    # Respuesta que no recuerda nada (fallo total)
    final_response_5 = "Gracias por contactarnos, esperamos ayudarte pronto"
    result_5 = validator5.validate_and_report(
        response=final_response_5,
        facts_to_check=['nombre', 'email', 'consulta'],
        title="Test 5 - Final validation (total failure)"
    )
    result_5['test_name'] = "Fallo Total"
    result_5['timestamp'] = datetime.now().isoformat()
    test_results.append(result_5)
    
    return test_results


def generate_html_report():
    """Genera el reporte HTML con todos los resultados."""
    
    print("\n🧪 Running chatbot tests...")
    results = run_chatbot_tests()
    
    print("\n📊 Generating HTML report...")
    
    # Crear reporter y generar reporte
    reporter = HTMLReporter()
    
    output_file = reporter.generate_report(
        results=results,
        output_file="chatbot_test_report.html",
        title="Chatbot Validation Report - December 2024",
        show_details=True
    )
    
    print(f"✅ HTML report generated successfully: {output_file}")
    print("\n📈 Results summary:")
    
    total = len(results)
    passed = sum(1 for r in results if r.get('all_retained', False))
    failed = total - passed
    pass_rate = (passed / total) * 100
    
    print(f"   Total tests: {total}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {failed}")
    print(f"   Success rate: {pass_rate:.1f}%")
    
    # Mostrar detalles por test
    print("\n📋 Details by test:")
    for i, result in enumerate(results, 1):
        test_name = result.get('test_name', f'Test {i}')
        score = result.get('retention_score', 0.0)
        status = "✅ PASS" if result.get('all_retained', False) else "❌ FAIL"
        facts = f"{result.get('facts_retained', 0)}/{result.get('total_facts', 0)}"
        
        print(f"   {i}. {test_name}: {status} (Score: {score:.3f}, Facts: {facts})")
    
    return output_file


def demo_advanced_usage():
    """Demuestra uso avanzado del HTML Reporter."""
    
    print("\n🚀 Demonstrating advanced HTML Reporter usage...")
    
    # Crear múltiples reportes con diferentes configuraciones
    reporter = HTMLReporter()
    
    # Ejecutar pruebas
    results = run_chatbot_tests()
    
    # Reporte básico (sin detalles)
    print("\n📊 Generating basic report...")
    basic_report = reporter.generate_report(
        results=results,
        output_file="basic_report.html",
        title="Chatbot Validation Summary Report",
        show_details=False
    )
    print(f"✅ Basic report: {basic_report}")
    
    # Reporte completo (con detalles)
    print("\n📊 Generating detailed report...")
    detailed_report = reporter.generate_report(
        results=results,
        output_file="detailed_report.html",
        title="Chatbot Validation Detailed Report",
        show_details=True
    )
    print(f"✅ Detailed report: {detailed_report}")
    
    # Reporte ejecutivo (solo métricas)
    print("\n📊 Generating executive report...")
    executive_results = [r for r in results if r.get('retention_score', 0) >= 0.7]
    executive_report = reporter.generate_report(
        results=executive_results,
        output_file="executive_report.html",
        title="Chatbot Validation Executive Report",
        show_details=False
    )
    print(f"✅ Executive report: {executive_report}")
    
    return {
        'basic': basic_report,
        'detailed': detailed_report,
        'executive': executive_report
    }


if __name__ == "__main__":
    print("🎭 True Lies Validator - HTML Reporter Demo")
    print("=" * 50)
    
    # Generar reporte principal
    main_report = generate_html_report()
    
    # Demostrar uso avanzado
    advanced_reports = demo_advanced_usage()
    
    print("\n🎉 Demo completed!")
    print("\n📁 Generated files:")
    print(f"   📊 Main report: {main_report}")
    for report_type, report_path in advanced_reports.items():
        print(f"   📊 {report_type} report: {report_path}")
    
    print("\n💡 Tips:")
    print("   • Open HTML files in your browser to view the reports")
    print("   • Use control buttons to filter and sort results")
    print("   • Expandable details show complete analysis of each failure")
    print("   • Design is responsive and works on mobile devices")
    
    print("\n🔧 To integrate into your project:")
    print("""
    from true_lies import ConversationValidator, HTMLReporter
    
    # Ejecutar pruebas
    validator = ConversationValidator()
    results = []
    
    # ... ejecutar tus pruebas ...
    
    # Generar reporte
    reporter = HTMLReporter()
    reporter.generate_report(
        results=results,
        output_file="mi_reporte.html",
        title="Mis Pruebas de Chatbot"
    )
    """)
