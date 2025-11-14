# Config defaults
DEFAULT_MODEL = "x-ai/grok-code-fast-1"
DEFAULT_FREE_MODEL = "minimax/minimax-m2:free"
DEFAULT_ASAP_MODEL = "openai/gpt-oss-safeguard-20b"
DEFAULT_SYSTEM_PROMPT = "Provide quick and concise answers while still answering fully and with sufficient detail. Match the brevity of the user unless otherwise directed."

PROGRAM_NAME = "ask"


ARGUMENT_DEFINITIONS: list[tuple[str, str, str | bool]] = [
    ("model", "m", ""),
    ("system-prompt", "sp", ""),
    ("asap", "a", False),
]
