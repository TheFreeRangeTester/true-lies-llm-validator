<div align="center">
  <img src="https://raw.githubusercontent.com/TheFreeRangeTester/true-lies-llm-validator/main/assets/logo.png" alt="True Lies Validator Logo" width="300">
</div>

# True Lies Validator 🎭

**The easiest library to validate LLM and chatbot responses**

Validates if your LLM or chatbot is telling the truth, remembering context and maintaining coherence. Perfect for automated conversation testing.

## 🚀 Quick Installation

```bash
# Install the library
pip install true-lies-validator

# Verify installation
python -c "from true_lies import ConversationValidator, HTMLReporter; print('✅ Installed successfully')"
```

> **📦 Current version: 0.8.0** - With interactive HTML reports, improved dashboards, and simplified CI/CD integration

## ⚡ Get Started in 2 Minutes

True Lies supports **two types of validation**:

1. **Candidate Validation** - Validate LLM responses against expected facts and semantic reference
2. **Multi-turn Conversation Validation** - Test if LLMs remember context across conversation turns

### Type 1: Candidate Validation (Most Common)

This is the most basic and common way to use True Lies - validate multiple LLM responses against a scenario:

```python
from true_lies import validate_llm_candidates, create_scenario

# Define your test scenario
scenario = create_scenario(
    facts={
        "patient_name": {"expected": "John Smith", "extractor": "regex", "pattern": r"(?:patient|name):\s*([A-Z][a-z]+\s+[A-Z][a-z]+)"},
        "appointment_date": {"expected": "March 15, 2024", "extractor": "regex", "pattern": r"(\w+\s+\d{1,2},\s+\d{4})"},
        "doctor": {"expected": "Dr. Johnson", "extractor": "regex", "pattern": r"(Dr\.\s+\w+)"}
    },
    semantic_reference="Patient John Smith has an appointment with Dr. Johnson on March 15, 2024"
)

# Test multiple LLM responses
candidates = [
    "John Smith's appointment with Dr. Johnson is scheduled for March 15, 2024",
    "Patient: John Smith. Doctor: Dr. Johnson. Date: March 15, 2024",
    "Appointment for John Smith on March 15, 2024 with Dr. Johnson"
]

# Validate all candidates and generate HTML report
result = validate_llm_candidates(
    scenario=scenario,
    candidates=candidates,
    threshold=0.65,
    generate_html_report=True,
    html_title="Appointment Booking Validation"
)

print(f"📊 Report: {result['html_report_path']}")
print(f"✅ Passed: {result['summary']['passed_count']}/{result['summary']['total_count']}")
```

