import requests
import json
import os
from rich.markdown import Markdown
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from dotenv import load_dotenv
import sys
import time
import platformdirs

from ask.util import log_stdout, parse_arguments, update_panel
from ask.constants import (
    DEFAULT_MODEL,
    DEFAULT_ASAP_MODEL,
    DEFAULT_FREE_MODEL,
    DEFAULT_SYSTEM_PROMPT,
    PROGRAM_NAME,
)


def setup(user_config_dir: str, config_file: str, env_file: str) -> bool:
    # Check for all files and return if everything is present
    user_config_exists = os.path.exists(user_config_dir)
    env_file_exists = os.path.exists(env_file)
    config_file_exists = os.path.exists(config_file)

    if env_file_exists and config_file_exists:  # user_config checked implicitly
        # Leave setup
        return True

    log_stdout("Running setup...", "dim bold")
    force_free: bool = False

    # Create user_data dir if not present
    if not user_config_exists:
        log_stdout("Creating user data...")
        os.mkdir(user_config_dir)

    # Create secret file if not present
    if not env_file_exists:
        log_stdout(
            '>> Generate API key at "https://openrouter.ai/settings/keys" and paste below:',
            "bold",
        )
        # Keep asking until key is valid
        api_key: str = ""
        while True:
            api_key = input().strip()
            # Check if key works
            response = requests.get(
                "https://openrouter.ai/api/v1/key",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            if response.ok:
                data = response.json()["data"]

                if data["limit"] == 0 or data["is_free_tier"]:
                    log_stdout(
                        "NOTE: The key provided or associated account can only use free models.",
                        "bold cyan",
                    )
                    force_free = True
                break
            log_stdout(">> Key invalid. Try again:", "yellow bold")

        # Write file
        with open(env_file, "w") as file:
            file.write(f"OPENROUTER_API_KEY={api_key}")
        log_stdout("API key saved!")

    # Load .env for rest of setup
    load_dotenv(env_file)

    # Create config file if not present
    if not config_file_exists:
        config_data: dict[str, str] = {}

        # Fetch all models for validation check later
        models_data_req = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"},
        )
        if not models_data_req.ok:
            log_stdout(
                "Failed to fetch model list from Openrouter API. Try again.", "yellow"
            )
            return False

        # Parse model data into model list
        model_list_data = models_data_req.json()["data"]
        model_list: list[str] = []
        for model in model_list_data:
            model_list.append(model["id"])

        # Obtain default model
        log_stdout(
            f'>> Enter preferred default model (default: "{DEFAULT_MODEL if not force_free else DEFAULT_FREE_MODEL}"):',
            "bold",
        )
        # Keep asking until model is valid
        model_exists: bool = False
        default_model_in: str = ""
        while not model_exists:
            default_model_in = input().strip()
            # Break with default model
            if default_model_in == "":
                default_model_in = (
                    DEFAULT_MODEL if not force_free else DEFAULT_FREE_MODEL
                )
                break
            # Check if model exists
            if default_model_in in model_list:
                if force_free:
                    # TODO: Replace with pricing check
                    if not default_model_in.endswith(":free"):
                        log_stdout(
                            f'>> This key or account can only use free models. Try again (default: "{DEFAULT_MODEL if not force_free else DEFAULT_FREE_MODEL}"):',
                            "yellow bold",
                        )

                break
            log_stdout(
                f'>> Model does not exist. Try again (default: "{DEFAULT_MODEL if not force_free else DEFAULT_FREE_MODEL}"):',
                "yellow bold",
            )

        # Obtain ASAP model
        log_stdout(
            f'>> Enter preferred default ASAP model (default: "{DEFAULT_ASAP_MODEL if not force_free else DEFAULT_FREE_MODEL}"):',
            "bold",
        )
        # Keep asking until model is valid
        model_exists: bool = False
        default_asap_model_in: str = ""
        while not model_exists:
            default_asap_model_in = input().strip()
            # Break with default model
            if default_asap_model_in == "":
                default_asap_model_in = (
                    DEFAULT_ASAP_MODEL if not force_free else DEFAULT_FREE_MODEL
                )
                break
            # Check if model exists
            if default_asap_model_in in model_list:
                if force_free:
                    # TODO: Replace with pricing check
                    if not default_asap_model_in.endswith(":free"):
                        log_stdout(
                            f'>> This key or account can only use free models. Try again (default: "{DEFAULT_ASAP_MODEL if not force_free else DEFAULT_FREE_MODEL}"):',
                            "yellow bold",
                        )

                break
            log_stdout(
                f'>> Model does not exist. Try again (default: "{DEFAULT_ASAP_MODEL if not force_free else DEFAULT_FREE_MODEL}"):',
                "yellow bold",
            )

        # Populate config data and write to file
        config_data["default_model"] = default_model_in
        config_data["default_asap_model"] = default_asap_model_in
        config_data["default_system_prompt"] = DEFAULT_SYSTEM_PROMPT

        with open(config_file, "w") as file:
            json.dump(config_data, file, indent=2)

    # All done, return gracefully
    log_stdout("Setup complete!", "bold dim green")
    return True


