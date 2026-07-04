from agents.llm import LLM
from utils.validator import validate_gherkin

llm = LLM()

FEATURE_WRITER_PROMPT = """
You are a BDD test automation expert.
Convert the following plain English test case into a single Gherkin step.

Current page elements (JSON) — use these to find EXACT locators:
{page_source_json}

You MUST use one of these existing universal step patterns:

NAVIGATION:
  Given I opened the page "<url>"

CLICKING:
  When I clicked link text "<exact link text from page elements above>"
  When I clicked id "<exact id from page elements above>"
  When I clicked xpath "<xpath based on page elements above>"

TYPING:
  When I typed "<text>" into id "<exact id from page elements above>"
  When I typed "<text>" into xpath "<xpath based on page elements above>"

VERIFICATION:
  Then I verified id "<exact id from page elements above>" is displayed
  Then I verified link text "<exact link text from page elements above>" is present
  Then I verified xpath "<xpath based on page elements above>" is visible

SCROLLING:
  When I scrolled down to id "<exact id from page elements above>"
  When I scrolled down to xpath "<xpath based on page elements above>"

Rules:
- Output ONLY the Gherkin step, nothing else
- No feature or scenario blocks
- No markdown, no backticks, no explanation
- Use the universal patterns above for all opening, clicking, typing, verifying, scrolling actions
- Pick locators ONLY from the page elements JSON provided above
- If page elements JSON is empty ([]), use your best judgment for the locator
- Only generate a completely custom Gherkin step if none of the patterns fit

Test case: {test_case}
"""


def run_feature_writer(test_case: str, page_source_json: str = "[]") -> str:
    prompt = FEATURE_WRITER_PROMPT.format(
        test_case=test_case,
        page_source_json=page_source_json
    )
    output = llm.generate(prompt)

    if not validate_gherkin(output):
        raise ValueError(f"FeatureWriter produced invalid Gherkin: {output}")

    return output.strip()