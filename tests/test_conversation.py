#!/usr/bin/env python3
"""
Tests para ConversationValidator - Validación Multiturno
======================================================

Tests unitarios para la funcionalidad de validación de memoria conversacional.
"""

import unittest
import sys
import os

# Agregar el directorio padre al path para importar true_lies
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from true_lies import ConversationValidator


class TestConversationValidator(unittest.TestCase):
    """Tests para la clase ConversationValidator."""
    
    def setUp(self):
        """Configurar validador para cada test."""
        self.conv = ConversationValidator()
    
    def test_initialization(self):
        """Test de inicialización del validador."""
        self.assertEqual(len(self.conv.conversation_facts), 0)
        self.assertEqual(len(self.conv.turn_history), 0)
    
    def test_add_turn_basic(self):
        """Test básico de agregar turno."""
        self.conv.add_turn(
            user_input="Hi, I'm John Doe",
            bot_response="Hello John!",
            expected_facts={'name': 'John Doe'}
        )
        
        self.assertEqual(len(self.conv.turn_history), 1)
        self.assertIn('name', self.conv.conversation_facts)
        self.assertEqual(self.conv.conversation_facts['name'], 'John Doe')
    
    def test_add_multiple_turns(self):
        """Test de agregar múltiples turnos."""
        # Turn 1
        self.conv.add_turn(
            user_input="I'm Sarah Johnson",
            bot_response="Hello Sarah!",
            expected_facts={'client_name': 'Sarah Johnson'}
        )
        
        # Turn 2
        self.conv.add_turn(
            user_input="I work at TechCorp",
            bot_response="Noted your employer",
            expected_facts={'employer': 'TechCorp'}
        )
        
        self.assertEqual(len(self.conv.turn_history), 2)
        self.assertEqual(len(self.conv.conversation_facts), 2)
        self.assertEqual(self.conv.conversation_facts['client_name'], 'Sarah Johnson')
        self.assertEqual(self.conv.conversation_facts['employer'], 'TechCorp')
    
    def test_validate_retention_perfect(self):
        """Test de validación de retención perfecta."""
        # Setup conversación
        self.conv.add_turn(
            user_input="I'm Sarah Johnson, salary $95,000",
            bot_response="Hello Sarah!",
            expected_facts={'client_name': 'Sarah Johnson', 'salary': '95000'}
        )
        
        # Test retención perfecta
        result = self.conv.validate_retention(
            response="Sarah, your salary is $95,000",
            facts_to_check=['client_name', 'salary']
        )
        
        self.assertEqual(result['retention_score'], 1.0)
        self.assertEqual(result['facts_retained'], 2)
        self.assertEqual(result['total_facts'], 2)
        self.assertTrue(result['all_retained'])
        self.assertTrue(result['client_name_retained'])
        self.assertTrue(result['salary_retained'])
    
    def test_validate_retention_partial(self):
        """Test de validación de retención parcial."""
        # Setup conversación
        self.conv.add_turn(
            user_input="I'm Sarah Johnson, salary $95,000",
            bot_response="Hello Sarah!",
            expected_facts={'client_name': 'Sarah Johnson', 'salary': '95000'}
        )
        
        # Test retención parcial (olvida el nombre)
        result = self.conv.validate_retention(
            response="Your salary is $95,000",
            facts_to_check=['client_name', 'salary']
        )
        
        self.assertEqual(result['retention_score'], 0.5)
        self.assertEqual(result['facts_retained'], 1)
        self.assertEqual(result['total_facts'], 2)
        self.assertFalse(result['all_retained'])
        self.assertFalse(result['client_name_retained'])
        self.assertTrue(result['salary_retained'])
    
    def test_validate_retention_none(self):
        """Test de validación sin retención."""
        # Setup conversación
        self.conv.add_turn(
            user_input="I'm Sarah Johnson, salary $95,000",
            bot_response="Hello Sarah!",
            expected_facts={'client_name': 'Sarah Johnson', 'salary': '95000'}
        )
        
        # Test sin retención
        result = self.conv.validate_retention(
            response="Thank you for your inquiry",
            facts_to_check=['client_name', 'salary']
        )
        
        self.assertEqual(result['retention_score'], 0.0)
        self.assertEqual(result['facts_retained'], 0)
        self.assertEqual(result['total_facts'], 2)
        self.assertFalse(result['all_retained'])
        self.assertFalse(result['client_name_retained'])
        self.assertFalse(result['salary_retained'])
    
    def test_detect_name_facts(self):
        """Test de detección de nombres."""
        # Setup
        self.conv.add_turn(
            user_input="I'm Sarah Johnson",
            bot_response="Hello!",
            expected_facts={'client_name': 'Sarah Johnson'}
        )
        
        # Test detección de nombre completo
        result = self.conv.validate_retention(
            response="Sarah Johnson, your application is ready",
            facts_to_check=['client_name']
        )
        self.assertTrue(result['client_name_retained'])
        
        # Test detección de nombre parcial
        result = self.conv.validate_retention(
            response="Sarah, your application is ready",
            facts_to_check=['client_name']
        )
        self.assertTrue(result['client_name_retained'])
    
    def test_detect_amount_facts(self):
        """Test de detección de montos."""
        # Setup
        self.conv.add_turn(
            user_input="I need a loan for $360,000",
            bot_response="Noted",
            expected_facts={'loan_amount': '360000'}
        )
        
        # Test diferentes formatos de montos
        test_cases = [
            ("Your loan of $360,000 is approved", True),
            ("Your loan of 360,000 is approved", True),
            ("Your loan of USD 360000 is approved", True),
            ("Your loan of 360000 dolares is approved", True),
            ("Your loan of $450,000 is approved", False),  # Monto incorrecto
        ]
        
        for response, expected in test_cases:
            with self.subTest(response=response):
                result = self.conv.validate_retention(
                    response=response,
                    facts_to_check=['loan_amount']
                )
                self.assertEqual(result['loan_amount_retained'], expected)
    
    def test_detect_employer_facts(self):
        """Test de detección de empleadores."""
        # Setup
        self.conv.add_turn(
            user_input="I work at TechCorp Inc",
            bot_response="Noted",
            expected_facts={'employer': 'TechCorp Inc'}
        )
        
        # Test detección de empleador
        result = self.conv.validate_retention(
            response="Your application at TechCorp Inc is processed",
            facts_to_check=['employer']
        )
        self.assertTrue(result['employer_retained'])
        
        # Test detección parcial
        result = self.conv.validate_retention(
            response="Your application at TechCorp is processed",
            facts_to_check=['employer']
        )
        self.assertTrue(result['employer_retained'])
    
    def test_detect_id_facts(self):
        """Test de detección de IDs."""
        # Setup
        self.conv.add_turn(
            user_input="My SSN is 123-45-6789",
            bot_response="Noted",
            expected_facts={'ssn': '123-45-6789'}
        )
        
        # Test detección exacta de ID
        result = self.conv.validate_retention(
            response="Your SSN 123-45-6789 is verified",
            facts_to_check=['ssn']
        )
        self.assertTrue(result['ssn_retained'])
        
        # Test ID incorrecto
        result = self.conv.validate_retention(
            response="Your SSN 987-65-4321 is verified",
            facts_to_check=['ssn']
        )
        self.assertFalse(result['ssn_retained'])
    
    def test_validate_full_conversation(self):
        """Test de validación completa de conversación."""
        # Setup conversación compleja
        self.conv.add_turn(
            user_input="I'm Sarah Johnson, SSN 123-45-6789",
            bot_response="Hello Sarah!",
            expected_facts={'client_name': 'Sarah Johnson', 'ssn': '123-45-6789'}
        )
        
        self.conv.add_turn(
            user_input="I work at TechCorp, salary $95,000",
            bot_response="Noted",
            expected_facts={'employer': 'TechCorp', 'salary': '95000'}
        )
        
        # Test validación completa
        result = self.conv.validate_full_conversation(
            final_response="Sarah, your $95,000 salary at TechCorp is verified",
            facts_to_check=['client_name', 'salary', 'employer'],
            similarity_threshold=0.8
        )
        
        self.assertIn('retention_score', result)
        self.assertIn('core_validation', result)
        self.assertIn('conversation_context', result)
        self.assertIn('turn_count', result)
        self.assertEqual(result['turn_count'], 2)
    
    def test_get_conversation_summary(self):
        """Test de obtención de resumen de conversación."""
        # Setup
        self.conv.add_turn(
            user_input="I'm John Doe",
            bot_response="Hello John!",
            expected_facts={'name': 'John Doe'}
        )
        
        summary = self.conv.get_conversation_summary()
        
        self.assertEqual(summary['total_turns'], 1)
        self.assertEqual(summary['total_facts'], 1)
        self.assertIn('facts', summary)
        self.assertIn('turn_history', summary)
        self.assertEqual(summary['facts']['name'], 'John Doe')
    
    def test_clear_conversation(self):
        """Test de limpieza de conversación."""
        # Setup
        self.conv.add_turn(
            user_input="I'm John Doe",
            bot_response="Hello John!",
            expected_facts={'name': 'John Doe'}
        )
        
        # Verificar que hay datos
        self.assertEqual(len(self.conv.conversation_facts), 1)
        self.assertEqual(len(self.conv.turn_history), 1)
        
        # Limpiar
        self.conv.clear_conversation()
        
        # Verificar que se limpió
        self.assertEqual(len(self.conv.conversation_facts), 0)
        self.assertEqual(len(self.conv.turn_history), 0)
    
    def test_fact_not_in_context(self):
        """Test de validación de fact que no está en el contexto."""
        # Setup con un fact
        self.conv.add_turn(
            user_input="I'm John Doe",
            bot_response="Hello John!",
            expected_facts={'name': 'John Doe'}
        )
        
        # Intentar validar un fact que no existe
        result = self.conv.validate_retention(
            response="Your salary is $50,000",
            facts_to_check=['salary']  # Este fact no está en el contexto
        )
        
        self.assertEqual(result['retention_score'], 0.0)
        self.assertEqual(result['facts_retained'], 0)
        self.assertEqual(result['total_facts'], 1)
        self.assertFalse(result['salary_retained'])
        self.assertEqual(result['salary_reason'], 'Fact not found in conversation context')
    
    def test_detect_email_facts(self):
        """Test de detección de emails."""
        # Setup
        self.conv.add_turn(
            user_input="My email is john@example.com",
            bot_response="Noted",
            expected_facts={'email': 'john@example.com'}
        )
        
        # Test detección de email
        result = self.conv.validate_retention(
            response="I'll send the details to john@example.com",
            facts_to_check=['email']
        )
        self.assertTrue(result['email_retained'])
        
        # Test email incorrecto
        result = self.conv.validate_retention(
            response="I'll send the details to jane@example.com",
            facts_to_check=['email']
        )
        self.assertFalse(result['email_retained'])
    
    def test_detect_phone_facts(self):
        """Test de detección de teléfonos."""
        # Setup
        self.conv.add_turn(
            user_input="My phone is (555) 123-4567",
            bot_response="Noted",
            expected_facts={'phone': '(555) 123-4567'}
        )
        
        # Test detección de teléfono
        result = self.conv.validate_retention(
            response="I'll call you at (555) 123-4567",
            facts_to_check=['phone']
        )
        self.assertTrue(result['phone_retained'])
        
        # Test teléfono incorrecto
        result = self.conv.validate_retention(
            response="I'll call you at (555) 987-6543",
            facts_to_check=['phone']
        )
        self.assertFalse(result['phone_retained'])
    
    def test_add_turn_and_report(self):
        """Test del método add_turn_and_report."""
        # Capturar output para verificar que se imprime
        import io
        import sys
        from contextlib import redirect_stdout
        
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            self.conv.add_turn_and_report(
                user_input="I'm John Doe",
                bot_response="Hello John!",
                expected_facts={'name': 'John Doe'},
                title="Test Turn"
            )
        
        output = captured_output.getvalue()
        
        # Verificar que se agregó el turno
        self.assertEqual(len(self.conv.turn_history), 1)
        self.assertEqual(len(self.conv.conversation_facts), 1)
        self.assertEqual(self.conv.conversation_facts['name'], 'John Doe')
        
        # Verificar que se imprimió el reporte
        self.assertIn("Test Turn", output)
        self.assertIn("I'm John Doe", output)
        self.assertIn("Hello John!", output)
    
    def test_validate_and_report(self):
        """Test del método validate_and_report."""
        # Setup
        self.conv.add_turn(
            user_input="I'm John Doe",
            bot_response="Hello John!",
            expected_facts={'name': 'John Doe'}
        )
        
        # Capturar output para verificar que se imprime
        import io
        import sys
        from contextlib import redirect_stdout
        
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            result = self.conv.validate_and_report(
                response="John, your application is ready",
                facts_to_check=['name'],
                title="Test Validation"
            )
        
        output = captured_output.getvalue()
        
        # Verificar que se validó correctamente
        self.assertEqual(result['retention_score'], 1.0)
        self.assertTrue(result['name_retained'])
        
        # Verificar que se imprimió el reporte
        self.assertIn("Test Validation", output)
        self.assertIn("John, your application is ready", output)
        self.assertIn("Retention Score: 1.00", output)
    
    # def test_print_conversation_summary(self):
    #     """Test del método print_conversation_summary."""
    #     # Setup
    #     self.conv.add_turn(
    #         user_input="I'm John Doe",
    #         bot_response="Hello John!",
    #         expected_facts={'name': 'John Doe'}
    #     )
    #     
    #     # Capturar output para verificar que se imprime
    #     import io
    #     import sys
    #     from contextlib import redirect_stdout
    #     
    #     captured_output = io.StringIO()
    #     with redirect_stdout(captured_output):
    #         self.conv.print_conversation_summary("Test Summary")
    #     
    #     output = captured_output.getvalue()
    #     
    #     # Verificar que se imprimió el resumen
    #     self.assertIn("Test Summary", output)
    #     self.assertIn("Total de turnos: 1", output)
    #     self.assertIn("Total de facts: 1", output)
    #     self.assertIn("name: John Doe", output)
    
    def test_print_retention_report(self):
        """Test del método print_retention_report."""
        # Setup
        self.conv.add_turn(
            user_input="I'm John Doe",
            bot_response="Hello John!",
            expected_facts={'name': 'John Doe'}
        )
        
        # Validar retención
        retention = self.conv.validate_retention(
            response="John, your application is ready",
            facts_to_check=['name']
        )
        
        # Capturar output para verificar que se imprime
        import io
        import sys
        from contextlib import redirect_stdout
        
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            self.conv.print_retention_report(
                retention_results=retention,
                facts_to_check=['name'],
                response="John, your application is ready",
                title="Test Retention Report"
            )
        
        output = captured_output.getvalue()
        
        # Verificar que se imprimió el reporte
        self.assertIn("Test Retention Report", output)
        self.assertIn("John, your application is ready", output)
        self.assertIn("Retention Score: 1.00", output)
        self.assertIn("✅ name:", output)


