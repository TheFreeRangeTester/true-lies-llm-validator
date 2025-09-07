#!/usr/bin/env python3
"""
Tests para Casos Edge - Validación de Casos Límite y Errores
============================================================

Tests unitarios para casos edge, errores y situaciones límite.
"""

import unittest
import sys
import os

# Agregar el directorio padre al path para importar true_lies
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from true_lies import ConversationValidator


class TestEdgeCases(unittest.TestCase):
    """Tests para casos edge y errores."""
    
    def setUp(self):
        """Configurar validador para cada test."""
        self.conv = ConversationValidator()
    
    def test_empty_inputs(self):
        """Test con entradas vacías."""
        # Test con user_input vacío
        self.conv.add_turn(
            user_input="",
            bot_response="Hello!",
            expected_facts={'name': 'John'}
        )
        
        self.assertEqual(len(self.conv.turn_history), 1)
        self.assertEqual(self.conv.turn_history[0]['user_input'], "")
        
        # Test con bot_response vacío
        self.conv.add_turn(
            user_input="Hi there",
            bot_response="",
            expected_facts={'greeting': 'hi'}
        )
        
        self.assertEqual(len(self.conv.turn_history), 2)
        self.assertEqual(self.conv.turn_history[1]['bot_response'], "")
        
        # Test con expected_facts vacío
        self.conv.add_turn(
            user_input="Just saying hello",
            bot_response="Hello back!",
            expected_facts={}
        )
        
        self.assertEqual(len(self.conv.turn_history), 3)
        self.assertEqual(len(self.conv.conversation_facts), 2)  # Solo los facts anteriores
    
    def test_none_inputs(self):
        """Test con entradas None."""
        # Test con user_input None
        self.conv.add_turn(
            user_input=None,
            bot_response="Hello!",
            expected_facts={'name': 'John'}
        )
        
        self.assertEqual(len(self.conv.turn_history), 1)
        self.assertIsNone(self.conv.turn_history[0]['user_input'])
        
        # Test con bot_response None
        self.conv.add_turn(
            user_input="Hi there",
            bot_response=None,
            expected_facts={'greeting': 'hi'}
        )
        
        self.assertEqual(len(self.conv.turn_history), 2)
        self.assertIsNone(self.conv.turn_history[1]['bot_response'])
        
        # Test con expected_facts None
        self.conv.add_turn(
            user_input="Just saying hello",
            bot_response="Hello back!",
            expected_facts=None
        )
        
        self.assertEqual(len(self.conv.turn_history), 3)
        self.assertEqual(len(self.conv.conversation_facts), 2)  # Solo los facts anteriores
    
    def test_very_long_inputs(self):
        """Test con entradas muy largas."""
        long_text = "A" * 10000  # 10,000 caracteres
        
        self.conv.add_turn(
            user_input=long_text,
            bot_response="Response to long input",
            expected_facts={'long_input': long_text}
        )
        
        self.assertEqual(len(self.conv.turn_history), 1)
        self.assertEqual(len(self.conv.conversation_facts), 1)
        self.assertEqual(self.conv.conversation_facts['long_input'], long_text)
    
    def test_special_characters(self):
        """Test con caracteres especiales."""
        special_text = "¡Hola! ¿Cómo estás? @#$%^&*()_+-=[]{}|;':\",./<>?`~"
        
        self.conv.add_turn(
            user_input=special_text,
            bot_response="¡Hola! ¿Cómo estás?",
            expected_facts={'special': special_text}
        )
        
        self.assertEqual(len(self.conv.turn_history), 1)
        self.assertEqual(self.conv.conversation_facts['special'], special_text)
    
    def test_unicode_characters(self):
        """Test con caracteres Unicode."""
        unicode_text = "Hello 世界 🌍 你好 مرحبا Здравствуй"
        
        self.conv.add_turn(
            user_input=unicode_text,
            bot_response="Hello world!",
            expected_facts={'unicode': unicode_text}
        )
        
        self.assertEqual(len(self.conv.turn_history), 1)
        self.assertEqual(self.conv.conversation_facts['unicode'], unicode_text)
    
    def test_duplicate_facts(self):
        """Test con facts duplicados."""
        # Agregar el mismo fact dos veces
        self.conv.add_turn(
            user_input="I'm John",
            bot_response="Hello John!",
            expected_facts={'name': 'John'}
        )
        
        self.conv.add_turn(
            user_input="My name is John again",
            bot_response="I know you're John",
            expected_facts={'name': 'John'}  # Mismo fact
        )
        
        # El fact debería mantenerse (no duplicarse)
        self.assertEqual(len(self.conv.conversation_facts), 1)
        self.assertEqual(self.conv.conversation_facts['name'], 'John')
        self.assertEqual(len(self.conv.turn_history), 2)
    
    def test_fact_overwrite(self):
        """Test con facts que se sobrescriben."""
        # Agregar fact inicial
        self.conv.add_turn(
            user_input="I'm John",
            bot_response="Hello John!",
            expected_facts={'name': 'John'}
        )
        
        # Sobrescribir con nuevo valor
        self.conv.add_turn(
            user_input="Actually, I'm Jane",
            bot_response="Oh, hello Jane!",
            expected_facts={'name': 'Jane'}
        )
        
        # El fact debería tener el último valor
        self.assertEqual(len(self.conv.conversation_facts), 1)
        self.assertEqual(self.conv.conversation_facts['name'], 'Jane')
        self.assertEqual(len(self.conv.turn_history), 2)
    
    def test_validate_retention_with_empty_facts(self):
        """Test de validación con facts vacíos."""
        # Setup con facts
        self.conv.add_turn(
            user_input="I'm John",
            bot_response="Hello John!",
            expected_facts={'name': 'John'}
        )
        
        # Validar con lista vacía de facts
        result = self.conv.validate_retention(
            response="Hello there",
            facts_to_check=[]
        )
        
        self.assertEqual(result['retention_score'], 1.0)  # 0/0 = 1.0
        self.assertEqual(result['facts_retained'], 0)
        self.assertEqual(result['total_facts'], 0)
        self.assertTrue(result['all_retained'])
    
    def test_validate_retention_with_nonexistent_facts(self):
        """Test de validación con facts que no existen."""
        # Setup con facts
        self.conv.add_turn(
            user_input="I'm John",
            bot_response="Hello John!",
            expected_facts={'name': 'John'}
        )
        
        # Validar con facts que no existen
        result = self.conv.validate_retention(
            response="Hello there",
            facts_to_check=['nonexistent1', 'nonexistent2']
        )
        
        self.assertEqual(result['retention_score'], 0.0)
        self.assertEqual(result['facts_retained'], 0)
        self.assertEqual(result['total_facts'], 2)
        self.assertFalse(result['all_retained'])
        self.assertFalse(result['nonexistent1_retained'])
        self.assertFalse(result['nonexistent2_retained'])
    
    def test_validate_retention_with_mixed_facts(self):
        """Test de validación con facts existentes y no existentes."""
        # Setup con facts
        self.conv.add_turn(
            user_input="I'm John, age 25",
            bot_response="Hello John!",
            expected_facts={'name': 'John', 'age': '25'}
        )
        
        # Validar con mix de facts existentes y no existentes
        result = self.conv.validate_retention(
            response="John is 25 years old",
            facts_to_check=['name', 'age', 'nonexistent']
        )
        
        self.assertEqual(result['retention_score'], 2/3)  # 2 de 3 facts
        self.assertEqual(result['facts_retained'], 2)
        self.assertEqual(result['total_facts'], 3)
        self.assertFalse(result['all_retained'])
        self.assertTrue(result['name_retained'])
        self.assertTrue(result['age_retained'])
        self.assertFalse(result['nonexistent_retained'])
    
    def test_clear_conversation_multiple_times(self):
        """Test de limpiar conversación múltiples veces."""
        # Setup
        self.conv.add_turn(
            user_input="I'm John",
            bot_response="Hello John!",
            expected_facts={'name': 'John'}
        )
        
        # Limpiar primera vez
        self.conv.clear_conversation()
        self.assertEqual(len(self.conv.conversation_facts), 0)
        self.assertEqual(len(self.conv.turn_history), 0)
        
        # Limpiar segunda vez (no debería causar error)
        self.conv.clear_conversation()
        self.assertEqual(len(self.conv.conversation_facts), 0)
        self.assertEqual(len(self.conv.turn_history), 0)
    
    def test_get_conversation_summary_empty(self):
        """Test de resumen de conversación vacía."""
        summary = self.conv.get_conversation_summary()
        
        self.assertEqual(summary['total_turns'], 0)
        self.assertEqual(summary['total_facts'], 0)
        self.assertEqual(len(summary['facts']), 0)
        self.assertEqual(len(summary['turn_history']), 0)
    
    def test_validate_full_conversation_empty(self):
        """Test de validación completa con conversación vacía."""
        result = self.conv.validate_full_conversation(
            final_response="Hello",
            facts_to_check=['name'],
            similarity_threshold=0.8
        )
        
        self.assertIn('retention_score', result)
        self.assertIn('core_validation', result)
        self.assertIn('conversation_context', result)
        self.assertIn('turn_count', result)
        self.assertEqual(result['turn_count'], 0)
    
    def test_very_long_fact_names(self):
        """Test con nombres de facts muy largos."""
        long_fact_name = "very_long_fact_name_" + "x" * 100
        
        self.conv.add_turn(
            user_input="Test input",
            bot_response="Test response",
            expected_facts={long_fact_name: 'test_value'}
        )
        
        self.assertEqual(len(self.conv.conversation_facts), 1)
        self.assertIn(long_fact_name, self.conv.conversation_facts)
        self.assertEqual(self.conv.conversation_facts[long_fact_name], 'test_value')
    
    def test_very_long_fact_values(self):
        """Test con valores de facts muy largos."""
        long_fact_value = "very_long_fact_value_" + "x" * 1000
        
        self.conv.add_turn(
            user_input="Test input",
            bot_response="Test response",
            expected_facts={'long_value': long_fact_value}
        )
        
        self.assertEqual(len(self.conv.conversation_facts), 1)
        self.assertEqual(self.conv.conversation_facts['long_value'], long_fact_value)
    
    def test_validate_retention_with_very_long_response(self):
        """Test de validación con respuesta muy larga."""
        # Setup
        self.conv.add_turn(
            user_input="I'm John",
            bot_response="Hello John!",
            expected_facts={'name': 'John'}
        )
        
        # Respuesta muy larga
        long_response = "John " + "is a great person " * 1000
        
        result = self.conv.validate_retention(
            response=long_response,
            facts_to_check=['name']
        )
        
        self.assertEqual(result['retention_score'], 1.0)
        self.assertTrue(result['name_retained'])


