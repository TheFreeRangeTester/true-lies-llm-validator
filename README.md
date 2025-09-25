# True Lies Validator 🎭

**The easiest library to validate LLM and chatbot responses**

Validates if your LLM or chatbot is telling the truth, remembering context and maintaining coherence. Perfect for automated conversation testing.

## 🚀 Quick Installation

```bash
# Install the library
pip install true-lies-validator

# Verify installation
python -c "from true_lies import ConversationValidator, HTMLReporter; print('✅ Installed correctly')"
```

> **📦 Current version: 0.7.0** - With HTML Reporter, interactive dashboards, and advanced analytics

## ⚡ Get Started in 2 Minutes

### 1. Basic Validation (1 minute)

```python
from true_lies import ConversationValidator

# Create validator
conv = ConversationValidator()

# Add conversation with automatic reporting
conv.add_turn_and_report(
    user_input="Hello, I'm John, my email is john@company.com",
    bot_response="Hello John! I'll help you with your inquiry.",
    expected_facts={'name': 'John', 'email': 'john@company.com'},
    title="Turn 1: User identifies themselves"
)

# Validate if the bot remembers the context
final_response = "John, your inquiry about john@company.com is resolved"
retention = conv.validate_and_report(
    response=final_response,
    facts_to_check=['name', 'email'],
    title="Retention Test"
)

# Automatic result: ✅ PASS or ❌ FAIL
```

### 2. Complete Multi-turn Validation (2 minutes)

```python
from true_lies import ConversationValidator

def test_chatbot_support():
    """Complete support chatbot test"""
    
    # Create validator
    conv = ConversationValidator()
    
    # Turn 1: User reports problem
    conv.add_turn_and_report(
        user_input="My app doesn't work, I'm user ID 12345",
        bot_response="Hello, I'll help you. What error do you see?",
        expected_facts={'user_id': '12345', 'issue_type': 'app_not_working'},
        title="Turn 1: User reports problem"
    )
    
    # Turn 2: User provides details
    conv.add_turn_and_report(
        user_input="Error 500 on login, email john@company.com",
        bot_response="I understand, error 500 on login. Checking your account.",
        expected_facts={'error_code': '500', 'email': 'john@company.com'},
        title="Turn 2: User provides details"
    )
    
    # Show conversation summary
    conv.print_conversation_summary("Conversation Summary")
    
    # Final test: Does the bot remember everything?
    final_response = "John (ID 12345), your error 500 will be fixed in 2 hours"
    retention = conv.validate_and_report(
        response=final_response,
        facts_to_check=['user_id', 'error_code', 'email'],
        title="Context Retention Test"
    )
    
    # Return result for automated tests
    return retention['retention_score'] >= 0.8

# Run test
if __name__ == "__main__":
    test_chatbot_support()
```

## 🎯 Popular Use Cases

### E-commerce
```python
# Customer buying product
conv.add_turn_and_report(
    user_input="Hello, I'm Maria, I want to buy a laptop for $1500",
    bot_response="Hello Maria! I'll help you with the laptop. Registered email: maria@store.com",
    expected_facts={'customer_name': 'Maria', 'product': 'laptop', 'budget': '1500'},
    title="Turn 1: Customer identifies themselves"
)
```

### Banking
```python
# Customer requesting loan
conv.add_turn_and_report(
    user_input="I'm Carlos, I work at TechCorp, I earn $95,000, I want a loan",
    bot_response="Hello Carlos! I'll help you with your loan. Email: carlos@bank.com",
    expected_facts={'customer_name': 'Carlos', 'employer': 'TechCorp', 'income': '95000'},
    title="Turn 1: Customer requests loan"
)
```

### Technical Support
```python
# User reports problem
conv.add_turn_and_report(
    user_input="My app doesn't work, I'm user ID 12345",
    bot_response="Hello, I'll help you. What error do you see?",
    expected_facts={'user_id': '12345', 'issue_type': 'app_not_working'},
    title="Turn 1: User reports problem"
)
```

## 🔧 Main Methods

### `add_turn_and_report()` - Add turn with automatic reporting
```python
conv.add_turn_and_report(
    user_input="...",
    bot_response="...",
    expected_facts={'key': 'value'},
    title="Turn description"
)
```

