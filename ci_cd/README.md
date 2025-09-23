# CI/CD Integration for True Lies Validator

This directory contains scripts and configurations for integrating chatbot validation tests into CI/CD pipelines.

## 📁 Files Overview

- `run_tests_and_report.py` - Main CI/CD runner script
- `sample_test_suite.json` - Example test suite configuration
- `../.github/workflows/chatbot-validation.yml` - GitHub Actions workflow
- `Jenkinsfile` - Jenkins pipeline configuration
- `../.gitlab-ci.yml` - GitLab CI configuration

## 🚀 Quick Start

### 1. Create a Test Suite

Create a JSON file with your test cases:

```json
{
  "name": "My Chatbot Test Suite",
  "description": "Test suite for my chatbot",
  "tests": [
    {
      "name": "Customer Service Test",
      "category": "Customer Service",
      "turns": [
        {
          "user_input": "Hello, I am John Doe, email john@company.com",
          "bot_response": "Hello John, I will help you",
          "expected_facts": { "name": "John Doe", "email": "john@company.com" }
        }
      ],
      "final_response": "John Doe, your request has been processed. Confirmation sent to john@company.com",
      "facts_to_check": ["name", "email"]
    }
  ]
}
```

### 2. Run Tests Locally

```bash
# Create sample test suite
python ci_cd/run_tests_and_report.py --create-sample

# Run tests with custom configuration
python ci_cd/run_tests_and_report.py \
  --test-suite my_test_suite.json \
  --output my_report.html \
  --title "My Chatbot Report" \
  --threshold 0.8
```

### 3. Set Environment Variables

```bash
export TL_TEST_SUITE="ci_cd/my_test_suite.json"
export TL_REPORT_OUTPUT="test_results.html"
export TL_REPORT_TITLE="CI/CD Test Report"
export TL_THRESHOLD="0.8"
export TL_SLACK_WEBHOOK="https://hooks.slack.com/services/..."
export TL_EMAIL_RECIPIENTS="team@company.com,manager@company.com"
```

## 🔧 CI/CD Platform Setup

### GitHub Actions

1. **Add Secrets** (in repository settings):

   - `SLACK_WEBHOOK_URL` - Slack webhook for notifications
   - `EMAIL_RECIPIENTS` - Comma-separated email addresses

2. **Workflow Features**:
   - Runs on push/PR to main/develop branches
   - Daily scheduled runs at 2 AM UTC
   - Uploads HTML report as artifact
   - Comments PR with test results
   - Notifies on failures

### Jenkins

1. **Install Plugins**:

   - HTML Publisher Plugin
   - Slack Plugin (optional)
   - Email Extension Plugin (optional)

2. **Configure Credentials**:

   - `slack-webhook-url` - Slack webhook URL
   - `email-recipients` - Email recipient list

3. **Pipeline Features**:
   - Publishes HTML reports
   - Sends Slack notifications
   - Sends email notifications
   - Archives test results

### GitLab CI

1. **Set Variables** (in project settings):

   - `GITLAB_WEBHOOK_URL` - Webhook for notifications
   - `SLACK_WEBHOOK_DAILY` - Daily report webhook
   - `EMAIL_RECIPIENTS_DAILY` - Daily report emails

2. **Pipeline Features**:
   - Multi-stage pipeline (test, report, notify)
   - Artifacts with 1-month retention
   - Success/failure notifications
   - Scheduled daily runs

## 📊 Test Suite Configuration

### Test Structure

Each test case supports:

```json
{
  "name": "Test Name",
  "category": "Test Category",
  "description": "Test description (optional)",
  "turns": [
    {
      "user_input": "User input text",
      "bot_response": "Bot response text",
      "expected_facts": {
        "fact_name": "expected_value"
      }
    }
  ],
  "final_response": "Final bot response to validate",
  "facts_to_check": ["fact_name1", "fact_name2"]
}
```

### Supported Fact Types

- `name` - Person names
- `email` - Email addresses
- `phone` - Phone numbers
- `user_id` - User identifiers
- `account` - Account numbers
- `order` - Order numbers
- `amount` - Monetary amounts
- `date` - Dates
- `address` - Addresses
- Custom facts (any string key)

## 🔔 Notifications

### Slack Integration

The runner sends Slack notifications with:

- Test results summary
- Pass rate and metrics
- Links to full reports
- Build/pipeline information

### Email Integration

Email notifications include:

- Test results summary
- Attached HTML report
- Build logs (optional)
- Failure alerts

## 📈 Metrics and Thresholds

### Default Thresholds

- **Pass Rate**: 80% (0.8)
- **Minimum Score**: 0.7 for individual tests
- **Grade Scale**: A (0.9+), B (0.8+), C (0.7+), D (0.5+), F (0.0-0.5)

### Exit Codes

- `0` - All tests passed threshold
- `1` - Tests failed threshold or errors occurred

## 🛠️ Advanced Configuration

### Custom Test Suites

Create multiple test suites for different scenarios:

```bash
# Production tests
python ci_cd/run_tests_and_report.py --test-suite tests/production.json

# Development tests
python ci_cd/run_tests_and_report.py --test-suite tests/development.json

# Regression tests
python ci_cd/run_tests_and_report.py --test-suite tests/regression.json
```

### Environment-Specific Settings

```bash
# Development environment
export TL_THRESHOLD="0.7"
export TL_REPORT_TITLE="Development Test Report"

# Production environment
export TL_THRESHOLD="0.9"
export TL_REPORT_TITLE="Production Test Report"
```

### Integration with Existing Tests

```bash
# Run after unit tests
python -m pytest tests/
python ci_cd/run_tests_and_report.py

# Run in parallel with other validations
python ci_cd/run_tests_and_report.py &
python other_validations.py &
wait
```

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**:

   ```bash
   # Ensure the package is installed
   pip install -e .
   ```

2. **Missing Dependencies**:

   ```bash
   # Install required packages
   pip install requests nltk
   ```

3. **Test Suite Not Found**:

   ```bash
   # Check file path and permissions
   ls -la ci_cd/sample_test_suite.json
   ```

4. **Notification Failures**:
   - Verify webhook URLs
   - Check network connectivity
   - Validate credentials

### Debug Mode

```bash
# Enable debug output
export TL_DEBUG="1"
python ci_cd/run_tests_and_report.py
```

## 📚 Examples

### Basic Usage

```bash
# Run with sample data
python ci_cd/run_tests_and_report.py --create-sample
python ci_cd/run_tests_and_report.py
```

### Custom Configuration

```bash
python ci_cd/run_tests_and_report.py \
  --test-suite custom_tests.json \
  --output custom_report.html \
  --title "Custom Report" \
  --threshold 0.85
```

### CI/CD Integration

```bash
# In your CI/CD script
python ci_cd/run_tests_and_report.py
if [ $? -eq 0 ]; then
  echo "✅ Chatbot validation passed"
else
  echo "❌ Chatbot validation failed"
  exit 1
fi
```

## 🤝 Contributing

To add support for new CI/CD platforms:

1. Create a new configuration file
2. Add documentation to this README
3. Test with sample data
4. Submit a pull request

## 📄 License

This CI/CD integration is part of the True Lies Validator project and follows the same MIT license.
