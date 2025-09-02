"""
Core validation functions for LLM responses
"""

import re
from difflib import SequenceMatcher
from .utils import extract_value_from_text, load_semantic_mapping, replace_synonyms, normalize_text_advanced

def validate_factual(candidate_text, reference_values, semantic_path=None, domain=None, field_configs=None):
    """
    Validates that candidate_text contains the expected reference_values.
    reference_values: dict of key -> expected value
    semantic_path: optional path to load external synonym mapping for account_type
    domain: optional domain for loading semantic mappings
    field_configs: optional dict of field configurations for custom extraction
    """
    details = {}
    all_valid = True
    # Load semantic mapping for account_type if needed
    mapping = None
    if semantic_path:
        try:
            # Use domain if provided, otherwise fallback to "account_type"
            mapping_domain = domain if domain else "account_type"
            mapping = load_semantic_mapping(mapping_domain, path=semantic_path)
        except Exception:
            mapping = None
    for key, expected in reference_values.items():
        extracted = extract_value_from_text(candidate_text, key, domain=domain, field_configs=field_configs)
        match = False
        # Normalize balances to float before comparing
        if key.lower() in ["balance", "saldo", "amount", "monto"]:
            try:
                extracted_float = float(str(extracted).replace(",", "").replace("$", ""))
                expected_float = float(str(expected).replace(",", "").replace("$", ""))
                match = extracted_float == expected_float
            except Exception:
                match = False
        # For account_type, map synonyms if mapping provided
        elif key.lower() in ["account_type", "tipo_de_cuenta", "tipo"]:
            if mapping:
                extracted_norm = replace_synonyms(str(extracted), mapping)
                expected_norm = replace_synonyms(str(expected), mapping)
                match = extracted_norm.lower() == expected_norm.lower()
            else:
                match = str(extracted).lower() == str(expected).lower()
        # For stock, compare as strings (numbers)
        elif key.lower() in ["stock", "inventory", "quantity"]:
            match = str(extracted) == str(expected)
        # For price, normalize and compare
        elif key.lower() in ["price", "cost", "premium"]:
            try:
                extracted_clean = str(extracted).replace("$", "").replace(",", "")
                expected_clean = str(expected).replace("$", "").replace(",", "")
                match = extracted_clean == expected_clean
            except Exception:
                match = False
        # For product_name and color, compare case-insensitive
        elif key.lower() in ["product_name", "color", "coverage_type", "condition"]:
            match = str(extracted).lower() == str(expected).lower()
        else:
            match = extracted == expected
        details[key] = {"expected": expected, "found": extracted, "match": match}
        if not match:
            all_valid = False
    return {"is_valid": all_valid, "details": details}




def validate_semantic(candidate_text, reference_text, threshold=0.7, domain=None, reference_values=None, semantic_path=None, semantic_mapping=None):
    """
    Validates semantic similarity between candidate_text and reference_text.
    Uses token overlap for robustness, with optional weighting for tokens from reference_values.
    Enhanced with semantic mapping for better synonym handling.
    
    Args:
        candidate_text: Text to validate
        reference_text: Reference text for comparison
        threshold: Similarity threshold (0.0-1.0)
        domain: Domain name for loading semantic mappings
        reference_values: Dict of key->value for weighting key tokens
        semantic_path: Path to semantic mapping file
        semantic_mapping: Direct semantic mapping dictionary
    """
    # Load and apply semantic mapping
    mapping = None
    if semantic_mapping:
        mapping = semantic_mapping
    elif domain:
        mapping = load_semantic_mapping(domain, path=semantic_path) if semantic_path else load_semantic_mapping(domain)
    
    # Apply synonym replacement if mapping exists
    if mapping:
        candidate_text = replace_synonyms(candidate_text, mapping)
        reference_text = replace_synonyms(reference_text, mapping)

    # Advanced normalization
    candidate_tokens = normalize_text_advanced(candidate_text)
    reference_tokens = normalize_text_advanced(reference_text)

    candidate_token_set = set(candidate_tokens)
    reference_token_set = set(reference_tokens)

    # Build weighted key tokens from reference_values
    key_tokens = set()
    if reference_values:
        for key, val in reference_values.items():
            key_tokens.update(normalize_text_advanced(key))
            key_tokens.update(normalize_text_advanced(str(val)))

    # Calculate weighted token overlap
    overlap = candidate_token_set.intersection(reference_token_set)

    # Enhanced weighting: key tokens get weight 3, semantic synonyms get weight 2, others get weight 1
    weighted_overlap_score = 0.0
    weighted_reference_total = 0.0

    for token in reference_token_set:
        if token in key_tokens:
            weight = 3.0  # Highest priority for fact tokens
        elif mapping and any(token in synonyms for synonyms in mapping.values()):
            weight = 2.0  # Medium priority for semantic synonyms
        else:
            weight = 1.0  # Base weight for other tokens
        
        weighted_reference_total += weight
        if token in overlap:
            weighted_overlap_score += weight

    token_score = weighted_overlap_score / max(weighted_reference_total, 1)

    # Sequence similarity score with enhanced normalization
    candidate_normalized = " ".join(candidate_tokens)
    reference_normalized = " ".join(reference_tokens)
    seq_score = SequenceMatcher(None, candidate_normalized, reference_normalized).ratio()

    # Enhanced score combination with semantic boost
    semantic_boost = 0.0
    if mapping and reference_values:
        # Calculate semantic boost based on synonym matches
        synonym_matches = 0
        total_possible_synonyms = 0
        
        for key, val in reference_values.items():
            if key in mapping:
                total_possible_synonyms += len(mapping[key])
                for synonym in mapping[key]:
                    if synonym.lower() in candidate_text.lower():
                        synonym_matches += 1
        
        if total_possible_synonyms > 0:
            semantic_boost = (synonym_matches / total_possible_synonyms) * 0.1  # Small boost

    # Combine scores with semantic enhancement
    base_score = (token_score + seq_score) / 2
    similarity_score = min(1.0, base_score + semantic_boost)
    
    is_valid = similarity_score >= threshold
    
    return {
        "similarity_score": similarity_score,
        "token_score": token_score,
        "seq_score": seq_score,
        "semantic_boost": semantic_boost,
        "is_valid": is_valid,
        "mapping_used": bool(mapping),
        "key_tokens_count": len(key_tokens),
        "overlap_count": len(overlap)
    }


