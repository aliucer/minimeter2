from typing import Tuple
from .base import BaseConnector


# Different format - more compact, different field names
SAMPLE_BILL_B = """
*******************************************
*      UTILITY PROVIDER B - INVOICE       *
*******************************************

Customer #: UA-98765
Location: 456 Oak Avenue, Suite 100
Period: 01/01/2025 - 31/01/2025

----- CONSUMPTION -----
Start Meter: 12,450 kWh
End Meter: 13,125 kWh
Used: 675 kWh

----- BREAKDOWN -----
Service Fee.............. $15.50
Usage (675 kWh x $0.11).. $74.25
Grid Maintenance......... $4.20
Environmental Surcharge.. $2.80
State Tax (5%)........... $4.84

===========================
AMOUNT DUE: $101.59
===========================

Pay by: Feb 15, 2025
*******************************************
"""


class MockUtilityBConnector(BaseConnector):
    """Mock connector B with different bill format."""

    def fetch_bill_artifact(self, utility_account_id: int) -> Tuple[bytes, str]:
        """Return a mock bill in format B."""
        content = SAMPLE_BILL_B.strip().encode("utf-8")
        filename = f"bill_b_account_{utility_account_id}.txt"
        return content, filename
