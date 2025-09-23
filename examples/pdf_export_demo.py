#!/usr/bin/env python3
"""
PDF Export Demo for HTML Reporter
=================================

This example demonstrates the PDF export capabilities of the HTML Reporter,
including high-quality rendering, multi-page support, and professional formatting.
"""

from datetime import datetime, timedelta
from true_lies import ConversationValidator, HTMLReporter

def create_comprehensive_test_data():
    """Create comprehensive test data for PDF export demonstration."""
    results = []
    
    # Test cases with different scenarios for comprehensive PDF
    test_scenarios = [
        {
            'name': 'Customer Service Excellence',
            'description': 'High-quality customer service interaction',
            'user_input': 'Hello, I am Sarah Johnson, email sarah@customer.com, urgent billing issue, account 12345',
            'bot_response': 'Hello Sarah Johnson, I will prioritize your urgent billing issue for account 12345',
            'expected_facts': {'name': 'Sarah Johnson', 'email': 'sarah@customer.com', 'urgency': 'urgent', 'account': '12345', 'issue': 'billing'},
            'final_response': 'Sarah Johnson, your urgent billing issue for account 12345 has been resolved. Confirmation sent to sarah@customer.com',
            'facts_check': ['name', 'email', 'urgency', 'account', 'issue']
        },
        {
            'name': 'Technical Support Success',
            'description': 'Successful technical support resolution',
            'user_input': 'Hi, I am Mike Chen, email mike@tech.com, software problem, version 2.1, Windows 10',
            'bot_response': 'Hello Mike Chen, I will help you with your software problem on Windows 10',
            'expected_facts': {'name': 'Mike Chen', 'email': 'mike@tech.com', 'issue': 'software', 'version': '2.1', 'os': 'Windows 10'},
            'final_response': 'Mike Chen, your software problem (version 2.1 on Windows 10) has been resolved. Details sent to mike@tech.com',
            'facts_check': ['name', 'email', 'issue', 'version', 'os']
        },
        {
            'name': 'Sales Follow-up Average',
            'description': 'Average sales follow-up performance',
            'user_input': 'Hello, I am Lisa Rodriguez, email lisa@sales.com, interested in premium package, budget $5000',
            'bot_response': 'Hello Lisa Rodriguez, I will help you with the premium package information',
            'expected_facts': {'name': 'Lisa Rodriguez', 'email': 'lisa@sales.com', 'interest': 'premium package', 'budget': '5000'},
            'final_response': 'Lisa Rodriguez, information about our premium package has been sent to lisa@sales.com',
            'facts_check': ['name', 'email', 'interest', 'budget']
        },
        {
            'name': 'E-commerce Order Processing',
            'description': 'E-commerce order processing and fulfillment',
            'user_input': 'Hi, I am David Kim, email david@shop.com, order 98765, product smartphone, delivery urgent',
            'bot_response': 'Hello David Kim, I will process your urgent smartphone order 98765',
            'expected_facts': {'name': 'David Kim', 'email': 'david@shop.com', 'order': '98765', 'product': 'smartphone', 'delivery': 'urgent'},
            'final_response': 'David Kim, your urgent smartphone order 98765 has been processed and shipped. Tracking sent to david@shop.com',
            'facts_check': ['name', 'email', 'order', 'product', 'delivery']
        },
        {
            'name': 'Banking Service Inquiry',
            'description': 'Banking service inquiry and resolution',
            'user_input': 'Hello, I am Maria Garcia, email maria@bank.com, account 54321, balance inquiry, need statement',
            'bot_response': 'Hello Maria Garcia, I will help you with your balance inquiry for account 54321',
            'expected_facts': {'name': 'Maria Garcia', 'email': 'maria@bank.com', 'account': '54321', 'service': 'balance inquiry', 'request': 'statement'},
            'final_response': 'Maria Garcia, your balance inquiry for account 54321 is complete. Statement sent to maria@bank.com',
            'facts_check': ['name', 'email', 'account', 'service', 'request']
        },
        {
            'name': 'Insurance Claim Processing',
            'description': 'Insurance claim processing and assessment',
            'user_input': 'Hi, I am Robert Wilson, email robert@insurance.com, claim 11111, auto accident, date 2024-12-01',
            'bot_response': 'Hello Robert Wilson, I will help you with your auto accident claim 11111',
            'expected_facts': {'name': 'Robert Wilson', 'email': 'robert@insurance.com', 'claim': '11111', 'type': 'auto accident', 'date': '2024-12-01'},
            'final_response': 'Robert Wilson, your auto accident claim 11111 from 2024-12-01 is being processed. Updates sent to robert@insurance.com',
            'facts_check': ['name', 'email', 'claim', 'type', 'date']
        },
        {
            'name': 'Support Case Failure',
            'description': 'Failed support case with poor retention',
            'user_input': 'Hello, I am Jennifer Lee, email jennifer@support.com, critical bug report, priority high',
            'bot_response': 'Hello Jennifer Lee, I will help you with your bug report',
            'expected_facts': {'name': 'Jennifer Lee', 'email': 'jennifer@support.com', 'issue': 'bug report', 'priority': 'high'},
            'final_response': 'Thank you for contacting support. We will review your request.',
            'facts_check': ['name', 'email', 'issue', 'priority']
        },
        {
            'name': 'Product Information Request',
            'description': 'Product information request and response',
            'user_input': 'Hi, I am Alex Thompson, email alex@product.com, interested in laptop specs, budget $2000',
            'bot_response': 'Hello Alex Thompson, I will provide you with laptop specifications',
            'expected_facts': {'name': 'Alex Thompson', 'email': 'alex@product.com', 'interest': 'laptop specs', 'budget': '2000'},
            'final_response': 'Alex Thompson, detailed laptop specifications within your $2000 budget have been sent to alex@product.com',
            'facts_check': ['name', 'email', 'interest', 'budget']
        },
        {
            'name': 'Account Management',
            'description': 'Account management and profile updates',
            'user_input': 'Hello, I am Emma Davis, email emma@account.com, need profile update, phone 555-1234, address 123 Main St',
            'bot_response': 'Hello Emma Davis, I will help you update your profile information',
            'expected_facts': {'name': 'Emma Davis', 'email': 'emma@account.com', 'request': 'profile update', 'phone': '555-1234', 'address': '123 Main St'},
            'final_response': 'Emma Davis, your profile has been updated with phone 555-1234 and address 123 Main St. Confirmation sent to emma@account.com',
            'facts_check': ['name', 'email', 'request', 'phone', 'address']
        },
        {
            'name': 'Complaint Resolution',
            'description': 'Customer complaint resolution process',
            'user_input': 'Hi, I am Tom Anderson, email tom@complaint.com, complaint about service delay, order 55555',
            'bot_response': 'Hello Tom Anderson, I will address your complaint about service delay for order 55555',
            'expected_facts': {'name': 'Tom Anderson', 'email': 'tom@complaint.com', 'issue': 'service delay', 'order': '55555'},
            'final_response': 'Tom Anderson, your complaint about service delay for order 55555 has been resolved. Apology and resolution sent to tom@complaint.com',
            'facts_check': ['name', 'email', 'issue', 'order']
        }
    ]
    
    # Generate results with different dates across the last week
    base_date = datetime.now()
    
    for i, scenario in enumerate(test_scenarios):
        validator = ConversationValidator()
        validator.add_turn(
            user_input=scenario['user_input'],
            bot_response=scenario['bot_response'],
            expected_facts=scenario['expected_facts']
        )
        
        result = validator.validate_retention(
            response=scenario['final_response'],
            facts_to_check=scenario['facts_check']
        )
        
        result['test_name'] = scenario['name']
        result['description'] = scenario['description']
        # Spread dates across the last week
        result['timestamp'] = (base_date - timedelta(days=i)).isoformat()
        results.append(result)
    
    return results

