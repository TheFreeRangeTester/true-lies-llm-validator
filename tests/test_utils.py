from true_lies import utils

def test_extract_email():
    """Test de extracción de emails."""
    result = utils.extract_email("Contact me at john@example.com")
    assert result == "john@example.com"
    
    result = utils.extract_email("No email here")
    assert result is None

def test_extract_phone():
    """Test de extracción de teléfonos."""
    result = utils.extract_phone("Call me at (555) 123-4567")
    assert result == "(555) 123-4567"
    
    result = utils.extract_phone("No phone here")
    assert result is None

def test_extract_fact():
    """Test de extracción de facts genéricos."""
    # Test extractor de dinero
    fact_config = {'extractor': 'money', 'expected': '$1,234.56'}
    result = utils.extract_fact("The price is $1,234.56", fact_config)
    assert result == "$1,234.56"
    
    # Test extractor de email
    fact_config = {'extractor': 'email', 'expected': 'test@example.com'}
    result = utils.extract_fact("Email: test@example.com", fact_config)
    assert result == "test@example.com"
    
    # Test extractor de número
    fact_config = {'extractor': 'number', 'expected': '25'}
    result = utils.extract_fact("The count is 25", fact_config)
    assert result == "25"
    
    # Test con extractor inválido
    fact_config = {'extractor': 'invalid', 'expected': 'test'}
    result = utils.extract_fact("Test text", fact_config)
    assert result is None
    
    # Test sin extractor en config
    fact_config = {'expected': 'test'}
    result = utils.extract_fact("Test text", fact_config)
    assert result is None