class TestErrorHandling(unittest.TestCase):
    """Tests para manejo de errores."""
    
    def setUp(self):
        """Configurar validador para cada test."""
        self.conv = ConversationValidator()
    
    def test_add_turn_with_invalid_facts_type(self):
        """Test de agregar turno con tipo de facts inválido."""
        # Test con facts que no es dict
        with self.assertRaises(TypeError):
            self.conv.add_turn(
                user_input="Test",
                bot_response="Test",
                expected_facts="not_a_dict"
            )
    
    def test_validate_retention_with_invalid_facts_type(self):
        """Test de validación con tipo de facts inválido."""
        # Setup
        self.conv.add_turn(
            user_input="I'm John",
            bot_response="Hello John!",
            expected_facts={'name': 'John'}
        )
        
        # Test con facts_to_check que no es lista
        with self.assertRaises(TypeError):
            self.conv.validate_retention(
                response="Hello John",
                facts_to_check="not_a_list"
            )
    
    def test_validate_retention_with_none_response(self):
        """Test de validación con respuesta None."""
        # Setup
        self.conv.add_turn(
            user_input="I'm John",
            bot_response="Hello John!",
            expected_facts={'name': 'John'}
        )
        
        # Test con response None
        result = self.conv.validate_retention(
            response=None,
            facts_to_check=['name']
        )
        
        # Debería manejar None gracefully
        self.assertEqual(result['retention_score'], 0.0)
        self.assertFalse(result['name_retained'])
    
    def test_validate_retention_with_empty_response(self):
        """Test de validación con respuesta vacía."""
        # Setup
        self.conv.add_turn(
            user_input="I'm John",
            bot_response="Hello John!",
            expected_facts={'name': 'John'}
        )
        
        # Test con response vacío
        result = self.conv.validate_retention(
            response="",
            facts_to_check=['name']
        )
        
        self.assertEqual(result['retention_score'], 0.0)
        self.assertFalse(result['name_retained'])


if __name__ == '__main__':
    # Ejecutar tests
    unittest.main(verbosity=2)
