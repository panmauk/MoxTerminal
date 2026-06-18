# MoxTerminal

**The PANMOX terminal for PMX OS.**  
Transparent. Blue. Blurry. No cloud. No telemetry. No boss.

## Requirements

| Package | Debian name |
|---|---|
| Python 3.8+ | `python3` |
| PyGObject | `python3-gi` |
| GTK 3 bindings | `gir1.2-gtk-3.0` |
| VTE 2.91 | `gir1.2-vte-2.91` |
| JetBrains Mono *(recommended)* | `fonts-jetbrains-mono` |

Blur-behind requires **KDE KWin** on an X11 session. On other compositors transparency still works; the blur hint is silently ignored.

## Install on PMX OS / Debian

### Option A — install script (simplest)
```sh
git clone https://panmox.org/git/moxterminal
cd moxterminal
sudo bash install.sh
```

### Option B — build a .deb
```sh
sudo apt-get install devscripts debhelper
bash build-deb.sh
sudo dpkg -i ../moxterminal_1.0.0_all.deb
```

### Option C — Makefile
```sh
sudo apt-get install python3 python3-gi gir1.2-gtk-3.0 gir1.2-vte-2.91
sudo make install
```

### Uninstall
```sh
sudo bash install.sh uninstall
# or
sudo make uninstall
```

## Usage

```
moxterminal                       # open a window
moxterminal --theme phosphor      # start in retro phosphor-green mode
moxterminal -w ~/projects         # open in a specific directory
moxterminal -e htop               # run a command instead of the shell
```

## Keyboard shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+Shift+T` | New tab |
| `Ctrl+Shift+W` | Close tab |
| `Ctrl+Shift+N` | New window |
| `Ctrl+Shift+C` | Copy |
| `Ctrl+Shift+V` | Paste |
| `Ctrl+Shift+P` | Switch theme (deep-cyan ↔ phosphor) |
| `Ctrl++` / `Ctrl+-` | Zoom in / out |
| `Ctrl+0` | Reset zoom |
| `Ctrl+PgDn` / `Ctrl+PgUp` | Next / previous tab |
| `Ctrl+Left-click` | Open URL under cursor |

## Configuration

Edit `~/.config/moxterminal/config.ini` (created on first run):

```ini
[appearance]
theme   = deep-cyan     # deep-cyan | phosphor
opacity = 0.82          # 0.30 – 1.0
blur    = true          # KDE blur-behind (X11/KWin only)
font    = JetBrains Mono 11
cursor_shape = block    # block | ibeam | underline
cursor_blink = true

[behavior]
scrollback_lines = 10000   # -1 = unlimited
audible_bell     = false
mouse_autohide   = true
login_shell      = false
```

Changes apply to newly opened windows. **Reload Config** from the menu applies most settings without restarting.

## Themes

| Name | Look |
|---|---|
| `deep-cyan` | Deep navy, cyan accent, pink cursor dot — the PMX OS default |
| `phosphor` | Near-black, retro phosphor-green — the Phosphor Node mode |

Toggle live with `Ctrl+Shift+P` or `moxterminal --theme phosphor`.

---

*Part of the PANMOX ecosystem — [panmox.org/pmxos](https://panmox.org/pmxos)*
