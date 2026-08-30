import pytest
from playwright.sync_api import Page, sync_playwright

@pytest.fixture(scope="function")
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        yield page
        context.close()
        browser.close()

def login(page: Page):
    page.goto("https://www.saucedemo.com")
    page.fill("#user-name", "standard_user")
    page.fill("#password", "secret_sauce")
    page.click("#login-button")
    assert page.url.endswith("/inventory.html")

def add_to_cart(page: Page, add_selector: str):
    page.click(add_selector)

def remove_from_cart(page: Page, remove_selector: str):
    page.click(remove_selector)

def test_successfully_remove_product_from_cart(page: Page):
    login(page)
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    page.click(".shopping_cart_link")
    remove_from_cart(page, "#remove-sauce-labs-backpack")
    assert not page.locator(".shopping_cart_badge").is_visible()

def test_attempt_to_remove_a_product_not_in_cart(page: Page):
    login(page)
    page.click(".shopping_cart_link")
    if page.locator("#remove-sauce-labs-backpack").is_visible():
        page.click("#remove-sauce-labs-backpack")
    assert not page.locator(".shopping_cart_badge").is_visible()

def test_successfully_add_product_to_cart(page: Page):
    login(page)
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    assert page.locator("#remove-sauce-labs-backpack").is_visible()
    assert page.locator(".shopping_cart_badge").inner_text() == "1"

def test_attempt_to_add_a_product_when_already_in_cart(page: Page):
    login(page)
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    assert page.locator("#remove-sauce-labs-backpack").is_visible()
    assert page.locator(".shopping_cart_badge").inner_text() == "1"

def test_successful_login_with_valid_credentials(page: Page):
    page.goto("https://www.saucedemo.com")
    page.fill("#user-name", "standard_user")
    page.fill("#password", "secret_sauce")
    page.click("#login-button")
    assert page.url.endswith("/inventory.html")
    assert page.locator(".inventory_list").is_visible()

def test_failed_login_with_invalid_credentials(page: Page):
    page.goto("https://www.saucedemo.com")
    page.fill("#user-name", "wrong_user")
    page.fill("#password", "wrong_pass")
    page.click("#login-button")
    assert page.locator('text="Epic sadface: Username and password do not match any user in this service"').is_visible()
    assert page.url.endswith("/")

def test_successful_checkout_with_all_details(page: Page):
    login(page)
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    page.click(".shopping_cart_link")
    page.click("#checkout")
    page.fill("#first-name", "John")
    page.fill("#last-name", "Doe")
    page.fill("#postal-code", "12345")
    page.click("#continue")
    assert page.locator(".summary_info").is_visible()
    page.click("#finish")
    assert page.locator(".complete-header").inner_text() == "Thank you for your order!"

def test_checkout_with_missing_postal_code(page: Page):
    login(page)
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    page.click(".shopping_cart_link")
    page.click("#checkout")
    page.fill("#first-name", "John")
    page.fill("#last-name", "Doe")
    page.fill("#postal-code", "")
    page.click("#continue")
    assert page.locator('text="Error: Postal Code is required"').is_visible()