# True Lies - Separating truth from AI fiction

A Python library for validating LLM (Large Language Model) responses against reference data, with factual, semantic, and polarity validation.

## 🚀 Key Features

- **Factual Validation**: Extracts and validates specific fields from LLM responses
- **Semantic Validation**: Compares semantic similarity with reference text
- **Polarity Validation**: Verifies consistent tone/attitude
- **Generic Extractors**: Reusable extractors for common cases (currency, date, categorical, etc.)
- **Semantic Mapping**: Support for synonyms and domain-specific terms
- **Flexible Configuration**: Customizable fields and extraction patterns
- **Multiple Domains**: Insurance, motorcycles, retail, banking and more
- **Domain Agnostic**: Works with any type of content

## 📦 Installation

```bash
pip install true-lies-validator
```

## 🎯 Quick Start

### "Facts" Concept

**Facts** are the values that **MUST** be present in the LLM response. These are automatically expanded using **semantic mapping** to include synonyms and variations.

**Example:**
- **Fact**: `"coverage_type": "auto insurance"`
- **Semantic Mapping**: `"auto insurance": ["car insurance", "automobile insurance"]`
- **Result**: The system will search for "auto insurance", "car insurance" or "automobile insurance" in the candidate

### Simplified API (Recommended)

```python
from true_lies import create_scenario, validate_llm_candidates

# 1. FACTS - Values that MUST be in the candidate
facts = {
    "policy_number": "POL-2024-001",
    "premium": "$850.00",
    "coverage_type": "auto insurance",
    "liability_limit": "$100,000",
    "expiry_date": "December 31, 2024"
}

# 2. REFERENCE TEXT - Reference text for semantic comparison
reference_text = "Your auto insurance policy #POL-2024-001 has a premium of $850.00 per month..."

# 3. SEMANTIC MAPPING - Synonyms that expand facts for validation
semantic_mapping = {
    "auto insurance": ["car insurance", "automobile insurance"],
    "liability": ["liability coverage", "liability protection"],
    "premium": ["monthly payment", "monthly cost"]
}

# 4. Create scenario
scenario = create_scenario(
    facts={
        'policy_number': {'extractor': 'categorical', 'expected': 'POL-2024-001'},
        'premium': {'extractor': 'money', 'expected': '850.00'},
        'coverage_type': {'extractor': 'categorical', 'expected': 'auto insurance'},
        'liability_limit': {'extractor': 'money', 'expected': '100000'},
        'expiry_date': {'extractor': 'date', 'expected': 'December 31, 2024'}
    },
    semantic_reference=reference_text,
    semantic_mappings=semantic_mapping
)

# 5. CANDIDATES - LLM responses to validate
candidates = [
    "Policy POL-2024-001 covers your automobile with monthly payments of $850.00...",
    "Your car insurance policy POL-2024-001 costs $850 monthly...",
    "Auto policy #POL-2024-001 has a $850.00 monthly premium..."
]

# 6. VALIDATE
results = validate_llm_candidates(
    scenario=scenario,
    candidates=candidates,
    threshold=0.7
)
```

## 🎯 Generic Extractors (New!)

The library includes reusable generic extractors that simplify configuration for common cases:

### Available Extractors

```python
from true_lies.utils import create_field_config_with_extractor

# Available generic extractors (truly domain agnostic):
extractors = {
    'currency': 'Extracts currency values ($1,234.56)',
    'currency_all': 'Extracts all currency values from text',
    'usd_currency': 'Extracts specific USD values (USD 27, dollars 100)',
    'percentage': 'Extracts percentages (12.34%)',
    'date': 'Extracts dates (DD/MM/YYYY, December 31, 2024)',
    'categorical': 'Extracts categorical values based on synonyms',
    'regex': 'Extracts using custom regex patterns',
    'number': 'Extracts general numbers (integers or decimals)',
    'hours': 'Extracts hour values (3 hours, 12 hours)',
    'email': 'Extracts email addresses',
    'phone': 'Extracts phone numbers',
    'id': 'Extracts generic IDs (configurable with pattern)',
    'product_name': 'Extracts product names generically',
    'vehicle_model': 'Extracts vehicle models generically',
    'distance': 'Extracts distance values (miles, km, meters, etc.)',
    'duration': 'Extracts duration values (months, years, days, etc.)',
}
```

