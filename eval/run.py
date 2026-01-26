#!/usr/bin/env python
"""LLM Extraction Evaluation - measures accuracy against test cases."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from worker.llm import extract_bill_data
from shared.schemas import BillNormalized

EVAL_DIR = Path(__file__).parent
BILLS_DIR = EVAL_DIR / "bills"
EXPECTED_FILE = EVAL_DIR / "expected.json"


def evaluate_bill(bill_path: Path, expected: dict) -> dict:
    """Evaluate LLM extraction against expected values."""
    with open(bill_path) as f:
        bill_text = f.read()
    
    result = {"file": bill_path.name, "passed": True, "errors": []}
    
    try:
        extracted = extract_bill_data(bill_text)
        validated = BillNormalized(**extracted)
        
        # Check total (1% tolerance)
        if abs(validated.total_amount - expected["total_amount"]) > expected["total_amount"] * 0.01:
            result["errors"].append(f"total: {validated.total_amount} vs expected {expected['total_amount']}")
            result["passed"] = False
        
        # Check dates
        if str(validated.billing_period_start) != expected["billing_period_start"]:
            result["errors"].append(f"start: {validated.billing_period_start}")
            result["passed"] = False
        
        if str(validated.billing_period_end) != expected["billing_period_end"]:
            result["errors"].append(f"end: {validated.billing_period_end}")
            result["passed"] = False
            
        result["total"] = validated.total_amount
        
    except Exception as e:
        result["passed"] = False
        result["errors"].append(str(e)[:100])
    
    return result


def main():
    with open(EXPECTED_FILE) as f:
        expected = json.load(f)
    
    results = []
    for bill_file, exp in expected.items():
        bill_path = BILLS_DIR / bill_file
        if not bill_path.exists():
            continue
        result = evaluate_bill(bill_path, exp)
        results.append(result)
        
        status = "PASS" if result["passed"] else "FAIL"
        print(f"{bill_file}: {status}", end="")
        if result.get("total"):
            print(f" (${result['total']})", end="")
        if result["errors"]:
            print(f" - {result['errors'][0]}", end="")
        print()
    
    passed = sum(1 for r in results if r["passed"])
    print(f"\nResult: {passed}/{len(results)}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    exit(main())
