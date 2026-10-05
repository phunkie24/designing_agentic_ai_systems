# Agentic AI Systems — Teaching Workspace

Twelve notebooks cover Chapters 1–13; Chapters 5 and 6 share a notebook.
The project environment targets Windows and Python 3.14. The lock file records
that environment; on other platforms, resolve from `requirements.txt` instead.
All 343 original cells and the original exercises are retained. Runtime fixes are
recorded in `tests/teaching_fixes.json`. The portable preservation baseline in
`tests/original_baseline.json` lets the tests run after cloning. Original backups
remain in the instructor's local `.backups/` folder and are not published.

## Start teaching on Windows

From PowerShell in this folder, run the setup once:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
```

Then start each teaching session with:

```powershell
.\start-course.cmd
```

Select **Python (Agentic AI Course)** in JupyterLab. Restart the kernel and run
cells from the top for a clean lesson. The optional `%pip` cell can be skipped
after setup. It uses the same locked dependencies as the setup script.

The setup command permits that PowerShell process to run the local setup script;
it does not change your saved execution policy. The `.cmd` launcher works with
the machine's existing restricted PowerShell policy.

To open an activated terminal without starting Jupyter:

```powershell
cmd /k .venv\Scripts\activate.bat
```

If PowerShell blocks scripts, use the interpreter directly (no policy change needed):

```powershell
.\.venv\Scripts\python.exe -m jupyterlab
```

`.venv` is the Python environment. `.env` is the private settings file, loaded
automatically by `course_config.py`. Your existing `.env` is preserved. Set
`DEEPSEEK_API_KEY`, `DEEPSEEK_MODEL`, and `DEEPSEEK_BASE_URL` using `.env.example`
as a reference. Restart the kernel after changing settings. Never display the key
while screen sharing or commit `.env`.

The default path uses DeepSeek through its
[Anthropic-compatible endpoint](https://api-docs.deepseek.com/guides/anthropic_api/).
The legacy optional Gemini branches remain in the notebooks, but they are not the
validated teaching path; changing their provider also requires Google credentials
and checking that their model is still available. Some tool examples explicitly
use the Anthropic SDK regardless of the introductory provider switch.

Legacy chain, memory, and agent examples use `langchain_classic`, following the
[LangChain migration guide](https://docs.langchain.com/oss/python/migrate/langchain-v1),
so the lesson patterns remain available on the installed Python version.

## Lesson sequence

| Chapter | Pattern | Check during the lesson |
| --- | --- | --- |
| 1 | Prompt chaining | Each step consumes the previous step's output |
| 2 | Routing | Different requests reach the intended specialist |
| 3 | Parallelization | Independent work runs concurrently; compare timings |
| 4 | Reflection | A critique changes the next draft and the loop stops |
| 5–6 | Tools and planning | Inspect arguments, results, dependencies, and replanning |
| 7 | Multi-agent collaboration | Trace what each agent contributes to the answer |
| 8 | Memory | Compare stateless, session, and cross-session recall |
| 9 | Learning and adaptation | Distinguish prompt adaptation from classifier training |
| 10 | MCP | Discover tools, inspect valid schemas, and call a tool |
| 11 | Goal monitoring | Compare an output against measurable acceptance criteria |
| 12 | Recovery | Observe a simulated failure, retry, fallback, and escalation |
| 13 | Human review | Explain when the simulated agent requests approval |

For each lesson: state the objective, explain the first example, run it, inspect
the intermediate outputs, change one input, then assign an existing exercise.
Full notebook runs make many paid API calls. Rehearse before class and keep the
executed copies in `.validation/` for reviewing outputs if the API is unavailable.

## Classroom assumptions

- Prices, weather, CRM records, emails, approvals, and transactions are simulated.
  Model-generated research is illustrative, not source-verified research.
- The human reviewer in Chapter 13 is simulated by an LLM; it is not a real
  approval system. No real payments, deployments, or messages are performed.
- Chapter 5's generated Python runs locally with limited builtins. This is not a
  security sandbox; use trusted classroom prompts and review generated code.
- The early MCP classes are in-memory teaching models. Chapter 10 also writes
  `fastmcp_server.py` in this folder. Run it in a separate activated terminal for
  the optional real server at `http://127.0.0.1:8000/mcp`. Connect with
  [`fastmcp.Client`](https://gofastmcp.com/clients/client), not the earlier teaching class.
- Random simulations and live model outputs vary. Check the behavior and criteria,
  rather than expecting identical wording, scores, or timings on every run.

## Validation and troubleshooting

See [TEACHING_READINESS.md](TEACHING_READINESS.md) for the recorded rehearsal
results, repairs, and remaining inspection limits.

The `.validation/` rehearsal outputs and private `.env` are local-only. After
cloning, run setup and add your own API key; rerun the validation commands below
to generate your own execution reports.

```powershell
# Installed imports and .env presence; no live model calls
.\.venv\Scripts\python.exe scripts/preflight.py

# A small live API check
.\.venv\Scripts\python.exe scripts/preflight.py --live

# Offline regression tests and syntax checks for every cell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts/validate_course.py

# Full live execution (uses API credits); results saved under .validation/
.\.venv\Scripts\python.exe scripts/validate_course.py --execute

# Rehearse just one chapter
.\.venv\Scripts\python.exe scripts/validate_course.py --execute --chapter 10
```

If a package import fails, rerun `setup.ps1` and select the course kernel. If a
model call fails, run the live preflight and check credentials, network access,
account balance, and rate limits. A `max_tokens` stop means the response was cut
short; increase that example's token budget. Tool loops stop after eight rounds.

Static checks do not prove live behavior. Consult `.validation/` reports and
executed notebooks for the actual run status; an unexecuted notebook is not a
verified live lesson.
