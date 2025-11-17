# `ask`

> A small plug-and-play oneshot openrouter cli.

## Installation

**Requirements**:
- [`uv`](https://github.com/astral-sh/uv)

Run `ask` transiently with [`uvx`](https://docs.astral.sh/uv/):

```shell
uvx --from git+https://github.com/ThatCrispyToast/ask/ ask Hello!
uvx --from git+https://github.com/ThatCrispyToast/ask/ ask -sp "Respond in Spanish." Who invented the computer?
```

Install with:

```shell
uv tool install git+https://github.com/ThatCrispyToast/ask/
```

This will expose an executable under the name `ask`.

Uninstall with:

```shell
uv tool uninstall ask
```


## Setup
When running `ask` for the first time, you'll be prompted to enter your Openrouter API key. Generate one at [the Openrouter website](https://openrouter.ai/settings/keys).
You'll also be prompted to enter the model(s) you'd like to use by default. Reasonable defaults are provided.

## Usage
Run `ask --help` to get a list of options and examples.

For the sake for convienence, `ask` parses arguments differently. Any passed arguments that don't match a known option are sent as a part of the prompt.

```shell
# These are functionally the same
ask "python set vs list"
ask python set vs list

# As are these
ask -m "openai/gpt-oss-20b" -10 + -10
ask -m "openai/gpt-oss-20b" "-10 + -10"

```

Note that system prompts do still require quotes.

```shell
ask Hello! --system-prompt "Speak in pig latin."
ask Hello! --system-prompt Speak in pig latin. # In this case, the system prompt will be set to "Speak" and "in pig latin" will be appended to the prompt.
```

## Development

### NixOS

A nix flake is provided to create an environment with all development dependencies.

### General

**Requirements**:
- [`uv`](https://github.com/astral-sh/uv)
- [`vhs`](https://github.com/charmbracelet/vhs)

[Python dependencies are managed by uv.](./pyproject.toml)
