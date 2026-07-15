"""The agent that answers a question.

There are two versions:
- LLMAgent: uses Claude with tool calling. The model decides which functions to
  call. This is the main version.
- RuleAgent: a simple keyword fallback so the app still runs with no API key.

build_agent() picks the LLM one if a key is set, otherwise the rule one.
"""

from __future__ import annotations

import os
import re
from typing import List, Protocol

from . import data
from .tools import TOOL_SCHEMAS, run_tool

DEFAULT_MODEL = os.environ.get("OWKIN_MODEL", "claude-sonnet-5")
MAX_AGENT_STEPS = 6

SYSTEM_PROMPT = """You are Owkin's gene-expression data assistant.

You help non-technical users explore a dataset of cancers, their genes, and
median expression values. Only answer from the dataset by calling the tools,
never from your own biology knowledge.

- To find genes for a cancer, call get_targets.
- For expression values, call get_targets first, then get_expressions.
- If a cancer is not in the dataset, say so and list the ones you do have
  (list_cancers). Do not make up data.
- Keep answers short and readable, e.g. a small table for expression values.
"""


class Agent(Protocol):
    def ask(self, question: str) -> str: ...


class LLMAgent:
    """Claude with tool calling."""

    def __init__(self, model: str = DEFAULT_MODEL):
        from anthropic import Anthropic  # imported here so the fallback needs no dep

        self.client = Anthropic()
        self.model = model

    def ask(self, question: str) -> str:
        messages = [{"role": "user", "content": question}]

        for _ in range(MAX_AGENT_STEPS):
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=TOOL_SCHEMAS,
                messages=messages,
            )
            messages.append({"role": "assistant", "content": response.content})

            # No tool call means the model gave its final answer.
            if response.stop_reason != "tool_use":
                return "".join(
                    block.text for block in response.content if block.type == "text"
                ).strip()

            # Run whatever tools the model asked for and send the results back.
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    try:
                        result = run_tool(block.name, block.input)
                    except Exception as exc:
                        result = {"error": str(exc)}
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(result),
                        }
                    )
            messages.append({"role": "user", "content": tool_results})

        return "Sorry, I couldn't finish that within the step limit."


class RuleAgent:
    """Fallback keyword matcher used when there is no API key."""

    WANTS_EXPRESSION = re.compile(r"express|median|value|level", re.IGNORECASE)
    WANTS_HELP = re.compile(r"help|what can you|who are you|capab", re.IGNORECASE)
    # the word right before "cancer", e.g. "esophageal" in "esophageal cancer"
    CANDIDATE_CANCER = re.compile(r"(\w+)\s+cancer", re.IGNORECASE)

    def _find_cancer(self, question: str) -> str | None:
        q = question.lower()
        for cancer in data.list_cancers():
            if cancer.lower() in q:
                return cancer
        return None

    def _candidate_term(self, question: str) -> str | None:
        match = self.CANDIDATE_CANCER.search(question)
        return match.group(1) if match else None

    def ask(self, question: str) -> str:
        if self.WANTS_HELP.search(question) and not self._find_cancer(question):
            return self._help()

        cancer = self._find_cancer(question)
        if cancer is None:
            term = self._candidate_term(question)
            named = f" on '{term}' cancer" if term else " for that cancer type"
            return f"I don't have any data{named} in the dataset.\n\n" + self._available()

        genes = data.get_targets(cancer)
        if not genes:
            return f"I don't have any data on '{cancer}'.\n\n" + self._available()

        if self.WANTS_EXPRESSION.search(question):
            expr = data.get_expressions(cancer, genes)
            lines = [f"Median expression values for genes involved in {cancer} cancer:"]
            for gene, value in sorted(expr.items(), key=lambda kv: kv[1], reverse=True):
                lines.append(f"  - {gene}: {value}")
            return "\n".join(lines)

        return f"The genes involved in {cancer} cancer are: " + ", ".join(genes) + "."

    def _available(self) -> str:
        return "Cancers I have data for: " + ", ".join(data.list_cancers()) + "."

    def _help(self) -> str:
        return (
            "I'm Owkin's gene-expression data assistant. I can:\n"
            "  1. List the genes involved in a given cancer type.\n"
            "  2. Report the median expression value of those genes.\n\n"
            "Try: 'What are the main genes involved in lung cancer?' or\n"
            "'What is the median expression of genes involved in breast cancer?'\n\n"
            + self._available()
        )


def build_agent(force_rule: bool = False) -> Agent:
    if not force_rule and os.environ.get("ANTHROPIC_API_KEY"):
        try:
            agent = LLMAgent()
            print(f"[agent] Using Claude ({agent.model}).")
            return agent
        except Exception as exc:
            print(f"[agent] LLM backend unavailable ({exc}); using offline mode.")
    else:
        reason = "forced" if force_rule else "no ANTHROPIC_API_KEY"
        print(f"[agent] Offline rule-based mode ({reason}).")
    return RuleAgent()