### `validate_and_report()` - Validate retention with automatic reporting
```python
retention = conv.validate_and_report(
    response="Bot response to validate",
    facts_to_check=['fact1', 'fact2'],
    title="Retention Test"
)
```

### `print_conversation_summary()` - Conversation summary
```python
conv.print_conversation_summary("Conversation Summary")
```

## 📊 Supported Fact Types

The library automatically detects these types of information:

- **Names**: "John", "Maria Gonzalez"
- **Emails**: "john@company.com", "maria@store.com"
- **Phones**: "+1-555-123-4567", "(555) 123-4567"
- **IDs**: "12345", "USER-001", "POL-2024-001"
- **Amounts**: "$1,500", "1500", "USD 1500"
- **Employers**: "TechCorp", "Google Inc", "Microsoft"
- **Dates**: "2024-12-31", "31/12/2024", "December 31, 2024"
- **Percentages**: "15%", "15 percent", "fifteen percent"

## 🎨 Automatic Reporting

True Lies handles all the reporting. You only need 3 lines:

```python
# Before (30+ lines of manual code)
print(f"📊 Detailed results:")
for fact in facts:
    retained = retention.get(f'{fact}_retained', False)
    # ... 25 more lines of manual prints

# After (3 simple lines)
retention = conv.validate_and_report(
    response=final_response,
    facts_to_check=['fact1', 'fact2'],
    title="Retention Test"
)
```

## 📊 HTML Reports & Dashboard

Generate professional HTML reports with interactive dashboards in just **one line**:

### 🚀 Super Simple HTML Reports

```python
from true_lies import validate_llm_candidates

# Define your test scenario
scenario = {
    "name": "Insurance Policy Test",
    "semantic_reference": "Your auto insurance policy #POL-2024-001 has a premium of $850.00",
    "facts": {
        "policy_number": {"expected": "POL-2024-001", "extractor": "regex", "pattern": r"#?(POL-\d{4}-\d{3})"},
        "premium_amount": {"expected": "850.00", "extractor": "money"},
        "insurance_type": {"expected": "auto insurance", "extractor": "categorical", "patterns": {"auto insurance": ["auto insurance", "car insurance"]}}
    }
}

# Test multiple candidates
candidates = [
    "Your auto insurance policy #POL-2024-001 has a premium of $850.00",
    "Auto insurance policy POL-2024-001 costs $850.00",
    "Policy #POL-2024-001: $850.00 for auto insurance"
]

# Generate HTML report with ONE line! 🎉
result = validate_llm_candidates(
    scenario=scenario,
    candidates=candidates,
    threshold=0.65,
    generate_html_report=True,  # ← This generates the report!
    html_title="Insurance Policy Validation Report"
)

print(f"📊 Report saved to: {result['html_report_path']}")
```

### 🎨 Interactive Dashboard Features

**📈 Real-time Analytics:**
- **Success Rate Distribution** - Centered chart showing pass/fail distribution
- **Performance Trend** - Historical performance with configurable target line
- **Similarity Score Trend** - Semantic similarity tracking over time
- **Fact Retention Trend** - Percentage of facts retained across tests

**🔍 Interactive Table:**
- **Sortable columns** - Click headers to sort by ID, Score, Status, etc.
- **Expandable details** - Click "View Details" to see full test information
- **Card-style details** - Professional styling with smooth transitions
- **Real-time filtering** - Filter and search through results

**📊 Historical Data:**
- **Automatic data persistence** - Results saved to `true_lies_reporting/validation_history.json`
- **Temporal analysis** - Track performance over days/weeks/months
- **Target control** - Set and adjust performance targets dynamically
- **Trend visualization** - See improvement patterns over time

### 🎯 Key Benefits

- ✅ **One-line report generation** - No complex setup required
- ✅ **Automatic data persistence** - Historical tracking built-in
- ✅ **Interactive dashboards** - Professional charts and visualizations
- ✅ **Real-time sorting** - Click to sort any column
- ✅ **Expandable details** - Toggle detailed test information
- ✅ **Responsive design** - Works on desktop and mobile
- ✅ **Professional styling** - Ready for stakeholder presentations
### 💡 Real-World Example: E-commerce Order Processing

