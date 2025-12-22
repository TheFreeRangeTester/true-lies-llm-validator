#!/usr/bin/env python3
"""
Patrones de Polaridad Universales
================================

Patrones de polaridad para detectar sentimientos en el texto.
"""

# Patrones de polaridad universales
POLARITY_PATTERNS = {
    'positive': [
        # Inglés
        'approved', 'accepted', 'successful', 'completed', 'confirmed', 'active', 
        'available', 'good', 'excellent', 'high', 'great', 'perfect', 'valid',
        'working', 'ready', 'done', 'finished', 'passed', 'won', 'gained',
        # Español
        'tenemos', 'ofrecemos', 'confirmado', 'confirmada', 'aprobado', 'aprobada',
        'exitoso', 'exitosa', 'completado', 'completada', 'activo', 'activa',
        'disponible', 'bueno', 'buena', 'excelente', 'alto', 'alta', 'perfecto',
        'perfecta', 'válido', 'válida', 'funcionando', 'listo', 'lista', 'terminado',
        'terminada', 'aprobado', 'aprobada', 'ganado', 'ganada'
    ],
    'negative': [
        # Inglés
        'denied', 'rejected', 'failed', 'cancelled', 'declined', 'inactive', 
        'unavailable', 'bad', 'poor', 'low', 'no', 'error', 'invalid', 'broken',
        'lost', 'missing', 'wrong', 'incorrect', 'blocked', 'stopped', 'ended',
        'not', 'does not', 'do not', 'will not', 'cannot', 'can not', 'should not',
        'would not', 'could not', 'did not', 'doesn\'t', 'don\'t', 'won\'t', 'can\'t',
        'shouldn\'t', 'wouldn\'t', 'couldn\'t', 'didn\'t', 'isn\'t', 'aren\'t',
        'wasn\'t', 'weren\'t', 'hasn\'t', 'haven\'t', 'hadn\'t',
        # Español
        'rechazado', 'rechazada', 'fallido', 'fallida', 'cancelado', 'cancelada',
        'negado', 'negada', 'inactivo', 'inactiva', 'no disponible', 'malo', 'mala',
        'bajo', 'baja', 'no', 'error', 'inválido', 'inválida', 'roto', 'rota',
        'perdido', 'perdida', 'faltante', 'incorrecto', 'incorrecta', 'bloqueado',
        'bloqueada', 'detenido', 'detenida', 'terminado', 'terminada', 'falló', 'fallo',
        'no es', 'no está', 'no tiene', 'no puede', 'no debe', 'no debería',
        'no funciona', 'no trabaja', 'no sirve', 'no vale', 'no es válido'
    ],
    'neutral': [
        # Inglés
        'pending', 'processing', 'under review', 'waiting', 'scheduled', 
        'normal', 'standard', 'regular', 'average', 'medium', 'in progress',
        'ongoing', 'current', 'present', 'existing', 'status', 'state',
        # Español
        'pendiente', 'procesando', 'en revisión', 'esperando', 'programado',
        'programada', 'normal', 'estándar', 'regular', 'promedio', 'medio',
        'media', 'en progreso', 'en curso', 'actual', 'presente', 'existente',
        'estado', 'situación'
    ]
}

def detect_polarity(text):
    """
    Detecta la polaridad del texto basado en patrones predefinidos.
    
    Args:
        text: Texto a analizar
    
    Returns:
        str: 'positive', 'negative', o 'neutral'
    """
    import re
    
    if not isinstance(text, str):
        return 'neutral'
    
    text_lower = text.lower()
    
    # Primero buscar frases de múltiples palabras y contracciones (más específicas)
    # Esto incluye patrones como "does not", "do not", "won't", "don't", etc.
    multi_word_patterns = [p for p in POLARITY_PATTERNS['negative'] if ' ' in p or "'" in p]
    for pattern in multi_word_patterns:
        # Escapar caracteres especiales para regex
        pattern_escaped = re.escape(pattern)
        if re.search(r'\b' + pattern_escaped + r'\b', text_lower):
            return 'negative'
    
    multi_word_patterns = [p for p in POLARITY_PATTERNS['positive'] if ' ' in p or "'" in p]
    for pattern in multi_word_patterns:
        pattern_escaped = re.escape(pattern)
        if re.search(r'\b' + pattern_escaped + r'\b', text_lower):
            return 'positive'
    
    multi_word_patterns = [p for p in POLARITY_PATTERNS['neutral'] if ' ' in p or "'" in p]
    for pattern in multi_word_patterns:
        pattern_escaped = re.escape(pattern)
        if re.search(r'\b' + pattern_escaped + r'\b', text_lower):
            return 'neutral'
    
    # Luego buscar palabras individuales (incluyendo contracciones como parte de palabras)
    # Usar un patrón que incluya apóstrofes para capturar contracciones
    words = re.findall(r"\b[\w']+\b", text_lower)
    
    # Priorizar patrones negativos (más específicos) - usando palabras completas
    if any(word in POLARITY_PATTERNS['negative'] for word in words):
        return 'negative'
    
    # Luego positivos - usando palabras completas
    if any(word in POLARITY_PATTERNS['positive'] for word in words):
        return 'positive'
    
    # Finalmente neutrales - usando palabras completas
    if any(word in POLARITY_PATTERNS['neutral'] for word in words):
        return 'neutral'
    
    return 'neutral'
