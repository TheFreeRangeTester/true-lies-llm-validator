#!/usr/bin/env python3
"""
Quick test script - Runs tests and generates HTML report for local development.
Use this to verify changes to the reporter (query, baseline, etc.)

Usage:
    python scripts/quick_test.py
    # or from project root:
    python -m scripts.quick_test
"""

import subprocess
import sys
from pathlib import Path

# Ensure we can import true_lies (run from project root)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_tests():
    """Run pytest and return success status."""
    print("🧪 Running tests...")
    try:
        import pytest  # noqa: F401
    except ImportError:
        print("   ⚠️  pytest not installed. Run: pip install -e \".[dev]\"")
        return None  # Skipped
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        cwd=project_root,
    )
    return result.returncode == 0


def generate_report():
    """Generate HTML report with query + baseline scenario."""
    print("\n📊 Generating HTML report...")
    from true_lies import validate_llm_candidates, create_scenario

    scenario = create_scenario(
        facts={
            "price": {"expected": "99.99", "extractor": "money"},
            "ship_date": {
                "expected": "March 15",
                "extractor": "categorical",
                "patterns": {"March 15": ["March 15", "Mar 15", "March 15, 2024"]},
            },
        },
        semantic_reference="The Game Boy Color costs $99.99 and ships on March 15, 2024",
    )
    scenario["name"] = "How much is the Game Boy Color and when does it ship?"

    # Generate ~50 candidates for pagination testing (mix of valid, partial, invalid)
    base_valid = [
        "The Game Boy Color is $99.99 and ships March 15.",
        "Price: $99.99, shipping March 15, 2024.",
        "The Game Boy Color costs $99.99 and will ship on March 15.",
        "You can get the Game Boy Color for $99.99, available March 15.",
        "Game Boy Color: $99.99, ships March 15, 2024.",
    ]
    base_partial = [
        "The price is $99.99 but I'm not sure about the date.",
        "It ships March 15. Price might be around $100.",
        "Game Boy Color - check our site for pricing and availability.",
    ]
    base_invalid = [
        "I don't have that information.",
        "Please contact support for pricing.",
        "The product is discontinued.",
        "Sorry, I cannot help with that.",
    ]
    # Build ~55 candidates for pagination testing
    candidates = []
    for _ in range(6):
        candidates.extend(base_valid)
        candidates.extend(base_partial[:2])
        candidates.extend(base_invalid[:2])

    result = validate_llm_candidates(
        scenario=scenario,
        candidates=candidates,
        threshold=0.65,
        generate_html_report=True,
        html_title="Quick Test - Game Boy Validation",
    )

    report_path = result["html_report_path"]
    print(f"✅ Report: {report_path}")
    return report_path


def main():
    print("🎭 True Lies - Quick Test")
    print("=" * 40)

    tests_ok = run_tests()
    report_path = generate_report()

    print("\n" + "=" * 40)
    if tests_ok is True:
        print("✅ All tests passed")
    elif tests_ok is False:
        print("⚠️  Some tests failed (see above)")
    else:
        print("⏭️  Tests skipped (pytest not installed)")
    print(f"\n📂 Open report: {report_path}")
    print("   (open the file in your browser to verify Query, Baseline, Candidate)")


if __name__ == "__main__":
    main()
