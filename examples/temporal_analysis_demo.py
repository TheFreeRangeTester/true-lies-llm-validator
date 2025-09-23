#!/usr/bin/env python3
"""
Temporal Analysis Demo for HTML Reporter
=======================================

This example demonstrates the temporal analysis capabilities of the HTML Reporter,
including weekly trends, performance comparisons, and baseline analysis.
"""

from datetime import datetime, timedelta
import random
from true_lies import ConversationValidator, HTMLReporter

def create_temporal_test_data():
    """Create test data spanning multiple weeks for temporal analysis."""
    results = []
    
    # Generate data for the last 4 weeks
    base_date = datetime.now() - timedelta(weeks=4)
    
    # Week 1: Lower performance
    for day in range(7):
        test_date = base_date + timedelta(days=day)
        
        validator = ConversationValidator()
        validator.add_turn(
            user_input=f'Hello, I am User {day+1}, email user{day+1}@test.com, ID {day+1:03d}',
            bot_response=f'Hello User {day+1}, I will help you',
            expected_facts={'name': f'User {day+1}', 'email': f'user{day+1}@test.com', 'id': f'{day+1:03d}'}
        )
        
        # Simulate lower performance for week 1
        response_quality = random.choice(['partial', 'good'])  # Week 1 has mixed results
        
        if response_quality == 'partial':
            response = f'Hello User {day+1}, your request is being processed'
        else:
            response = f'User {day+1} (ID {day+1:03d}), your request has been processed. Confirmation sent to user{day+1}@test.com'
        
        result = validator.validate_retention(
            response=response,
            facts_to_check=['name', 'email', 'id']
        )
        result['test_name'] = f'Week 1 - Day {day+1}'
        result['test_category'] = 'Customer Service'
        result['timestamp'] = test_date.isoformat()
        result['user_input'] = f'Hello, I am User {day+1}, email user{day+1}@test.com, ID {day+1:03d}'
        result['bot_response'] = response
        result['expected_response'] = f'User {day+1} (ID {day+1:03d}), your request has been processed. Confirmation sent to user{day+1}@test.com'
        results.append(result)
    
    # Week 2: Improving performance
    for day in range(7):
        test_date = base_date + timedelta(weeks=1, days=day)
        
        validator = ConversationValidator()
        validator.add_turn(
            user_input=f'Hi, I am Customer {day+1}, email customer{day+1}@company.com, phone 555-{day+1:04d}',
            bot_response=f'Hello Customer {day+1}, I will assist you',
            expected_facts={'name': f'Customer {day+1}', 'email': f'customer{day+1}@company.com', 'phone': f'555-{day+1:04d}'}
        )
        
        # Simulate improving performance for week 2
        response_quality = random.choice(['good', 'excellent'])  # Week 2 is better
        
        if response_quality == 'good':
            response = f'Customer {day+1}, your request has been processed'
        else:
            response = f'Customer {day+1}, your request has been processed. Confirmation sent to customer{day+1}@company.com. Contact: 555-{day+1:04d}'
        
        result = validator.validate_retention(
            response=response,
            facts_to_check=['name', 'email', 'phone']
        )
        result['test_name'] = f'Week 2 - Day {day+1}'
        result['test_category'] = 'Technical Support'
        result['timestamp'] = test_date.isoformat()
        result['user_input'] = f'Hi, I am Customer {day+1}, email customer{day+1}@company.com, phone 555-{day+1:04d}'
        result['bot_response'] = response
        result['expected_response'] = f'Customer {day+1}, your request has been processed. Confirmation sent to customer{day+1}@company.com. Contact: 555-{day+1:04d}'
        results.append(result)
    
    # Week 3: Peak performance
    for day in range(7):
        test_date = base_date + timedelta(weeks=2, days=day)
        
        validator = ConversationValidator()
        validator.add_turn(
            user_input=f'Hello, I am Client {day+1}, email client{day+1}@business.com, department Sales, manager John Smith',
            bot_response=f'Hello Client {day+1}, I will help you with your request',
            expected_facts={'name': f'Client {day+1}', 'email': f'client{day+1}@business.com', 'dept': 'Sales', 'manager': 'John Smith'}
        )
        
        # Simulate peak performance for week 3
        response_quality = 'excellent'  # Week 3 is peak
        
        response = f'Client {day+1} from Sales department, your request has been processed. Manager John Smith has been notified. Confirmation sent to client{day+1}@business.com'
        
        result = validator.validate_retention(
            response=response,
            facts_to_check=['name', 'email', 'dept', 'manager']
        )
        result['test_name'] = f'Week 3 - Day {day+1}'
        result['test_category'] = 'Sales'
        result['timestamp'] = test_date.isoformat()
        result['user_input'] = f'Hello, I am Client {day+1}, email client{day+1}@business.com, department Sales, manager John Smith'
        result['bot_response'] = response
        result['expected_response'] = f'Client {day+1} from Sales department, your request has been processed. Manager John Smith has been notified. Confirmation sent to client{day+1}@business.com'
        results.append(result)
    
    # Week 4: Slight decline
    for day in range(7):
        test_date = base_date + timedelta(weeks=3, days=day)
        
        validator = ConversationValidator()
        validator.add_turn(
            user_input=f'Hi, I am Partner {day+1}, email partner{day+1}@partner.com, priority high, category urgent',
            bot_response=f'Hello Partner {day+1}, I will prioritize your urgent request',
            expected_facts={'name': f'Partner {day+1}', 'email': f'partner{day+1}@partner.com', 'priority': 'high', 'category': 'urgent'}
        )
        
        # Simulate slight decline for week 4
        response_quality = random.choice(['good', 'excellent'])  # Week 4 is slightly down
        
        if response_quality == 'good':
            response = f'Partner {day+1}, your high priority request has been processed'
        else:
            response = f'Partner {day+1}, your urgent high priority request has been processed. Confirmation sent to partner{day+1}@partner.com'
        
        result = validator.validate_retention(
            response=response,
            facts_to_check=['name', 'email', 'priority', 'category']
        )
        result['test_name'] = f'Week 4 - Day {day+1}'
        result['test_category'] = 'Partnership'
        result['timestamp'] = test_date.isoformat()
        result['user_input'] = f'Hi, I am Partner {day+1}, email partner{day+1}@partner.com, priority high, category urgent'
        result['bot_response'] = response
        result['expected_response'] = f'Partner {day+1}, your urgent high priority request has been processed. Confirmation sent to partner{day+1}@partner.com'
        results.append(result)
    
    return results

