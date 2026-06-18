"""Small GTK/Gdk helpers shared across MoxTerminal."""

from gi.repository import Gdk

from . import HAS_GDK_X11

if HAS_GDK_X11:
    from gi.repository import GdkX11  # noqa: F401  (registers the type)


def rgba(hex_color: str, alpha: float = 1.0) -> Gdk.RGBA:
    """Build a ``Gdk.RGBA`` from ``#rrggbb`` (or ``#rgb``) and an alpha."""
    c = Gdk.RGBA()
    c.parse(hex_color)
    c.alpha = max(0.0, min(1.0, alpha))
    return c


# KDE / KWin "blur the region behind this window" hint. Setting the property
# with an empty value means "blur the entire window".
_BLUR_ATOM = "_KDE_NET_WM_BLUR_BEHIND_REGION"


def _is_x11(gdk_window) -> bool:
    if not HAS_GDK_X11:
        return False
    try:
        return isinstance(gdk_window, GdkX11.X11Window)
    except Exception:
        return False


def set_kde_blur(gdk_window, enabled: bool) -> bool:
    """Enable/disable KDE blur-behind for a realized ``Gdk.Window``.

    Returns ``True`` if the hint was applied. No-ops (returning ``False``)
    on Wayland, non-KDE compositors, or when GdkX11 is unavailable — blur is
    a nice-to-have, never a hard requirement.
    """
    if gdk_window is None or not _is_x11(gdk_window):
        return False

    prop = Gdk.Atom.intern(_BLUR_ATOM, False)
    cardinal = Gdk.Atom.intern("CARDINAL", False)
    try:
        if enabled:
            # Empty CARDINAL array -> blur whole window.
            Gdk.property_change(
                gdk_window, prop, cardinal, 32,
                Gdk.PropMode.REPLACE, b"", 0,
            )
        else:
            Gdk.property_delete(gdk_window, prop)
        return True
    except Exception:
        return False
