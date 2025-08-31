"""
Core validation functions for LLM responses
"""

import re
from difflib import SequenceMatcher
from .utils import extract_value_from_text, normalize_extracted_value, load_semantic_mapping, replace_synonyms

def validate_factual(candidate_text, reference_values):
    """
    Validates that candidate_text contains the expected reference_values.
    reference_values: dict of key -> expected value
    """
    details = {}
    all_valid = True
    for key, expected in reference_values.items():
        extracted = extract_value_from_text(candidate_text, key)
        match = normalize_extracted_value(extracted, key) == normalize_extracted_value(expected, key)
        details[key] = {"expected": expected, "found": extracted, "match": match}
        if not match:
            all_valid = False
    return {"is_valid": all_valid, "details": details}


# Normalization helper for semantic validation
def normalize_text(text):
    # lower, remove punctuation and symbols
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text.split()


def validate_semantic(candidate_text, reference_text, threshold=0.7, domain=None):
    """
    Validates semantic similarity between candidate_text and reference_text.
    Uses token overlap for robustness.
    domain: optional string to load domain-specific synonym mappings.
    """
    # Aplicar mapeo de sinónimos si se indica un dominio
    if domain:
        mapping = load_semantic_mapping(domain)
        candidate_text = replace_synonyms(candidate_text, mapping)
        reference_text = replace_synonyms(reference_text, mapping)

    candidate_tokens = set(normalize_text(candidate_text))
    reference_tokens = set(normalize_text(reference_text))
    overlap = candidate_tokens.intersection(reference_tokens)
    similarity_score = len(overlap) / max(len(reference_tokens), 1)
    is_valid = similarity_score >= threshold
    return {"similarity_score": similarity_score, "is_valid": is_valid}


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