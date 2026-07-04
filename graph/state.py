from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    all_lines : List[str]
    current_line_index : int
    current_line : str
    feature_file_content : str
    step_functions : List[str]
    page_source_json : str
    device_caps : dict
    loop_done : bool
    