from graph.state import AgentState

UNIVERSAL_PATTERNS = [
    'i opened the page',
    'i clicked ',
    'i typed ',
    'i verified ',
    'i took a screenshot',
    'i scrolled',
]

def should_write_step(state: AgentState) -> str:
    gherkin_step = state["current_line"].lower()
    step_functions = state["step_functions"]

    for pattern in UNIVERSAL_PATTERNS:
        if pattern in gherkin_step:
            print(f"[Edge] Covered by universal step. Skipping StepWriter.")
            return "skip"

    for func_name in step_functions:
        if func_name in gherkin_step.replace(" ", "_"):
            print(f"[Edge] Step function already exists. Skipping StepWriter.")
            return "skip"

    print(f"[Edge] Step function missing. Running StepWriter.")
    return "write"


def should_continue_loop(state: AgentState) -> str:
    if state["loop_done"]:
        return "done"
    return "continue"