from abc import ABC, abstractmethod
from typing import Tuple


class BaseConnector(ABC):
    """Base interface for utility data connectors."""

    @abstractmethod
    def fetch_bill_artifact(self, utility_account_id: int) -> Tuple[bytes, str]:
        """
        Fetch a bill artifact from the utility provider.
        
        Returns:
            Tuple of (content_bytes, filename)
        """
        pass
