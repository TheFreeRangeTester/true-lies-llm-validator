"""
Runner for executing validation scenarios and printing formatted reports
"""

from .core import validate_factual, validate_semantic, validate_polarity
from .utils import load_semantic_mapping
import json
from pathlib import Path

def validate_llm_response(facts, reference_text, candidates, semantic_mapping=None, threshold=0.7, domain=None, field_configs=None):
    """
    Validates LLM responses against expected facts and semantic similarity.
    
    Args:
        facts (dict): Dictionary of expected key-value pairs to extract and validate
        reference_text (str): Reference text for semantic similarity comparison
        candidates (list): List of candidate texts to validate
        semantic_mapping (dict, optional): Dictionary of synonyms for semantic enhancement
        threshold (float): Semantic similarity threshold (0.0-1.0), default 0.7
        domain (str, optional): Domain name for loading semantic mappings from files
        field_configs (dict, optional): Custom field extraction configurations
    
    Returns:
        dict: Validation results with detailed information
    """
    # Load semantic mapping if provided or from domain
    semantic_path = None
    if semantic_mapping:
        # Use provided semantic mapping
        pass
    elif domain:
        # Try to load from domain file
        try:
            semantic_mapping = load_semantic_mapping(domain)
            semantic_path = f"llm_validator/semantic_data/{domain}.json"
        except Exception:
            semantic_mapping = {}
    
    total_candidates = len(candidates)
    factual_pass = 0
    fully_valid = 0
    results = []

    print(f"🔍 VALIDATING LLM RESPONSES")
    print(f"📋 Expected Facts: {len(facts)} fields")
    print(f"📝 Reference Text: {reference_text[:100]}{'...' if len(reference_text) > 100 else ''}")
    print(f"🎯 Candidates: {total_candidates}")
    print(f"📊 Threshold: {threshold}")
    if semantic_mapping:
        print(f"🗂️  Semantic Mapping: {len(semantic_mapping)} synonym groups")
    print("-" * 80)

    for i, candidate in enumerate(candidates, 1):
        # Validate factual accuracy
        factual_result = validate_factual(
            candidate, 
            facts, 
            semantic_path=semantic_path, 
            domain=domain, 
            field_configs=field_configs
        )
        
        # Validate semantic similarity
        semantic_result = validate_semantic(
            candidate, 
            reference_text, 
            threshold=threshold, 
            domain=domain, 
            semantic_path=semantic_path,
            semantic_mapping=semantic_mapping,
            reference_values=facts
        )
        
        # Validate polarity
        polarity_result = validate_polarity(candidate, reference_text)

        # Determine overall validity
        is_factually_accurate = factual_result["is_valid"]
        is_semantically_valid = semantic_result["is_valid"]
        is_polarity_valid = polarity_result["polarity_match"]
        is_fully_valid = is_factually_accurate and is_semantically_valid and is_polarity_valid

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

    # Print results
    _print_enhanced_summary(total_candidates, factual_pass, fully_valid, facts)
    _print_enhanced_detailed_results(results, facts)
    
    return {
        "total_candidates": total_candidates,
        "factual_pass": factual_pass,
        "fully_valid": fully_valid,
        "success_rate": (fully_valid / total_candidates * 100) if total_candidates else 0.0,
        "results": results,
        "facts": facts,
        "reference_text": reference_text
    }