**💡 Best Practice:** Keep your facts and candidates in separate files (JSON/YAML) for better organization. See our [live demo](https://github.com/TheFreeRangeTester/demo_truelies) for examples.

### Type 2: Multi-turn Conversation Validation

Test if your LLM remembers context across multiple conversation turns:

```python
from true_lies import ConversationValidator

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

# Test: Does the bot remember everything from previous turns?
final_response = "John (ID 12345), your error 500 will be fixed in 2 hours"
retention = conv.validate_and_report(
    response=final_response,
    facts_to_check=['user_id', 'error_code', 'email'],
    title="Context Retention Test"
)

print(f"📊 Retention Score: {retention['retention_score']:.2f}")
print(f"✅ Facts Retained: {retention['facts_retained']}/{retention['total_facts']}")
```

### 📁 Best Practice: External Data Files

For production use, keep your test data in separate files:

**scenario.json:**

```json
{
  "name": "Appointment Booking Test",
  "semantic_reference": "Patient John Smith has an appointment with Dr. Johnson on March 15, 2024",
  "facts": {
    "patient_name": {
      "expected": "John Smith",
      "extractor": "regex",
      "pattern": "(?:patient|name):\\s*([A-Z][a-z]+\\s+[A-Z][a-z]+)"
    },
    "appointment_date": {
      "expected": "March 15, 2024",
      "extractor": "regex",
      "pattern": "(\\w+\\s+\\d{1,2},\\s+\\d{4})"
    }
  }
}
```

**candidates.json:**

```json
[
  "John Smith's appointment with Dr. Johnson is scheduled for March 15, 2024",
  "Patient: John Smith. Date: March 15, 2024",
  "Appointment for John Smith on March 15"
]
```

**test_appointment.py:**

```python
import json
from true_lies import validate_llm_candidates

# Load test data
with open('scenario.json', 'r') as f:
    scenario = json.load(f)

with open('candidates.json', 'r') as f:
    candidates = json.load(f)

# Run validation
result = validate_llm_candidates(
    scenario=scenario,
    candidates=candidates,
    threshold=0.65,
    generate_html_report=True
)

print(f"✅ Passed: {result['summary']['passed_count']}/{result['summary']['total_count']}")
```

**See it in action:** Check out our [live demo project](https://github.com/TheFreeRangeTester/demo_truelies) for a complete example with external data files.

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
from true_lies import validate_llm_candidates, create_scenario

# Define your test scenario
scenario = create_scenario(
    facts={
        "policy_number": {"expected": "POL-2024-001", "extractor": "regex", "pattern": r"#?(POL-\d{4}-\d{3})"},
        "premium_amount": {"expected": "850.00", "extractor": "money"},
        "insurance_type": {"expected": "auto insurance", "extractor": "categorical",
                          "patterns": {"auto insurance": ["auto insurance", "car insurance", "vehicle insurance"]}}
    },
    semantic_reference="Your auto insurance policy #POL-2024-001 has a premium of $850.00"
)

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

## 🚀 CI/CD Integration

True Lies integrates seamlessly into CI/CD pipelines for automated LLM validation. Here's a complete example based on a [real project](https://github.com/TheFreeRangeTester/demo_truelies):

### Complete Example with GitHub Actions

**1. Project structure:**

```
your-project/
├── .github/
│   └── workflows/
│       └── test-and-report.yml    # GitHub Actions workflow
├── tests/
│   └── test_chatbot.py            # Your tests with True Lies
├── true_lies_reporting/           # Reports and history (auto-generated)
└── requirements.txt               # Includes true-lies-validator
```

**2. Test file (`tests/test_chatbot.py`):**

```python
from true_lies import validate_llm_candidates, create_scenario

def test_support_chatbot():
    """Technical support chatbot test"""

    scenario = create_scenario(
        facts={
            "user_id": {"expected": "12345", "extractor": "regex", "pattern": r"ID\s*(\d+)"},
            "issue": {"expected": "login", "extractor": "categorical",
                     "patterns": {"login": ["login", "sign in", "log in"]}}
        },
        semantic_reference="User ID 12345 reports login problem"
    )

    candidates = [
        "User ID 12345 has a login problem",
        "User with ID 12345 cannot sign in to the system",
    ]

    result = validate_llm_candidates(
        scenario=scenario,
        candidates=candidates,
        threshold=0.65,
        generate_html_report=True,
        html_title="Support Chatbot Test"
    )

    print(f"✅ Report generated: {result['html_report_path']}")
    return result

if __name__ == "__main__":
    test_support_chatbot()
```

**3. GitHub Actions Workflow (`.github/workflows/test-and-report.yml`):**

```yaml
name: LLM Validation with True Lies

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-and-report:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"

      - name: Install dependencies
        run: |
          pip install true-lies-validator
          pip install -r requirements.txt

      - name: Run tests and generate reports
        run: |
          python tests/test_chatbot.py

      - name: Upload HTML reports as artifacts
        uses: actions/upload-artifact@v4
        with:
          name: llm-validation-reports
          path: |
            *.html
            true_lies_reporting/
          retention-days: 30

      - name: Publish reports to GitHub Pages (optional)
        if: github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./
          publish_branch: gh-pages
          keep_files: false
```

**4. View the reports:**

- **As artifacts:** In GitHub Actions → Your workflow → Artifacts → Download `llm-validation-reports`
- **On GitHub Pages:** Configure GitHub Pages and access `https://your-username.github.io/your-repo/`
- **Live example:** [Demo True Lies](https://thefreerangetester.github.io/demo_truelies/)

### 🎯 CI/CD Features with True Lies:

- ✅ **Automatic execution** - Tests run on every push/PR
- ✅ **Automatic HTML reports** - Generated and saved automatically
- ✅ **Preserved history** - Historical data maintained in `true_lies_reporting/`
- ✅ **GitHub Pages publishing** - Reports accessible from any browser
- ✅ **Trends and metrics** - Dashboards with automatic temporal analysis
- ✅ **No complex setup** - Just add the workflow and run your tests

## 📈 Automatic Metrics

- **Retention Score**: 0.0 - 1.0 (how well it remembers)
- **Facts Retained**: X/Y facts remembered
- **Evaluation**: A, B, C, D, F (automatic grading)
- **Details per Fact**: What was found and what wasn't

## 🔍 Advanced Validation (Optional)

For more complex cases, you can also use traditional validation with scenarios:

```python
from true_lies import create_scenario, validate_llm_candidates

# Facts that MUST be in the response
facts = {
    'policy_number': {'extractor': 'regex', 'expected': 'POL-2024-001', 'pattern': r'POL-\d{4}-\d{3}'},
    'premium': {'extractor': 'money', 'expected': '850.00'},
    'coverage_type': {'extractor': 'categorical', 'expected': 'auto insurance',
                      'patterns': {'auto insurance': ['auto insurance', 'car insurance']}}
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
    threshold=0.7,
    generate_html_report=True
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
'account_number': {'extractor': 'regex', 'expected': '2992', 'pattern': r'\d+'}

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
    "balance": ["saldo", "amount"]
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

- **`money`**: Monetary values ($1,234.56, USD 27, 100 dollars) [[memory:7971937]]
- **`number`**: General numbers (25, 3.14, 1000)
- **`categorical`**: Categorical values with synonyms [[memory:7877404]]
- **`email`**: Email addresses
- **`phone`**: Phone numbers
- **`hours`**: Time schedules (9:00 AM, 14:30, 3:00 PM)
- **`id`**: Identifiers (USER-001, POL-2024-001)
- **`regex`**: Custom patterns

### 🔧 Extractor Improvements

**Improved `money` extractor:**

- Prioritizes amounts with currency symbols ($, USD, dollars)
- Avoids capturing non-monetary numbers
- Better accuracy in banking scenarios
- Uses the `money` key exclusively (not `currency` or other aliases)

**Improved `categorical` extractor:**

- Whole word matches (avoids false positives)
- Better detection of specific patterns
- Compatible with exact expected values
- Domain-agnostic - use categorical patterns for domain-specific needs

## 🎯 Examples & Demos

### Available Examples

- **[Basic HTML Report](examples/html_report_example.py)** - Simple report generation
- **[Advanced Filters Demo](examples/advanced_filters_demo.py)** - Advanced filtering capabilities
- **[Temporal Analysis Demo](examples/temporal_analysis_demo.py)** - Temporal analysis features
- **[Advanced Search Demo](examples/advanced_search_demo.py)** - Real-time search functionality
- **[PDF Export Demo](examples/pdf_export_demo.py)** - PDF export capabilities

### Real CI/CD Example

- **[Demo True Lies](https://github.com/TheFreeRangeTester/demo_truelies)** - Complete project with GitHub Actions
- **[Live Reports](https://thefreerangetester.github.io/demo_truelies/)** - Reports published on GitHub Pages

## 🛠️ Diagnostic Tool

To diagnose similarity and extraction issues:

```python
from diagnostic_tool import run_custom_diagnosis

# Your configuration
fact_configs = {
    'account_number': {'extractor': 'regex', 'expected': '2992', 'pattern': r'\d+'},
    'balance_amount': {'extractor': 'money', 'expected': '3000.60'}
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

### v0.8.0 (Current) - 2024-12-31

**🎨 Interactive Dashboard Improvements:**

- ✅ Interactive expand/collapse functionality for "View Details" buttons
- ✅ Dynamic button text changes ("View Details" ↔ "Hide Details")
- ✅ Visual feedback with button color changes (blue → red when expanded)
- ✅ Card-style styling with left border and smooth transitions
- ✅ Professional styling for detailed test information

**📊 Enhanced Analytics & Visualizations:**

- ✅ Similarity Score Trend chart showing semantic similarity over time
- ✅ Fact Retention Trend chart tracking percentage of facts retained
- ✅ Performance Trend with configurable target line
- ✅ Historical data persistence in `true_lies_reporting/validation_history.json`
- ✅ Automatic data cleanup (30-day retention policy)

**🚀 Simplified HTML Report Generation:**

- ✅ One-line HTML report generation with `generate_html_report=True` parameter
- ✅ Automatic file naming with timestamps
- ✅ Integration with `validate_llm_candidates` function
- ✅ Streamlined API for report generation

**🔧 Interactive Table Improvements:**

- ✅ Sortable columns with click-to-sort functionality
- ✅ Toggle between ascending and descending order
- ✅ Row filtering to handle inconsistent table structures
- ✅ Visual sort indicators (↕, ↑, ↓) on column headers

### v0.7.0 - 2024-12-30

- ✅ **HTML Reporter** - Professional HTML reports with interactive dashboards
- ✅ **Interactive Charts** - Chart.js integration for visual analytics
- ✅ **Advanced Filtering** - Real-time search and filtering capabilities
- ✅ **Temporal Analysis** - Daily/Weekly/Monthly performance tracking
- ✅ **CI/CD Integration** - GitHub Actions, Jenkins, GitLab CI support

### v0.6.0 - 2024-12-29

- ✅ Multi-turn conversation validation
- ✅ Automatic fact extraction and validation
- ✅ Comprehensive reporting system
- ✅ Support for various data types (emails, money, dates, IDs)

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

- The open source community for inspiration and feedback

---

**True Lies - Where AI meets reality** 🎭

_Have questions? Open an issue or contact the development team._