def main():
    """Main demo function."""
    print("📄 PDF Export Demo for HTML Reporter")
    print("=" * 50)
    
    # Create comprehensive test data
    print("🧪 Creating comprehensive test data for PDF export...")
    results = create_comprehensive_test_data()
    
    print(f"✅ Created {len(results)} test cases with varied scenarios")
    
    # Generate HTML report
    print("\n📊 Generating HTML report with PDF export capability...")
    reporter = HTMLReporter()
    
    output_file = reporter.generate_report(
        results=results,
        output_file="pdf_export_demo.html",
        title="PDF Export Demo - Comprehensive Chatbot Validation Report",
        show_details=True
    )
    
    print(f"✅ HTML report generated: {output_file}")
    
    print("\n📄 PDF Export Features:")
    print("   🖼️ High-Quality Rendering:")
    print("      • 2x scale for crisp graphics")
    print("      • Full-color charts and graphs")
    print("      • Professional formatting")
    
    print("\n   📑 Multi-Page Support:")
    print("      • Automatic page breaks")
    print("      • Proper content distribution")
    print("      • A4 format optimization")
    
    print("\n   🎨 Professional Output:")
    print("      • Clean white background")
    print("      • Preserved styling and layout")
    print("      • Timestamped filenames")
    
    print("\n   ⚡ User Experience:")
    print("      • Loading indicators")
    print("      • Success/error notifications")
    print("      • Progress feedback")
    
    print("\n🚀 How to use:")
    print("   1. Open the HTML report in your browser")
    print("   2. Click the '📄 Export PDF' button")
    print("   3. Wait for the PDF generation (loading indicator)")
    print("   4. PDF will download automatically")
    print("   5. View the high-quality PDF report")
    
    print("\n💡 PDF Features Demonstrated:")
    print("   • Complete analytics dashboard with charts")
    print("   • Detailed test results table")
    print("   • Temporal analysis controls")
    print("   • Professional formatting and layout")
    print("   • Multi-page content distribution")
    
    print("\n📋 Use Cases:")
    print("   • Executive reports for stakeholders")
    print("   • Compliance documentation")
    print("   • Audit trails and records")
    print("   • Client presentations")
    print("   • Archival and backup")
    
    return output_file

if __name__ == "__main__":
    main()
