#!/usr/bin/env python3
"""
Advanced Search Demo for HTML Reporter
=====================================

This example demonstrates the advanced search capabilities of the HTML Reporter,
including smart operators, keyword search, and real-time filtering.
"""

from datetime import datetime, timedelta
from true_lies import ConversationValidator, HTMLReporter

def create_search_demo_data():
    """Create diverse test data to demonstrate search capabilities."""
    results = []
    
    # Test cases with different characteristics for search demo
    test_cases = [
        {
            'name': 'Excellent Customer Service',
            'user_input': 'Hello, I am John Smith, email john@company.com, urgent request',
            'bot_response': 'Hello John Smith, I will prioritize your urgent request',
            'expected_facts': {'name': 'John Smith', 'email': 'john@company.com', 'urgency': 'urgent'},
            'final_response': 'John Smith, your urgent request has been resolved. Confirmation sent to john@company.com',
            'facts_check': ['name', 'email', 'urgency']
        },
        {
            'name': 'Good Technical Support',
            'user_input': 'Hi, I am Alice Johnson, email alice@tech.com, ID 12345, need help with software',
            'bot_response': 'Hello Alice, I will help you with your software issue',
            'expected_facts': {'name': 'Alice Johnson', 'email': 'alice@tech.com', 'id': '12345', 'issue': 'software'},
            'final_response': 'Alice Johnson (ID 12345), your software issue has been resolved. Contact alice@tech.com for details',
            'facts_check': ['name', 'email', 'id', 'issue']
        },
        {
            'name': 'Average Billing Inquiry',
            'user_input': 'Hello, I am Bob Wilson, email bob@billing.com, account 98765',
            'bot_response': 'Hello Bob, I will help with your billing inquiry',
            'expected_facts': {'name': 'Bob Wilson', 'email': 'bob@billing.com', 'account': '98765'},
            'final_response': 'Bob Wilson, your billing inquiry is being processed',
            'facts_check': ['name', 'email', 'account']
        },
        {
            'name': 'Poor Sales Follow-up',
            'user_input': 'Hi, I am Carol Davis, email carol@sales.com, interested in product X',
            'bot_response': 'Hello Carol, I will help you with product information',
            'expected_facts': {'name': 'Carol Davis', 'email': 'carol@sales.com', 'interest': 'product X'},
            'final_response': 'Thank you for your interest',
            'facts_check': ['name', 'email', 'interest']
        },
        {
            'name': 'Failed Support Case',
            'user_input': 'Hello, I am David Brown, email david@support.com, critical issue',
            'bot_response': 'Hello David, I will help you',
            'expected_facts': {'name': 'David Brown', 'email': 'david@support.com', 'priority': 'critical'},
            'final_response': 'We will get back to you soon',
            'facts_check': ['name', 'email', 'priority']
        },
        {
            'name': 'Excellent E-commerce',
            'user_input': 'Hi, I am Eve Miller, email eve@shop.com, order 54321, product laptop',
            'bot_response': 'Hello Eve, I will help you with your laptop order',
            'expected_facts': {'name': 'Eve Miller', 'email': 'eve@shop.com', 'order': '54321', 'product': 'laptop'},
            'final_response': 'Eve Miller, your laptop order 54321 has been processed. Confirmation sent to eve@shop.com',
            'facts_check': ['name', 'email', 'order', 'product']
        },
        {
            'name': 'Good Banking Service',
            'user_input': 'Hello, I am Frank Garcia, email frank@bank.com, account 11111, balance inquiry',
            'bot_response': 'Hello Frank, I will help you with your balance inquiry',
            'expected_facts': {'name': 'Frank Garcia', 'email': 'frank@bank.com', 'account': '11111', 'service': 'balance'},
            'final_response': 'Frank Garcia (account 11111), your balance inquiry has been processed. Details sent to frank@bank.com',
            'facts_check': ['name', 'email', 'account', 'service']
        },
        {
            'name': 'Average Insurance Claim',
            'user_input': 'Hi, I am Grace Lee, email grace@insurance.com, claim 22222, auto damage',
            'bot_response': 'Hello Grace, I will help you with your auto claim',
            'expected_facts': {'name': 'Grace Lee', 'email': 'grace@insurance.com', 'claim': '22222', 'type': 'auto'},
            'final_response': 'Grace Lee, your auto claim 22222 is being reviewed',
            'facts_check': ['name', 'email', 'claim', 'type']
        }
    ]
    
    # Generate results with different dates
    base_date = datetime.now()
    
    for i, test_case in enumerate(test_cases):
        validator = ConversationValidator()
        validator.add_turn(
            user_input=test_case['user_input'],
            bot_response=test_case['bot_response'],
            expected_facts=test_case['expected_facts']
        )
        
        result = validator.validate_retention(
            response=test_case['final_response'],
            facts_to_check=test_case['facts_check']
        )
        
        result['test_name'] = test_case['name']
        # Spread dates across the last week
        result['timestamp'] = (base_date - timedelta(days=i)).isoformat()
        results.append(result)
    
    return results

def main():
    """Main demo function."""
    print("🔍 Advanced Search Demo for HTML Reporter")
    print("=" * 50)
    
    # Create search demo data
    print("🧪 Creating diverse test data for search demo...")
    results = create_search_demo_data()
    
    print(f"✅ Created {len(results)} test cases with varied characteristics")
    
    # Generate HTML report
    print("\n📊 Generating HTML report with advanced search...")
    reporter = HTMLReporter()
    
    output_file = reporter.generate_report(
        results=results,
        output_file="advanced_search_demo.html",
        title="Advanced Search Demo - Chatbot Validation Report",
        show_details=True
    )
    
    print(f"✅ HTML report generated: {output_file}")
    
    print("\n🔍 Advanced Search Features:")
    print("   🎯 Smart Operators:")
    print("      • score:0.8 (scores >= 0.8)")
    print("      • score>0.9 (scores > 0.9)")
    print("      • score<0.5 (scores < 0.5)")
    print("      • date:2024-12-01 (specific date)")
    print("      • facts:3 (specific number of facts)")
    print("      • status:pass (passed tests only)")
    print("      • status:fail (failed tests only)")
    
    print("\n   🧠 Smart Keywords:")
    print("      • pass, fail, excellent, good, average, poor")
    print("      • today, yesterday, this week")
    print("      • high score, low score")
    
    print("\n   ⚡ Performance Features:")
    print("      • Real-time search with 300ms debounce")
    print("      • Live result counter")
    print("      • Intelligent text matching")
    print("      • Multi-field search")
    
    print("\n🚀 How to use:")
    print("   1. Open the HTML report in your browser")
    print("   2. Use the search box with smart operators:")
    print("      - Try: 'score:0.8' (high scores)")
    print("      - Try: 'excellent' (excellent performance)")
    print("      - Try: 'fail' (failed tests)")
    print("      - Try: 'today' (today's tests)")
    print("   3. See live results counter update")
    print("   4. Combine with filters for advanced analysis")
    
    print("\n💡 Example Searches:")
    print("   • 'score:0.9' - Find tests with 90%+ scores")
    print("   • 'excellent' - Find excellent performance tests")
    print("   • 'fail' - Find all failed tests")
    print("   • 'facts:4' - Find tests with 4 facts")
    print("   • 'today' - Find today's tests")
    print("   • 'john' - Find tests mentioning John")
    
    return output_file

if __name__ == "__main__":
    main()
