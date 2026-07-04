from behave import given, when, then, use_step_matcher
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

use_step_matcher("parse")

LOCATOR_MAP = {
    'id': By.ID,
    'xpath': By.XPATH,
    'class name': By.CLASS_NAME,
    'css selector': By.CSS_SELECTOR,
    'link text': By.LINK_TEXT,
    'partial link text': By.PARTIAL_LINK_TEXT,
    'name': By.NAME,
    'tag name': By.TAG_NAME
}


@given('I opened the page "{web_page}"')
def i_opened_the_page(context, web_page):
    context.driver.get(web_page)


@when('I clicked {selector} "{locator}"')
def i_clicked_method_selector(context, selector, locator):
    by = LOCATOR_MAP.get(selector.lower())
    if not by:
        raise ValueError(f"Unsupported selector: '{selector}'")
    wait = WebDriverWait(context.driver, 15)
    elem = wait.until(EC.element_to_be_clickable((by, locator)))
    try:
        elem.click()
    except Exception:
        context.driver.execute_script("arguments[0].click();", elem)


@when('I typed "{text}" into {selector} "{locator}"')
def i_typed_into_field(context, text, selector, locator):
    by = LOCATOR_MAP.get(selector.lower())
    if not by:
        raise ValueError(f"Unsupported selector: '{selector}'")
    wait = WebDriverWait(context.driver, 15)
    elem = wait.until(EC.presence_of_element_located((by, locator)))
    elem.click()
    elem.clear()
    elem.send_keys(text)


@then('I verified {selector} "{locator}" is {status}')
def i_verified_element(context, selector, locator, status):
    by = LOCATOR_MAP.get(selector.lower())
    if not by:
        raise ValueError(f"Unsupported selector: '{selector}'")
    VISIBILITY_MAP = {
        'displayed': EC.visibility_of_element_located,
        'visible': EC.visibility_of_element_located,
        'present': EC.presence_of_element_located,
        'gone': EC.invisibility_of_element_located,
        'invisible': EC.invisibility_of_element_located
    }
    status = status.lower()
    wait = WebDriverWait(context.driver, 15)
    if status in VISIBILITY_MAP:
        wait.until(VISIBILITY_MAP[status]((by, locator)))
        print(f"Verified: [{selector}='{locator}'] is {status}.")
    else:
        raise ValueError(f"Unsupported status: '{status}'")


@when('I took a screenshot of current page')
def i_took_a_screenshot(context):
    context.driver.save_screenshot("current_page.png")


@when('I scrolled down to {selector} "{locator}"')
def i_scrolled_to_element(context, selector, locator):
    by = LOCATOR_MAP.get(selector.lower())
    if not by:
        raise ValueError(f"Unsupported selector: '{selector}'")
    wait = WebDriverWait(context.driver, 15)
    elem = wait.until(EC.presence_of_element_located((by, locator)))
    context.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", elem)