```python
from true_lies import validate_llm_candidates

# E-commerce order scenario
scenario = {
    "name": "Order Processing Test",
    "semantic_reference": "Order #ORD-2024-789 for John Smith (john@email.com) - 2x Laptop ($1,200 each) = $2,400 total",
    "facts": {
        "order_id": {"expected": "ORD-2024-789", "extractor": "regex", "pattern": r"#?(ORD-\d{4}-\d{3})"},
        "customer_name": {"expected": "John Smith", "extractor": "regex", "pattern": r"for\s+([A-Za-z\s]+)\s+\("},
        "customer_email": {"expected": "john@email.com", "extractor": "email"},
        "product_quantity": {"expected": "2", "extractor": "regex", "pattern": r"(\d+)x\s+Laptop"},
        "product_name": {"expected": "Laptop", "extractor": "regex", "pattern": r"\d+x\s+([A-Za-z]+)"},
        "unit_price": {"expected": "1200", "extractor": "money"},
        "total_amount": {"expected": "2400", "extractor": "money"}
    }
}

# Test various order processing responses
candidates = [
    "Order #ORD-2024-789 confirmed for John Smith (john@email.com) - 2x Laptop at $1,200 each = $2,400 total",
    "John Smith's order ORD-2024-789: 2 Laptops for $1,200 each, total $2,400. Email: john@email.com",
    "Order ORD-2024-789 processed. Customer: John Smith, 2x Laptop, $1,200 per unit, $2,400 total. Contact: john@email.com"
]

# Generate comprehensive report
result = validate_llm_candidates(
    scenario=scenario,
    candidates=candidates,
    threshold=0.70,
    generate_html_report=True,
    html_title="E-commerce Order Processing Validation"
)

print(f"📊 Order processing report: {result['html_report_path']}")
print(f"✅ Overall accuracy: {result['summary']['overall_accuracy']:.1%}")
```

### 🚀 CI/CD Integration

Perfect for automated testing pipelines:

```yaml
# GitHub Actions example
- name: Run LLM Validation Tests
  run: |
    python -c "
    from true_lies import validate_llm_candidates
    scenario = {'name': 'CI Test', 'semantic_reference': 'Test data', 'facts': {}}
    candidates = ['Test response 1', 'Test response 2']
    result = validate_llm_candidates(scenario, candidates, generate_html_report=True)
    print(f'Report: {result[\"html_report_path\"]}')
    "

- name: Upload Validation Report
  uses: actions/upload-artifact@v4
  with:
    name: llm-validation-report
    path: "validation_report_*.html"
```

## 📈 Automatic Metrics

- **Retention Score**: 0.0 - 1.0 (how well it remembers)
- **Facts Retained**: X/Y facts remembered
- **Evaluation**: A, B, C, D, F (automatic grading)
- **Details per Fact**: What was found and what wasn't

## 🚀 Complete Examples

### Example 1: Support Chatbot
```python
from true_lies import ConversationValidator

def test_support_chatbot():
    conv = ConversationValidator()
    
    # Turn 1: User reports problem
    conv.add_turn_and_report(
        user_input="My app doesn't work, I'm user ID 12345",
        bot_response="Hello, I'll help you. What error do you see?",
        expected_facts={'user_id': '12345', 'issue_type': 'app_not_working'},
        title="Turn 1: User reports problem"
    )
    
    # Turn 2: User provides details
    conv.add_turn_and_report(
        user_input="Error 500 on login, email john@company.com",
        bot_response="I understand, error 500 on login. Checking your account.",
        expected_facts={'error_code': '500', 'email': 'john@company.com'},
        title="Turn 2: User provides details"
    )
    
    # Final test
    final_response = "John (ID 12345), your error 500 will be fixed in 2 hours"
    retention = conv.validate_and_report(
        response=final_response,
        facts_to_check=['user_id', 'error_code', 'email'],
        title="Context Retention Test"
    )
    
    return retention['retention_score'] >= 0.8

if __name__ == "__main__":
    test_support_chatbot()
```

