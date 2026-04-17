import re
from typing import Any, Dict


PATTERN = re.compile(r"\$\{([a-zA-Z0-9_]+)\}")


def render_value(value: Any, context: Dict[str, Any]) -> Any:
    if isinstance(value, str):
        def _replace(match: re.Match) -> str:
            key = match.group(1)
            return str(context.get(key, match.group(0)))

        return PATTERN.sub(_replace, value)
    if isinstance(value, list):
        return [render_value(item, context) for item in value]
    if isinstance(value, dict):
        return {k: render_value(v, context) for k, v in value.items()}
    return value
