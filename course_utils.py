"""Small, explicit helpers shared by the teaching notebooks."""

import json
import re


def parse_json_response(text):
    """Parse a JSON response, allowing an outer Markdown code fence.

    Malformed or truncated JSON still raises JSONDecodeError; we never invent
    missing fields or silently substitute an empty result.
    """
    text = text.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*\n?(.*?)\n?```", text, flags=re.DOTALL | re.IGNORECASE)
    return json.loads(fenced.group(1).strip() if fenced else text)
