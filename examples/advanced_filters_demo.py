#!/usr/bin/env python3
"""
Advanced Filters Demo for HTML Reporter
======================================

This example demonstrates the advanced filtering capabilities of the HTML Reporter,
including score ranges, date ranges, and facts-based filtering.
"""

from datetime import datetime, timedelta
from true_lies import ConversationValidator, HTMLReporter

def create_diverse_test_data():
    """Create diverse test data with varying scores, dates, and facts."""
    results = []
    
    # Test 1: High score, recent date, many facts
    validator1 = ConversationValidator()
    validator1.add_turn(
        user_input='Hello, I am Alice Johnson, email alice@company.com, ID 001, department Engineering',
        bot_response='Hello Alice, I will help you with your request',
        expected_facts={'name': 'Alice Johnson', 'email': 'alice@company.com', 'id': '001', 'dept': 'Engineering'}
    )
    
    result1 = validator1.validate_retention(
        response='Alice Johnson (ID 001), your Engineering request has been processed. Confirmation sent to alice@company.com',
        facts_to_check=['name', 'email', 'id', 'dept']
    )
    result1['test_name'] = 'High Performance Test'
    result1['timestamp'] = datetime.now().isoformat()
    results.append(result1)
    
    # Test 2: Medium score, yesterday, medium facts
    validator2 = ConversationValidator()
    validator2.add_turn(
        user_input='Hi, I am Bob Smith, email bob@test.com, need help with billing',
        bot_response='Hello Bob, I will assist you with billing',
        expected_facts={'name': 'Bob Smith', 'email': 'bob@test.com', 'issue': 'billing'}
    )
    
    result2 = validator2.validate_retention(
        response='Bob Smith, your billing issue has been resolved',
        facts_to_check=['name', 'email', 'issue']
    )
    result2['test_name'] = 'Medium Performance Test'
    result2['timestamp'] = (datetime.now() - timedelta(days=1)).isoformat()
    results.append(result2)
    
    # Test 3: Low score, week ago, few facts
    validator3 = ConversationValidator()
    validator3.add_turn(
        user_input='Hello, I am Charlie Brown, email charlie@example.com, phone 555-1234, address 123 Main St',
        bot_response='Hello Charlie, I will help you',
        expected_facts={'name': 'Charlie Brown', 'email': 'charlie@example.com', 'phone': '555-1234', 'address': '123 Main St'}
    )
    
    result3 = validator3.validate_retention(
        response='Hello, how can I help you today?',
        facts_to_check=['name', 'email', 'phone', 'address']
    )
    result3['test_name'] = 'Low Performance Test'
    result3['timestamp'] = (datetime.now() - timedelta(days=7)).isoformat()
    results.append(result3)
    
    # Test 4: Very high score, recent, many facts
    validator4 = ConversationValidator()
    validator4.add_turn(
        user_input='Hi, I am Diana Prince, email diana@justice.com, ID 007, role Hero, location Metropolis',
        bot_response='Hello Diana, I will process your request',
        expected_facts={'name': 'Diana Prince', 'email': 'diana@justice.com', 'id': '007', 'role': 'Hero', 'location': 'Metropolis'}
    )
    
    result4 = validator4.validate_retention(
        response='Diana Prince (ID 007), your Hero request in Metropolis has been processed. Confirmation sent to diana@justice.com',
        facts_to_check=['name', 'email', 'id', 'role', 'location']
    )
    result4['test_name'] = 'Excellent Performance Test'
    result4['timestamp'] = datetime.now().isoformat()
    results.append(result4)
    
    # Test 5: Zero score, old date, no facts retained
    validator5 = ConversationValidator()
    validator5.add_turn(
        user_input='Hello, I am Eve Wilson, email eve@test.org, need urgent help',
        bot_response='Hello Eve, I will help you',
        expected_facts={'name': 'Eve Wilson', 'email': 'eve@test.org', 'urgency': 'urgent'}
    )
    
    result5 = validator5.validate_retention(
        response='Thank you for contacting us. We will get back to you soon.',
        facts_to_check=['name', 'email', 'urgency']
    )
    result5['test_name'] = 'Failed Test Case'
    result5['timestamp'] = (datetime.now() - timedelta(days=30)).isoformat()
    results.append(result5)
    
    return results

def main():
    """Main demo function."""
    print("🎯 Advanced Filters Demo for HTML Reporter")
    print("=" * 50)
    
    # Create diverse test data
    print("🧪 Creating diverse test data...")
    results = create_diverse_test_data()
    
    print(f"✅ Created {len(results)} test cases with varying:")
    print("   • Scores: from 0.0 to 1.0")
    print("   • Dates: from 30 days ago to now")
    print("   • Facts: from 0 to 5 facts retained")
    
    # Generate HTML report
    print("\n📊 Generating HTML report with advanced filtering...")
    reporter = HTMLReporter()
    
    output_file = reporter.generate_report(
        results=results,
        output_file="advanced_filters_demo.html",
        title="Advanced Filters Demo - Chatbot Validation Report",
        show_details=True
    )
    
    print(f"✅ HTML report generated: {output_file}")
    
    # Show summary
    print("\n📈 Test Summary:")
    for i, result in enumerate(results, 1):
        score = result.get('retention_score', 0.0)
        facts_retained = result.get('facts_retained', 0)
        total_facts = result.get('total_facts', 1)
        test_name = result.get('test_name', f'Test {i}')
        
        print(f"   {i}. {test_name}: {score:.3f} ({facts_retained}/{total_facts} facts)")
    
    print("\n💡 Advanced Filtering Features:")
    print("   🔍 Filter by Score Range: 0.0 - 1.0")
    print("   📅 Filter by Date Range: Any date range")
    print("   📊 Filter by Facts Count: Number of facts retained")
    print("   🔄 Combine multiple filters")
    print("   📈 Real-time result counter")
    
    print("\n🚀 How to use:")
    print("   1. Open the HTML report in your browser")
    print("   2. Click '🔍 Advanced Filters' button")
    print("   3. Choose filter type (Score/Date/Facts)")
    print("   4. Enter your criteria")
    print("   5. See filtered results with counter")
    
    return output_file

if __name__ == "__main__":
    main()
