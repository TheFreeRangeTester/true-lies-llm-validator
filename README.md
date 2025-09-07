# True Lies Validator 🎭

**La librería más fácil para validar respuestas de LLMs y chatbots**

Valida si tu LLM o chatbot está diciendo la verdad, recordando el contexto y manteniendo la coherencia. Perfecto para testing automatizado de conversaciones.

## 🚀 Instalación Rápida

```bash
# Instalar la librería
pip install true-lies-validator

# Verificar instalación
python -c "from true_lies import ConversationValidator; print('✅ Instalado correctamente')"
```

## ⚡ Empezar en 2 Minutos

### 1. Validación Básica (1 minuto)

```python
from true_lies import ConversationValidator

# Crear validador
conv = ConversationValidator()

# Agregar conversación con reporting automático
conv.add_turn_and_report(
    user_input="Hola, soy Juan, mi email es juan@empresa.com",
    bot_response="Hola Juan! Te ayudo con tu consulta.",
    expected_facts={'name': 'Juan', 'email': 'juan@empresa.com'},
    title="Turn 1: Usuario se identifica"
)

# Validar si el bot recuerda el contexto
final_response = "Juan, tu consulta sobre juan@empresa.com está resuelta"
retention = conv.validate_and_report(
    response=final_response,
    facts_to_check=['name', 'email'],
    title="Test de Retención"
)

# Resultado automático: ✅ PASS o ❌ FAIL
```

### 2. Validación Multiturno Completa (2 minutos)

```python
from true_lies import ConversationValidator

def test_chatbot_support():
    """Test completo de chatbot de soporte"""
    
    # Crear validador
    conv = ConversationValidator()
    
    # Turn 1: Usuario reporta problema
    conv.add_turn_and_report(
        user_input="Mi app no funciona, soy usuario ID 12345",
        bot_response="Hola, voy a ayudarte. ¿Qué error ves?",
        expected_facts={'user_id': '12345', 'issue_type': 'app_no_funciona'},
        title="Turn 1: Usuario reporta problema"
    )
    
    # Turn 2: Usuario da detalles
    conv.add_turn_and_report(
        user_input="Error 500 en login, email juan@empresa.com",
        bot_response="Entiendo, error 500 en login. Revisando tu cuenta.",
        expected_facts={'error_code': '500', 'email': 'juan@empresa.com'},
        title="Turn 2: Usuario proporciona detalles"
    )
    
    # Mostrar resumen de conversación
    conv.print_conversation_summary("Resumen de Conversación")
    
    # Test final: ¿El bot recuerda todo?
    final_response = "Juan (ID 12345), tu error 500 será solucionado en 2 horas"
    retention = conv.validate_and_report(
        response=final_response,
        facts_to_check=['user_id', 'error_code', 'email'],
        title="Test de Retención de Contexto"
    )
    
    # Retornar resultado para tests automatizados
    return retention['retention_score'] >= 0.8

# Ejecutar test
if __name__ == "__main__":
    test_chatbot_support()
```

## 🎯 Casos de Uso Populares

### E-commerce
```python
# Cliente comprando producto
conv.add_turn_and_report(
    user_input="Hola, soy María, quiero comprar una laptop por $1500",
    bot_response="Hola María! Te ayudo con la laptop. Email registrado: maria@tienda.com",
    expected_facts={'customer_name': 'María', 'product': 'laptop', 'budget': '1500'},
    title="Turn 1: Cliente se identifica"
)
```

### Banking
```python
# Cliente solicitando préstamo
conv.add_turn_and_report(
    user_input="Soy Carlos, trabajo en TechCorp, gano $95,000, quiero un préstamo",
    bot_response="Hola Carlos! Te ayudo con tu préstamo. Email: carlos@banco.com",
    expected_facts={'customer_name': 'Carlos', 'employer': 'TechCorp', 'income': '95000'},
    title="Turn 1: Cliente solicita préstamo"
)
```

### Soporte Técnico
```python
# Usuario reporta problema
conv.add_turn_and_report(
    user_input="Mi app no funciona, soy usuario ID 12345",
    bot_response="Hola, voy a ayudarte. ¿Qué error ves?",
    expected_facts={'user_id': '12345', 'issue_type': 'app_no_funciona'},
    title="Turn 1: Usuario reporta problema"
)
```

## 🔧 Métodos Principales

### `add_turn_and_report()` - Agregar turno con reporting automático
```python
conv.add_turn_and_report(
    user_input="...",
    bot_response="...",
    expected_facts={'key': 'value'},
    title="Descripción del turno"
)
```

### `validate_and_report()` - Validar retención con reporting automático
```python
retention = conv.validate_and_report(
    response="Respuesta del bot a validar",
    facts_to_check=['fact1', 'fact2'],
    title="Test de Retención"
)
```

### `print_conversation_summary()` - Resumen de conversación
```python
conv.print_conversation_summary("Resumen de Conversación")
```

## 📊 Tipos de Facts Soportados

La librería detecta automáticamente estos tipos de información:

