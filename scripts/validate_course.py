"""Validate course structure, or execute notebooks with the configured live API."""

import argparse
import ast
import json
from pathlib import Path
import re
import sys
import time

import nbformat
from IPython.core.inputtransformer2 import TransformerManager

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Calls the live API; uses account credits")
    parser.add_argument("--chapter", type=int, help="Run only this chapter (5 includes 6)")
    args = parser.parse_args()
    paths = sorted(ROOT.glob("*.ipynb"), key=lambda p: int(re.search(r"\d+", p.name)[0]))
    if args.chapter:
        paths = [p for p in paths if int(re.search(r"\d+", p.name)[0]) == (5 if args.chapter == 6 else args.chapter)]
        if not paths:
            parser.error("Chapter must be between 1 and 13")
    output_dir = ROOT / ".validation"
    output_dir.mkdir(exist_ok=True)
    reports = []
    for path in paths:
        started = time.monotonic()
        notebook = nbformat.read(path, as_version=4)
        report = {"notebook": path.name, "mode": "live" if args.execute else "static"}
        print(f"Checking {path.name}", flush=True)
        try:
            nbformat.validate(notebook)
            for index, cell in enumerate(notebook.cells):
                if cell.cell_type == "code":
                    code = TransformerManager().transform_cell(cell.source)
                    compile(code, f"{path.name}:cell-{index + 1}", "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
            if args.execute:
                from nbclient import NotebookClient
                # Dependencies are installed once by setup.ps1, not during a lesson.
                client = NotebookClient(notebook, timeout=600, kernel_name="agentic-ai-course",
                                        resources={"metadata": {"path": str(ROOT)}},
                                        skip_cells_with_tag="installation")
                def progress(cell, cell_index, **kwargs):
                    print(f"  Cell {cell_index + 1}/{len(notebook.cells)}", flush=True)
                client.on_cell_start = progress
                try:
                    client.execute()
                finally:
                    nbformat.write(notebook, output_dir / path.name)
            report["status"] = "passed"
        except Exception as exc:
            report.update(status="failed", error=str(exc))
            print(f"FAILED: {path.name}: {type(exc).__name__}: {exc}", flush=True)
        report["seconds"] = round(time.monotonic() - started, 1)
        reports.append(report)
        print(f"{report['status'].upper()} ({report['seconds']}s)", flush=True)
    suffix = f"-chapter-{args.chapter}" if args.chapter else ""
    report_path = output_dir / f"{'live' if args.execute else 'static'}{suffix}.json"
    report_path.write_text(json.dumps(reports, indent=2), encoding="utf-8")
    return int(any(r["status"] == "failed" for r in reports))


if __name__ == "__main__":
    sys.exit(main())
