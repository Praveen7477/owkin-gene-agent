"""Command-line chat interface for the Owkin gene-expression assistant."""

from __future__ import annotations

import argparse
import sys

from .agent import build_agent

BANNER = """
============================================================
 Owkin gene-expression assistant  (proof of concept)
============================================================
Ask questions in plain English, for example:
  - How can you help me?
  - What are the main genes involved in lung cancer?
  - What is the median expression of genes involved in breast cancer?

Type 'exit' or 'quit' to leave.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Owkin gene-expression assistant")
    parser.add_argument(
        "-q",
        "--question",
        help="Ask a single question and exit (non-interactive mode).",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Force the offline rule-based agent (no API calls).",
    )
    args = parser.parse_args(argv)

    agent = build_agent(force_rule=args.offline)

    # One-shot mode: handy for scripting and grading.
    if args.question:
        print(agent.ask(args.question))
        return 0

    # Interactive REPL.
    print(BANNER)
    while True:
        try:
            question = input("you > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break
        print("\nassistant >", agent.ask(question), "\n")

    print("Goodbye.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
