from true_lies import validation_core as core

# --------------------------
# Original tests
# --------------------------
def test_validate_factual_match():
    candidate = "price: 299.99, color: red, size: L"
    reference_values = {"price": "299.99", "color": "red", "size": "L"}
    result = core.validate_factual(candidate, reference_values)
    assert result["is_valid"] is True
    for detail in result["details"].values():
        assert detail["match"] is True

def test_validate_factual_mismatch():
    candidate = "price: 299.99, color: blue, size: L"
    reference_values = {"price": "299.99", "color": "red", "size": "L"}
    result = core.validate_factual(candidate, reference_values)
    assert result["is_valid"] is False
    assert result["details"]["color"]["match"] is False

def test_validate_semantic_high_similarity():
    candidate = "The red shirt costs $299.99 and is size L"
    reference = "price: 299.99, color: red, size: L"
    result = core.validate_semantic(candidate, reference, threshold=0.5)
    assert result["is_valid"] is True
    assert 0 <= result["similarity_score"] <= 1

def test_validate_semantic_low_similarity():
    candidate = "A green hat for $49"
    reference = "price: 299.99, color: red, size: L"
    result = core.validate_semantic(candidate, reference, threshold=0.5)
    assert result["is_valid"] is False

def test_validate_polarity_positive():
    candidate = "You can earn rewards daily"
    reference = "This account earns interest daily"
    result = core.validate_polarity(candidate, reference)
    assert result["polarity_match"] is True

def test_validate_polarity_negative():
    candidate = "You cannot earn rewards"
    reference = "This account earns interest daily"
    result = core.validate_polarity(candidate, reference)
    assert result["polarity_match"] is False
    assert "Polarity mismatch" in result["failure_reason"]

# --------------------------
# Banking scenarios
# --------------------------
def test_bank_factual():
    candidate = "balance: 5250.75, account_type: term_deposit"
    reference_values = {"balance": "5250.75", "account_type": "term_deposit"}
    result = core.validate_factual(candidate, reference_values)
    assert result["is_valid"] is True

def test_bank_polarity_negative():
    candidate = "You cannot earn interest on this account"
    reference = "This account earns interest daily"
    result = core.validate_polarity(candidate, reference)
    assert result["polarity_match"] is False

# --------------------------
# Energy utility scenarios
# --------------------------
def test_energy_factual():
    candidate = "consumption: 350 kWh, account: residential"
    reference_values = {"consumption": "350", "account": "residential"}
    result = core.validate_factual(candidate, reference_values)
    assert result["is_valid"] is True

def test_energy_semantic():
    candidate = "Your home used 350 kilowatt hours last month"
    reference = "consumption: 350 kWh, account: residential"
    result = core.validate_semantic(candidate, reference, threshold=0.5, domain="energy")
    assert result["is_valid"] is True

# --------------------------
# Retail scenarios
# --------------------------
def test_retail_factual():
    candidate = "price: 49.99, color: blue, size: M"
    reference_values = {"price": "49.99", "color": "blue", "size": "M"}
    result = core.validate_factual(candidate, reference_values)
    assert result["is_valid"] is True

def test_retail_semantic_low_similarity():
    candidate = "A red hat for $59"
    reference = "price: 49.99, color: blue, size: M"
    result = core.validate_semantic(candidate, reference, threshold=0.5)
    assert result["is_valid"] is False

def test_retail_polarity_positive():
    candidate = "You can purchase this item now"
    reference = "Item is available for purchase"
    result = core.validate_polarity(candidate, reference)
    assert result["polarity_match"] is True

# --------------------------
# validate_all tests
# --------------------------
def test_validate_all_pass():
    candidate = "balance: 100, account_type: savings"
    reference_values = {"balance": "100", "account_type": "savings"}
    reference_text = "Your savings account balance is 100"

    result = core.validate_all(candidate, reference_values, reference_text, domain="banking")

    # Debug detallado por componente
    print("\n=== DEBUG validate_all ===")
    print("Overall is_valid:", result.get("is_valid"))

    # Factual
    factual = result.get("factual")
    if factual:
        print("\n[Factual Validation]")
        for key, match in factual.items():
            print(f"  Field '{key}': match={match}")

    # Semantic
    semantic = result.get("semantic")
    if semantic:
        print("\n[Semantic Validation]")
        print("is_valid:", semantic.get("is_valid"))
        print("similarity_score:", semantic.get("similarity_score"))

    # Polarity
    polarity = result.get("polarity")
    if polarity:
        print("\n[Polarity Validation]")
        print("polarity_match:", polarity.get("polarity_match"))
        if not polarity.get("polarity_match"):
            print("failure_reason:", polarity.get("failure_reason"))

    print("=========================\n")

    # Asserts finales
    assert result["is_valid"] is True

def test_validate_all_factual_fail():
    candidate = "balance: 200, account_type: savings"
    reference_values = {"balance": "100", "account_type": "savings"}
    reference_text = "Your savings account balance is 100"
    result = core.validate_all(candidate, reference_values, reference_text, domain="banking")
    assert result["is_valid"] is False
    assert result["factual"]["is_valid"] is False

def test_validate_all_semantic_fail():
    candidate = "balance: 100, account_type: savings"
    reference_values = {"balance": "100", "account_type": "savings"}
    reference_text = "Completely unrelated text"
    result = core.validate_all(candidate, reference_values, reference_text, domain="banking")
    assert result["is_valid"] is False
    assert result["semantic"]["is_valid"] is False

def test_validate_all_polarity_fail():
    candidate = "You cannot withdraw funds"
    reference_values = {}
    reference_text = "You can withdraw funds"
    result = core.validate_all(candidate, reference_values, reference_text)
    assert result["is_valid"] is False
    assert result["polarity"]["polarity_match"] is False


# --------------------------
# Custom polarity direction test
# --------------------------
def test_polarity_reference_negative_candidate_positive():
    """
    Test that polarity validation fails when reference is negative and candidate is positive.
    """
    candidate = "You can withdraw funds at any time"
    reference = "You cannot withdraw funds"
    result = core.validate_polarity(candidate, reference)
    assert result["polarity_match"] is False
    assert "Polarity mismatch" in result["failure_reason"]