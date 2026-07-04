from agents.llm import LLM
from utils.validator import validate_python

llm = LLM()

STEP_WRITER_PROMPT = """
You are a Python test automation expert working with the Behave BDD framework and Selenium.

Your job is to write a single Python step function for the following Gherkin step.

Gherkin step: {gherkin_step}

Page source (JSON format showing available elements):
{page_source_json}

Rules:
- Output ONLY the Python function, nothing else
- Use the @given, @when, or @then decorator from behave matching the Gherkin step
- The function must accept (context) as its parameter
- Use context.driver to interact with elements
- No imports, no markdown, no backticks, no explanation
- If the Gherkin step involves navigation (navigate, open, go to, visit), always use context.driver.get(url) 
- If page source is empty ([]), generate a reasonable step using standard Selenium patterns
- Base your element selectors on the page source JSON when available
- Based on this appium version 2.19.0 or appium-python-client>=5.3.1 should write the functions and syntax or code.
- For click actions, try native click first, and use JavaScript executor as fallback to handle any interception or element-type propagation issues:
  element = context.driver.find_element(By.XPATH, "//your-locator")
  try:
      element.click()
  except Exception:
      context.driver.execute_script("arguments[0].click();", element)

Example output format:
@when('user clicks the login button')
def step_impl(context):
    context.driver.find_element(By.ID, 'login-btn').click()
"""


def run_step_writer(gherkin_step: str, page_source_json: str) -> str:
    prompt = STEP_WRITER_PROMPT.format(
        gherkin_step=gherkin_step,
        page_source_json=page_source_json
    )
    output = llm.generate(prompt)

    if not validate_python(output):
        raise ValueError(f"StepWriter produced invalid Python: {output}")

    return output.strip()