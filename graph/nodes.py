import os
import sys
import subprocess

from graph.state import AgentState
from agents.feature_writer import run_feature_writer
from agents.step_writer import run_step_writer
from utils.source_compressor import compress_page_source
from utils.validator import extract_function_names

FEATURE_FILE_PATH = "bdd/features/test_cases.feature"
CORE_PY_PATH = "bdd/steps/generated.py"
PAGE_SOURCE_PATH = "bdd/page_source.html"


def line_reader_node(state: AgentState) -> dict:
    index = state["current_line_index"]
    current_line = state["all_lines"][index]
    print(f"\n[LineReader] Processing line {index + 1}: {current_line}")
    return {
        "current_line": current_line,
        "current_line_index": index + 1
    }


def feature_writer_node(state: AgentState) -> dict:
    current_line = state["current_line"]
    page_source_json = state["page_source_json"]
    print(f"[FeatureWriter] Converting to Gherkin: {current_line}")

    gherkin = run_feature_writer(current_line, page_source_json)
    print(f"[FeatureWriter] Generated: {gherkin}")

    with open(FEATURE_FILE_PATH, "a") as f:
        f.write(gherkin + "\n")

    updated_content = state["feature_file_content"] + gherkin + "\n"

    return {
        "current_line": gherkin,
        "feature_file_content": updated_content
    }


def behave_runner_node(state: AgentState) -> dict:
    print(f"[BehaveRunner] Running Behave framework...")

    # Determine device key based on the selected caps platform
    platform = state["device_caps"].get("platformName", "web").lower()
    device_env = "android" if platform == "android" else "chrome"

    # Inject the environment variable explicitly into the subprocess execution context
    env = os.environ.copy()
    env["DEVICE"] = device_env

    result = subprocess.run(
        [sys.executable, "-m", "behave", "bdd/features",
         "--no-capture", "--no-skipped"],
        capture_output=True,
        text=True,
        cwd=os.getcwd(),
        env=env  # Pass down the selection
    )

    print(f"[BehaveRunner] STDOUT:\n{result.stdout}")
    print(f"[BehaveRunner] STDERR:\n{result.stderr}")
    print(f"[BehaveRunner] Return code: {result.returncode}")

    if os.path.exists(PAGE_SOURCE_PATH):
        with open(PAGE_SOURCE_PATH, "r", encoding="utf-8") as f:
            raw_html = f.read()
        page_source_json = compress_page_source(raw_html)
    else:
        page_source_json = "[]"

    # Compile step functions from both core.py and generated.py
    step_functions = []
    for step_file in ["bdd/steps/core.py", "bdd/steps/generated.py"]:
        if os.path.exists(step_file):
            try:
                with open(step_file, "r") as f:
                    content = f.read()
                step_functions.extend(extract_function_names(content))
            except Exception as e:
                print(f"[BehaveRunner] Error reading {step_file}: {e}")

    return {
        "page_source_json": page_source_json,
        "step_functions": step_functions
    }


def step_writer_node(state: AgentState) -> dict:
    gherkin_step = state["current_line"]
    page_source_json = state["page_source_json"]
    print(f"[StepWriter] Generating Python function for: {gherkin_step}")

    py_function = run_step_writer(gherkin_step, page_source_json)
    print(f"[StepWriter] Generated function:\n{py_function}")

    with open(CORE_PY_PATH, "a") as f:
        f.write("\n\n" + py_function)

    return {}


def loop_check_node(state: AgentState) -> dict:
    total_lines = len(state["all_lines"])
    current_index = state["current_line_index"]

    if current_index >= total_lines:
        print(f"\n[LoopCheck] All {total_lines} lines processed. Done.")
        return {"loop_done": True}

    print(f"[LoopCheck] {current_index}/{total_lines} done. Continuing...")
    return {"loop_done": False}