- **Nombres**: "Juan", "María González"
- **Emails**: "juan@empresa.com", "maria@tienda.com"
- **Teléfonos**: "+1-555-123-4567", "(555) 123-4567"
- **IDs**: "12345", "USER-001", "POL-2024-001"
- **Montos**: "$1,500", "1500", "USD 1500"
- **Empleadores**: "TechCorp", "Google Inc", "Microsoft"
- **Fechas**: "2024-12-31", "31/12/2024", "December 31, 2024"
- **Porcentajes**: "15%", "15 percent", "fifteen percent"

## 🎨 Reporting Automático

True Lies se encarga de todo el reporting. Solo necesitas 3 líneas:

```python
# Antes (30+ líneas de código manual)
print(f"📊 Resultados detallados:")
for fact in facts:
    retained = retention.get(f'{fact}_retained', False)
    # ... 25 líneas más de prints manuales

# Después (3 líneas simples)
retention = conv.validate_and_report(
    response=final_response,
    facts_to_check=['fact1', 'fact2'],
    title="Test de Retención"
)
```

## 📈 Métricas Automáticas

- **Retention Score**: 0.0 - 1.0 (qué tan bien recuerda)
- **Facts Retained**: X/Y facts recordados
- **Evaluación**: A, B, C, D, F (calificación automática)
- **Detalles por Fact**: Qué se encontró y qué no

## 🚀 Ejemplos Completos

### Ejemplo 1: Chatbot de Soporte
```python
from true_lies import ConversationValidator

def test_support_chatbot():
    conv = ConversationValidator()
    
    # Turn 1: Usuario reporta problema
    conv.add_turn_and_report(
        user_input="Mi app no funciona, soy usuario ID 12345",
        bot_response="Hola, voy a ayudarte. ¿Qué error ves?",
        expected_facts={'user_id': '12345', 'issue_type': 'app_no_funciona'},
        title="Turn 1: Usuario reporta problema"
    )
    
    # Turn 2: Usuario da detalles
    conv.add_turn_and_report(
        user_input="Error 500 en login, email juan@empresa.com",
        bot_response="Entiendo, error 500 en login. Revisando tu cuenta.",
        expected_facts={'error_code': '500', 'email': 'juan@empresa.com'},
        title="Turn 2: Usuario proporciona detalles"
    )
    
    # Test final
    final_response = "Juan (ID 12345), tu error 500 será solucionado en 2 horas"
    retention = conv.validate_and_report(
        response=final_response,
        facts_to_check=['user_id', 'error_code', 'email'],
        title="Test de Retención de Contexto"
    )
    
    return retention['retention_score'] >= 0.8

if __name__ == "__main__":
    test_support_chatbot()
```

### Ejemplo 2: E-commerce
```python
from true_lies import ConversationValidator

def test_ecommerce_chatbot():
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
    
    # Test final
    final_response = "María, tu laptop de programación por $1500 está lista. Te envío la factura a maria@tienda.com"
    retention = conv.validate_and_report(
        response=final_response,
        facts_to_check=['customer_name', 'email', 'budget', 'use_case'],
        title="Test de Retención E-commerce"
    )
    
    return retention['retention_score'] >= 0.8

if __name__ == "__main__":
    test_ecommerce_chatbot()
```

## 🔍 Validación Avanzada (Opcional)

Para casos más complejos, también puedes usar la validación tradicional:

```python
from true_lies import create_scenario, validate_llm_candidates

# Facts que DEBEN estar en la respuesta
facts = {
    'policy_number': {'extractor': 'categorical', 'expected': 'POL-2024-001'},
    'premium': {'extractor': 'money', 'expected': '850.00'},
    'coverage_type': {'extractor': 'categorical', 'expected': 'auto insurance'}
}

# Texto de referencia para comparación semántica
reference_text = "Your auto insurance policy #POL-2024-001 has a premium of $850.00"

# Crear escenario
scenario = create_scenario(
    facts=facts,
    semantic_reference=reference_text,
    semantic_mappings={}
)

# Validar respuestas
candidates = [
    "Policy POL-2024-001 covers your automobile with monthly payments of $850.00",
    "Your car insurance policy POL-2024-001 costs $850 monthly"
]

results = validate_llm_candidates(
    scenario=scenario,
    candidates=candidates,
    threshold=0.7
)
```

## 🎯 Extractores Disponibles

- **`money`**: Valores monetarios ($1,234.56, USD 27, 100 dollars)
- **`number`**: Números generales (25, 3.14, 1000)
- **`date`**: Fechas (December 31, 2024, 31/12/2024)
- **`email`**: Direcciones de email
- **`phone`**: Números de teléfono
- **`categorical`**: Valores categóricos con sinónimos
- **`regex`**: Patrones personalizados

## 📚 Documentación Completa

- **[Guía de Validación Multiturno](MULTITURN_VALIDATION_README.md)** - Detalles completos
- **[Guía de Integración](INTEGRATION_GUIDE.md)** - Cómo integrar en tu proyecto
- **[Guía de Extracción de Emails](EMAIL_EXTRACTION_GUIDE.md)** - Extracción avanzada
- **[Comparación Antes/Después](COMPARISON_BEFORE_AFTER.md)** - Mejoras de la librería

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🙏 Agradecimientos

- NLTK por las capacidades de procesamiento de lenguaje natural
- La comunidad open source por la inspiración y feedback

---

**True Lies - Donde la IA se encuentra con la realidad** 🎭

*¿Tienes preguntas? Abre un issue o contacta al equipo de desarrollo.*