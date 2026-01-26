"""Connector registry - maps providers to connector classes."""
from typing import Dict, Type
from .base import BaseConnector
from .mock_utility_a import MockUtilityAConnector
from .mock_utility_b import MockUtilityBConnector

# Provider to Connector mapping - "Tool Selection"
CONNECTOR_REGISTRY: Dict[str, Type[BaseConnector]] = {
    "MOCK_A": MockUtilityAConnector,
    "MOCK_B": MockUtilityBConnector,
    # Default fallback
    "PG&E": MockUtilityAConnector,
    "SCE": MockUtilityBConnector,
}


def get_connector(provider: str) -> BaseConnector:
    """Get the appropriate connector for a provider."""
    connector_class = CONNECTOR_REGISTRY.get(provider, MockUtilityAConnector)
    return connector_class()
