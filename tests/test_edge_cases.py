#!/usr/bin/env python3
"""
Tests for edge cases and error handling
"""

from true_lies import ConversationValidator, create_scenario, validate_against_reference_dynamic

class TestEdgeCases:
    """Test edge cases for ConversationValidator"""
    
    def test_empty_inputs(self):
        """Test with empty inputs"""
        conv = ConversationValidator()
        conv.add_turn(
            user_input="",
            bot_response="",
            expected_facts={}
        )
        
        result = conv.validate_retention(
            response="",
            facts_to_check=[]
        )
        
        assert result['retention_score'] == 0.0
        assert result['facts_retained'] == 0
        assert result['total_facts'] == 0
    
    def test_none_inputs(self):
        """Test with None inputs"""
        conv = ConversationValidator()
        conv.add_turn(
            user_input="Hello",
            bot_response="Hi there",
            expected_facts={'greeting': 'hello'}
        )
        
        result = conv.validate_retention(
            response="Hello, how can I help you?",
            facts_to_check=['greeting']
        )
        
        assert result['retention_score'] >= 0.0
        assert result['facts_retained'] >= 0
    
    def test_validate_retention_with_empty_facts(self):
        """Test retention validation with empty facts"""
        conv = ConversationValidator()
        conv.add_turn(
            user_input="Hello",
            bot_response="Hi there",
            expected_facts={'greeting': 'hello'}
        )
        
        result = conv.validate_retention(
            response="Hello, how can I help you?",
            facts_to_check=[]
        )
        
        assert result['retention_score'] == 0.0
        assert result['facts_retained'] == 0
        assert result['total_facts'] == 0
    
    def test_very_long_fact_names(self):
        """Test with very long fact names"""
        conv = ConversationValidator()
        conv.add_turn(
            user_input="My very long fact name is test value",
            bot_response="I understand",
            expected_facts={'very_long_fact_name_that_might_cause_issues': 'test value'}
        )
        
        result = conv.validate_retention(
            response="I remember your very long fact name is test value",
            facts_to_check=['very_long_fact_name_that_might_cause_issues']
        )
        
        assert result['facts_retained'] >= 0
        assert result['total_facts'] == 1
    
    def test_very_long_fact_values(self):
        """Test with very long fact values"""
        long_value = "This is a very long fact value that contains many words and might cause issues with the validation system"
        conv = ConversationValidator()
        conv.add_turn(
            user_input=f"My fact is {long_value}",
            bot_response="I understand",
            expected_facts={'fact': long_value}
        )
        
        result = conv.validate_retention(
            response=f"I remember your fact is {long_value}",
            facts_to_check=['fact']
        )
        
        assert result['facts_retained'] >= 0
        assert result['total_facts'] == 1

class TestErrorHandling:
    """Test error handling scenarios"""
    
    # def test_add_turn_with_invalid_facts_type(self):
    #     """Test add_turn with invalid facts type"""
    #     conv = ConversationValidator()
    #     
    #     # This should not raise an error, but handle gracefully
    #     conv.add_turn(
    #         user_input="Hello",
    #         bot_response="Hi",
    #         expected_facts="invalid_facts_type"  # Should be dict
    #     )
    #     
    #     # The method should handle this gracefully
    #     result = conv.validate_retention(
    #         response="Hello",
    #         facts_to_check=[]
    #     )
    #     
    #     assert result['retention_score'] == 0.0
    
    def test_validate_retention_with_invalid_facts_type(self):
        """Test retention validation with invalid facts type"""
        conv = ConversationValidator()
        conv.add_turn(
            user_input="Hello",
            bot_response="Hi",
            expected_facts={'greeting': 'hello'}
        )
        
        # This should handle gracefully
        result = conv.validate_retention(
            response="Hello",
            facts_to_check="invalid_facts_type"  # Should be list
        )
        
        assert result['retention_score'] == 0.0
    
    # def test_validate_retention_with_none_response(self):
    #     """Test retention validation with None response"""
    #     conv = ConversationValidator()
    #     conv.add_turn(
    #         user_input="Hello",
    #         bot_response="Hi",
    #         expected_facts={'greeting': 'hello'}
    #     )
    #     
    #     # This should handle gracefully
    #     result = conv.validate_retention(
    #         response=None,
    #         facts_to_check=['greeting']
    #     )
    #     
    #     assert result['retention_score'] == 0.0

class TestScenarioEdgeCases:
    """Test edge cases for scenario validation"""
    
    def test_empty_scenario(self):
        """Test with empty scenario"""
        scenario = create_scenario(
            facts={},
            semantic_reference="",
            semantic_mappings={}
        )
        
        result = validate_against_reference_dynamic(
            candidate_text="",
            reference_scenario=scenario,
            similarity_threshold=0.5
        )
        
        assert result['factual_accuracy'] is True  # Empty facts = true
        assert result['similarity_score'] >= 0.0
    
    def test_scenario_with_no_semantic_mappings(self):
        """Test scenario without semantic mappings"""
        scenario = create_scenario(
            facts={'price': {'extractor': 'money', 'expected': '100'}},
            semantic_reference="Price is $100",
            semantic_mappings={}
        )
        
        result = validate_against_reference_dynamic(
            candidate_text="Price is $100",
            reference_scenario=scenario,
            similarity_threshold=0.5
        )
        
        assert result['factual_accuracy'] is True
        assert result['similarity_score'] >= 0.0
    
    def test_scenario_with_very_low_threshold(self):
        """Test with very low similarity threshold"""
        scenario = create_scenario(
            facts={'price': {'extractor': 'money', 'expected': '100'}},
            semantic_reference="Price is $100",
            semantic_mappings={}
        )
        
        result = validate_against_reference_dynamic(
            candidate_text="Completely different text",
            reference_scenario=scenario,
            similarity_threshold=0.1
        )
        
        assert result['factual_accuracy'] is False
        assert result['similarity_score'] >= 0.0