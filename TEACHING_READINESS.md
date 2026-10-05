# Teaching validation — 5 October 2026

All 12 notebooks completed live execution against the configured DeepSeek API.
Executed code and Markdown match the delivered notebooks. The 343 original cells
and all original exercises remain present. Installation cells were skipped during
rehearsal because dependencies were installed in `.venv` first.

The final offline suite passes 13 tests, all notebooks pass syntax/schema checks,
and `pip check` reports no dependency conflicts. The course kernel is registered as
**Python (Agentic AI Course)**. Windows batch activation was verified to select
this project's `.venv/Scripts/python.exe`. `.env` was preserved and a live API
smoke check returned `READY` without exposing the key.

## Live rehearsal results

Times are observed for these runs; model responses and network latency vary.

| Chapter | Result | Duration |
| --- | --- | --- |
| 1 | Passed | 87.1 s |
| 2 | Passed | 73.5 s |
| 3 | Passed | 80.4 s |
| 4 | Passed | 129.7 s |
| 5–6 | Passed | 99.6 s |
| 7 | Passed | 236.9 s |
| 8 | Passed | 231.7 s |
| 9 | Passed | 115.8 s |
| 10 | Passed | 40.3 s |
| 11 | Passed | 94.2 s |
| 12 | Passed | 31.2 s |
| 13 | Passed | 109.7 s |

## Repairs

- Consistent locked dependency installation and dedicated Jupyter kernel.
- Python 3.14-compatible LangChain packages and classic imports for legacy examples.
- Markdown-fenced JSON handling in prompt chaining.
- Bounded tool loops and handling of truncated tool responses.
- Valid MCP JSON schema types, Windows-compatible server path, and step-field references.
- Tool signatures supplied to planning argument generation; plans list available tools.
- Stratified classifier evaluation with explicit, correctly ordered class labels.
- Null-safe human-review output and strict boolean approval checks.

## Rehearsal artifacts and limits

Executed notebook copies, per-chapter JSON reports, logs, and three rendered HTML
previews are in `.validation/`. Root notebooks have clean outputs for presenting
and running the lesson live. Original and pre-debug backups are in `.backups/`.
These directories are local instructor artifacts and are excluded from GitHub.
The committed `tests/original_baseline.json` contains the original cell types,
normalized code hashes, and exercise labels so preservation tests work in a fresh clone.

Visual inspection could not be completed because no browser or native-app surface
was available. Open `.validation/html/Chapter_1_Prompt_Chaining.html` and the MCP and
goal-monitoring previews beside it to review layout, or open the executed copies in
JupyterLab. The optional external HTTP FastMCP server was not exercised over HTTP;
its generated server was tested through the real FastMCP in-process client.
Optional Gemini branches were not executed. Simulated tools and reviewer decisions
are labeled in the notebooks and README. Live output correctness still needs the
instructor's review; a successful run does not verify generated research claims.

Run `start-course.cmd` to activate the environment and open JupyterLab. Use the
README commands to rehearse again before class. API calls consume account credits.