def calculate_weekly_metrics(results):
    """Calculate weekly performance metrics."""
    weekly_data = {}
    
    for result in results:
        test_date = datetime.fromisoformat(result['timestamp'])
        week_key = test_date.strftime('%Y-W%U')
        
        if week_key not in weekly_data:
            weekly_data[week_key] = {
                'scores': [],
                'passed': 0,
                'total': 0,
                'date': test_date
            }
        
        weekly_data[week_key]['scores'].append(result.get('retention_score', 0.0))
        weekly_data[week_key]['total'] += 1
        
        if result.get('retention_score', 0.0) >= 0.7:
            weekly_data[week_key]['passed'] += 1
    
    # Calculate averages
    for week_key in weekly_data:
        scores = weekly_data[week_key]['scores']
        weekly_data[week_key]['average_score'] = sum(scores) / len(scores) if scores else 0.0
        weekly_data[week_key]['pass_rate'] = weekly_data[week_key]['passed'] / weekly_data[week_key]['total']
    
    return weekly_data

def main():
    """Main demo function."""
    print("📊 Temporal Analysis Demo for HTML Reporter")
    print("=" * 50)
    
    # Create temporal test data
    print("🧪 Creating temporal test data spanning 4 weeks...")
    results = create_temporal_test_data()
    
    print(f"✅ Created {len(results)} test cases across 4 weeks")
    
    # Calculate weekly metrics
    weekly_metrics = calculate_weekly_metrics(results)
    
    print("\n📈 Weekly Performance Summary:")
    for week_key in sorted(weekly_metrics.keys()):
        metrics = weekly_metrics[week_key]
        print(f"   Week {week_key}: {metrics['average_score']:.3f} avg, {metrics['pass_rate']:.1%} pass rate ({metrics['passed']}/{metrics['total']})")
    
    # Generate HTML report
    print("\n📊 Generating HTML report with temporal analysis...")
    reporter = HTMLReporter()
    
    output_file = reporter.generate_report(
        results=results,
        output_file="temporal_analysis_demo.html",
        title="Temporal Analysis Demo - Chatbot Performance Trends",
        show_details=True
    )
    
    print(f"✅ HTML report generated: {output_file}")
    
    print("\n💡 Temporal Analysis Features:")
    print("   📈 Weekly Performance Trend Chart")
    print("   📊 Performance Comparison (Current vs Previous vs Historical)")
    print("   🎯 Target Line (80% performance threshold)")
    print("   📅 Interactive Period Selection (Daily/Weekly/Monthly)")
    print("   🔄 Dynamic Baseline Comparison")
    
    print("\n🚀 How to use:")
    print("   1. Open the HTML report in your browser")
    print("   2. View the 'Weekly Performance Trend' chart")
    print("   3. Use 'Performance Comparison' to see relative performance")
    print("   4. Adjust analysis period with dropdown controls")
    print("   5. Compare against different baselines")
    
    return output_file

if __name__ == "__main__":
    main()
