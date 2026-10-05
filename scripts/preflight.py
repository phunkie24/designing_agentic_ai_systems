"""Check the teaching environment without printing credentials."""

import argparse
import importlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Make a small paid API request")
    args = parser.parse_args()
    print(f"Python: {sys.version.split()[0]}\nInterpreter: {sys.executable}")
    errors = []
    for name in ("anthropic", "dotenv", "langchain_anthropic", "langchain_classic.agents",
                 "langchain_classic.memory", "sklearn", "numpy", "fastmcp", "mcp",
                 "jupyterlab", "nbformat", "nbclient", "ipykernel"):
        try:
            importlib.import_module(name)
            print(f"OK: {name}")
        except Exception as exc:
            errors.append(name)
            print(f"FAIL: {name}: {type(exc).__name__}: {exc}")
    try:
        from course_config import MODEL, base_url
        print(f"Configuration loaded: {MODEL} at {base_url}; API key present (hidden)")
        if args.live:
            import anthropic
            with anthropic.Anthropic(timeout=30, max_retries=0) as client:
                result = client.messages.create(
                    model=MODEL, max_tokens=16, thinking={"type": "disabled"},
                    messages=[{"role": "user", "content": "Reply only READY"}])
            text = "".join(b.text for b in result.content if b.type == "text")
            if not text.strip():
                raise RuntimeError("API returned no text")
            print(f"Live API responded: {text.strip()}")
    except Exception as exc:
        errors.append("configuration/API")
        # Provider errors may include request details; never print the credential.
        print(f"FAIL: configuration/API: {type(exc).__name__}")
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
