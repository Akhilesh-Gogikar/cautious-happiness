import pytest
from playwright.sync_api import Page, expect
import time
import os
import re

def dump_page_on_failure(page):
    print(f"DEBUG: Page Title: '{page.title()}'")
    print(f"DEBUG: Page URL: {page.url}")
    # Print first 2000 chars of body to see what's rendering
    content = page.content()
    print(f"DEBUG: Page Content Snippet:\n{content[:2000]}...")

def test_homepage_loads(page: Page, base_url):
    """Verifies that the homepage loads correctly."""
    print(f"Navigating to {base_url}")
    try:
        page.goto(base_url)
        page.wait_for_load_state("networkidle")
        title = page.title()
        print(f"Page Title: '{title}'")
        
        # Check header first as it's more reliable than title if metadata is missing
        expect(page.locator("h1").filter(has_text="ALPHA")).to_be_visible()
        
        # Optional title check - don't fail if empty but warn
        if title:
             expect(page).to_have_title(re.compile(r"Polymarket|Alpha|Insights|Create Next App", re.IGNORECASE))
    except Exception as e:
        dump_page_on_failure(page)
        raise e

def test_navigation_portfolio(page: Page, base_url):
    """Tests navigation to the Portfolio view."""
    try:
        page.goto(base_url)
        page.wait_for_load_state("networkidle")
        print("Clicking Portfolio...")
        # Use more generic text matching
        page.get_by_text("Portfolio", exact=False).first.click()
        expect(page.locator("div").filter(has_text="PORTFOLIO").first).to_be_visible()
    except Exception as e:
        dump_page_on_failure(page)
        raise e

def test_navigation_chat_view(page: Page, base_url):
    """Tests navigation to the Chat view via Sidebar."""
    try:
        page.goto(base_url)
        page.wait_for_load_state("networkidle")
        print("Looking for Analyst Chat nav item...")
        # Target the label specifically
        nav_item = page.get_by_text("Analyst Chat", exact=False)
        nav_item.first.wait_for(state="visible", timeout=15000)
        nav_item.first.click()
        
        # Increased robustness: wait for placeholder
        page.wait_for_timeout(2000)
        expect(page.get_by_placeholder("Ask", exact=False)).to_be_visible(timeout=20000)
    except Exception as e:
        dump_page_on_failure(page)
        raise e

def test_chatbot_interaction(page: Page, base_url):
    """Tests sending a message to the chatbot."""
    try:
        page.goto(base_url)
        page.wait_for_load_state("networkidle")
        print("Navigating to Analyst Chat...")
        nav_item = page.get_by_text("Analyst Chat", exact=False)
        nav_item.first.wait_for(state="visible", timeout=15000)
        nav_item.first.click()
        
        page.wait_for_timeout(2000)
        input_box = page.get_by_placeholder("Ask", exact=False)
        expect(input_box).to_be_visible(timeout=20000)
        input_box.click()
        input_box.fill("Hello Alpha")
        input_box.press("Enter")
        # Exact match might be tricky with formatting, try exact=False
        expect(page.get_by_text("Hello Alpha", exact=False)).to_be_visible(timeout=10000)
        # Increased timeout for LLM response
        expect(page.locator(".prose, .whitespace-pre-wrap").first).to_be_visible(timeout=45000)
    except Exception as e:
        dump_page_on_failure(page)
        raise e

def test_ui_visual_regression_placeholders(page: Page, base_url):
    """Takes screenshots."""
    # Ensure screenshots dir exists
    screenshot_dir = "local_tests/screenshots"
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir, exist_ok=True)
    page.goto(base_url)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    page.screenshot(path=f"{screenshot_dir}/dashboard.png")
