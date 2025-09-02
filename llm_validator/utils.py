def extract_balance(text):
    import re
    if not isinstance(text, str):
        return None
    # Buscar patrones de números con $ y comas, ejemplo: $1,234.56 o 1234.56
    matches = re.findall(r'\$?\s*[\d{1,3}(?:,\d{3})*(?:\.\d+)?]+', text)
    for match in matches:
        # Limpiar el valor para convertir a float
        cleaned = match.replace('$', '').replace(',', '').strip()
        # Remover puntos al final que no son parte del decimal
        if cleaned.endswith('.') and '.' in cleaned[:-1]:
            cleaned = cleaned[:-1]
        try:
            value = float(cleaned)
            return value
        except ValueError:
            continue
    return None

def extract_product_name(text):
    """
    Extrae el nombre del producto del texto.
    Busca patrones como "iPhone 15 Pro", "Samsung Galaxy", etc.
    """
    if not isinstance(text, str):
        return None
    
    import re
    
    # Patrones comunes para nombres de productos
    patterns = [
        r'(iPhone\s+\d+(?:\s+Pro)?(?:\s+Max)?(?:\s+Mini)?)',
        r'(Samsung\s+Galaxy\s+\w+)',
        r'(Google\s+Pixel\s+\d+)',
        r'(MacBook\s+(?:Pro|Air)\s+\w+)',
        r'(iPad\s+(?:Pro|Air|Mini)?\s*\d*)',
        r'(Apple\s+Watch\s+Series\s+\d+)',
        r'([A-Z][a-zA-Z0-9\s]+(?:\s+\d+)?(?:\s+Pro)?(?:\s+Max)?(?:\s+Mini)?)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            product_name = match.group(1).strip()
            # Filtrar palabras que no son nombres de productos
            if len(product_name.split()) >= 2 and not any(word.lower() in ['the', 'is', 'currently', 'available', 'with', 'units', 'price', 'comes', 'color'] for word in product_name.split()):
                return product_name
    
    return None

def extract_stock(text):
    """
    Extrae la cantidad de stock del texto.
    Busca patrones como "25 units", "in stock with 25", etc.
    """
    if not isinstance(text, str):
        return None
    
    import re
    
    # Patrones para extraer stock
    patterns = [
        r'(\d+)\s+units?\s+available',
        r'in\s+stock\s+with\s+(\d+)',
        r'stock\s+with\s+(\d+)',
        r'(\d+)\s+units?\s+in\s+stock',
        r'available\s+(\d+)\s+units?'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def extract_price(text):
    """
    Extrae el precio del texto.
    Busca patrones como "$999.99", "price is $999.99", etc.
    """
    if not isinstance(text, str):
        return None
    
    import re
    
    # Patrones para extraer precio
    patterns = [
        r'price\s+is\s+(\$\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'(\$\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'costs?\s+(\$\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'priced?\s+at\s+(\$\d+(?:,\d{3})*(?:\.\d{2})?)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def extract_color(text):
    """
    Extrae el color del producto del texto.
    Busca patrones como "Space Black color", "comes in Space Black", etc.
    """
    if not isinstance(text, str):
        return None
    
    import re
    
    # Lista de colores comunes
    colors = [
        'Space Black', 'Space Gray', 'Silver', 'Gold', 'Rose Gold', 'Blue', 'Red', 'Green', 'Yellow',
        'White', 'Black', 'Gray', 'Pink', 'Purple', 'Orange', 'Brown', 'Cyan', 'Magenta',
        'Midnight', 'Starlight', 'Product Red', 'Alpine Green', 'Sierra Blue', 'Pacific Blue'
    ]
    
    # Patrones para extraer color
    patterns = [
        r'comes?\s+in\s+([A-Za-z\s]+?)(?:\s+color)?',
        r'color\s+is\s+([A-Za-z\s]+)',
        r'([A-Za-z\s]+?)\s+color',
        r'in\s+([A-Za-z\s]+?)\s+color'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            found_color = match.group(1).strip()
            # Verificar si el color encontrado está en nuestra lista
            for color in colors:
                if color.lower() in found_color.lower() or found_color.lower() in color.lower():
                    return color
    
    return None

def extract_policy_number(text):
    """
    Extrae el número de póliza del texto.
    Busca patrones como "POL-2024-001", "#POL-2024-001", etc.
    """
    if not isinstance(text, str):
        return None
    
    import re
    
    patterns = [
        r'policy\s+#?([A-Z0-9-]+)',
        r'#([A-Z0-9-]+)',
        r'policy\s+([A-Z0-9-]+)',
        r'([A-Z0-9-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def extract_premium(text):
    """
    Extrae la prima del seguro del texto.
    Busca patrones como "$850.00 per month", "premium of $850.00", etc.
    """
    if not isinstance(text, str):
        return None
    
    import re
    
    patterns = [
        r'premium\s+of\s+(\$\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'(\$\d+(?:,\d{3})*(?:\.\d{2})?)\s+per\s+month',
        r'costs?\s+(\$\d+(?:,\d{3})*(?:\.\d{2})?)\s+monthly',
        r'(\$\d+(?:,\d{3})*(?:\.\d{2})?)\s+monthly',
        r'monthly\s+payments?\s+of\s+(\$\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'(\$\d+(?:,\d{3})*(?:\.\d{2})?)\s+monthly\s+premium',
        r'(\$\d+(?:,\d{3})*(?:\.\d{2})?)\s+monthly'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def extract_coverage_type(text):
    """
    Extrae el tipo de cobertura del texto.
    Busca patrones como "auto insurance", "car insurance", etc.
    """
    if not isinstance(text, str):
        return None
    
    import re
    
    patterns = [
        r'(auto\s+insurance)',
        r'(car\s+insurance)',
        r'(automobile\s+insurance)',
        r'(vehicle\s+insurance)',
        r'(auto\s+policy)',
        r'(car\s+policy)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def extract_liability_limit(text):
    """
    Extrae el límite de responsabilidad del texto.
    Busca patrones como "liability up to $100,000", "$100,000 liability", etc.
    """
    if not isinstance(text, str):
        return None
    
    import re
    
    patterns = [
        r'liability\s+up\s+to\s+(\$\d+(?:,\d{3})*)',
        r'liability\s+(\$\d+(?:,\d{3})*)',
        r'(\$\d+(?:,\d{3})*)\s+liability'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def extract_expiry_date(text):
    """
    Extrae la fecha de expiración del texto.
    Busca patrones como "expires on December 31, 2024", "valid until December 31, 2024", etc.
    """
    if not isinstance(text, str):
        return None
    
    import re
    
    patterns = [
        r'expires?\s+on\s+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
        r'valid\s+until\s+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
        r'expiry\s+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
        r'([A-Za-z]+\s+\d{1,2},?\s+\d{4})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def extract_motorcycle_model(text):
    """
    Extrae el modelo de motocicleta del texto.
    Busca patrones como "Honda CBR 600RR", "Yamaha R1", etc.
    """
    if not isinstance(text, str):
        return None
    
    import re
    
    # Patrones más específicos para modelos de motocicletas
    patterns = [
        r'(Honda\s+CBR\s+\d+[A-Z]*)',
        r'(Honda\s+[A-Z]+\s+\d+[A-Z]*)',
        r'(Yamaha\s+[A-Z]+\s*\d*[A-Z]*)',
        r'(Kawasaki\s+[A-Z]+\s*\d*[A-Z]*)',
        r'(Suzuki\s+[A-Z]+\s*\d*[A-Z]*)',
        r'(Ducati\s+[A-Z]+\s*\d*[A-Z]*)',
        r'(BMW\s+[A-Z]+\s*\d*[A-Z]*)',
        r'(Harley\s+Davidson\s+[A-Z]+\s*\d*)',
        r'(Triumph\s+[A-Z]+\s*\d*)',
        r'(Aprilia\s+[A-Z]+\s*\d*)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            model = match.group(1).strip()
            # Verificar que el modelo no contenga palabras que no deberían estar ahí
            words = model.split()
            if len(words) >= 2:
                # Filtrar palabras que no son parte del modelo
                filtered_words = []
                for word in words:
                    if word.lower() not in ['the', 'is', 'available', 'for', 'priced', 'at', 'with', 'miles', 'on', 'the', 'odometer', 'and', 'comes', 'warranty', 'condition', 'motorcycle']:
                        filtered_words.append(word)
                
                if len(filtered_words) >= 2:
                    return ' '.join(filtered_words)
    
    # Si no se encuentra con patrones específicos, intentar extraer el modelo completo
    # Buscar "Honda CBR 600RR" específicamente
    specific_pattern = r'(Honda\s+CBR\s+600RR)'
    match = re.search(specific_pattern, text, re.IGNORECASE)
    if match:
        return match.group(1)
    
    return None

def extract_mileage(text):
    """
    Extrae el kilometraje del texto.
    Busca patrones como "1500 miles on the odometer", "odometer shows 1500", etc.
    """
    if not isinstance(text, str):
        return None
    
    import re
    
    patterns = [
        r'(\d+)\s+miles?\s+on\s+the\s+odometer',
        r'odometer\s+shows\s+(\d+)',
        r'(\d+)\s+miles?\s+on\s+the\s+clock',
        r'(\d+)\s+miles?'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def extract_warranty(text):
    """
    Extrae la garantía del texto.
    Busca patrones como "6-month warranty", "6 month warranty", etc.
    """
    if not isinstance(text, str):
        return None
    
    import re
    
    patterns = [
        r'(\d+)-month\s+warranty',
        r'(\d+)\s+month\s+warranty',
        r'warranty\s+(\d+)\s+months?',
        r'(\d+)\s+month\s+warranty\s+included',
        r'(\d+)-month\s+warranty\s+included',
        r'(\d+)-month\s+warranty\s+included'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return f"{match.group(1)}-month"
    
    return None

def extract_condition(text):
    """
    Extrae la condición del texto.
    Busca patrones como "excellent condition", "condition: excellent", etc.
    """
    if not isinstance(text, str):
        return None
    
    import re
    
    patterns = [
        r'in\s+([a-zA-Z]+)\s+condition',
        r'condition:\s+([a-zA-Z]+)',
        r'([a-zA-Z]+)\s+condition'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).lower()
    
    return None

def extract_account_type(text, domain=None):
    if not isinstance(text, str):
        return None
    
    text_lower = text.lower()
    
    # Cargar mapping de sinónimos para account_type
    mapping = load_semantic_mapping(domain) if domain else load_semantic_mapping('account_type')
    
    # Buscar coincidencias exactas primero
    for key, synonyms in mapping.items():
        # Buscar la clave principal
        if key in text_lower:
            return key
        # Buscar en los sinónimos
        for synonym in synonyms:
            if synonym in text_lower:
                return key
    
    # Si no se encuentra con el mapping, intentar extraer patrones comunes
    # Buscar patrones como "term deposit", "savings account", etc.
    import re
    
    # Patrones comunes para tipos de cuenta
    patterns = [
        r'term\s+deposit',
        r'savings\s+account',
        r'checking\s+account',
        r'current\s+account',
        r'credit\s+card',
        r'debit\s+card',
        r'loan\s+account',
        r'mortgage\s+account'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            found_type = match.group().replace(' ', '_')
            return found_type
    
    return None

def extract_value_from_text(text, key, normalize_for_comparison=True, domain=None, field_configs=None):
    """
    Extrae valores de strings del tipo "key: value, key2: value2" o texto natural
    normalize_for_comparison: si True, devuelve el valor normalizado listo para comparación.
    domain: optional domain for loading semantic mappings
    field_configs: optional dict of field configurations for custom extraction
    """
    if not isinstance(text, str):
        return None

    key_lower = key.lower().strip()
    
    # Si se proporcionan configuraciones de campo personalizadas, usarlas
    if field_configs and key_lower in field_configs:
        return extract_value_generic(text, field_configs[key_lower], domain)
    
    # Usar configuraciones predefinidas si existen
    if key_lower in PREDEFINED_FIELD_CONFIGS:
        return extract_value_generic(text, PREDEFINED_FIELD_CONFIGS[key_lower], domain)
    
    # Fallback a funciones específicas para compatibilidad
    if key_lower == 'balance':
        return extract_balance(text)
    
    if key_lower == 'account_type':
        return extract_account_type(text, domain=domain)
    
    if key_lower == 'product_name':
        return extract_product_name(text)
    
    if key_lower == 'stock':
        return extract_stock(text)
    
    if key_lower == 'price':
        return extract_price(text)
    
    if key_lower == 'color':
        return extract_color(text)
    
    # Nuevas funciones específicas para seguros y motocicletas
    if key_lower == 'policy_number':
        return extract_policy_number(text)
    
    if key_lower == 'premium':
        return extract_premium(text)
    
    if key_lower == 'coverage_type':
        return extract_coverage_type(text)
    
    if key_lower == 'liability_limit':
        return extract_liability_limit(text)
    
    if key_lower == 'expiry_date':
        return extract_expiry_date(text)
    
    if key_lower == 'motorcycle_model':
        return extract_motorcycle_model(text)
    
    if key_lower == 'mileage':
        return extract_mileage(text)
    
    if key_lower == 'warranty':
        return extract_warranty(text)
    
    if key_lower == 'condition':
        return extract_condition(text)

    # Intentar formato "key: value" como fallback
    pairs = [pair.strip() for pair in text.split(",")]
    for pair in pairs:
        if ":" in pair:
            k, v = pair.split(":", 1)
            if k.strip().lower() == key_lower:
                value = v.strip()
                if normalize_for_comparison:
                    return normalize_extracted_value(value, key)
                return value
    
    return None

def normalize_extracted_value(value, key):
    """
    Normaliza un valor extraído para comparación
    """
    if key.lower() == 'balance':
        try:
            # Limpiar y convertir a float
            cleaned = str(value).replace('$', '').replace(',', '').strip()
            return float(cleaned)
        except:
            return value
    return value

import json
from pathlib import Path

def load_semantic_mapping(domain, path=None):
    """
    Carga el diccionario de sinónimos para el dominio dado desde un JSON.
    Si se provee 'path', carga desde esa ubicación; si no, carga desde semantic_data/{domain}.json.
    Devuelve un dict vacío si no se encuentra el archivo.
    """
    if path is not None:
        file_path = Path(path)
    else:
        file_path = Path(__file__).parent / "semantic_data" / f"{domain}.json"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[Warning] Semantic mapping for domain '{domain}' not found.")
        return {}

def replace_synonyms(text, mapping):
    """
    Reemplaza en el texto los sinónimos definidos en mapping por el término principal.
    mapping: dict {term_principal: [sinonimo1, sinonimo2, ...]}
    """
    for key, synonyms in mapping.items():
        for synonym in synonyms:
            text = text.replace(synonym, key)
    return text

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Descargar recursos necesarios de NLTK
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('stopwords')

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def normalize_text_advanced(text):
    """
    Tokeniza el texto usando regex, elimina stopwords y realiza lematización.
    Devuelve una lista de tokens normalizados.
    """
    import re
    text = text.lower()
    # Tokenizar usando regex: palabras y números
    tokens = re.findall(r'\b[a-zA-Z0-9]+\b', text)
    # Filtrar stopwords y lematizar
    filtered_tokens = [lemmatizer.lemmatize(token) for token in tokens if token not in stop_words]
    return filtered_tokens

def extract_value_generic(text, field_config, domain=None):
    """
    Función genérica para extraer valores basada en configuración.
    Esta función es completamente agnóstica de dominio y soporta tanto
    extractores genéricos como patrones específicos.
    
    Args:
        text: Texto del cual extraer el valor
        field_config: Configuración del campo a extraer
        domain: Dominio para cargar mapeos semánticos
    
    field_config puede tener dos estructuras:
    
    1. Con extractor genérico:
    {
        "name": "nombre_del_campo",
        "extractor": "currency|categorical|regex|...",
        "patterns": {...},  # para extractores que lo requieren
        "expected": "valor_esperado",
        "normalize": "function_name",  # opcional
        "validation": "validation_function"  # opcional
    }
    
    2. Con patrones específicos (estructura original):
    {
        "name": "nombre_del_campo",
        "patterns": ["patrón1", "patrón2", ...],
        "synonyms": ["sinónimo1", "sinónimo2", ...],
        "normalize": "function_name",  # opcional
        "validation": "validation_function"  # opcional
    }
    """
    if not isinstance(text, str):
        return None
    
    import re
    
    field_name = field_config.get("name", "").lower()
    normalize_func = field_config.get("normalize")
    
    # Cargar mapeo semántico si existe
    mapping = None
    if domain:
        try:
            mapping = load_semantic_mapping(domain)
        except Exception:
            mapping = {}
    
    # NUEVO: Si tiene extractor genérico, usarlo primero
    if "extractor" in field_config:
        extracted_value = extract_value_with_generic_extractor(text, field_config)
        if extracted_value is not None:
            # Aplicar función de normalización si existe
            if normalize_func and callable(normalize_func):
                extracted_value = normalize_func(extracted_value)
            
            # Si hay mapeo semántico, buscar coincidencias
            if mapping:
                for key, synonym_list in mapping.items():
                    if key.lower() in str(extracted_value).lower():
                        return key
                    for synonym in synonym_list:
                        if synonym.lower() in str(extracted_value).lower():
                            return key
            
            return extracted_value
    
    # MÉTODO ORIGINAL: Buscar usando patrones regex específicos
    patterns = field_config.get("patterns", [])
    synonyms = field_config.get("synonyms", [])
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted_value = match.group(1).strip()
            
            # Aplicar función de normalización si existe
            if normalize_func and callable(normalize_func):
                extracted_value = normalize_func(extracted_value)
            
            # Si hay sinónimos definidos, verificar si el valor extraído coincide
            if synonyms:
                for synonym in synonyms:
                    if synonym.lower() in str(extracted_value).lower() or str(extracted_value).lower() in synonym.lower():
                        return synonym
            
            # Si hay mapeo semántico, buscar coincidencias
            if mapping:
                for key, synonym_list in mapping.items():
                    if key.lower() in str(extracted_value).lower():
                        return key
                    for synonym in synonym_list:
                        if synonym.lower() in str(extracted_value).lower():
                            return key
            
            # Si no hay sinónimos ni mapeo, devolver el valor extraído
            return extracted_value
    
    # Si no se encuentra con patrones, intentar formato "key: value"
    pairs = [pair.strip() for pair in text.split(",")]
    for pair in pairs:
        if ":" in pair:
            k, v = pair.split(":", 1)
            if k.strip().lower() == field_name:
                value = v.strip()
                # Aplicar función de normalización si existe
                if normalize_func and callable(normalize_func):
                    value = normalize_func(value)
                return value
    
    return None

def create_field_config(field_name, patterns, synonyms=None, normalize_func=None, validation_func=None):
    """
    Función helper para crear configuración de campos de manera fácil.
    
    Args:
        field_name: Nombre del campo
        patterns: Lista de patrones regex para extraer el valor
        synonyms: Lista de sinónimos válidos (opcional)
        normalize_func: Función de normalización (opcional)
        validation_func: Función de validación (opcional)
    
    Returns:
        dict: Configuración del campo
    """
    config = {
        "name": field_name,
        "patterns": patterns,
        "synonyms": synonyms or [],
        "validation": validation_func
    }
    
    # Solo agregar normalize si se proporciona una función
    if normalize_func and callable(normalize_func):
        config["normalize"] = normalize_func
    
    return config

# Configuraciones predefinidas para casos comunes (opcional, para facilitar el uso)
PREDEFINED_FIELD_CONFIGS = {
    "product_name": create_field_config(
        "product_name",
        [
            r'(iPhone\s+\d+(?:\s+Pro)?(?:\s+Max)?(?:\s+Mini)?)',
            r'(Samsung\s+Galaxy\s+\w+)',
            r'(Google\s+Pixel\s+\d+)',
            r'(MacBook\s+(?:Pro|Air)\s+\w+)',
            r'(iPad\s+(?:Pro|Air|Mini)?\s*\d*)',
            r'(Apple\s+Watch\s+Series\s+\d+)',
            r'([A-Z][a-zA-Z0-9\s]+(?:\s+\d+)?(?:\s+Pro)?(?:\s+Max)?(?:\s+Mini)?)'
        ]
    ),
    "stock": create_field_config(
        "stock",
        [
            r'(\d+)\s+units?\s+available',
            r'in\s+stock\s+with\s+(\d+)',
            r'stock\s+with\s+(\d+)',
            r'(\d+)\s+units?\s+in\s+stock',
            r'available\s+(\d+)\s+units?'
        ]
    ),
    "price": create_field_config(
        "price",
        [
            r'price\s+is\s+(\$\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(\$\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'costs?\s+(\$\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'priced?\s+at\s+(\$\d+(?:,\d{3})*(?:\.\d{2})?)'
        ]
    ),
    "color": create_field_config(
        "color",
        [
            r'comes?\s+in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*?)(?:\s+color)?',
            r'color\s+is\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
            r'([A-Za-z]+(?:\s+[A-Za-z]+)*?)\s+color',
            r'in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*?)\s+color',
            r'Available\s+in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
            r'available\s+in\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)'
        ],
        [
            'Space Black', 'Space Gray', 'Silver', 'Gold', 'Rose Gold', 'Blue', 'Red', 'Green', 'Yellow',
            'White', 'Black', 'Gray', 'Pink', 'Purple', 'Orange', 'Brown', 'Cyan', 'Magenta',
            'Midnight', 'Starlight', 'Product Red', 'Alpine Green', 'Sierra Blue', 'Pacific Blue'
        ]
    ),
    "balance": create_field_config(
        "balance",
        [
            r'balance\s+of\s+(\$?\s*[\d{1,3}(?:,\d{3})*(?:\.\d+)?]+)',
            r'(\$?\s*[\d{1,3}(?:,\d{3})*(?:\.\d+)?]+)',
            r'amount\s+(\$?\s*[\d{1,3}(?:,\d{3})*(?:\.\d+)?]+)'
        ]
    ),
    # Configuraciones para seguros
    "policy_number": create_field_config(
        "policy_number",
        [
            r'policy\s+#?([A-Z0-9-]+)',
            r'#([A-Z0-9-]+)',
            r'policy\s+([A-Z0-9-]+)',
            r'([A-Z0-9-]+)'
        ]
    ),
    "premium": create_field_config(
        "premium",
        [
            r'premium\s+of\s+(\$\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(\$\d+(?:,\d{3})*(?:\.\d{2})?)\s+per\s+month',
            r'costs?\s+(\$\d+(?:,\d{3})*(?:\.\d{2})?)\s+monthly',
            r'(\$\d+(?:,\d{3})*(?:\.\d{2})?)\s+monthly'
        ]
    ),
    "coverage_type": create_field_config(
        "coverage_type",
        [
            r'(auto\s+insurance)',
            r'(car\s+insurance)',
            r'(automobile\s+insurance)',
            r'(vehicle\s+insurance)'
        ]
    ),
    "liability_limit": create_field_config(
        "liability_limit",
        [
            r'liability\s+up\s+to\s+(\$\d+(?:,\d{3})*)',
            r'liability\s+(\$\d+(?:,\d{3})*)',
            r'(\$\d+(?:,\d{3})*)\s+liability'
        ]
    ),
    "expiry_date": create_field_config(
        "expiry_date",
        [
            r'expires?\s+on\s+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
            r'valid\s+until\s+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
            r'expiry\s+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
            r'([A-Za-z]+\s+\d{1,2},?\s+\d{4})'
        ]
    ),
    # Configuraciones para motocicletas
    "motorcycle_model": create_field_config(
        "motorcycle_model",
        [
            r'(Honda\s+[A-Z0-9\s]+)',
            r'(Yamaha\s+[A-Z0-9\s]+)',
            r'(Kawasaki\s+[A-Z0-9\s]+)',
            r'(Suzuki\s+[A-Z0-9\s]+)',
            r'(Ducati\s+[A-Z0-9\s]+)',
            r'(BMW\s+[A-Z0-9\s]+)',
            r'([A-Z][a-zA-Z0-9\s]+(?:\s+\d+)?(?:\s+[A-Z]+)?)'
        ]
    ),
    "mileage": create_field_config(
        "mileage",
        [
            r'(\d+)\s+miles?\s+on\s+the\s+odometer',
            r'odometer\s+shows\s+(\d+)',
            r'(\d+)\s+miles?\s+on\s+the\s+clock',
            r'(\d+)\s+miles?'
        ]
    ),
    "warranty": create_field_config(
        "warranty",
        [
            r'(\d+)-month\s+warranty',
            r'(\d+)\s+month\s+warranty',
            r'warranty\s+(\d+)\s+months?'
        ]
    ),
    "condition": create_field_config(
        "condition",
        [
            r'in\s+([a-zA-Z]+)\s+condition',
            r'condition:\s+([a-zA-Z]+)',
            r'([a-zA-Z]+)\s+condition'
        ]
    )
}

# ============================================================================
# EXTRACTORES GENÉRICOS REUTILIZABLES
# ============================================================================

def extract_currency(text):
    """
    Extrae valores de moneda (ej: $1,234.56, $850.00)
    """
    import re
    if not isinstance(text, str):
        return None
    
    matches = re.findall(r'\$[\d,]+\.?\d*', text)
    if matches:
        # Retornar el primer match encontrado
        return matches[0]
    return None

def extract_currency_all(text):
    """
    Extrae todos los valores de moneda del texto
    """
    import re
    if not isinstance(text, str):
        return None
    
    matches = re.findall(r'\$[\d,]+\.?\d*', text)
    return matches if matches else None

def extract_usd_currency(text):
    """
    Extrae valores USD específicamente (ej: USD 27, USD 850, dolares 100)
    """
    import re
    if not isinstance(text, str):
        return None
    
    # Patrones para USD
    patterns = [
        r'USD\s*(\d+(?:,\d{3})*)',
        r'dolares?\s*(\d+(?:,\d{3})*)',
        r'dolar\s*(\d+(?:,\d{3})*)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return f"${match.group(1)}"
    
    return None

def extract_percentage(text):
    """
    Extrae porcentajes (ej: 12.34%, 85%)
    """
    import re
    if not isinstance(text, str):
        return None
    
    match = re.search(r'(\d+(?:\.\d+)?)%', text)
    if match:
        return f"{match.group(1)}%"
    return None

def extract_date(text):
    """
    Extrae fechas en formato DD/MM/YYYY o D/M/YYYY
    """
    import re
    if not isinstance(text, str):
        return None
    
    patterns = [
        r'(\d{1,2}/\d{1,2}/\d{4})',
        r'(\d{1,2}-\d{1,2}-\d{4})',
        r'([A-Za-z]+\s+\d{1,2},\s+\d{4})'  # December 31, 2024
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None

def extract_categorical(text, patterns):
    """
    Extrae valores categóricos basado en patrones de sinónimos
    
    Args:
        text: Texto a analizar
        patterns: Diccionario {valor_esperado: [sinonimos]}
    
    Returns:
        str: El valor esperado si encuentra algún sinónimo, None si no
    """
    if not isinstance(text, str) or not isinstance(patterns, dict):
        return None
    
    text_lower = text.lower()
    
    # Buscar coincidencias exactas primero (más específicas)
    for expected_value, synonyms in patterns.items():
        for synonym in synonyms:
            synonym_lower = synonym.lower()
            # Buscar coincidencias exactas de palabras
            if f" {synonym_lower} " in f" {text_lower} " or text_lower.startswith(synonym_lower + " ") or text_lower.endswith(" " + synonym_lower):
                return expected_value
    
    # Si no hay coincidencias exactas, buscar substrings
    for expected_value, synonyms in patterns.items():
        for synonym in synonyms:
            if synonym.lower() in text_lower:
                return expected_value
    
    return None

def extract_regex(text, pattern):
    """
    Extrae valores usando un patrón regex personalizado
    
    Args:
        text: Texto a analizar
        pattern: Patrón regex con grupo de captura
    
    Returns:
        str: Primer match encontrado, None si no hay match
    """
    import re
    if not isinstance(text, str):
        return None
    
    match = re.search(pattern, text)
    if match:
        return match.group(1) if match.groups() else match.group(0)
    return None

def extract_number(text):
    """
    Extrae números generales (enteros o decimales)
    """
    import re
    if not isinstance(text, str):
        return None
    
    matches = re.findall(r'\d+(?:\.\d+)?', text)
    if matches:
        return matches[0]
    return None

def extract_hours(text):
    """
    Extrae valores de horas (ej: 3 horas, 12 hours)
    """
    import re
    if not isinstance(text, str):
        return None
    
    patterns = [
        r'(\d+)\s+horas?',
        r'(\d+)\s+hours?',
        r'(\d+)\s+h'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

# Diccionario de extractores genéricos
GENERIC_EXTRACTORS = {
    'currency': extract_currency,
    'currency_all': extract_currency_all,
    'usd_currency': extract_usd_currency,
    'percentage': extract_percentage,
    'date': extract_date,
    'categorical': extract_categorical,
    'regex': extract_regex,
    'number': extract_number,
    'hours': extract_hours
}

def create_field_config_with_extractor(field_name, extractor_name, expected_value=None, patterns=None, normalize_func=None, validation_func=None):
    """
    Crea configuración de campo usando extractores genéricos
    
    Args:
        field_name: Nombre del campo
        extractor_name: Nombre del extractor genérico a usar
        expected_value: Valor esperado (opcional)
        patterns: Patrones específicos para extractores que los requieren (categorical, regex)
        normalize_func: Función de normalización (opcional)
        validation_func: Función de validación (opcional)
    
    Returns:
        dict: Configuración del campo con extractor genérico
    """
    if extractor_name not in GENERIC_EXTRACTORS:
        raise ValueError(f"Extractor '{extractor_name}' no encontrado. Extractores disponibles: {list(GENERIC_EXTRACTORS.keys())}")
    
    config = {
        "name": field_name,
        "extractor": extractor_name,
        "expected": expected_value,
        "patterns": patterns,
        "validation": validation_func
    }
    
    # Solo agregar normalize si se proporciona una función
    if normalize_func and callable(normalize_func):
        config["normalize"] = normalize_func
    
    return config

def extract_value_with_generic_extractor(text, field_config):
    """
    Extrae valor usando extractores genéricos
    
    Args:
        text: Texto a analizar
        field_config: Configuración del campo con extractor genérico
    
    Returns:
        Valor extraído o None
    """
    if 'extractor' not in field_config:
        return None
    
    extractor_name = field_config['extractor']
    if extractor_name not in GENERIC_EXTRACTORS:
        return None
    
    extractor_func = GENERIC_EXTRACTORS[extractor_name]
    
    # Manejar extractores que requieren parámetros adicionales
    if extractor_name in ['categorical', 'regex']:
        patterns = field_config.get('patterns')
        if not patterns:
            return None
        return extractor_func(text, patterns)
    else:
        return extractor_func(text)