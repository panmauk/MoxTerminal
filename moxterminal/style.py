"""Dynamic GTK CSS for MoxTerminal.

The chrome (header bar, tab strip, scrollbars, menus) is recolored from the
active theme and made translucent to match the terminal's opacity, so the
whole window reads as one cohesive, blurry PANMOX surface.
"""

from . import themes


def _rgb(hex_color: str) -> str:
    """'#rrggbb' -> 'r, g, b' for use inside CSS rgba()."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"{r}, {g}, {b}"


def build_css(theme: themes.Theme, opacity: float) -> str:
    """Return the full stylesheet for the given theme + opacity."""
    fg = _rgb(theme.foreground)
    accent = _rgb(theme.accent)
    accent_dim = _rgb(theme.accent_dim)
    pink = _rgb(theme.pink)
    chrome = _rgb(theme.chrome)

    # Chrome sits a touch more opaque than the terminal body so text/controls
    # stay legible, but still clearly translucent.
    chrome_a = round(min(0.96, opacity * 0.85 + 0.10), 3)

    return f"""
/* ---- window ---------------------------------------------------------- */
window.moxterminal {{
    background-color: transparent;
}}

/* ---- header bar / title bar ----------------------------------------- */
.moxterminal headerbar,
.moxterminal .titlebar {{
    min-height: 34px;
    padding: 0 6px;
    color: rgba({fg}, 0.92);
    border-bottom: 1px solid rgba({accent}, 0.30);
    background-image: linear-gradient(
        to bottom,
        rgba({chrome}, {chrome_a}),
        rgba({chrome}, {min(0.96, chrome_a + 0.04)})
    );
    box-shadow: inset 0 1px 0 rgba({accent}, 0.10);
}}

.moxterminal headerbar button,
.moxterminal .titlebar button {{
    background: none;
    border: none;
    box-shadow: none;
    padding: 2px 8px;
    margin: 4px 1px;
    border-radius: 7px;
    color: rgba({fg}, 0.78);
}}
.moxterminal headerbar button:hover {{
    background-color: rgba({accent}, 0.16);
    color: rgba({accent}, 1.0);
}}
.moxterminal headerbar button:active,
.moxterminal headerbar button:checked {{
    background-color: rgba({accent}, 0.24);
    color: rgba({accent}, 1.0);
}}

/* ---- branding (centered title) -------------------------------------- */
.brand-tag {{
    font-family: monospace;
    font-size: 10px;
    letter-spacing: 2px;
    font-weight: 700;
    color: rgba({accent}, 0.88);
}}
.brand-dot {{
    font-size: 13px;
    color: rgb({pink});
    text-shadow: 0 0 6px rgba({pink}, 0.8);
    margin-left: 5px;
}}

/* ---- tabs ------------------------------------------------------------ */
.moxterminal notebook > header {{
    background-color: rgba({chrome}, {chrome_a});
    border: none;
    box-shadow: inset 0 -1px 0 rgba({accent}, 0.18);
}}
.moxterminal notebook > header > tabs {{
    margin: 0;
}}
.moxterminal notebook tab {{
    border: none;
    background: transparent;
    padding: 3px 4px 3px 12px;
    min-height: 26px;
    color: rgba({fg}, 0.55);
}}
.moxterminal notebook tab:hover {{
    color: rgba({fg}, 0.85);
}}
.moxterminal notebook tab:checked {{
    color: rgba({accent}, 1.0);
    box-shadow: inset 0 -2px 0 rgb({accent});
    background-image: linear-gradient(
        to top, rgba({accent}, 0.10), transparent
    );
}}
.moxterminal notebook tab label {{
    font-size: 12px;
}}
.moxterminal notebook tab button {{
    padding: 0;
    margin-left: 6px;
    min-width: 18px;
    min-height: 18px;
    border-radius: 5px;
    color: rgba({fg}, 0.45);
    background: none;
}}
.moxterminal notebook tab button:hover {{
    background-color: rgba({pink}, 0.30);
    color: #ffffff;
}}

/* ---- scrollbar ------------------------------------------------------- */
.moxterminal scrollbar {{
    background: transparent;
    border: none;
}}
.moxterminal scrollbar slider {{
    min-width: 6px;
    border-radius: 6px;
    background-color: rgba({accent}, 0.30);
}}
.moxterminal scrollbar slider:hover {{
    background-color: rgba({accent}, 0.55);
}}

/* ---- menus / popovers ------------------------------------------------ */
.mox-menu {{
    background-color: rgba({chrome}, 0.97);
    border: 1px solid rgba({accent}, 0.30);
    border-radius: 10px;
    padding: 4px;
    color: rgba({fg}, 0.92);
}}
.mox-menu menuitem {{
    padding: 5px 12px;
    border-radius: 6px;
}}
.mox-menu menuitem:hover {{
    background-color: rgba({accent}, 0.18);
    color: rgba({accent}, 1.0);
}}
.mox-menu separator {{
    background-color: rgba({accent_dim}, 0.30);
    margin: 4px 6px;
}}
"""
