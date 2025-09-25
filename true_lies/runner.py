"""
Runner for executing validation scenarios and printing formatted reports
"""

from .validation_core import validate_against_reference_dynamic
from .scenario import create_scenario
import json
from pathlib import Path


def validate_llm_candidates(scenario, candidates, threshold=0.65, generate_html_report=False, html_output_file=None, html_title=None):
    """
    Validates candidates using a scenario created with create_scenario and optionally generates HTML report.
    
    Args:
        scenario: Scenario created with create_scenario (allows custom extractors)
        candidates: List of candidate texts
        threshold: Similarity threshold
        generate_html_report: Whether to generate HTML report automatically
        html_output_file: HTML output file path (default: auto-generated)
        html_title: HTML report title (default: auto-generated)
    
    Returns:
        dict: Validation results with optional HTML report path
    """
    total_candidates = len(candidates)
    factual_pass = 0
    fully_valid = 0
    results = []

    print(f"🔍 VALIDATING LLM RESPONSES")
    print(f"📋 Expected Facts: {len(scenario['facts'])} fields")
    print(f"📝 Reference Text: {scenario['semantic_reference'][:100]}{'...' if len(scenario['semantic_reference']) > 100 else ''}")
    print(f"🎯 Candidates: {total_candidates}")
    print(f"📊 Threshold: {threshold}")
    if scenario.get('semantic_mappings'):
        print(f"🗂️  Semantic Mapping: {len(scenario['semantic_mappings'])} synonym groups")
    print("-" * 80)

    for i, candidate in enumerate(candidates, 1):
        # Validate using the scenario
        result = validate_against_reference_dynamic(
            candidate_text=candidate,
            reference_scenario=scenario,
            similarity_threshold=threshold
        )
        
        # Count results
        if result['factual_accuracy']:
            factual_pass += 1
        if result['is_valid']:
            fully_valid += 1
        
        # Store result
        results.append({
            'index': i,
            'candidate': candidate,
            'result': result,
            'is_valid': result['is_valid']
        })
        
        # Print formatted result with candidate text
        status = "✅ VALID" if result['is_valid'] else "❌ INVALID"
        print(f"Candidate {i}: {status} Similarity: {result['similarity_score']:.3f}")
        print(f"  📝 Text: {candidate}")
        
        # Print factual details
        for fact_name in scenario['facts'].keys():
            accuracy = result.get(f'{fact_name}_accuracy', False)
            extracted = result.get(f'extracted_{fact_name}', 'None')
            expected = scenario['facts'][fact_name]['expected']
            field_status = "✅" if accuracy else "❌"
            print(f"  {field_status} {fact_name}: expected='{expected}', found='{extracted}'")
        
        # Print semantic and polarity details with proper emojis
        semantic_status = "✅" if result['similarity_score'] >= threshold else "❌"
        polarity_status = "✅" if result['polarity_match'] else "❌"
        print(f"  {semantic_status} Semantic: {result['similarity_score']:.3f} (threshold: {threshold})")
        print(f"  {polarity_status} Polarity: {result['reference_polarity']} → {result['candidate_polarity']}")
        
        # Show failure reason if exists
        if result.get('failure_reason'):
            print(f"  ⚠️  Reason: {result['failure_reason']}")
        print()
    
    # Summary
    print("=" * 80)
    print("📊 SUMMARY")
    print("-" * 30)
    print(f"Total candidates: {total_candidates}")
    print(f"Factual accuracy: {factual_pass}/{total_candidates} ({factual_pass/total_candidates*100:.1f}%)")
    print(f"Fully valid: {fully_valid}/{total_candidates} ({fully_valid/total_candidates*100:.1f}%)")
    
    # Programmatic summary for further analysis
    print(f"\n📊 PROGRAMMATIC SUMMARY:")
    print(f"Total valid: {fully_valid}/{total_candidates}")
    print(f"Factual accuracy: {factual_pass/total_candidates:.1%}")
    print(f"Overall accuracy: {fully_valid/total_candidates:.1%}")
    
    # Generate HTML report if requested
    html_report_path = None
    if generate_html_report:
        from .html_reporter import HTMLReporter
        
        # Generate default file name and title if not provided
        if not html_output_file:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_output_file = f"validation_report_{timestamp}.html"
        
        if not html_title:
            html_title = f"LLM Validation Report - {total_candidates} candidates"
        
        # Generate HTML report
        reporter = HTMLReporter()
        html_report_path = reporter.generate_report(
            results=results,
            output_file=html_output_file,
            title=html_title,
            scenario=scenario,
            save_to_history=True
        )
        
        print(f"\n📊 HTML REPORT GENERATED:")
        print(f"Report saved to: {html_report_path}")
    
    return {
        'total_candidates': total_candidates,
        'factual_pass': factual_pass,
        'fully_valid': fully_valid,
        'results': results,
        'summary': {
            'factual_accuracy': factual_pass/total_candidates,
            'overall_accuracy': fully_valid/total_candidates
        },
        'html_report_path': html_report_path
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

    # Convert facts to new format if needed
    formatted_facts = {}
    for key, expected in reference_values.items():
        if isinstance(expected, str):
            # Simple string value - use 'money' extractor for numbers, 'categorical' for others
            if expected.replace('.', '').replace(',', '').isdigit():
                formatted_facts[key] = {'extractor': 'money', 'expected': expected}
            else:
                formatted_facts[key] = {'extractor': 'categorical', 'expected': expected}
        elif isinstance(expected, dict):
            # Already in new format
            formatted_facts[key] = expected
        else:
            # Convert to string and use appropriate extractor
            formatted_facts[key] = {'extractor': 'money', 'expected': str(expected)}
    
    # Create scenario using new system
    scenario = create_scenario(
        facts=formatted_facts,
        semantic_reference=reference_text,
        semantic_mappings={}  # No semantic mappings for legacy compatibility
    )
    
    # Use the new system
    result = validate_llm_candidates(
        scenario=scenario,
        candidates=candidates,
        threshold=threshold
    )
    
    return result['results']