### Example 2: E-commerce
```python
from true_lies import ConversationValidator

def test_ecommerce_chatbot():
    conv = ConversationValidator()
    
    # Turn 1: Customer identifies themselves
    conv.add_turn_and_report(
        user_input="Hello, I'm Maria Gonzalez, email maria@store.com, I want to buy a laptop",
        bot_response="Hello Maria! I'll help you with the laptop. Registered email: maria@store.com",
        expected_facts={'customer_name': 'Maria Gonzalez', 'email': 'maria@store.com', 'product_interest': 'laptop'},
        title="Turn 1: Customer identifies themselves"
    )
    
    # Turn 2: Customer specifies budget
    conv.add_turn_and_report(
        user_input="My budget is $1500, I need it for programming",
        bot_response="Perfect Maria, we have laptops for programming in that range. I'll send options to maria@store.com",
        expected_facts={'budget': '1500', 'use_case': 'programming'},
        title="Turn 2: Customer specifies budget"
    )
    
    # Final test
    final_response = "Maria, your programming laptop for $1500 is ready. I'll send the invoice to maria@store.com"
    retention = conv.validate_and_report(
        response=final_response,
        facts_to_check=['customer_name', 'email', 'budget', 'use_case'],
        title="E-commerce Retention Test"
    )
    
    return retention['retention_score'] >= 0.8

if __name__ == "__main__":
    test_ecommerce_chatbot()
```

## 🔍 Advanced Validation (Optional)

For more complex cases, you can also use traditional validation:

```python
from true_lies import create_scenario, validate_llm_candidates

# Facts that MUST be in the response
facts = {
    'policy_number': {'extractor': 'categorical', 'expected': 'POL-2024-001'},
    'premium': {'extractor': 'money', 'expected': '850.00'},
    'coverage_type': {'extractor': 'categorical', 'expected': 'auto insurance'}
}

# Reference text for semantic comparison
reference_text = "Your auto insurance policy #POL-2024-001 has a premium of $850.00"

# Create scenario (with automatic fact weighting)
scenario = create_scenario(
    facts=facts,
    semantic_reference=reference_text,
    semantic_mappings={}  # Weights are applied automatically
)

# Validate responses
candidates = [
    "Policy POL-2024-001 covers your automobile with monthly payments of $850.00",
    "Your car insurance policy POL-2024-001 costs $850 monthly"
]

results = validate_llm_candidates(
    scenario=scenario,
    candidates=candidates,
    threshold=0.7
)
```

### 🎯 Advanced Features

**Automatic Fact Weighting:**
- Values in your `expected` facts are automatically weighted
- Significant improvement in similarity scores (+55% in typical cases)
- No additional configuration needed

**Improved Polarity Detection:**
- Correctly detects negative phrases with "not", "does not", "don't", etc.
- Patterns in English and Spanish
- Avoids false positives with substrings

**Optimized Semantic Mappings:**
- Use simple and specific mappings
- Avoid over-mapping that can worsen scores
- Recommendation: minimal mappings or no mappings

### 💡 Best Practices

**1. Fact Configuration:**
```python
# ✅ CORRECT - For specific numbers
'account_number': {'extractor': 'number', 'expected': '2992'}

# ❌ INCORRECT - For specific numbers
'account_number': {'extractor': 'categorical', 'expected': '2992'}

# ✅ CORRECT - For categories
'account_type': {'extractor': 'categorical', 'expected': 'savings'}
```

**2. Semantic Mappings:**
```python
# ✅ CORRECT - Simple mappings
semantic_mappings = {
    "account": ["cuenta"],
    "balance": ["saldo", "monto"]
}

# ❌ INCORRECT - Excessive mappings
semantic_mappings = {
    "phrases": ["the balance of your", "your term deposit account", ...]  # Too aggressive
}
```

**3. Thresholds:**
- **0.6-0.7**: For strict validation
- **0.5-0.6**: For permissive validation
- **0.8+**: Only for exact cases

## 🎯 Available Extractors

