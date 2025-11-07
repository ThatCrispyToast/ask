import requests
import json
import os
from rich import print
from dotenv import load_dotenv


SCRIPT_DIRECTORY = __file__
DEFAULT_MODEL = "x-ai/grok-code-fast-1"
DEFAULT_SYSTEM_PROMPT =  "Provide quick and concise answers while still answering fully and with sufficient detail. Match the brevity of the user unless otherwise directed."


def log_stdout(text: str, style: str = "dim"):
    print(f"[{style}]{text}[/{style}]")


def setup() -> bool:
    # Resolve relevant directories and files
    user_data_dir = os.path.join(os.path.dirname(__file__), "..", "user_data")
    config_file: str = os.path.join(user_data_dir, "config.json")
    env_file: str = os.path.join(user_data_dir, ".env")

    # Check for all files and return if everything is present
    user_data_exists = os.path.exists(user_data_dir)
    env_file_exists = os.path.exists(env_file)
    config_file_exists = os.path.exists(config_file)

    if user_data_exists and env_file_exists and config_file_exists:
        # Leave setup
        return True

    # Create user_data dir if not present
    if not user_data_exists:
        log_stdout("Creating user data...")
        os.mkdir(user_data_dir)

    # Create secret file if not present
    if not env_file_exists:
        log_stdout(
            'Generate API key at "https://openrouter.ai/settings/keys" and paste below:', "bold")
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
                break
            log_stdout("Key invalid, try again:", "yellow")

        # Write file
        with open(env_file, 'w') as file:
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
                headers={"Authorization": f"Bearer {os.getenv("OPENROUTER_API_KEY")}"},
        )
        if not models_data_req.ok:
            log_stdout("Failed to fetch models from Oopenrouter API. Try again.", "yellow")
            return False

            # Parse model data into model list
        model_list: list[str] = []
        for model in models_data_req.json()["data"]:
            model_list.append(model["id"])


        log_stdout(f">> Enter preferred default model (default: \"{DEFAULT_MODEL}\"):", "bold")
        # Keep asking until model is valid
        model_exists: bool = False
        default_model_in: str = ""
        while not model_exists:
            default_model_in = input().strip()
            # Break with default model
            if default_model_in == "":
                default_model_in = DEFAULT_MODEL
                break
            # Check if model exists
            if default_model_in in model_list:
                break
            print()

        # Populate config data and write to file
        config_data["default_model"] = default_model_in
        config_data["default_system_prompt"] = DEFAULT_SYSTEM_PROMPT

        with open(config_file, 'w') as file:
            json.dump(config_data, file)

    # All done, return gracefully
    log_stdout("Setup complete!", "green")
    return True



def main():
    # Run setup
    setup_status = setup()
    if setup_status == False:
        log_stdout("Setup Failed.", "bold red")
        return

    # Load dotenv and config
    user_data_dir = os.path.join(os.path.dirname(__file__), "..", "user_data")
    load_dotenv(os.path.join(user_data_dir, ".env"))
    config_data: dict[str, str] = {}
    with open(os.path.join(user_data_dir, "config.json"), 'r') as file:
        config_data = json.load(file)


    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv("OPENROUTER_API_KEY")}",
        },
        data=json.dumps(
            {
                "model": config_data["default_model"],
                "messages": [
                    {"role": "user", "content": "How many r's are in strawberry?"}
                ],
            }
        ),
    )

    print(response.json())


if __name__ == "__main__":
    main()
