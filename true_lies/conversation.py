#!/usr/bin/env python3
"""
ConversationValidator - Validación Multiturno para Memoria Conversacional
=======================================================================

Sistema que valida si los modelos de LLM mantienen memoria conversacional,
es decir, si recuerdan y utilizan información de turnos anteriores en sus respuestas finales.

Uso básico:
    from true_lies import ConversationValidator
    
    conv = ConversationValidator()
    conv.add_turn(
        user_input="Hi, I'm Sarah Johnson, SSN 987-65-4321",
        bot_response="Hello Sarah, I'll help with your mortgage",
        expected_facts={'client_name': 'Sarah Johnson', 'ssn': '987-65-4321'}
    )
    
    retention = conv.validate_retention(
        response="Sarah, your $360,000 mortgage at TechCorp is approved",
        facts_to_check=['client_name', 'loan_amount', 'employer']
    )
"""

import re
from typing import Dict, List, Any, Optional, Union
from .utils import extract_fact
from .extractors import EXTRACTORS


class ConversationValidator:
    """
    Validador de memoria conversacional para sistemas multiturno.
    
    Acumula facts conversacionales a través de múltiples turnos y valida
    si el LLM mantiene el contexto en respuestas posteriores.
    """
    
    def __init__(self):
        """Inicializar el validador de conversación."""
        self.conversation_facts = {}
        self.turn_history = []
    
    def add_turn(self, user_input: str, bot_response: str, expected_facts: Dict[str, Any]) -> None:
        """
        Acumula facts conversacionales de un turno.
        
        Args:
            user_input: Entrada del usuario en este turno
            bot_response: Respuesta del bot en este turno
            expected_facts: Facts esperados a extraer de este turno
        """
        # Extraer facts del turno actual
        turn_facts = {}
        for fact_name, expected_value in expected_facts.items():
            # Usar extractores existentes para detectar facts
            extracted = self._detect_fact_in_response(
                f"{user_input} {bot_response}", 
                fact_name, 
                expected_value
            )
            if extracted is not None:
                turn_facts[fact_name] = extracted
        
        # Acumular facts en el contexto conversacional
        self.conversation_facts.update(turn_facts)
        
        # Guardar historial del turno
        self.turn_history.append({
            'user_input': user_input,
            'bot_response': bot_response,
            'expected_facts': expected_facts,
            'extracted_facts': turn_facts
        })
    
    def validate_retention(self, response: str, facts_to_check: List[str]) -> Dict[str, Any]:
        """
        Valida memoria en respuesta final.
        
        Args:
            response: Respuesta del bot a validar
            facts_to_check: Lista de facts a verificar en la respuesta
            
        Returns:
            dict: Métricas de retención detalladas
        """
        retention_results = {}
        facts_retained = 0
        total_facts = len(facts_to_check)
        
        # Verificar cada fact individualmente
        for fact_name in facts_to_check:
            if fact_name not in self.conversation_facts:
                retention_results[f'{fact_name}_retained'] = False
                retention_results[f'{fact_name}_reason'] = 'Fact not found in conversation context'
                continue
            
            expected_value = self.conversation_facts[fact_name]
            is_retained = self._detect_fact_in_response(response, fact_name, expected_value)
            
            retention_results[f'{fact_name}_retained'] = is_retained is not None
            retention_results[f'{fact_name}_detected'] = is_retained
            retention_results[f'{fact_name}_expected'] = expected_value
            
            if is_retained is not None:
                facts_retained += 1
        
        # Calcular métricas generales
        retention_score = facts_retained / total_facts if total_facts > 0 else 0.0
        all_retained = facts_retained == total_facts
        
        return {
            'retention_score': retention_score,
            'facts_retained': facts_retained,
            'total_facts': total_facts,
            'all_retained': all_retained,
            **retention_results
        }
    
    def validate_full_conversation(self, final_response: str, facts_to_check: List[str], 
                                 similarity_threshold: float = 0.8) -> Dict[str, Any]:
        """
        Combina retención + validación core para análisis completo.
        
        Args:
            final_response: Respuesta final del bot
            facts_to_check: Facts a verificar
            similarity_threshold: Umbral de similitud semántica (para uso futuro)
            
        Returns:
            dict: Resultados combinados de retención y validación core
        """
        # Validar retención
        retention_results = self.validate_retention(final_response, facts_to_check)
        
        # Crear escenario para validación core (usando facts acumulados)
        core_facts = {}
        for fact_name in facts_to_check:
            if fact_name in self.conversation_facts:
                # Usar extractores apropiados según el tipo de fact
                extractor_type = self._get_extractor_type(fact_name)
                core_facts[fact_name] = {
                    'extractor': extractor_type,
                    'expected': str(self.conversation_facts[fact_name])
                }
        
        # Crear referencia semántica basada en facts acumulados
        # semantic_reference = self._build_semantic_reference()  # TODO: Implementar validación semántica
        
        # Aplicar validación core (simulada - en implementación real usaría validation_core)
        # similarity_threshold se usará para validación semántica futura
        core_validation = {
            'factual_accuracy': retention_results['all_retained'],
            'similarity_score': 1.0,  # Placeholder - implementar con semantic.py
            'polarity_match': True,   # Placeholder - implementar con polarity.py
            'is_valid': retention_results['all_retained']
        }
        
        return {
            **retention_results,
            'core_validation': core_validation,
            'conversation_context': self.conversation_facts,
            'turn_count': len(self.turn_history)
        }
    
    def _detect_fact_in_response(self, response: str, fact_name: str, expected_value: Any) -> Optional[Any]:
        """
        Lógica inteligente de detección de facts por tipo.
        
        Args:
            response: Texto donde buscar el fact
            fact_name: Nombre del fact a detectar
            expected_value: Valor esperado del fact
            
        Returns:
            Valor detectado o None si no se encuentra
        """
        # Detección específica por tipo de fact
        if 'name' in fact_name.lower() or 'nombre' in fact_name.lower():
            return self._detect_name_in_response(response, expected_value)
        elif 'amount' in fact_name.lower() or 'monto' in fact_name.lower() or 'precio' in fact_name.lower() or 'salary' in fact_name.lower() or 'income' in fact_name.lower():
            return self._detect_amount_in_response(response, expected_value)
        elif 'id' in fact_name.lower() or 'ssn' in fact_name.lower() or 'cuenta' in fact_name.lower():
            return self._detect_id_in_response(response, expected_value)
        elif 'email' in fact_name.lower() or 'correo' in fact_name.lower():
            return self._detect_email_in_response(response, expected_value)
        elif 'phone' in fact_name.lower() or 'telefono' in fact_name.lower() or 'teléfono' in fact_name.lower():
            return self._detect_phone_in_response(response, expected_value)
        elif 'employer' in fact_name.lower() or 'empleador' in fact_name.lower():
            return self._detect_employer_in_response(response, expected_value)
        elif 'score' in fact_name.lower() or 'puntaje' in fact_name.lower():
            return self._detect_score_in_response(response, expected_value)
        else:
            # Detección genérica usando extractores existentes
            return self._detect_generic_fact(response, fact_name, expected_value)
    
    def _detect_name_in_response(self, response: str, expected_name: str) -> Optional[str]:
        """Detecta nombres (partes individuales)."""
        name_parts = expected_name.lower().split()
        response_lower = response.lower()
        
        # Buscar partes del nombre individualmente
        found_parts = [part for part in name_parts if part in response_lower]
        
        if len(found_parts) >= len(name_parts) * 0.5:  # Al menos 50% de las partes
            return expected_name
        return None
    
    def _detect_amount_in_response(self, response: str, expected_amount: str) -> Optional[str]:
        """Detecta montos (múltiples formatos)."""
        # Normalizar expected_amount
        expected_num = re.sub(r'[^\d]', '', str(expected_amount))
        
        # Buscar patrones de montos
        amount_patterns = [
            r'\$[\d,]+\.?\d*',  # $360,000
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # 360,000
            r'USD\s*(\d+)',  # USD 360000
            r'(\d+)\s*dolares?',  # 360000 dolares
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                match_num = re.sub(r'[^\d]', '', str(match))
                if match_num == expected_num:
                    return match
        
        return None
    
    def _detect_id_in_response(self, response: str, expected_id: str) -> Optional[str]:
        """Detecta IDs (coincidencia exacta)."""
        # Para IDs, buscar coincidencia exacta
        if str(expected_id).lower() in response.lower():
            return expected_id
        return None
    
    def _detect_email_in_response(self, response: str, expected_email: str) -> Optional[str]:
        """Detecta emails."""
        # Usar el extractor de email de utils.py
        from .utils import extract_email
        detected_email = extract_email(response)
        
        if detected_email and detected_email.lower() == expected_email.lower():
            return detected_email
        
        return None
    
    def _detect_phone_in_response(self, response: str, expected_phone: str) -> Optional[str]:
        """Detecta números de teléfono."""
        # Usar el extractor de teléfono de utils.py
        from .utils import extract_phone
        detected_phone = extract_phone(response)
        
        if detected_phone:
            # Normalizar ambos números para comparar
            def normalize_phone(phone):
                return re.sub(r'[^\d]', '', phone)
            
            if normalize_phone(detected_phone) == normalize_phone(expected_phone):
                return detected_phone
        
        return None
    
    def _detect_employer_in_response(self, response: str, expected_employer: str) -> Optional[str]:
        """Detecta empleadores."""
        employer_lower = expected_employer.lower()
        response_lower = response.lower()
        
        # Buscar coincidencia exacta
        if employer_lower in response_lower:
            return expected_employer
        
        # Buscar palabras clave del empleador (sin palabras comunes como Inc, Corp, etc.)
        employer_words = employer_lower.split()
        # Filtrar palabras comunes que pueden no estar en la respuesta
        common_words = {'inc', 'corp', 'llc', 'ltd', 'company', 'co'}
        meaningful_words = [word for word in employer_words if word not in common_words]
        
        if meaningful_words:
            found_words = [word for word in meaningful_words if word in response_lower]
            if len(found_words) >= len(meaningful_words) * 0.5:  # Al menos 50% de las palabras significativas
                return expected_employer
        else:
            # Si todas las palabras son comunes, usar la lógica original
            found_words = [word for word in employer_words if word in response_lower]
            if len(found_words) >= len(employer_words) * 0.7:
                return expected_employer
        
        return None
    
    def _detect_score_in_response(self, response: str, expected_score: str) -> Optional[str]:
        """Detecta scores y términos."""
        # Buscar el score exacto
        if str(expected_score) in response:
            return expected_score
        
        # Buscar patrones de score
        score_patterns = [
            r'score[:\s]*(\d+)',
            r'puntaje[:\s]*(\d+)',
            r'(\d+)\s*points?',
        ]
        
        for pattern in score_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                if match == str(expected_score):
                    return match
        
        return None
    
    def _detect_generic_fact(self, response: str, fact_name: str, expected_value: Any) -> Optional[Any]:
        """Detección genérica usando extractores existentes."""
        # fact_name se puede usar en el futuro para lógica específica por tipo de fact
        _ = fact_name  # Evitar warning de parámetro no usado
        # Intentar con diferentes extractores
        for extractor_name, extractor_func in EXTRACTORS.items():
            try:
                if extractor_name == 'categorical':
                    # Para categorical necesitamos patterns
                    continue
                elif extractor_name == 'regex':
                    # Para regex necesitamos pattern
                    continue
                else:
                    result = extractor_func(response)
                    if result and str(result) == str(expected_value):
                        return result
            except Exception:
                continue
        
        # Fallback: búsqueda de texto simple
        if str(expected_value).lower() in response.lower():
            return expected_value
        
        return None
    
    def _get_extractor_type(self, fact_name: str) -> str:
        """Determina el tipo de extractor basado en el nombre del fact."""
        fact_lower = fact_name.lower()
        
        if 'amount' in fact_lower or 'monto' in fact_lower or 'precio' in fact_lower:
            return 'currency'
        elif 'date' in fact_lower or 'fecha' in fact_lower:
            return 'date'
        elif 'percentage' in fact_lower or 'porcentaje' in fact_lower:
            return 'percentage'
        elif 'hours' in fact_lower or 'horas' in fact_lower:
            return 'hours'
        else:
            return 'number'
    
    def _build_semantic_reference(self) -> str:
        """Construye referencia semántica basada en facts acumulados."""
        if not self.conversation_facts:
            return ""
        
        # Crear una descripción semántica de los facts acumulados
        reference_parts = []
        
        if 'client_name' in self.conversation_facts:
            reference_parts.append(f"Cliente: {self.conversation_facts['client_name']}")
        
        if 'loan_amount' in self.conversation_facts:
            reference_parts.append(f"Monto del préstamo: ${self.conversation_facts['loan_amount']}")
        
        if 'employer' in self.conversation_facts:
            reference_parts.append(f"Empleador: {self.conversation_facts['employer']}")
        
        if 'annual_income' in self.conversation_facts:
            reference_parts.append(f"Ingresos anuales: ${self.conversation_facts['annual_income']}")
        
        return ". ".join(reference_parts)
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de la conversación actual."""
        return {
            'total_turns': len(self.turn_history),
            'total_facts': len(self.conversation_facts),
            'facts': self.conversation_facts,
            'turn_history': self.turn_history
        }
    
    def clear_conversation(self) -> None:
        """Limpia el contexto conversacional."""
        self.conversation_facts = {}
        self.turn_history = []
    
    def print_retention_report(self, retention_results: Dict[str, Any], facts_to_check: List[str], 
                             response: str = None, title: str = "Retention Report") -> None:
        """
        Prints a detailed and elegant report of retention results.
        
        Args:
            retention_results: Results from validate_retention()
            facts_to_check: List of facts to verify
            response: Bot response (optional)
            title: Report title
        """
        print("=" * 80)
        print(f"📊 {title}")
        print("=" * 80)
        
        if response:
            print(f"📝 Response: '{response}'")
            print()
        
        print(f"📈 General Metrics:")
        print(f"   Retention Score: {retention_results['retention_score']:.2f}")
        print(f"   Facts Retained: {retention_results['facts_retained']}/{retention_results['total_facts']}")
        print(f"   All Retained: {'✅' if retention_results['all_retained'] else '❌'}")
        print()
        
        print(f"🔍 Details by Fact:")
        for fact in facts_to_check:
            retained = retention_results.get(f'{fact}_retained', False)
            detected = retention_results.get(f'{fact}_detected', 'N/A')
            expected = retention_results.get(f'{fact}_expected', 'N/A')
            reason = retention_results.get(f'{fact}_reason', '')
            
            status = "✅" if retained else "❌"
            print(f"   {status} {fact}:")
            print(f"      Expected: '{expected}'")
            print(f"      Detected: '{detected}'")
            if not retained and reason:
                print(f"      Reason: {reason}")
            print()
        
        # General evaluation
        score = retention_results['retention_score']
        if score >= 0.9:
            grade = "A"
            comment = "Excellent context retention"
        elif score >= 0.8:
            grade = "B"
            comment = "Good context retention"
        elif score >= 0.7:
            grade = "C"
            comment = "Acceptable retention"
        elif score >= 0.5:
            grade = "D"
            comment = "Poor retention"
        else:
            grade = "F"
            comment = "Very poor retention"
        
        print(f"🎯 Evaluation: {grade} - {comment}")
        print("=" * 80)
    
    def print_conversation_summary(self, title: str = "Conversation Summary") -> None:
        """
        Prints an elegant summary of the current conversation.
        
        Args:
            title: Summary title
        """
        summary = self.get_conversation_summary()
        
        print("=" * 80)
        print(f"💬 {title}")
        print("=" * 80)
        
        print(f"📊 Statistics:")
        print(f"   Total turns: {summary['total_turns']}")
        print(f"   Total facts: {summary['total_facts']}")
        print()
        
        if summary['facts']:
            print(f"📋 Accumulated Facts:")
            for fact_name, fact_value in summary['facts'].items():
                print(f"   {fact_name}: {fact_value}")
            print()
        
        if summary['turn_history']:
            print(f"🔄 Turn History:")
            for i, turn in enumerate(summary['turn_history'], 1):
                print(f"   Turn {i}:")
                print(f"      User: {turn['user_input'][:50]}{'...' if len(turn['user_input']) > 50 else ''}")
                print(f"      Bot: {turn['bot_response'][:50]}{'...' if len(turn['bot_response']) > 50 else ''}")
                print(f"      Extracted facts: {len(turn['extracted_facts'])}")
            print()
        
        print("=" * 80)
    
    def validate_and_report(self, response: str, facts_to_check: List[str], 
                          title: str = "Validation Report") -> Dict[str, Any]:
        """
        Validates retention and prints report automatically.
        
        Args:
            response: Bot response to validate
            facts_to_check: List of facts to verify
            title: Report title
        
        Returns:
            dict: Validation results
        """
        retention = self.validate_retention(response, facts_to_check)
        self.print_retention_report(retention, facts_to_check, response, title)
        return retention
    
    def add_turn_and_report(self, user_input: str, bot_response: str, 
                          expected_facts: Dict[str, Any], 
                          title: str = "Turn Added") -> None:
        """
        Agrega turno e imprime resumen automáticamente.
        
        Args:
            user_input: Entrada del usuario
            bot_response: Respuesta del bot
            expected_facts: Facts esperados
            title: Título del resumen
        """
        self.add_turn(user_input, bot_response, expected_facts)
        
        print("=" * 80)
        print(f"➕ {title}")
        print("=" * 80)
        print(f"👤 User: {user_input}")
        print(f"🤖 Bot: {bot_response}")
        print(f"📋 Expected facts: {expected_facts}")
        print(f"📊 Extracted facts: {len(self.conversation_facts)} total")
        print("=" * 80)
