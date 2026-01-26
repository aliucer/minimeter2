from typing import Tuple
from .base import BaseConnector


SAMPLE_BILL = """
========================================
        UTILITY COMPANY A
        Monthly Statement
========================================

Account Number: 12345-67890
Service Address: 123 Main Street
Billing Period: Dec 1 - Dec 31, 2025

----------------------------------------
USAGE SUMMARY
----------------------------------------
Previous Reading:     45,230 kWh
Current Reading:      45,892 kWh
Total Usage:             662 kWh

----------------------------------------
CHARGES
----------------------------------------
Basic Service Charge:        $12.00
Energy Charge (662 kWh):    $79.44
  @ $0.12/kWh
Fuel Cost Adjustment:         $6.62
Taxes & Fees:                 $8.34
----------------------------------------
TOTAL DUE:                  $106.40

Due Date: January 15, 2026

Thank you for being our customer!
========================================
"""


class MockUtilityAConnector(BaseConnector):
    """Mock connector for testing. Returns a sample bill."""

    def fetch_bill_artifact(self, utility_account_id: int) -> Tuple[bytes, str]:
        """Return a mock bill as text."""
        content = SAMPLE_BILL.strip().encode("utf-8")
        filename = f"bill_account_{utility_account_id}.txt"
        return content, filename
