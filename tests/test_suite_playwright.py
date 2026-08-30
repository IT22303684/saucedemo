import pytest
from playwright.sync_api import Page, Browser, sync_playwright

@pytest.fixture(scope="function")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

@pytest.fixture(scope="function")
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()

def login(page):
    page.goto("https://www.saucedemo.com")
    page.fill("#user-name", "standard_user")
    page.fill("#password", "secret_sauce")
    page.click("#login-button")
    
def add_to_cart(page, add_selector):
    page.click(add_selector)

def remove_from_cart(page, remove_selector):
    page.click(remove_selector)

def test_successfully_remove_product_from_cart(page):
    login(page)
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    remove_from_cart(page, "#remove-sauce-labs-backpack")
    assert not page.locator(".shopping_cart_badge").is_visible()
    assert page.locator("#remove-sauce-labs-backpack").is_visible() is False

def test_attempt_to_remove_a_product_not_in_the_cart(page):
    login(page)
    # Attempting to remove an item not in the cart
    if page.locator("#remove-sauce-labs-backpack").is_visible():
        remove_from_cart(page, "#remove-sauce-labs-backpack")
    assert not page.locator(".shopping_cart_badge").is_visible()

def test_successfully_add_product_to_cart(page):
    login(page)
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    assert page.locator(".shopping_cart_badge").is_visible()
    assert page.locator(".shopping_cart_badge").inner_text() == "1"

def test_verify_cart_badge_is_not_displayed_when_no_products_are_added(page):
    assert not page.locator(".shopping_cart_badge").is_visible()

def test_successful_checkout_with_all_details(page):
    login(page)
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    page.click(".shopping_cart_link")
    page.click("#checkout")
    page.fill("#first-name", "John")
    page.fill("#last-name", "Doe")
    page.fill("#postal-code", "")
    page.click("#continue")
    assert page.locator(".summary_info").is_visible()  # Assuming an order summary element is visible
    page.click("#finish")
    assert page.locator(".complete-header").inner_text() == "Thank you for your order!"

def test_checkout_with_missing_postal_code(page):
    login(page)
    add_to_cart(page, "#add-to-cart-sauce-labs-backpack")
    page.click(".shopping_cart_link")
    page.click("#checkout")
    page.fill("#first-name", "John")
    page.fill("#last-name", "Doe")
    page.fill("#postal-code", "")
    page.click("#continue")
    assert page.locator(".error-message-container").inner_text() == "Error: Postal Code is required"

def test_successful_login_with_valid_credentials(page):
    page.goto("https://www.saucedemo.com")
    page.fill("#user-name", "standard_user")
    page.fill("#password", "secret_sauce")
    page.click("#login-button")
    assert page.url.endswith("/inventory.html")
    assert page.locator(".inventory_list").is_visible()  # Assuming inventory list is visible

def test_failed_login_with_invalid_credentials(page):
    page.goto("https://www.saucedemo.com/")
    page.fill("#user-name", "wrong_user")
    page.fill("#password", "wrong_pass")
    page.click("#login-button")
    assert page.locator("h3").inner_text() == "Epic sadface: Username and password do not match any user in this service"
    assert page.url == "https://www.saucedemo.com/"  # Ensure we remain on the login page