### Usage Examples

#### Method 1: Generic Extractors (Simplest)

```python
# Use generic extractors for simple cases
field_configs = {
    "price": create_field_config_with_extractor(
        "price",
        "currency",
        expected_value="$999.99"
    ),
    "stock": create_field_config_with_extractor(
        "stock",
        "number",
        expected_value="25"
    ),
    "product": create_field_config_with_extractor(
        "product",
        "categorical",
        expected_value="iPhone 15 Pro"
    )
}

results = validate_llm_candidates(
    scenario=scenario,
    candidates=candidates,
    threshold=0.7
)
```

#### Method 2: Specific Patterns (Advanced)

```python
# Use specific patterns for complex cases
field_configs = {
    "product_name": create_field_config(
        "product_name",
        patterns=[
            r'(iPhone\s+\d+(?:\s+Pro)?(?:\s+Max)?)',
            r'(Samsung\s+Galaxy\s+\w+)',
            r'(MacBook\s+(?:Pro|Air)\s+\w+)'
        ]
    )
}

results = validate_llm_candidates(
    scenario=scenario,
    candidates=candidates,
    threshold=0.7
)
```

#### Method 3: Hybrid (Best of Both Worlds)

```python
# Combine generic extractors with specific patterns
field_configs = {
    # Use generic extractor for simple cases
    "price": create_field_config_with_extractor(
        "price",
        "currency",
        expected_value="$999.99"
    ),
    # Use specific patterns for complex cases
    "product_name": create_field_config(
        "product_name",
        patterns=[
            r'(iPhone\s+\d+(?:\s+Pro)?(?:\s+Max)?)',
            r'(Samsung\s+Galaxy\s+\w+)',
            r'(MacBook\s+(?:Pro|Air)\s+\w+)'
        ]
    )
}
```

## 📊 Results

The function returns a dictionary with detailed information:

```python
{
    "total_candidates": 3,
    "factual_pass": 1,
    "fully_valid": 1,
    "success_rate": 33.3,
    "results": [
        {
            "index": 1,
            "candidate": "...",
            "factual": {"is_valid": True, "details": {...}},
            "semantic": {
                "similarity_score": 0.85,
                "token_score": 0.90,
                "seq_score": 0.80,
                "semantic_boost": 0.05,
                "is_valid": True
            },
            "polarity": {"polarity_match": True, ...},
            "is_valid": True
        }
    ],
    "facts": {...},  # Original facts that were validated
    "reference_text": "..."
}
```

## 🏗️ Supported Domains

### Insurance (`insurance`)
- `policy_number`: Policy numbers
- `premium`: Monthly premiums
- `coverage_type`: Coverage types
- `liability_limit`: Liability limits
- `expiry_date`: Expiration dates

### Motorcycles (`motorcycle_dealership`)
- `motorcycle_model`: Motorcycle models
- `price`: Prices
- `mileage`: Mileage
- `warranty`: Warranties
- `condition`: Condition

### Retail (`retail`)
- `product_name`: Product names
- `price`: Prices
- `stock`: Stock levels
- `brand`: Brands
- `category`: Categories

### Banking (`banking`)
- `account_number`: Account numbers
- `balance`: Account balances
- `transaction_amount`: Transaction amounts
- `account_type`: Account types

### Energy (`energy`)
- `meter_number`: Meter numbers
- `consumption`: Consumption values
- `billing_period`: Billing periods
- `rate_type`: Rate types

## 🔍 Enhanced Semantic Validation

Semantic validation includes:

- **Token Overlap**: Normalized token comparison
- **Sequence Similarity**: Sequence similarity using difflib
- **Semantic Boost**: Bonus for synonym matches
- **Weighted Scoring**: Higher weight for key fact tokens

### Semantic Scoring

```python
# Token weights:
# - Fact tokens: weight 3.0
# - Semantic synonyms: weight 2.0  
# - Other tokens: weight 1.0

# Final score = (token_score + seq_score) / 2 + semantic_boost
```

## 🔧 Individual API

### validate_llm_candidates()

To validate a single candidate with all validation types:

