"""Unit tests for the data layer, tool dispatch, and offline agent.

These run without any API key so anyone can verify the core logic with `pytest`.
"""

from src import data
from src.agent import RuleAgent
from src.tools import run_tool


def test_get_targets_known_cancer():
    genes = data.get_targets("lung")
    assert "KRAS" in genes
    assert len(genes) == 5


def test_get_targets_is_case_insensitive():
    assert data.get_targets("LUNG") == data.get_targets("lung")


def test_get_targets_unknown_cancer_is_empty():
    assert data.get_targets("esophageal") == []


def test_get_expressions_is_cancer_scoped():
    # TP53 exists in many cancers; scoping to breast must return breast's value.
    expr = data.get_expressions("breast", ["TP53"])
    assert expr == {"TP53": 0.233}


def test_run_tool_dispatch():
    result = run_tool("get_targets", {"cancer_name": "breast"})
    assert "BRCA1" in result["genes"]


def test_rule_agent_lists_genes():
    answer = RuleAgent().ask("What are the main genes involved in lung cancer?")
    assert "KRAS" in answer


def test_rule_agent_reports_expression():
    answer = RuleAgent().ask(
        "What is the median expression of genes involved in breast cancer?"
    )
    assert "TP53" in answer and "0.233" in answer


def test_rule_agent_handles_unknown_cancer_gracefully():
    answer = RuleAgent().ask(
        "What is the median expression of genes involved in esophageal cancer?"
    )
    assert "esophageal" in answer.lower()
    assert "lung" in answer  # suggests what IS available


def test_rule_agent_help():
    answer = RuleAgent().ask("How can you help me?")
    assert "assistant" in answer.lower()
