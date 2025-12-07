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
        "Set the Openrouter model to use. Overrides '--asap' and '--preset'. Default in 'config.json'",
    ),
    (
        "system-prompt",
        "sp",
        "",
        "Set the system prompt passed to the model. Overrides '--preset'. Default in 'config.json'",
    ),
    (
        "asap",
        "a",
        False,
        "Use your config's 'default_asap_model' to retrieve a response faster",
    ),
    (
        "plain",
        "P",
        False,
        "Respond without text decorations, streaming, or pretty output",
    ),
    (
        "reasoning-effort",
        "r",
        "medium",
        "Set model reasoning level (default 'medium'): 'none', 'minimal', 'low', 'medium', 'high'",

    ),
    # (
    #     "preset",
    #     "p",
    #     "",
    #     "Use a model/system-prompt preset defined in your 'config.json'",
    # ),
]