def validate_polarity(
    candidate_text, reference_text, positive_markers=None, negative_markers=None
):
    """
    Validates polarity (positive/negative/neutral) of candidate_text against reference_text.
    """
    if positive_markers is None:
        positive_markers = ["can", "allowed", "unlimited", "earn", "earns", "accrues",
                            "compounds", "applied", "applies", "calculated", "credited",
                            "added", "gains", "yields", "returns", "benefits"]
    if negative_markers is None:
        negative_markers = ["cannot", "not allowed", "no ", "not", "limited", "does not",
                            "can't", "not supposed to", "should not", "not expected to", "never"]

    def extract_polarity(text):
        text_lower = text.lower()
        if any(marker in text_lower for marker in negative_markers):
            return "negative"
        elif any(marker in text_lower for marker in positive_markers):
            return "positive"
        else:
            return "neutral"

    reference_polarity = extract_polarity(reference_text)
    candidate_polarity = extract_polarity(candidate_text)
    polarity_match = (reference_polarity == candidate_polarity) or reference_polarity == "neutral"

    failure_reason = []
    if not polarity_match:
        failure_reason.append("Polarity mismatch")

    return {
        "reference_polarity": reference_polarity,
        "candidate_polarity": candidate_polarity,
        "polarity_match": polarity_match,
        "failure_reason": failure_reason,
    }

def validate_all(candidate_text, facts, reference_text, threshold=0.7, domain=None, semantic_path=None, semantic_mapping=None):
    """
    Validates a candidate text against facts and reference text using all validation types.
    
    Args:
        candidate_text: Text to validate
        facts: Dictionary of expected key-value pairs that MUST be present in the candidate
        reference_text: Reference text for semantic similarity comparison
        threshold: Semantic similarity threshold (0.0-1.0)
        domain: Domain name for loading semantic mappings
        semantic_path: Path to semantic mapping file
        semantic_mapping: Direct semantic mapping dictionary for synonym expansion
    
    Returns:
        dict: Complete validation results
    """
    factual_result = validate_factual(candidate_text, facts, semantic_path=semantic_path, domain=domain)
    semantic_result = validate_semantic(candidate_text, reference_text, threshold, domain, facts, semantic_path=semantic_path, semantic_mapping=semantic_mapping)
    polarity_result = validate_polarity(candidate_text, reference_text)

    is_valid = (
        factual_result["is_valid"] and
        semantic_result["is_valid"] and
        polarity_result["polarity_match"]
    )

    return {
        "reference_text": reference_text,
        "candidate_text": candidate_text,
        "facts": facts,
        "factual": factual_result,
        "semantic": semantic_result,
        "polarity": polarity_result,
        "semantic_score": semantic_result["similarity_score"],
        "is_valid": is_valid,
    }