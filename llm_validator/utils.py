def extract_balance(text):
    return []

def extract_account_type(text):
    return None

def normalize_extracted_value(value, key):
    import re
    key = key.lower()
    if value is None:
        return None

    if "price" in key or "balance" in key:
        # Mantener solo dígitos y punto
        cleaned = re.sub(r"[^0-9\.]", "", value)
    elif "consumption" in key:
        # Para consumo, extraer solo el número
        cleaned = re.sub(r"[^0-9\.]", "", value)
    elif "size" in key:
        # Mantener letras y números, normalizar a minúsculas
        cleaned = re.sub(r"[^a-z0-9]", "", value.lower())
    elif "color" in key:
        # Mantener solo letras, normalizar a minúsculas
        cleaned = re.sub(r"[^a-z]", "", value.lower())
    else:
        # Limpieza genérica: quitar puntuación
        cleaned = re.sub(r"[^\w\s]", "", value).strip()

    return cleaned


def extract_value_from_text(text, key, normalize_for_comparison=True):
    """
    Extrae un valor aproximado asociado a la clave `key` desde el texto.
    normalize_for_comparison: si True, devuelve el valor normalizado listo para comparación.
    """
    import re

    # Normalizamos el texto
    text_lower = text.lower()
    key_lower = key.lower()

    # Patrones básicos: "key: value" o "key is value"
    patterns = [
        rf"{re.escape(key_lower)}\s*:\s*([^,;]+)",
        rf"{re.escape(key_lower)}\s+is\s+([^,;]+)",
        rf"{re.escape(key_lower)}\s+equals\s+([^,;]+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            raw_value = match.group(1).strip()
            if normalize_for_comparison:
                return normalize_extracted_value(raw_value, key)
            else:
                return raw_value

    return None

import json
from pathlib import Path

def load_semantic_mapping(domain):
    """
    Carga el diccionario de sinónimos para el dominio dado desde un JSON.
    Devuelve un dict vacío si no se encuentra el archivo.
    """
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