from __future__ import annotations

import ast
from pathlib import Path
from typing import TypedDict

from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    root: str
    files: list[str]
    modules: list[dict]
    overview: str


IGNORE = {".git", ".venv", "__pycache__", ".mypy_cache", ".pytest_cache", "dist", "build"}


def scan_repo(state: State) -> State:
    root = Path(state["root"])
    files = [
        str(p.relative_to(root))
        for p in root.rglob("*.py")
        if not any(part in IGNORE for part in p.parts)
    ]
    return {**state, "files": files}


def extract_python_structure(state: State) -> State:
    root = Path(state["root"])
    modules = []

    for rel in state["files"]:
        path = root / rel
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except Exception as e:
            modules.append({"file": rel, "error": str(e)})
            continue

        imports = []
        classes = []
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                functions.append(node.name)

        modules.append({
            "file": rel,
            "imports": sorted(set(imports)),
            "classes": classes,
            "functions": functions,
        })

    return {**state, "modules": modules}


def write_overview(state: State) -> State:
    lines = ["# Project Overview", "", "## Python Modules", ""]

    for mod in state["modules"]:
        lines.append(f"### `{mod['file']}`")
        if "error" in mod:
            lines.append(f"- Parse error: {mod['error']}")
        else:
            lines.append(f"- Classes: {', '.join(mod['classes']) or 'none'}")
            lines.append(f"- Functions: {', '.join(mod['functions']) or 'none'}")
            lines.append(f"- Imports: {', '.join(mod['imports'][:20]) or 'none'}")
        lines.append("")

    overview = "\n".join(lines)
    Path(state["root"], "PROJECT_OVERVIEW.md").write_text(overview, encoding="utf-8")
    return {**state, "overview": overview}


graph = StateGraph(State)
graph.add_node("scan_repo", scan_repo)
graph.add_node("extract_python_structure", extract_python_structure)
graph.add_node("write_overview", write_overview)

graph.add_edge(START, "scan_repo")
graph.add_edge("scan_repo", "extract_python_structure")
graph.add_edge("extract_python_structure", "write_overview")
graph.add_edge("write_overview", END)

app = graph.compile()


if __name__ == "__main__":
    app.invoke({
        "root": ".",
        "files": [],
        "modules": [],
        "overview": "",
    })


    print(f"Scanned {len(['files'])} Python files")
    print("Wrote PROJECT_OVERVIEW.md")