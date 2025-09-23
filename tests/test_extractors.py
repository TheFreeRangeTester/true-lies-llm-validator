#!/usr/bin/env python3
"""
Tests for extractors functionality
"""

from true_lies import extract_fact

class TestExtractors:
    """Test various extractors"""
    
    def test_money_extractor(self):
        """Test money extraction"""
        config = {'extractor': 'money', 'expected': '299.99'}
        
        # Test with dollar sign
        result = extract_fact("The price is $299.99", config)
        assert result == '299.99'
        
        # Test with USD prefix
        result = extract_fact("Cost is USD 299.99", config)
        assert result == '299.99'
        
        # Test with dollars suffix
        result = extract_fact("Price is 299.99 dollars", config)
        assert result == '299.99'
    
    def test_number_extractor(self):
        """Test number extraction"""
        config = {'extractor': 'number', 'expected': '25'}
        
        result = extract_fact("There are 25 items", config)
        assert result == '25'
        
        result = extract_fact("Count: 25", config)
        assert result == '25'
        
        result = extract_fact("Number 25 is special", config)
        assert result == '25'
    
    def test_email_extractor(self):
        """Test email extraction"""
        config = {'extractor': 'email', 'expected': 'test@example.com'}
        
        result = extract_fact("Contact us at test@example.com", config)
        assert result == 'test@example.com'
        
        result = extract_fact("Email: test@example.com for support", config)
        assert result == 'test@example.com'
    
    def test_phone_extractor(self):
        """Test phone extraction"""
        config = {'extractor': 'phone', 'expected': '+1-555-123-4567'}
        
        result = extract_fact("Call us at +1-555-123-4567", config)
        assert result == '+1-555-123-4567'
        
        result = extract_fact("Phone: (555) 123-4567", config)
        assert result == '(555) 123-4567'
    
    # def test_id_extractor(self):
    #     """Test ID extraction"""
    #     config = {'extractor': 'id', 'expected': 'USER-001'}
    #     
    #     result = extract_fact("Your ID is USER-001", config)
    #     assert result == 'USER-001'
    #     
    #     result = extract_fact("ID: POL-2024-001", config)
    #     assert result == 'POL-2024-001'
    
    def test_categorical_extractor(self):
        """Test categorical extraction"""
        config = {
            'extractor': 'categorical',
            'expected': 'red',
            'patterns': {
                'red': ['red', 'crimson', 'scarlet'],
                'blue': ['blue', 'navy', 'azure'],
                'green': ['green', 'emerald', 'forest']
            }
        }
        
        result = extract_fact("The color is red", config)
        assert result == 'red'
        
        result = extract_fact("Color: crimson", config)
        assert result == 'red'
        
        result = extract_fact("The item is blue", config)
        assert result == 'blue'
    
    # def test_hours_extractor(self):
    #     """Test hours extraction"""
    #     config = {'extractor': 'hours', 'expected': '09:00'}
    #     
    #     result = extract_fact("Meeting at 09:00 AM", config)
    #     assert result == '09:00'
    #     
    #     result = extract_fact("Time: 14:30", config)
    #     assert result == '14:30'
    #     
    #     result = extract_fact("Start time is 3:00 PM", config)
    #     assert result == '15:00'
    
    def test_regex_extractor(self):
        """Test regex extraction"""
        config = {
            'extractor': 'regex',
            'expected': 'ABC123',
            'pattern': r'[A-Z]{3}\d{3}'
        }
        
        result = extract_fact("Code: ABC123", config)
        assert result == 'ABC123'
        
        result = extract_fact("Reference XYZ789", config)
        assert result == 'XYZ789'
    
    def test_extractor_not_found(self):
        """Test when extractor doesn't find anything"""
        config = {'extractor': 'money', 'expected': '299.99'}
        
        result = extract_fact("No money mentioned here", config)
        assert result is None
        
        result = extract_fact("", config)
        assert result is None
    
    # def test_extractor_partial_match(self):
    #     """Test partial matching"""
    #     config = {
    #         'extractor': 'categorical',
    #         'expected': 'red',
    #         'patterns': {
    #             'red': ['red', 'crimson', 'scarlet'],
    #             'blue': ['blue', 'navy', 'azure']
    #         }
    #     }
    #     
    #     result = extract_fact("The item is reddish", config)
    #     # Should not match "reddish" as it's not in the patterns
    #     assert result is None
    #     
    #     result = extract_fact("Color is red", config)
    #     assert result == 'red'
    
    def test_extractor_case_sensitivity(self):
        """Test case sensitivity"""
        config = {
            'extractor': 'categorical',
            'expected': 'red',
            'patterns': {
                'red': ['red', 'RED', 'Red'],
                'blue': ['blue', 'BLUE', 'Blue']
            }
        }
        
        result = extract_fact("The color is RED", config)
        assert result == 'red'
        
        result = extract_fact("Color: Red", config)
        assert result == 'red'
        
        result = extract_fact("The item is red", config)
        assert result == 'red'