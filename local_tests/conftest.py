import pytest
from playwright.sync_api import sync_playwright
import os

@pytest.fixture(scope="session")
def base_url():
    """Returns the base URL of the local application."""
    return os.getenv("BASE_URL", "http://localhost:3000")

# Note: pytest-playwright provides a 'page' fixture automatically, 
# but we can customize context here if needed.
# For now, default 'page' fixture is sufficient.
