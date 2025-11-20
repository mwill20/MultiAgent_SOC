"""Pytest configuration for async tests."""
import asyncio
import pytest


# Fix Windows + Python 3.13 event loop issues
if asyncio.get_event_loop_policy().__class__.__name__ == 'WindowsProactorEventLoopPolicy':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.fixture(scope="function", autouse=True)
def event_loop_policy():
    """Ensure clean event loop policy for each test."""
    policy = asyncio.get_event_loop_policy()
    yield policy
    # No cleanup needed - pytest-asyncio handles it