```python
from true_lies import create_scenario, validate_llm_candidates

# Facts that MUST be in the candidate
facts = {
    "policy_number": "POL-2024-001",
    "premium": "$850.00",
    "coverage_type": "auto insurance"
}

reference_text = "Your auto insurance policy #POL-2024-001 has a premium of $850.00"

candidate = "Policy POL-2024-001 covers your automobile with monthly payments of $850.00"

# Semantic mapping to expand facts
semantic_mapping = {
    "auto insurance": ["car insurance", "automobile insurance"],
    "premium": ["monthly payment", "monthly cost"]
}

# Create scenario
scenario = create_scenario(
    facts={
        'policy_number': {'extractor': 'categorical', 'expected': 'POL-2024-001'},
        'premium': {'extractor': 'money', 'expected': '850.00'},
        'coverage_type': {'extractor': 'categorical', 'expected': 'auto insurance'}
    },
    semantic_reference=reference_text,
    semantic_mappings=semantic_mapping
)

# Validate
results = validate_llm_candidates(
    scenario=scenario,
    candidates=[candidate],
    threshold=0.7
)
```

## 🔄 Migration Guide

### Migrating from Specific Patterns to Generic Extractors

#### Before (v0.2.0):
```python
from true_lies.utils import create_field_config

field_configs = {
    "price": create_field_config(
        "price",
        patterns=[r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)']
    )
}
```

#### After (v0.4.0+):
```python
from true_lies.utils import create_field_config_with_extractor

field_configs = {
    "price": create_field_config_with_extractor(
        "price",
        "currency",
        expected_value="$999.99"
    )
}
```

## 📝 Examples

### Example 1: Insurance Policy Validation

```python
# Configuration for insurance policies
facts = {
    "policy_number": "POL-2024-001",
    "premium": "$850",
    "coverage": "auto"
}

reference_text = "Your auto insurance policy POL-2024-001 has a premium of $850..."

candidates = [
    "Policy POL-2024-001 covers your automobile with monthly payments of $850.00...",
    "Your car insurance policy POL-2024-001 costs $850 monthly...",
    "Auto policy #POL-2024-001 has a $850.00 monthly premium..."
]

# Create scenario
scenario = create_scenario(
    facts={
        'policy_number': {'extractor': 'categorical', 'expected': 'POL-2024-001'},
        'premium': {'extractor': 'money', 'expected': '850'},
        'coverage': {'extractor': 'categorical', 'expected': 'auto'}
    },
    semantic_reference=reference_text,
    semantic_mappings={}
)

results = validate_llm_candidates(
    scenario=scenario,
    candidates=candidates,
    threshold=0.7
)
```

### Example 2: Retail Inventory Validation

```python
# Configuration for retail products
facts = {
    "product_name": "iPhone 15 Pro",
    "stock": "25",
    "price": "$999.99",
    "color": "Space Black"
}

field_configs = {
    "product_name": create_field_config_with_extractor(
        "product_name",
        "categorical",
        expected_value="iPhone 15 Pro",
        patterns={
            "iPhone 15 Pro": ["iPhone 15 Pro", "iPhone15Pro", "iPhone 15Pro"],
            "Samsung Galaxy S24": ["Samsung Galaxy S24", "Galaxy S24", "S24"]
        }
    ),
    "stock": create_field_config_with_extractor(
        "stock",
        "number",
        expected_value="25"
    ),
    "price": create_field_config_with_extractor(
        "price",
        "currency",
        expected_value="$999.99"
    ),
    "color": create_field_config_with_extractor(
        "color",
        "categorical",
        expected_value="Space Black",
        patterns={
            "Space Black": ["Space Black", "black", "space black"],
            "Space Gray": ["Space Gray", "gray", "space gray"],
            "Silver": ["Silver", "silver"]
        }
    )
}

reference_text = "The iPhone 15 Pro is currently in stock with 25 units available..."

results = validate_llm_candidates(
    scenario=scenario,
    candidates=candidates,
    threshold=0.7
)
```

### Example: Inventory Validation

```python
# Configuration for motorcycles
facts = {
    "motorcycle_model": "Honda CBR 600RR",
    "price": "$12,500",
    "mileage": "1500",
    "warranty": "6-month",
    "condition": "excellent"
}

reference_text = "The Honda CBR 600RR is available for $12,500..."

results = validate_llm_candidates(
    scenario=scenario,
    candidates=candidates,
    threshold=0.7
)
```

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- NLTK for natural language processing capabilities
- The open source community for inspiration and feedback

---

**True Lies - Where AI meets reality** 🎭
