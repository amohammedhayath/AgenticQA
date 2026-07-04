# bdd/environment.py (Partial Update)
import time
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

CAPS_PATH = "bdd/config/caps.json"
PAGE_SOURCE_PATH = "bdd/page_source.html"


def before_all(context):
    caps_path = os.path.join(os.getcwd(), CAPS_PATH)
    with open(caps_path, "r") as f:
        all_caps = json.load(f)

    device = os.getenv("DEVICE", "chrome")
    caps = all_caps.get(device, all_caps["chrome"])

    if caps.get("platformName") == "web":
        options = Options()
        options.add_argument("--disable-save-password-bubble")

        # Headless mode toggle for background/automated execution environments
        if os.getenv("HEADLESS") == "true":
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
        else:
            options.add_argument("--start-maximized")

        # Suppress Chrome Password Manager prompts and security leak alerts
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.password_manager_leak_detection": False
        }
        options.add_experimental_option("prefs", prefs)

        context.driver = webdriver.Chrome(options=options)
    else:
        from appium import webdriver as appium_driver
        from appium.options.common.base import AppiumOptions

        appium_options = AppiumOptions()
        appium_options.load_capabilities(caps)

        context.driver = appium_driver.Remote(
            command_executor="http://127.0.0.1:4723",
            options=appium_options
        )

    context.driver.implicitly_wait(10)
    context.wait = WebDriverWait(context.driver, 10)
    print("[Behave] before_all: Driver initialized.")


def before_feature(context, feature):
    print(f"[Behave] before_feature: {feature.name}")


def before_scenario(context, scenario):
    print(f"[Behave] before_scenario: {scenario.name}")


def before_step(context, step):
    print(f"[Behave] before_step: {step.keyword} {step.name}")




def after_step(context, step):
    print(f"[Behave] after_step: {step.keyword} {step.name} — {step.status}")
    try:
        # Simple safeguard: allow animations/XHR to settle down slightly on success actions
        if step.status == "passed":
            time.sleep(1.0)

        page_source = context.driver.page_source
        with open(PAGE_SOURCE_PATH, "w", encoding="utf-8") as f:
            f.write(page_source)
        print(f"[Behave] Page source saved.")
    except Exception as e:
        print(f"[Behave] Could not save page source: {e}")


def after_scenario(context, scenario):
    print(f"[Behave] after_scenario: {scenario.name} — {scenario.status}")


def after_feature(context, feature):
    print(f"[Behave] after_feature: {feature.name}")


def after_all(context):
    if hasattr(context, "driver"):
        context.driver.quit()
        print("[Behave] after_all: Driver closed.")