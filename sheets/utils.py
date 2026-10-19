import re


def sanitize_cell(value: str) -> str:
    return re.sub(r'^[=+\-@]+', '', value.strip())
