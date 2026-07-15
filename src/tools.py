"""The tools the LLM is allowed to call, plus their JSON schemas."""

from typing import Any, Dict, List

from . import data

# Schemas we pass to the Anthropic API so the model knows what it can call.
TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "name": "list_cancers",
        "description": (
            "List every cancer type in the dataset. Useful for help questions or "
            "when a requested cancer is not found."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_targets",
        "description": (
            "Return the genes for a given cancer type. Empty list if the cancer "
            "is not in the dataset."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "cancer_name": {
                    "type": "string",
                    "description": "Cancer type, e.g. 'lung', 'breast'.",
                }
            },
            "required": ["cancer_name"],
        },
    },
    {
        "name": "get_expressions",
        "description": (
            "Return median expression values for genes of a cancer. Call "
            "get_targets first to get the gene list, then pass it here."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "cancer_name": {
                    "type": "string",
                    "description": "Cancer the genes belong to.",
                },
                "genes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Gene symbols to look up.",
                },
            },
            "required": ["cancer_name", "genes"],
        },
    },
]


def run_tool(name: str, tool_input: Dict[str, Any]) -> Any:
    """Run a tool by name and return the result."""
    if name == "list_cancers":
        return {"available_cancers": data.list_cancers()}
    if name == "get_targets":
        cancer = tool_input["cancer_name"]
        return {"cancer": cancer, "genes": data.get_targets(cancer)}
    if name == "get_expressions":
        cancer = tool_input["cancer_name"]
        genes = tool_input["genes"]
        return {"cancer": cancer, "expressions": data.get_expressions(cancer, genes)}
    raise ValueError(f"Unknown tool: {name}")
