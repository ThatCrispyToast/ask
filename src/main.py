import requests
import json
import os
from rich import print
from dotenv import load_dotenv


DEFAULT_MODEL = "x-ai/grok-code-fast-1"
DEFAULT_FREE_MODEL = "minimax/minimax-m2:free"
DEFAULT_SYSTEM_PROMPT = "Provide quick and concise answers while still answering fully and with sufficient detail. Match the brevity of the user unless otherwise directed."


def log_stdout(text: str, style: str = "dim"):
    print(f"[{style}]{text}[/{style}]")


def setup(user_data_dir: str, config_file: str, env_file: str) -> bool:
    # Check for all files and return if everything is present
    user_data_exists = os.path.exists(user_data_dir)
    env_file_exists = os.path.exists(env_file)
    config_file_exists = os.path.exists(config_file)


    if env_file_exists and config_file_exists: # user_data checked implicitly
        # Leave setup
        return True

    log_stdout("Running setup...", "dim bold")
    force_free: bool = False

    # Create user_data dir if not present
    if not user_data_exists:
        log_stdout("Creating user data...")
        os.mkdir(user_data_dir)

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

                if data["limit"] == 0 or data["is_free_tier"] == True:
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

        log_stdout(
            f'>> Enter preferred default model (default: "{DEFAULT_MODEL if not force_free else DEFAULT_FREE_MODEL}"):', "bold"
        )
        # Keep asking until model is valid
        model_exists: bool = False
        default_model_in: str = ""
        while model_exists == False:
            default_model_in = input().strip()
            # Break with default model
            if default_model_in == "":
                default_model_in = DEFAULT_MODEL if not force_free else DEFAULT_FREE_MODEL
                break
            # Check if model exists
            if default_model_in in model_list:
                if force_free:
                    # TODO: Replace with pricing check
                    if default_model_in.endswith(":free") == False:
                        log_stdout(f'>> This key or account can only use free models. Try again (default: "{DEFAULT_MODEL if not force_free else DEFAULT_FREE_MODEL}"):', "yellow bold")

                break
            log_stdout(f'>> Model does not exist. Try again (default: "{DEFAULT_MODEL if not force_free else DEFAULT_FREE_MODEL}"):', "yellow bold")

        # Populate config data and write to file
        config_data["default_model"] = default_model_in
        config_data["default_system_prompt"] = DEFAULT_SYSTEM_PROMPT

        with open(config_file, "w") as file:
            json.dump(config_data, file)

    # All done, return gracefully
    log_stdout("Setup complete!", "green")
    return True


def main():
    # Resolve relevant directories and files
    user_data_dir = os.path.join(os.path.dirname(__file__), "..", "user_data")
    config_file: str = os.path.join(user_data_dir, "config.json")
    env_file: str = os.path.join(user_data_dir, ".env")

    # Run setup
    setup_status = setup(user_data_dir, config_file, env_file)
    if setup_status == False:
        log_stdout("Setup Failed.", "bold red")
        return

    # Load dotenv and config
    user_data_dir = os.path.join(os.path.dirname(__file__), "..", "user_data")
    load_dotenv(os.path.join(user_data_dir, ".env"))
    config_data: dict[str, str] = {}
    with open(os.path.join(user_data_dir, "config.json"), "r") as file:
        config_data = json.load(file)

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        },
        data=json.dumps(
            {
                "model": config_data["default_model"],
                "messages": [
                    {"role": "user", "content": "x86 asm vs riscv asm"}
                ],
            }
        ),
    )

    print(response.json()["choices"][0]["message"]["content"])


if __name__ == "__main__":
    main()
