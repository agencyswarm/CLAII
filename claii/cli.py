# claii/cli.py
import sys
from .agent import run_agent


CLAII_LOGO = r"""
   ██████╗ ██╗      █████╗ ██╗██╗
  ██╔════╝ ██║     ██╔══██╗██║██║
  ██║      ██║     ███████║██║██║
  ██║      ██║     ██╔══██║██║██║
  ╚██████╗ ███████╗██║  ██║██║██║
   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝╚═╝   (CLAII)
"""


def main() -> None:
    # ASCII banner
    print(CLAII_LOGO)

    # Strip off the program name
    argv = sys.argv[1:]

    if not argv:
        print('Usage: claii "<prompt>" [--verbose]')
        sys.exit(1)

    # Delegate to the core agent logic
    run_agent(argv, banner_shown=True)
