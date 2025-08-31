from llm_validator import core

candidate = "Your term deposit shows $5,250.75. Daily interest is applied to this account"
reference_values = {"balance": "5250.75", "account_type": "term_deposit"}
reference_text = "Your term deposit balance is $5,250.75. This account earns interest daily."

factual_result = core.validate_factual(candidate, reference_values)
semantic_result = core.validate_semantic(candidate, reference_text)
polarity_result = core.validate_polarity(candidate, reference_text)

print("Factual:", factual_result)
print("Semantic:", semantic_result)
print("Polarity:", polarity_result)