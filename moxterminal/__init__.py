"""MoxTerminal — the PANMOX terminal for PMX OS.

A transparent, blue, blurry terminal emulator built on GTK 3 + VTE.
Designed to feel unmistakably PANMOX from the moment it opens.

All ``gi.require_version`` calls live here so they run before any
submodule imports ``gi.repository`` namespaces (importing this package
always triggers ``__init__`` first).
"""

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Vte", "2.91")
gi.require_version("Pango", "1.0")

# GdkX11 is only present under an X11 backend; it is required for the
# KDE "blur behind window" hint. Wayland / non-X11 sessions degrade
# gracefully (no blur), so a missing namespace must never be fatal.
try:
    gi.require_version("GdkX11", "3.0")
    HAS_GDK_X11 = True
except (ValueError, ImportError):
    HAS_GDK_X11 = False

__app_id__ = "org.panmox.MoxTerminal"
__app_name__ = "MoxTerminal"
__version__ = "1.0.0"