- **`money`**: Monetary values ($1,234.56, USD 27, 100 dollars) - **Improved v0.6.2+**
- **`number`**: General numbers (25, 3.14, 1000)
- **`categorical`**: Categorical values with synonyms - **Improved v0.6.2+**
- **`email`**: Email addresses
- **`phone`**: Phone numbers
- **`hours`**: Time schedules (9:00 AM, 14:30, 3:00 PM)
- **`id`**: Identifiers (USER-001, POL-2024-001)
- **`regex`**: Custom patterns

### 🔧 Extractor Improvements (v0.6.2+)

**Improved `money` extractor:**
- Prioritizes amounts with currency symbols ($, USD, dollars)
- Avoids capturing non-monetary numbers
- Better accuracy in banking scenarios

**Improved `categorical` extractor:**
- Whole word matches (avoids false positives)
- Better detection of specific patterns
- Compatible with exact expected values

## 📚 Complete Documentation

- **[Multi-turn Validation Guide](MULTITURN_VALIDATION_README.md)** - Complete details
- **[Integration Guide](INTEGRATION_GUIDE.md)** - How to integrate into your project
- **[Email Extraction Guide](EMAIL_EXTRACTION_GUIDE.md)** - Advanced extraction
- **[Before/After Comparison](COMPARISON_BEFORE_AFTER.md)** - Library improvements
- **[HTML Reporter Guide](HTML_REPORTER_README.md)** - Complete HTML reporting documentation

## 🎯 Examples & Demos

### HTML Reporter Examples
- **[Basic HTML Report](examples/html_report_example.py)** - Simple report generation
- **[Advanced Filters Demo](examples/advanced_filters_demo.py)** - Advanced filtering capabilities
- **[Temporal Analysis Demo](examples/temporal_analysis_demo.py)** - Temporal analysis features
- **[Advanced Search Demo](examples/advanced_search_demo.py)** - Real-time search functionality
- **[PDF Export Demo](examples/pdf_export_demo.py)** - PDF export capabilities

### CI/CD Integration Examples
- **[GitHub Actions](.github/workflows/chatbot-validation.yml)** - Automated testing workflow
- **[Jenkins Pipeline](ci_cd/Jenkinsfile)** - Jenkins integration
- **[GitLab CI](.gitlab-ci.yml)** - GitLab CI configuration
- **[Test Runner](ci_cd/run_tests_and_report.py)** - Automated test execution

## 🛠️ Diagnostic Tools

### Diagnostic Tool
To diagnose similarity and extraction issues:

```python
from diagnostic_tool import run_custom_diagnosis

# Your configuration
fact_configs = {
    'account_number': {'extractor': 'number', 'expected': '2992'},
    'balance_amount': {'extractor': 'money', 'expected': '3,000.60'}
}
candidates = ["Your account 2992 has $3,000.60"]

# Diagnose
run_custom_diagnosis(
    text="The balance of your Term Deposit account 2992 is $3,000.60",
    fact_configs=fact_configs,
    candidates=candidates
)
```

## 🔄 Changelog

### v0.7.0 (Current)
- ✅ **NEW: HTML Reporter** - Professional HTML reports with interactive dashboards
- ✅ **NEW: Interactive Charts** - Chart.js integration for visual analytics
- ✅ **NEW: Advanced Filtering** - Real-time search and filtering capabilities
- ✅ **NEW: Temporal Analysis** - Daily/Weekly/Monthly performance tracking
- ✅ **NEW: PDF Export** - High-quality PDF reports with full formatting
- ✅ **NEW: CI/CD Integration** - GitHub Actions, Jenkins, GitLab CI support
- ✅ **NEW: Detailed Test Information** - User input, bot response, expected response comparison
- ✅ **NEW: Responsive Design** - Mobile-friendly professional interface

### v0.6.4
- ✅ Improved polarity detection (detects "not", "does not", etc.)
- ✅ Complete negative patterns in English and Spanish
- ✅ Avoids false positives with substrings

### v0.6.3
- ✅ Duplicate function removed
- ✅ Consistent API
- ✅ Clean code

### v0.6.2
- ✅ Automatic fact weighting
- ✅ Improved similarity (+55% in typical cases)
- ✅ Improved money extractor
- ✅ English reporting

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- NLTK for natural language processing capabilities
- The open source community for inspiration and feedback

---

**True Lies - Where AI meets reality** 🎭

*Have questions? Open an issue or contact the development team.*