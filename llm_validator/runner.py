"""
Runner for executing validation scenarios and printing formatted reports
"""

from .core import validate_factual, validate_semantic, validate_polarity

def run_validation_scenario(scenario_name, reference_text, reference_values, candidates, threshold=0.7):
    """
    Runs a validation scenario and prints a formatted report.
    """
    print(f"Testing scenario: {scenario_name}")
    print(f"Reference: {reference_text}")
    for key, val in reference_values.items():
        print(f"Expected {key}: {val}")
    print("-" * 80)

    total_candidates = len(candidates)
    factual_pass = 0
    fully_valid = 0
    results = []

    for i, candidate in enumerate(candidates, 1):
        factual_result = validate_factual(candidate, reference_values)
        semantic_result = validate_semantic(candidate, reference_text, threshold=threshold)
        polarity_result = validate_polarity(candidate, reference_text)

        is_factually_accurate = factual_result["is_valid"]
        is_fully_valid = is_factually_accurate and semantic_result["is_valid"] and polarity_result["polarity_match"]

        if is_factually_accurate:
            factual_pass += 1
        if is_fully_valid:
            fully_valid += 1

        results.append({
            "index": i,
            "candidate": candidate,
            "factual": factual_result,
            "semantic": semantic_result,
            "polarity": polarity_result,
            "is_valid": is_fully_valid,
        })

    _print_summary(total_candidates, factual_pass, fully_valid)
    _print_detailed_results(results)


def _print_summary(total_candidates, factual_pass, fully_valid):
    success_rate = (fully_valid / total_candidates * 100) if total_candidates else 0.0
    print("\nSUMMARY:")
    print(f"Total candidates: {total_candidates}")
    print(f"Factually accurate: {factual_pass}")
    print(f"Fully valid (factual + semantic): {fully_valid}")
    print(f"Success rate: {success_rate:.1f}%")


def _print_detailed_results(results):
    print("\nDETAILED RESULTS:")
    for r in results:
        status = "✅ VALID" if r["is_valid"] else "❌ INVALID"
        balance_ok = r["factual"]["details"].get("balance", {}).get("match")
        acct_type_ok = r["factual"]["details"].get("account_type", {}).get("match")
        sim_score = r["semantic"]["similarity_score"]

        print(f"Candidate {r['index']}:{status}")
        if balance_ok is not None:
            print(f" Balance: {balance_ok},Account Type: {acct_type_ok}, Similarity: {sim_score:.3f}")
        else:
            print(f" Similarity: {sim_score:.3f}")
        if "account_type" in r["factual"]["details"]:
            print(f" Extracted Type: {r['factual']['details']['account_type'].get('found')}")
        print(f" Text: {r['candidate'][:80]}...")
        if not r["polarity"]["polarity_match"]:
            print(f" Failure Reason: {'; '.join(r['polarity']['failure_reason'])}")
        print()