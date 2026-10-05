"""Load DeepSeek credentials for the notebooks' existing Anthropic SDK examples."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-flash").strip() or "deepseek-flash"
api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
if not api_key:
    raise ValueError("Add DEEPSEEK_API_KEY to .env, then restart the notebook kernel.")

base_url = (os.getenv("DEEPSEEK_BASE_URL", "").strip() or "https://api.deepseek.com").rstrip("/")
if not base_url.endswith("/anthropic"):
    base_url += "/anthropic"
os.environ["ANTHROPIC_API_KEY"] = api_key
os.environ["ANTHROPIC_BASE_URL"] = base_url
