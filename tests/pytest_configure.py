"""Comprehensive test configuration and shared fixtures."""

import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests that don't require database or external services")
    config.addinivalue_line("markers", "integration: Integration tests that use database")
    config.addinivalue_line("markers", "smoke: Quick smoke tests for CI/CD")
    config.addinivalue_line("markers", "slow: Tests that take longer to run")


# Test collection
def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their names or locations.

    This helps ensure tests are properly categorized even if developers
    forget to add markers.
    """
    for item in items:
        # Auto-mark unit tests
        if "unit" in item.nodeid or "test_bunq_adapter" in item.nodeid or "test_schemas" in item.nodeid:
            if "integration" not in [mark.name for mark in item.iter_markers()]:
                item.add_marker(pytest.mark.unit)

        # Auto-mark integration tests
        if "integration" in item.nodeid or "db_session" in item.fixturenames:
            if "unit" not in [mark.name for mark in item.iter_markers()]:
                item.add_marker(pytest.mark.integration)

        # Auto-mark slow tests
        if "slow" in item.nodeid or "performance" in item.name.lower():
            item.add_marker(pytest.mark.slow)
