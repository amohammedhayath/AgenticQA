import os
import json
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

from graph.state import AgentState
from graph.nodes import (
    line_reader_node,
    feature_writer_node,
    behave_runner_node,
    step_writer_node,
    loop_check_node
)
from graph.edges import should_write_step, should_continue_loop

load_dotenv()

CORE_PY_RESET_CONTENT = open("bdd/steps/core.py", "r").read()
CAPS_PATH = "bdd/config/caps.json"
TEST_INPUT_PATH = "test_input.txt"
FEATURE_FILE_PATH = "bdd/features/test_cases.feature"
CORE_PY_PATH = "bdd/steps/generated.py"

def load_initial_state() -> AgentState:
    with open(TEST_INPUT_PATH, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    with open(CAPS_PATH, "r") as f:
        caps = json.load(f)

    # device = input("Enter device (chrome = 1 / android = 2): ").strip().lower()
    device = 'chrome' # if device == '1' else 'android'
    device_caps = caps.get(device, caps["chrome"])

    with open(FEATURE_FILE_PATH, "w") as f:
        f.write("Feature: Automated test cases\n\n  Scenario: Generated scenario\n\n")

    with open(CORE_PY_PATH, "w") as f:
        f.write("from behave import given, when, then\nfrom selenium.webdriver.common.by import By\n")

    return AgentState(
        all_lines=lines,
        current_line_index=0,
        current_line="",
        feature_file_content="",
        step_functions=[],
        page_source_json="[]",
        device_caps=device_caps,
        loop_done=False
    )

def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("line_reader", line_reader_node)
    graph.add_node("feature_writer", feature_writer_node)
    graph.add_node("behave_runner", behave_runner_node)
    graph.add_node("step_writer", step_writer_node)
    graph.add_node("loop_check", loop_check_node)

    graph.set_entry_point("line_reader")

    graph.add_edge("line_reader", "feature_writer")

    graph.add_conditional_edges(
        "feature_writer",
        should_write_step,
        {
            "write": "step_writer",
            "skip": "behave_runner"
        }
    )

    graph.add_edge("step_writer", "behave_runner")
    graph.add_edge("behave_runner", "loop_check")

    graph.add_conditional_edges(
        "loop_check",
        should_continue_loop,
        {
            "continue": "line_reader",
            "done": END
        }
    )

    return graph


if __name__ == "__main__":
    print("AgenticQA — Starting...\n")

    initial_state = load_initial_state()
    graph = build_graph()
    app = graph.compile()

    final_state = app.invoke(initial_state)

    print("\n[SUCCESS] AgenticQA completed successfully.")
    print(f"[SUCCESS] Total lines processed: {len(final_state['all_lines'])}")

    # Ask the user if they want to append generated custom step definitions to core.py
    try:
        if os.path.exists(CORE_PY_PATH):
            with open(CORE_PY_PATH, "r") as f:
                generated_content = f.read()

            # Filter out standard base imports to isolate custom code
            custom_lines = [
                line for line in generated_content.splitlines()
                if "from behave import" not in line and "from selenium.webdriver.common.by import" not in line
            ]
            custom_code = "\n".join(custom_lines).strip()

            if custom_code:
                print("\n" + "="*50)
                print("💾 CUSTOM STEP DEFINITIONS DETECTED")
                print("="*50)
                print("The following custom step definitions were generated during this run:")
                print("-"*50)
                print(custom_code)
                print("-"*50)

                # Non-interactive / Auto-pilot mode detection
                auto_persist = os.getenv("AUTO_PERSIST", "").strip().lower()
                if auto_persist in ["true", "yes", "y"]:
                    user_choice = "yes"
                    print("[Auto-Pilot] AUTO_PERSIST=true detected. Automatically appending steps.")
                elif auto_persist in ["false", "no", "n"]:
                    user_choice = "no"
                    print("[Auto-Pilot] AUTO_PERSIST=false detected. Automatically skipping steps.")
                else:
                    user_choice = input("Would you like to append these functions permanently to core.py? (y/n): ").strip().lower()

                if user_choice in ["y", "yes"]:
                    with open("bdd/steps/core.py", "a") as f:
                        f.write("\n\n# Dynamic Custom Steps Appended Automatically\n" + custom_code)
                    print("\n[SUCCESS] Successfully saved custom steps permanently to bdd/steps/core.py!")
                else:
                    print("\nSkipped saving. Custom steps will be discarded on the next run.")
    except Exception as e:
        print(f"\nCould not check or save generated steps: {e}")