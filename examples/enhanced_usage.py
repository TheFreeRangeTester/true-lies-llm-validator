tos #!/usr/bin/env python3
"""
Enhanced usage example showing the improved LLM Validator API
"""

from llm_validator.runner import validate_llm_response

def example_insurance_validation():
    """Example: Insurance policy validation with semantic mapping"""
    
    # 1. FACTS - The values that MUST be present in the candidate
    facts = {
        "policy_number": "POL-2024-001",
        "premium": "$850.00",
        "coverage_type": "auto insurance",
        "liability_limit": "$100,000",
        "expiry_date": "December 31, 2024"
    }
     
    # 2. REFERENCE TEXT - Used for semantic similarity comparison
    reference_text = "Your auto insurance policy #POL-2024-001 has a premium of $850.00 per month. The coverage includes liability up to $100,000 and comprehensive protection. Your policy expires on December 31, 2024."
    
    # 3. SEMANTIC MAPPING - Synonyms that expand the facts for validation
    semantic_mapping = {
        "auto insurance": ["car insurance", "automobile insurance", "vehicle insurance"],
        "liability": ["liability coverage", "liability protection", "third party coverage"],
        "comprehensive": ["comprehensive coverage", "full coverage", "complete protection"],
        "premium": ["monthly payment", "monthly cost", "payment amount"],
        "policy": ["insurance policy", "coverage policy", "insurance plan"]
    }
    
    # 4. CANDIDATES - LLM responses to validate
    candidates = [
        "Policy POL-2024-001 covers your automobile with monthly payments of $850.00. You're protected with $100,000 liability coverage plus comprehensive insurance. This policy is valid until December 31, 2024.",
        "Your car insurance policy POL-2024-001 costs $850 monthly. It provides $100,000 liability protection and comprehensive coverage. Expires on December 31, 2024.",
        "Auto policy #POL-2024-001 has a $850.00 monthly premium with $100,000 liability and comprehensive coverage. Valid until December 31, 2024."
    ]
    
    print("🚗 INSURANCE POLICY VALIDATION EXAMPLE")
    print("=" * 60)
    
    # 5. RUN VALIDATION with enhanced API
    results = validate_llm_response(
        facts=facts,
        reference_text=reference_text,
        candidates=candidates,
        semantic_mapping=semantic_mapping,
        threshold=0.7
    )
    
    return results

def example_motorcycle_validation():
    """Example: Motorcycle inventory validation with domain-based mapping"""
    
    # 1. FACTS
    facts = {
        "motorcycle_model": "Honda CBR 600RR",
        "price": "$12,500",
        "mileage": "1500",
        "warranty": "6-month",
        "condition": "excellent"
    }
    
    # 2. REFERENCE TEXT
    reference_text = "The Honda CBR 600RR is available for $12,500. It has 1500 miles on the odometer and comes with a 6-month warranty. The bike is in excellent condition."
    
    # 3. CANDIDATES
    candidates = [
        "The Honda CBR 600RR is available for $12,500. It has 1500 miles on the odometer and comes with a 6-month warranty. The bike is in excellent condition.",
        "Honda CBR 600RR motorcycle priced at $12,500. Odometer shows 1500 miles. Includes 6-month warranty. Condition: excellent.",
        "Available: Honda CBR 600RR for $12,500. 1500 miles on the clock. 6-month warranty included. Excellent condition."
    ]
    
    print("\n🏍️ MOTORCYCLE INVENTORY VALIDATION EXAMPLE")
    print("=" * 60)
    
    # 4. RUN VALIDATION using domain-based mapping
    results = validate_llm_response(
        facts=facts,
        reference_text=reference_text,
        candidates=candidates,
        domain="motorcycle_dealership",  # Uses semantic_data/motorcycle_dealership.json
        threshold=0.7
    )
    
    return results