def run_validation_scenario(scenario_name, reference_text, reference_values, candidates, threshold=0.7, domain=None, semantic_path=None, field_configs=None):
    """
    Legacy function for backward compatibility.
    Runs a validation scenario and prints a formatted report.
    
    Args:
        scenario_name: Name of the validation scenario
        reference_text: Reference text to compare against
        reference_values: Dictionary of expected values
        candidates: List of candidate texts to validate
        threshold: Semantic similarity threshold (0.0-1.0)
        domain: Domain for loading semantic mappings
        semantic_path: Optional path to semantic mapping file
        field_configs: Optional dictionary of field configurations for custom extraction
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
        factual_result = validate_factual(candidate, reference_values, semantic_path=semantic_path, domain=domain, field_configs=field_configs)
        semantic_result = validate_semantic(candidate, reference_text, threshold=threshold, domain=domain, semantic_path=semantic_path)
        polarity_result = validate_polarity(candidate, reference_text)

        is_factually_accurate = factual_result["is_valid"]
        is_semantically_valid = semantic_result["is_valid"]
        is_polarity_valid = polarity_result["polarity_match"]
        is_fully_valid = is_factually_accurate and is_semantically_valid and is_polarity_valid

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
    return results


def _print_enhanced_summary(total_candidates, factual_pass, fully_valid, facts):
    """Enhanced summary with better formatting and insights"""
    success_rate = (fully_valid / total_candidates * 100) if total_candidates else 0.0
    factual_rate = (factual_pass / total_candidates * 100) if total_candidates else 0.0
    
    print("\n📊 VALIDATION SUMMARY:")
    print(f"   Total candidates: {total_candidates}")
    print(f"   Factually accurate: {factual_pass} ({factual_rate:.1f}%)")
    print(f"   Fully valid: {fully_valid} ({success_rate:.1f}%)")
    print(f"   Fields to validate: {len(facts)}")
    
    # Color coding based on success rate
    if success_rate >= 80:
        print(f"   🟢 Overall Status: EXCELLENT")
    elif success_rate >= 60:
        print(f"   🟡 Overall Status: GOOD")
    elif success_rate >= 40:
        print(f"   🟠 Overall Status: FAIR")
    else:
        print(f"   🔴 Overall Status: NEEDS IMPROVEMENT")


def _print_enhanced_detailed_results(results, facts):
    """Enhanced detailed results with better formatting"""
    print("\n🔍 DETAILED RESULTS:")
    
    for r in results:
        status = "✅ VALID" if r["is_valid"] else "❌ INVALID"
        sim_score = r["semantic"]["similarity_score"]
        
        # Enhanced status with emojis
        if r["is_valid"]:
            status_emoji = "🟢"
        elif r["factual"]["is_valid"]:
            status_emoji = "🟡"
        else:
            status_emoji = "🔴"
        
        print(f"\n{status_emoji} Candidate {r['index']}: {status}")
        print(f"   📈 Similarity Score: {sim_score:.3f}")
        
        # Show factual validation details
        factual_details = r["factual"]["details"]
        correct_fields = sum(1 for detail in factual_details.values() if detail.get("match"))
        total_fields = len(factual_details)
        
        print(f"   📋 Factual Accuracy: {correct_fields}/{total_fields} fields correct")
        
        # Show field-by-field results
        for key, detail in factual_details.items():
            expected = detail.get("expected")
            found = detail.get("found")
            match = detail.get("match")
            status_icon = "✅" if match else "❌"
            print(f"      {status_icon} {key}: expected='{expected}', found='{found}'")
        
        # Show semantic breakdown
        semantic = r["semantic"]
        print(f"   🧠 Semantic Analysis:")
        print(f"      Token Score: {semantic['token_score']:.3f}")
        print(f"      Sequence Score: {semantic['seq_score']:.3f}")
        
        # Show polarity if there's an issue
        if not r["polarity"]["polarity_match"]:
            print(f"   ⚠️  Polarity Issue: {r['polarity']['failure_reason']}")
        
        # Show candidate text (truncated)
        candidate_text = r['candidate']
        if len(candidate_text) > 100:
            candidate_text = candidate_text[:100] + "..."
        print(f"   📝 Text: {candidate_text}")


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
        sim_score = r["semantic"]["similarity_score"]

        print(f"Candidate {r['index']}:{status}")
        print(f" Similarity: {sim_score:.3f}")
        
        # Mostrar detalles de validación factual
        factual_details = r["factual"]["details"]
        for key, detail in factual_details.items():
            expected = detail.get("expected")
            found = detail.get("found")
            match = detail.get("match")
            status_icon = "✅" if match else "❌"
            print(f" {status_icon} {key}: expected='{expected}', found='{found}'")
        
        print(f" Text: {r['candidate'][:80]}...")
        if not r["polarity"]["polarity_match"]:
            print(f" Failure Reason: {'; '.join(r['polarity']['failure_reason'])}")
        print()