def main():
    # Resolve relevant directories and files
    user_config_dir: str = platformdirs.user_config_dir(PROGRAM_NAME, ensure_exists=True)
    config_file: str = os.path.join(user_config_dir, "config.json")
    env_file: str = os.path.join(user_config_dir, ".env")

    # Run setup
    setup_status = setup(user_config_dir, config_file, env_file)
    if not setup_status:
        log_stdout("Setup Failed.", "bold red")
        return

    # Parse Arguments
    args: dict[str, str | bool] = parse_arguments(sys.argv[1:])

    # Load dotenv and config
    load_dotenv(env_file)
    config_data: dict[str, str] = {}
    with open(config_file, "r") as file:
        config_data = json.load(file)

    # Define payload arguments
    model: str = args["model"] or (
        config_data["default_asap_model"]
        if args["asap"]
        else config_data["default_model"]
    )
    system_prompt: str = args["system-prompt"] or config_data["default_system_prompt"]
    prompt: str = args["prompt"]

    # Assemble payload
    payload: dict = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "stream": True,
        "reasoning": {
            "effort": args["reasoning-effort"],
            "enabled": True if args["reasoning-effort"] != "none" else False,
        },
    }

    # Create display
    display_console: Console = Console(
        quiet=args["plain"],
    )
    display_panel: Panel = Panel(
        title=f"[bold]{model}[/bold]",
        renderable="Establishing Connection...",
        subtitle="0.00s",
        border_style="dim",
    )

    # Create buffers
    buffer: str = ""
    content_buffer: str = ""
    reasoning_buffer: str = ""

    # Stream cancellation
    cancelled: bool = False

    # Log start time and open display panel
    start_time = time.time()
    with Live(
        display_panel,
        console=display_console,
        refresh_per_second=20,
        vertical_overflow="visible",
    ):
        # Stream back response
        with requests.Session() as session:
            with session.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                    "Content-Type": "application/json",
                },
                json=payload,
                stream=True,
            ) as r:
                try:
                    if r.status_code != 200:
                        update_panel(
                            display_panel,
                            renderable=f"[bold red]Status Code {r.status_code} - {r.reason}[/bold red]",
                            elapsed=(time.time() - start_time),
                            border_style="dim red",
                        )
                    for chunk in r.iter_content(chunk_size=1024, decode_unicode=False):
                        # Decode Chunk
                        # try:
                        #     chunk = chunk.decode("utf-8")
                        # except UnicodeDecodeError:
                        #     chunk = chunk.decode("latin-1")
                        # WARN: above block probable cause of table bug, temporary fix below
                        chunk = chunk.decode("utf-8") 

                        # Read reasoning and response content
                        buffer += chunk
                        while True:
                            try:
                                # Find the next complete SSE line
                                line_end = buffer.find("\n")
                                if line_end == -1:
                                    break

                                line = buffer[:line_end].strip()
                                buffer = buffer[line_end + 1 :]

                                if line.startswith("data: "):
                                    data = line[6:]
                                    if data == "[DONE]":
                                        break

                                    try:
                                        data_obj = json.loads(data)
                                        if "error" in data_obj:
                                            raise Exception(
                                                data_obj["error"]["message"]
                                            )
                                        content = data_obj["choices"][0]["delta"].get(
                                            "content"
                                        )
                                        reasoning_content = data_obj["choices"][0][
                                            "delta"
                                        ].get("reasoning")
                                        if content:
                                            update_panel(
                                                display_panel,
                                                renderable=Markdown(content_buffer),
                                                elapsed=(time.time() - start_time),
                                                border_style="dim green",
                                            )
                                            content_buffer += content
                                        if reasoning_content:
                                            update_panel(
                                                display_panel,
                                                renderable=Markdown(reasoning_buffer),
                                                elapsed=(time.time() - start_time),
                                                border_style="dim blue",
                                            )
                                            reasoning_buffer += reasoning_content
                                    except json.JSONDecodeError:
                                        pass
                            except Exception as e:
                                update_panel(
                                    display_panel,
                                    renderable=f"[bold red]Unhandled Exception: `{e}`[/bold red]",
                                    elapsed=(time.time() - start_time),
                                    border_style="dim red",
                                )
                                break
                except KeyboardInterrupt:
                    # Stream Cancellation
                    cancelled = True
                    display_console.clear()
            r.close()
        update_panel(
            display_panel,
            renderable=Markdown(content_buffer or reasoning_buffer),
            elapsed=(time.time() - start_time),
            border_style="green" if content_buffer else "blue",
        )
        if cancelled:
            display_panel.subtitle = f"{time.time() - start_time:.2f}s (CANCELLED)"
    if args["plain"]:
        __import__("builtins").print(content_buffer)


if __name__ == "__main__":
    main()
