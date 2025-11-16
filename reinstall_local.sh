#!/usr/bin/env bash

set -xe

# Clear .config
if [[ "$1" == "clear" ]]; then
	CONFIG_PATH="$(python -c 'import platformdirs; print(platformdirs.user_data_dir("ask") + "/config.json")')"
	rm "$CONFIG_PATH"
fi

# Reinstall Local Package
uv tool install "$(git rev-parse --show-toplevel)" --reinstall

# Run Help Page
ask --help