class TestConversationValidatorIntegration(unittest.TestCase):
    """Tests de integración para ConversationValidator."""
    
    def test_banking_scenario(self):
        """Test del escenario bancario completo."""
        conv = ConversationValidator()
        
        # Turn 1: Identificación
        conv.add_turn(
            user_input="Hi, I'm Sarah Johnson, SSN 987-65-4321. I'm interested in a mortgage",
            bot_response="Hello Sarah, I'll help with your mortgage application",
            expected_facts={'client_name': 'Sarah Johnson', 'ssn': '987-65-4321', 'loan_type': 'mortgage'}
        )
        
        # Turn 2: Empleo e ingresos
        conv.add_turn(
            user_input="I work at TechCorp as Senior Developer, salary $95,000",
            bot_response="Thank you Sarah. Recorded TechCorp employment with $95,000 income",
            expected_facts={'employer': 'TechCorp', 'job_title': 'Senior Developer', 'annual_income': '95000'}
        )
        
        # Turn 3: Propiedad y enganche
        conv.add_turn(
            user_input="House costs $450,000, I have $90,000 down payment",
            bot_response="Perfect Sarah. $450,000 property with $90,000 down = $360,000 mortgage needed",
            expected_facts={'property_value': '450000', 'down_payment': '90000', 'loan_amount': '360000'}
        )
        
        # Test retención perfecta
        perfect_response = "Sarah, your $360,000 mortgage at TechCorp with $95,000 income approved"
        retention = conv.validate_retention(
            response=perfect_response,
            facts_to_check=['client_name', 'loan_amount', 'employer', 'annual_income']
        )
        
        self.assertEqual(retention['retention_score'], 1.0)
        self.assertEqual(retention['facts_retained'], 4)
        self.assertEqual(retention['total_facts'], 4)
        self.assertTrue(retention['all_retained'])
        
        # Verificar cada fact individualmente
        self.assertTrue(retention['client_name_retained'])
        self.assertTrue(retention['loan_amount_retained'])
        self.assertTrue(retention['employer_retained'])
        self.assertTrue(retention['annual_income_retained'])


if __name__ == '__main__':
    # Ejecutar tests
    unittest.main(verbosity=2)
