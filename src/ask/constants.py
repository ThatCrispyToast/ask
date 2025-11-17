# Config defaults
DEFAULT_MODEL = "openai/gpt-oss-120b"
DEFAULT_FREE_MODEL = "kwaipilot/kat-coder-pro:free"
DEFAULT_ASAP_MODEL = "openai/gpt-oss-safeguard-20b"
DEFAULT_SYSTEM_PROMPT = "Provide quick and concise answers while still answering fully and with sufficient detail. Match the brevity of the user unless otherwise directed."

# Meta constants
PROGRAM_NAME = "ask"

# Define arguments in parse step (long_name, short_name, default_value, description)
ARGUMENT_DEFINITIONS: list[tuple[str, str, str | bool, str]] = [
    (
        "model",
        "m",
        "",
        "Sets the Openrouter model to use. Overrides '--asap'. Default: 'config.default_model'.",
    ),
    (
        "system-prompt",
        "sp",
        "",
        "Sets the system prompt passed to the model. Default: 'config.default_system_prompt'.",
    ),
    (
        "asap",
        "a",
        False,
        "Uses your config's 'default_asap_model' to retrieve a response faster.",
    ),
    (
        "plain",
        "p",
        False,
        "Responds without text decorations, streaming, or pretty output.",
    ),
    (
        "reasoning-effort",
        "r",
        "medium",
        "Controls the model's reasoning behavior. Default: 'medium'. ('none', 'minimal', 'low', 'medium', 'high')",
    ),
]
