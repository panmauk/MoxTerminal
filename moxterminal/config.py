"""Configuration for MoxTerminal.

Settings live in an INI file at ``$XDG_CONFIG_HOME/moxterminal/config.ini``
(``~/.config/moxterminal/config.ini`` by default). On first run the file is
written with sensible defaults and inline comments so it is hand-editable.

The module deliberately avoids importing ``gi`` so it can be imported and
tested anywhere.
"""

import configparser
import os
from typing import Dict

from . import themes

_XDG = os.environ.get("XDG_CONFIG_HOME") or os.path.join(
    os.path.expanduser("~"), ".config"
)
CONFIG_DIR = os.path.join(_XDG, "moxterminal")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.ini")

DEFAULTS: Dict[str, Dict[str, str]] = {
    "appearance": {
        "theme": themes.DEFAULT_THEME,   # deep-cyan | phosphor
        "opacity": "0.82",                # terminal background alpha, 0.30-1.0
        "blur": "true",                   # KDE blur-behind (X11 / KWin only)
        "font": "JetBrains Mono 11",      # any installed monospace + size
        "cursor_shape": "block",          # block | ibeam | underline
        "cursor_blink": "true",
    },
    "behavior": {
        "scrollback_lines": "10000",      # -1 for unlimited
        "audible_bell": "false",
        "mouse_autohide": "true",
        "login_shell": "false",           # launch $SHELL as a login shell
    },
}

_HEADER = (
    "# MoxTerminal configuration — the PANMOX terminal for PMX OS.\n"
    "# Edit and save; changes apply to newly opened windows/tabs, and most\n"
    "# can be toggled live from the in-app menu. Delete this file to reset.\n"
)


class Config:
    """Thin wrapper over ``configparser`` with typed getters and defaults."""

    def __init__(self, path: str = CONFIG_PATH):
        self.path = path
        self._parser = configparser.ConfigParser()
        # Seed defaults so missing keys always resolve.
        self._parser.read_dict(DEFAULTS)
        if os.path.exists(path):
            try:
                self._parser.read(path, encoding="utf-8")
            except (configparser.Error, OSError):
                pass  # keep defaults on a corrupt file
        else:
            self.save()

    # --- typed accessors -------------------------------------------------
    def get(self, section: str, key: str) -> str:
        return self._parser.get(section, key, fallback=DEFAULTS[section][key])

    def get_float(self, section: str, key: str) -> float:
        try:
            return float(self.get(section, key))
        except (TypeError, ValueError):
            return float(DEFAULTS[section][key])

    def get_int(self, section: str, key: str) -> int:
        try:
            return int(self.get(section, key))
        except (TypeError, ValueError):
            return int(DEFAULTS[section][key])

    def get_bool(self, section: str, key: str) -> bool:
        val = self.get(section, key)
        return str(val).strip().lower() in ("1", "true", "yes", "on")

    def set(self, section: str, key: str, value) -> None:
        if not self._parser.has_section(section):
            self._parser.add_section(section)
        self._parser.set(section, key, str(value))

    # --- convenience -----------------------------------------------------
    @property
    def theme(self) -> str:
        return self.get("appearance", "theme")

    @theme.setter
    def theme(self, name: str) -> None:
        self.set("appearance", "theme", name)

    @property
    def opacity(self) -> float:
        # Clamp to a sane visible range so the terminal never vanishes.
        return max(0.30, min(1.0, self.get_float("appearance", "opacity")))

    @opacity.setter
    def opacity(self, value: float) -> None:
        self.set("appearance", "opacity", round(max(0.30, min(1.0, value)), 2))

    @property
    def blur(self) -> bool:
        return self.get_bool("appearance", "blur")

    @blur.setter
    def blur(self, value: bool) -> None:
        self.set("appearance", "blur", "true" if value else "false")

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as fh:
            fh.write(_HEADER + "\n")
            self._parser.write(fh)
