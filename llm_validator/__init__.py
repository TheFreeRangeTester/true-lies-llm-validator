"""
llm_validator: 🚀 LLM Response Validator Library

This library helps you validate LLM responses on multiple dimensions:
- Factual correctness
- Semantic similarity
- Polarity (positive/negative)

You can use it to check candidate responses against reference values and texts,
with support for domain-specific synonym mappings.

Public functions:
- validate_llm_response (NEW - Recommended API)
- validate_factual
- validate_semantic
- validate_polarity
- validate_all
- run_validation_scenario (Legacy)

Example usage:

from llm_validator import validate_llm_response

# New simplified API
facts = {"policy_number": "POL-2024-001", "premium": "$850.00"}
reference_text = "Your auto insurance policy #POL-2024-001 has a premium of $850.00"
candidates = ["Policy POL-2024-001 costs $850.00", "Your car insurance is $850"]

results = validate_llm_response(
    facts=facts,
    reference_text=reference_text,
    candidates=candidates,
    semantic_mapping={"auto insurance": ["car insurance"]},
    threshold=0.7
)

# Legacy API
from llm_validator import run_validation_scenario
results = run_validation_scenario(
    scenario_name="insurance",
    reference_text=reference_text,
    reference_values=facts,  # Note: legacy API still uses reference_values
    candidates=candidates,
    domain="insurance"
)
"""

from .core import validate_factual, validate_semantic, validate_polarity, validate_all
from .runner import validate_llm_response, run_validation_scenario

__all__ = [
    'validate_llm_response',  # New main function
    'validate_factual',
    'validate_semantic', 
    'validate_polarity',
    'validate_all',
    'run_validation_scenario'  # Legacy function
]