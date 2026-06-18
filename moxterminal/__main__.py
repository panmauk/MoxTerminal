"""Entry point: ``python -m moxterminal`` (and the installed launcher)."""

import sys

from . import __app_name__, __version__

_USAGE = f"""\
{__app_name__} {__version__} — the PANMOX terminal for PMX OS.

Usage:
  moxterminal [OPTIONS]
  moxterminal -e COMMAND [ARGS...]

Options:
  -w, --working-directory DIR   Start the shell in DIR
  -e, -x, --command CMD ...     Run CMD instead of the login shell
      --theme NAME              Start in a theme: deep-cyan | phosphor
  -h, --help                    Show this help and exit
  -v, --version                 Show version and exit

Shortcuts:
  Ctrl+Shift+T  new tab        Ctrl+Shift+W  close tab
  Ctrl+Shift+N  new window     Ctrl+Shift+C/V  copy / paste
  Ctrl+Shift+P  switch theme   Ctrl +/-/0   zoom in / out / reset
"""


def main(argv=None):
    argv = list(sys.argv if argv is None else argv)
    if any(a in ("-h", "--help") for a in argv[1:]):
        print(_USAGE)
        return 0
    if any(a in ("-v", "--version") for a in argv[1:]):
        print(f"{__app_name__} {__version__}")
        return 0

    # Imported here so --help/--version work even without GTK present.
    from .app import MoxApplication
    return MoxApplication().run(argv)


if __name__ == "__main__":
    sys.exit(main())
