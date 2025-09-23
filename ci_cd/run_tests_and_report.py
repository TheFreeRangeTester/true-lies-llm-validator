#!/usr/bin/env python3
"""
CI/CD Integration Script for True Lies Validator
===============================================

This script is designed to run chatbot validation tests in CI/CD pipelines
and generate HTML reports automatically.

Usage:
    python run_tests_and_report.py [options]

Environment Variables:
    TL_REPORT_TITLE: Title for the generated report
    TL_REPORT_OUTPUT: Output file path for the HTML report
    TL_TEST_SUITE: Path to test suite configuration
    TL_THRESHOLD: Minimum pass rate threshold (default: 0.8)
    TL_SLACK_WEBHOOK: Slack webhook URL for notifications
    TL_EMAIL_RECIPIENTS: Comma-separated email addresses for notifications
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from true_lies import ConversationValidator, HTMLReporter

class CICDRunner:
    """CI/CD runner for chatbot validation tests."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results = []
        self.metrics = {}
        
    def load_test_suite(self, test_suite_path: str) -> List[Dict[str, Any]]:
        """Load test suite from JSON configuration file."""
        try:
            with open(test_suite_path, 'r', encoding='utf-8') as f:
                test_suite = json.load(f)
            return test_suite.get('tests', [])
        except FileNotFoundError:
            print(f"❌ Test suite file not found: {test_suite_path}")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in test suite file: {e}")
            return []
    
    def run_test(self, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test case."""
        validator = ConversationValidator()
        
        # Add conversation turns
        for turn in test_config.get('turns', []):
            validator.add_turn(
                user_input=turn['user_input'],
                bot_response=turn['bot_response'],
                expected_facts=turn.get('expected_facts', {})
            )
        
        # Validate retention
        result = validator.validate_retention(
            response=test_config['final_response'],
            facts_to_check=test_config.get('facts_to_check', [])
        )
        
        # Add test metadata
        result['test_name'] = test_config.get('name', 'Unnamed Test')
        result['test_category'] = test_config.get('category', 'General')
        result['timestamp'] = datetime.now().isoformat()
        
        return result
    
    def run_all_tests(self, test_suite: List[Dict[str, Any]]) -> None:
        """Run all tests in the test suite."""
        print(f"🧪 Running {len(test_suite)} test cases...")
        
        for i, test_config in enumerate(test_suite, 1):
            print(f"   Running test {i}/{len(test_suite)}: {test_config.get('name', 'Unnamed')}")
            
            try:
                result = self.run_test(test_config)
                self.results.append(result)
                
                status = "✅ PASS" if result.get('retention_score', 0) >= 0.7 else "❌ FAIL"
                score = result.get('retention_score', 0)
                print(f"      {status} (Score: {score:.3f})")
                
            except Exception as e:
                print(f"      ❌ ERROR: {e}")
                # Add error result
                error_result = {
                    'test_name': test_config.get('name', 'Unnamed Test'),
                    'test_category': test_config.get('category', 'General'),
                    'retention_score': 0.0,
                    'facts_retained': 0,
                    'total_facts': len(test_config.get('facts_to_check', [])),
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e)
                }
                self.results.append(error_result)
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate overall metrics from test results."""
        if not self.results:
            return {}
        
        scores = [r.get('retention_score', 0.0) for r in self.results if 'error' not in r]
        passed = sum(1 for score in scores if score >= 0.7)
        total = len(self.results)
        
        self.metrics = {
            'total_candidates': total,
            'passed': passed,
            'failed': total - passed,
            'pass_rate': passed / total if total > 0 else 0.0,
            'avg_score': sum(scores) / len(scores) if scores else 0.0,
            'min_score': min(scores) if scores else 0.0,
            'max_score': max(scores) if scores else 0.0
        }
        
        return self.metrics
    
    def generate_report(self) -> str:
        """Generate HTML report."""
        if not self.results:
            print("❌ No test results to generate report")
            return ""
        
        print("📊 Generating HTML report...")
        
        reporter = HTMLReporter()
        output_file = self.config.get('output_file', 'ci_cd_report.html')
        title = self.config.get('title', f'CI/CD Test Report - {datetime.now().strftime("%Y-%m-%d %H:%M")}')
        
        report_path = reporter.generate_report(
            results=self.results,
            output_file=output_file,
            title=title,
            show_details=True
        )
        
        print(f"✅ Report generated: {report_path}")
        return report_path
    
    def check_threshold(self, threshold: float = 0.8) -> bool:
        """Check if pass rate meets the threshold."""
        pass_rate = self.metrics.get('pass_rate', 0.0)
        meets_threshold = pass_rate >= threshold
        
        status = "✅ PASSED" if meets_threshold else "❌ FAILED"
        print(f"📊 Pass Rate: {pass_rate:.1%} (Threshold: {threshold:.1%}) - {status}")
        
        return meets_threshold
    
    def send_slack_notification(self, webhook_url: str) -> None:
        """Send notification to Slack."""
        if not webhook_url:
            return
        
        pass_rate = self.metrics.get('pass_rate', 0.0)
        total_tests = self.metrics.get('total_candidates', 0)
        passed_tests = self.metrics.get('passed', 0)
        
        status = "✅ PASSED" if pass_rate >= 0.8 else "❌ FAILED"
        color = "good" if pass_rate >= 0.8 else "danger"
        
        payload = {
            "text": f"Chatbot Validation Test Results - {status}",
            "attachments": [
                {
                    "color": color,
                    "fields": [
                        {"title": "Pass Rate", "value": f"{pass_rate:.1%}", "short": True},
                        {"title": "Tests Passed", "value": f"{passed_tests}/{total_tests}", "short": True},
                        {"title": "Average Score", "value": f"{self.metrics.get('avg_score', 0):.3f}", "short": True},
                        {"title": "Timestamp", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "short": True}
                    ]
                }
            ]
        }
        
        try:
            import requests
            response = requests.post(webhook_url, json=payload)
            if response.status_code == 200:
                print("✅ Slack notification sent successfully")
            else:
                print(f"❌ Failed to send Slack notification: {response.status_code}")
        except ImportError:
            print("⚠️  requests library not available for Slack notifications")
        except Exception as e:
            print(f"❌ Error sending Slack notification: {e}")
    
    def send_email_notification(self, recipients: str) -> None:
        """Send email notification."""
        if not recipients:
            return
        
        pass_rate = self.metrics.get('pass_rate', 0.0)
        status = "PASSED" if pass_rate >= 0.8 else "FAILED"
        
        subject = f"Chatbot Validation Tests - {status}"
        body = f"""
Chatbot Validation Test Results

Status: {status}
Pass Rate: {pass_rate:.1%}
Tests Passed: {self.metrics.get('passed', 0)}/{self.metrics.get('total_candidates', 0)}
Average Score: {self.metrics.get('avg_score', 0):.3f}
Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Report generated: {self.config.get('output_file', 'ci_cd_report.html')}
        """
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            # This is a basic implementation - in production, use proper SMTP configuration
            print("📧 Email notification functionality requires SMTP configuration")
            print(f"   Subject: {subject}")
            print(f"   Recipients: {recipients}")
            print(f"   Body: {body.strip()}")
            
        except Exception as e:
            print(f"❌ Error preparing email notification: {e}")

def create_sample_test_suite():
    """Create a sample test suite configuration."""
    sample_suite = {
        "name": "CI/CD Test Suite",
        "description": "Sample test suite for CI/CD integration",
        "tests": [
            {
                "name": "Customer Service Test",
                "category": "Customer Service",
                "turns": [
                    {
                        "user_input": "Hello, I am John Doe, email john@company.com, account 12345",
                        "bot_response": "Hello John, I will help you with your request",
                        "expected_facts": {"name": "John Doe", "email": "john@company.com", "account": "12345"}
                    }
                ],
                "final_response": "John Doe, your request for account 12345 has been processed. Confirmation sent to john@company.com",
                "facts_to_check": ["name", "email", "account"]
            },
            {
                "name": "Technical Support Test",
                "category": "Technical Support",
                "turns": [
                    {
                        "user_input": "Hi, I am Jane Smith, email jane@tech.com, software issue",
                        "bot_response": "Hello Jane, I will help you with your software issue",
                        "expected_facts": {"name": "Jane Smith", "email": "jane@tech.com", "issue": "software"}
                    }
                ],
                "final_response": "Jane Smith, your software issue has been resolved. Details sent to jane@tech.com",
                "facts_to_check": ["name", "email", "issue"]
            }
        ]
    }
    
    # Create ci_cd directory if it doesn't exist
    ci_cd_dir = Path(__file__).parent
    ci_cd_dir.mkdir(exist_ok=True)
    
    # Write sample test suite
    sample_file = ci_cd_dir / "sample_test_suite.json"
    with open(sample_file, 'w', encoding='utf-8') as f:
        json.dump(sample_suite, f, indent=2)
    
    print(f"✅ Sample test suite created: {sample_file}")
    return sample_file

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Run chatbot validation tests in CI/CD')
    parser.add_argument('--test-suite', help='Path to test suite JSON file')
    parser.add_argument('--output', help='Output HTML report file path')
    parser.add_argument('--title', help='Report title')
    parser.add_argument('--threshold', type=float, default=0.8, help='Pass rate threshold (default: 0.8)')
    parser.add_argument('--create-sample', action='store_true', help='Create sample test suite')
    
    args = parser.parse_args()
    
    # Create sample test suite if requested
    if args.create_sample:
        create_sample_test_suite()
        return
    
    # Get configuration from environment variables and arguments
    config = {
        'test_suite_path': args.test_suite or os.getenv('TL_TEST_SUITE', 'ci_cd/sample_test_suite.json'),
        'output_file': args.output or os.getenv('TL_REPORT_OUTPUT', 'ci_cd_report.html'),
        'title': args.title or os.getenv('TL_REPORT_TITLE', f'CI/CD Test Report - {datetime.now().strftime("%Y-%m-%d %H:%M")}'),
        'threshold': float(os.getenv('TL_THRESHOLD', args.threshold))
    }
    
    print("🚀 CI/CD Chatbot Validation Runner")
    print("=" * 50)
    print(f"Test Suite: {config['test_suite_path']}")
    print(f"Output File: {config['output_file']}")
    print(f"Threshold: {config['threshold']:.1%}")
    print()
    
    # Initialize runner
    runner = CICDRunner(config)
    
    # Load and run tests
    test_suite = runner.load_test_suite(config['test_suite_path'])
    if not test_suite:
        print("❌ No tests to run")
        sys.exit(1)
    
    runner.run_all_tests(test_suite)
    print()
    
    # Calculate metrics
    metrics = runner.calculate_metrics()
    print("📊 Test Results Summary:")
    print(f"   Total Tests: {metrics.get('total_candidates', 0)}")
    print(f"   Passed: {metrics.get('passed', 0)}")
    print(f"   Failed: {metrics.get('failed', 0)}")
    print(f"   Pass Rate: {metrics.get('pass_rate', 0):.1%}")
    print(f"   Average Score: {metrics.get('avg_score', 0):.3f}")
    print()
    
    # Check threshold
    meets_threshold = runner.check_threshold(config['threshold'])
    print()
    
    # Generate report
    report_path = runner.generate_report()
    print()
    
    # Send notifications
    slack_webhook = os.getenv('TL_SLACK_WEBHOOK')
    if slack_webhook:
        runner.send_slack_notification(slack_webhook)
    
    email_recipients = os.getenv('TL_EMAIL_RECIPIENTS')
    if email_recipients:
        runner.send_email_notification(email_recipients)
    
    # Exit with appropriate code
    exit_code = 0 if meets_threshold else 1
    print(f"\n🏁 CI/CD Pipeline {'PASSED' if meets_threshold else 'FAILED'}")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
