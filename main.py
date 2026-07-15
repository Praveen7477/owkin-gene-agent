"""Entry point: `python main.py`.

Loads a local .env (if present) so ANTHROPIC_API_KEY can live in a file, then
starts the CLI.
"""

import sys

from dotenv import load_dotenv

from src.cli import main

# Windows consoles default to cp1252, which garbles dashes/bullets in the LLM
# answers. Force UTF-8 output so those render correctly.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

if __name__ == "__main__":
    load_dotenv()
    raise SystemExit(main())