def example_retail_validation():
    """Example: Retail product validation with custom field configs"""
    
    # 1. FACTS
    facts = {
        "product_name": "iPhone 15 Pro",
        "stock": "25",
        "price": "$999.99",
        "color": "Space Black"
    }
    
    # 2. REFERENCE TEXT
    reference_text = "The iPhone 15 Pro is currently in stock with 25 units available. The price is $999.99 and it comes in Space Black color."
    
    # 3. CUSTOM FIELD CONFIGURATIONS
    field_configs = {
        "stock": {
            "name": "stock",
            "patterns": [
                r'(\d+)\s+units?\s+available',
                r'in\s+stock\s+with\s+(\d+)',
                r'(\d+)\s+units?\s+in\s+stock',
                r'we\s+have\s+(\d+)\s+units?'
            ]
        }
    }
    
    # 4. CANDIDATES
    candidates = [
        "The iPhone 15 Pro is currently in stock with 25 units available. The price is $999.99 and it comes in Space Black color.",
        "iPhone 15 Pro available: 25 units in stock. Price: $999.99. Color: Space Black.",
        "We have 25 iPhone 15 Pro units in Space Black color available for $999.99 each."
    ]
    
    print("\n📱 RETAIL PRODUCT VALIDATION EXAMPLE")
    print("=" * 60)
    
    # 5. RUN VALIDATION with custom field configs
    results = validate_llm_response(
        facts=facts,
        reference_text=reference_text,
        candidates=candidates,
        domain="retail",
        field_configs=field_configs,
        threshold=0.7
    )
    
    return results

def example_advanced_usage():
    """Example: Advanced usage with custom semantic mapping and analysis"""
    
    # 1. FACTS for a banking scenario
    facts = {
        "account_type": "savings account",
        "balance": "$5,250.75",
        "interest_rate": "2.5%",
        "account_number": "1234-5678-9012"
    }
    
    # 2. REFERENCE TEXT
    reference_text = "Your savings account #1234-5678-9012 has a current balance of $5,250.75 and earns 2.5% annual interest."
    
    # 3. ADVANCED SEMANTIC MAPPING
    semantic_mapping = {
        "savings account": ["savings", "deposit account", "savings deposit"],
        "balance": ["current balance", "account balance", "available balance"],
        "interest": ["interest rate", "annual interest", "yield", "earnings"],
        "account": ["account number", "account #", "acct"]
    }
    
    # 4. CANDIDATES
    candidates = [
        "Your savings account #1234-5678-9012 has a current balance of $5,250.75 and earns 2.5% annual interest.",
        "Account 1234-5678-9012 is a savings deposit with $5,250.75 balance. Interest rate: 2.5%.",
        "Savings account 1234-5678-9012: Balance $5,250.75, Annual yield 2.5%."
    ]
    
    print("\n🏦 ADVANCED BANKING VALIDATION EXAMPLE")
    print("=" * 60)
    
    # 5. RUN VALIDATION with advanced settings
    results = validate_llm_response(
        facts=facts,
        reference_text=reference_text,
        candidates=candidates,
        semantic_mapping=semantic_mapping,
        threshold=0.6,  # Lower threshold for more flexible matching
        domain="banking"  # Also load domain-specific mappings
    )
    
    # 6. ANALYZE RESULTS
    print("\n📊 ADVANCED ANALYSIS:")
    for i, result in enumerate(results["results"], 1):
        print(f"\nCandidate {i} Analysis:")
        print(f"  Factual Accuracy: {result['factual']['is_valid']}")
        print(f"  Semantic Score: {result['semantic']['similarity_score']:.3f}")
        print(f"  Semantic Boost: {result['semantic']['semantic_boost']:.3f}")
        print(f"  Key Tokens Found: {result['semantic']['key_tokens_count']}")
        print(f"  Overlap Count: {result['semantic']['overlap_count']}")
    
    return results

if __name__ == "__main__":
    print("🎯 LLM VALIDATOR - ENHANCED USAGE EXAMPLES")
    print("=" * 60)
    
    # Run all examples
    insurance_results = example_insurance_validation()
    motorcycle_results = example_motorcycle_validation()
    retail_results = example_retail_validation()
    advanced_results = example_advanced_usage()
    
    print("\n🎉 ALL EXAMPLES COMPLETED!")
    print("=" * 60)
    print("Key improvements in this enhanced API:")
    print("✅ Simplified function call with facts, reference_text, and candidates")
    print("✅ Facts parameter for clarity (instead of reference_values)")
    print("✅ Semantic mapping that expands facts with synonyms")
    print("✅ Domain-based mapping loading")
    print("✅ Custom field configurations")
    print("✅ Enhanced semantic scoring with boost")
    print("✅ Better result formatting and analysis")
