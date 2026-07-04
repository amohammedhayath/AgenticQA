import ast


def validate_gherkin(text: str) -> bool:
    if not text:
        return False

    valid_keywords = ("given", "when", "then", "and", "but")
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]

    for line in lines:
        if not any(line.lower().startswith(kw) for kw in valid_keywords):
            return False

    return True


def validate_python(text: str) -> bool:
    if not text:
        return False

    try:
        ast.parse(text)
        return True
    except SyntaxError:
        return False


def extract_function_names(code: str) -> list:
    try:
        tree = ast.parse(code)
        return [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        ]
    except SyntaxError:
        return []