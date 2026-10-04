import argparse
import sys

from ui.terminal_ui import main_menu, run_session


def parse_args():
    parser = argparse.ArgumentParser(description="Local AI phone-routing assistant")
    parser.add_argument(
        "--voice",
        action="store_true",
        help="start a live microphone call immediately instead of opening the demo menu",
    )
    return parser.parse_args()

if __name__ == "__main__":
    try:
        args = parse_args()
        if args.voice:
            run_session(use_config=True)
        else:
            main_menu()
    except KeyboardInterrupt:
        print("\nExiting Phone Assistant PoC. Goodbye.")
        sys.exit(0)
