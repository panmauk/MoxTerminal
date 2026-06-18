"""Color themes for MoxTerminal.

Two themes mirror the PMX OS desktop modes:

* ``deep-cyan``  — the modern default. Dark translucent navy, cyan accents,
  a pink/magenta cursor (the signature PANMOX dot).
* ``phosphor``   — the retro "Phosphor Node" mode. Near-black green CRT look.

Colors are kept as hex strings here and converted to ``Gdk.RGBA`` at the
point of use (see ``util.rgba``), so this module stays free of GTK imports
and is trivial to test.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class Theme:
    """A complete look: terminal palette plus UI chrome accents."""

    name: str
    label: str

    # --- terminal surface ---
    foreground: str
    background: str            # base RGB; the alpha comes from config opacity
    cursor: str
    cursor_foreground: str
    highlight: str             # selection background
    highlight_foreground: str
    bold: str
    palette: List[str]         # 16 ANSI colors (0-7 normal, 8-15 bright)

    # --- window chrome / branding ---
    accent: str                # primary accent (cyan or green)
    accent_dim: str            # muted accent for borders/labels
    pink: str                  # signature PANMOX magenta dot
    chrome: str                # base RGB for header bar / tab strip


DEEP_CYAN = Theme(
    name="deep-cyan",
    label="Deep Cyan",
    foreground="#d6f3ff",
    background="#071019",
    cursor="#ff3d8a",
    cursor_foreground="#06121b",
    highlight="#16455c",
    highlight_foreground="#eafaff",
    bold="#ffffff",
    palette=[
        "#0a1620", "#ff5c7a", "#3ee6a6", "#ffcf5c",
        "#36b5ff", "#ff5cc8", "#2fe6e0", "#cfe9f5",
        "#2a3a4a", "#ff7d95", "#6bf0bf", "#ffe08a",
        "#7fceff", "#ff8fd8", "#7ff5f0", "#ffffff",
    ],
    accent="#2fe6e0",
    accent_dim="#1c8f96",
    pink="#ff3d8a",
    chrome="#0a1722",
)

PHOSPHOR = Theme(
    name="phosphor",
    label="Phosphor",
    foreground="#33e673",
    background="#02140b",
    cursor="#7dffae",
    cursor_foreground="#02140b",
    highlight="#0f4a2c",
    highlight_foreground="#dffff0",
    bold="#7af0a0",
    palette=[
        "#031a0e", "#e0593f", "#33e673", "#a9e05a",
        "#2faf63", "#46d69b", "#5ef0b0", "#bdf7d2",
        "#0d3a22", "#ff7d5f", "#6bf2a0", "#c9f08a",
        "#6bd69a", "#7af0c2", "#9bf5d0", "#e8fff0",
    ],
    accent="#33e673",
    accent_dim="#1c8f55",
    pink="#ff5cc8",
    chrome="#04170d",
)

THEMES: Dict[str, Theme] = {
    DEEP_CYAN.name: DEEP_CYAN,
    PHOSPHOR.name: PHOSPHOR,
}

DEFAULT_THEME = DEEP_CYAN.name


def get(name: str) -> Theme:
    """Return the named theme, falling back to the default."""
    return THEMES.get(name, THEMES[DEFAULT_THEME])


def next_theme(name: str) -> str:
    """Return the name of the theme after ``name`` (cycles)."""
    names = list(THEMES.keys())
    try:
        idx = names.index(name)
    except ValueError:
        return DEFAULT_THEME
    return names[(idx + 1) % len(names)]
