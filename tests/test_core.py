#!/usr/bin/env python3
"""
Tests for the core validation functionality using the new API
"""

from true_lies import create_scenario, validate_against_reference_dynamic, extract_fact

def test_create_scenario():
    """Test scenario creation"""
    scenario = create_scenario(
        facts={
            'price': {'extractor': 'money', 'expected': '299.99'},
            'color': {
                'extractor': 'categorical', 
                'expected': 'red',
                'patterns': {
                    'red': ['red', 'crimson', 'scarlet'],
                    'blue': ['blue', 'navy', 'azure']
                }
            },
            'size': {
                'extractor': 'categorical', 
                'expected': 'L',
                'patterns': {
                    'L': ['L', 'large', 'Large'],
                    'M': ['M', 'medium', 'Medium'],
                    'S': ['S', 'small', 'Small']
                }
            }
        },
        semantic_reference='Product with price $299.99, color red, size L',
        semantic_mappings={
            'product': ['item', 'article'],
            'price': ['cost', 'amount']
        }
    )
    
    assert 'facts' in scenario
    assert 'semantic_reference' in scenario
    assert 'semantic_mappings' in scenario
    assert scenario['facts']['price']['expected'] == '299.99'

def test_validate_against_reference_dynamic_pass():
    """Test validation with matching facts"""
    scenario = create_scenario(
        facts={
            'price': {'extractor': 'money', 'expected': '299.99'},
            'color': {
                'extractor': 'categorical', 
                'expected': 'red',
                'patterns': {
                    'red': ['red', 'crimson', 'scarlet'],
                    'blue': ['blue', 'navy', 'azure']
                }
            },
            'size': {
                'extractor': 'categorical', 
                'expected': 'L',
                'patterns': {
                    'L': ['L', 'large', 'Large'],
                    'M': ['M', 'medium', 'Medium'],
                    'S': ['S', 'small', 'Small']
                }
            }
        },
        semantic_reference='Product with price $299.99, color red, size L',
        semantic_mappings={
            'product': ['item', 'article'],
            'price': ['cost', 'amount']
        }
    )
    
    candidate = "This item costs $299.99, comes in red color and size L"
    result = validate_against_reference_dynamic(candidate, scenario, similarity_threshold=0.7)
    
    assert result['factual_accuracy'] is True
    assert result['similarity_score'] > 0.7
    assert result['is_valid'] is True

def test_validate_against_reference_dynamic_fail():
    """Test validation with mismatching facts"""
    scenario = create_scenario(
        facts={
            'price': {'extractor': 'money', 'expected': '299.99'},
            'color': {
                'extractor': 'categorical', 
                'expected': 'red',
                'patterns': {
                    'red': ['red', 'crimson', 'scarlet'],
                    'blue': ['blue', 'navy', 'azure']
                }
            },
            'size': {
                'extractor': 'categorical', 
                'expected': 'L',
                'patterns': {
                    'L': ['L', 'large', 'Large'],
                    'M': ['M', 'medium', 'Medium'],
                    'S': ['S', 'small', 'Small']
                }
            }
        },
        semantic_reference='Product with price $299.99, color red, size L',
        semantic_mappings={
            'product': ['item', 'article'],
            'price': ['cost', 'amount']
        }
    )
    
    candidate = "This item costs $199.99, comes in blue color and size M"
    result = validate_against_reference_dynamic(candidate, scenario, similarity_threshold=0.7)
    
    assert result['factual_accuracy'] is False
    assert result['is_valid'] is False

def test_extract_fact_money():
    """Test money extraction"""
    config = {'extractor': 'money', 'expected': '299.99'}
    text = "The price is $299.99"
    result = extract_fact(text, config)
    assert result == '299.99'

def test_extract_fact_categorical():
    """Test categorical extraction"""
    config = {
        'extractor': 'categorical', 
        'expected': 'red',
        'patterns': {
            'red': ['red', 'crimson', 'scarlet'],
            'blue': ['blue', 'navy', 'azure']
        }
    }
    text = "The color is red"
    result = extract_fact(text, config)
    assert result == 'red'

def test_extract_fact_number():
    """Test number extraction"""
    config = {'extractor': 'number', 'expected': '25'}
    text = "There are 25 items"
    result = extract_fact(text, config)
    assert result == '25'

def test_extract_fact_email():
    """Test email extraction"""
    config = {'extractor': 'email', 'expected': 'test@example.com'}
    text = "Contact us at test@example.com"
    result = extract_fact(text, config)
    assert result == 'test@example.com'

def test_bank_scenario():
    """Test banking scenario"""
    scenario = create_scenario(
        facts={
            'account_balance': {'extractor': 'money', 'expected': '1500.00'},
            'account_type': {
                'extractor': 'categorical', 
                'expected': 'savings',
                'patterns': {
                    'savings': ['savings', 'ahorro', 'ahorros'],
                    'checking': ['checking', 'corriente', 'corrientes']
                }
            }
        },
        semantic_reference='Your savings account has a balance of $1500.00',
        semantic_mappings={
            'account': ['cuenta'],
            'balance': ['saldo', 'monto'],
            'savings': ['ahorro']
        }
    )
    
    candidate = "Su cuenta de ahorro tiene un saldo de $1500.00"
    result = validate_against_reference_dynamic(candidate, scenario, similarity_threshold=0.6)
    
    assert result['factual_accuracy'] is True
    assert result['similarity_score'] > 0.5

def test_energy_scenario():
    """Test energy scenario"""
    scenario = create_scenario(
        facts={
            'consumption': {'extractor': 'number', 'expected': '250'},
            'unit': {
                'extractor': 'categorical', 
                'expected': 'kWh',
                'patterns': {
                    'kWh': ['kWh', 'kilowatt', 'kilowatts'],
                    'W': ['W', 'watt', 'watts']
                }
            }
        },
        semantic_reference='Energy consumption is 250 kWh',
        semantic_mappings={
            'energy': ['energia', 'electricidad'],
            'consumption': ['consumo', 'gasto']
        }
    )
    
    candidate = "El consumo de energia es 250 kWh"
    result = validate_against_reference_dynamic(candidate, scenario, similarity_threshold=0.6)
    
    assert result['factual_accuracy'] is True
    assert result['similarity_score'] > 0.6

def test_retail_scenario():
    """Test retail scenario"""
    scenario = create_scenario(
        facts={
            'product_name': {
                'extractor': 'categorical', 
                'expected': 'laptop',
                'patterns': {
                    'laptop': ['laptop', 'portatil', 'computadora'],
                    'desktop': ['desktop', 'escritorio', 'computadora de escritorio']
                }
            },
            'price': {'extractor': 'money', 'expected': '999.99'}
        },
        semantic_reference='Laptop on sale for $999.99',
        semantic_mappings={
            'laptop': ['portatil', 'computadora'],
            'sale': ['oferta', 'rebaja']
        }
    )
    
    candidate = "Portatil en oferta por $999.99"
    result = validate_against_reference_dynamic(candidate, scenario, similarity_threshold=0.6)
    
    assert result['factual_accuracy'] is True
    assert result['similarity_score'] > 0.6