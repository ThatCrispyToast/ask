from rich import print
from rich.markdown import Markdown
from rich.panel import Panel
import sys

from ask.constants import ARGUMENT_DEFINITIONS, PROGRAM_NAME


def log_stdout(text: str, style: str = "dim"):
    print(f"[{style}]{text}[/{style}]")


def update_panel(
    display_panel: Panel, renderable: Markdown | str, elapsed: float, border_style: str
) -> None:
    display_panel.renderable = renderable
    display_panel.subtitle = f"{elapsed:.2f}s"
    display_panel.border_style = border_style


def build_help_page() -> str:
    page_buf: str = ""

    page_buf += "[b]Quickly get a response to a prompt from the Openrouter API.[/b]\n\n"
    page_buf += f"Usage: {PROGRAM_NAME} [OPTIONS] PROMPT\n"

    page_buf += "Example: `ask rust borrow checker eli5`\n\n"

    page_buf += "Positional Arguments:\n"
    page_buf += "\tPROMPT\tThe user prompt to pass to the model.\n\n"

    page_buf += "Options:\n"
    for argument in ARGUMENT_DEFINITIONS:
        usage: str = f' <{argument[0].upper().replace("-", "_")}>' if type(argument[2]) is not bool else ''
        page_buf += f"\t-{argument[1]}{usage}, --{argument[0]}{usage}\n"
        page_buf += f"\t\t{argument[3]}\n"

    page_buf += "\t-h, --help\n"
    page_buf += "\t\tDisplays this help page.\n"



    return page_buf


def parse_arguments(argv: list[str]) -> dict[str, str | bool]:
    # Assemble argument definition lists for option parsing
    long_names: list[str] = [adef[0] for adef in ARGUMENT_DEFINITIONS]
    short_names: list[str] = [adef[1] for adef in ARGUMENT_DEFINITIONS]

    # Build argument list w/ defaults
    args: dict[str, str | bool] = {}
    for defined_argument in ARGUMENT_DEFINITIONS:
        args[defined_argument[0]] = defined_argument[2]
    # Default to plain if output is being piped
    if not sys.stdout.isatty():
        args["plain"] = True

    # Build prompt and options
    prompt_list: list[str] = []
    skip_next: bool = False
    for argument_idx in range(len(argv)):
        # Skip if argument is an option's previously set value
        if skip_next:
            skip_next = False
            continue
        # Read options (arguments starting with '-')
        if argv[argument_idx].startswith("-"):
            # First, handle long and short aliases, then check if option is a 'switch' (False->True)
            option = argv[argument_idx].lstrip("-")
            if option in long_names:
                if type(ARGUMENT_DEFINITIONS[long_names.index(option)][2]) is bool:
                    args[option] = True
                else:
                    args[option] = argv[argument_idx + 1]
                    skip_next = True
            elif option in short_names:
                option_index: int = short_names.index(option)
                if type(ARGUMENT_DEFINITIONS[option_index][2]) is bool:
                    args[long_names[option_index]] = True
                else:
                    args[long_names[option_index]] = argv[argument_idx + 1]
                    skip_next = True
            # Help Check
            elif option in ["h", "help"]:
                print(build_help_page())
                sys.exit(0)
            # If option doesnt exist, assume its meant to be a part of the prompt
            else:
                log_stdout(
                    f"unrecognized option: '{argv[argument_idx]}', passing to prompt...",
                    "yellow",
                )
                prompt_list.append(argv[argument_idx])
        # If argument does not starts with '-', add to prompt
        else:
            prompt_list.append(argv[argument_idx])
    if len(prompt_list) == 0:
        log_stdout(
            f"no prompt provided, try '{PROGRAM_NAME} --help'",
            "bold yellow",
        )
        sys.exit(1)

    args["prompt"] = " ".join(prompt_list)

    return args
