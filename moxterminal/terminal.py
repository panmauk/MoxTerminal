"""The terminal surface: a thin, themed wrapper around ``Vte.Terminal``."""

import os

from gi.repository import Gdk, Gio, GLib, Gtk, Pango, Vte

from . import themes
from .config import Config
from .util import rgba

# PCRE2 flag: ^/$ match at line boundaries (harmless, keeps URL matching sane).
_PCRE2_MULTILINE = 0x00000400

# Match http(s):// and bare www. links. Kept deliberately simple/robust.
_URL_REGEX = (
    r"(?:https?://|www\.)"
    r"[-\w.]+(?::\d+)?"
    r"(?:/[-\w()@:%+.~#?&/=]*)?"
)

_CURSOR_SHAPES = {
    "block": Vte.CursorShape.BLOCK,
    "ibeam": Vte.CursorShape.IBEAM,
    "underline": Vte.CursorShape.UNDERLINE,
}


def _user_shell() -> str:
    """Best-effort path to the user's login shell."""
    shell = os.environ.get("SHELL")
    if shell and os.path.exists(shell):
        return shell
    try:
        import pwd
        return pwd.getpwuid(os.getuid()).pw_shell or "/bin/bash"
    except Exception:
        return "/bin/bash"


class MoxTerminal(Vte.Terminal):
    """A single VTE terminal, styled to the active PANMOX theme."""

    def __init__(self, config: Config):
        super().__init__()
        self._config = config
        self._url_tag = -1
        self._zoom = 1.0

        self.set_scroll_on_output(False)
        self.set_scroll_on_keystroke(True)
        self.set_mouse_autohide(config.get_bool("behavior", "mouse_autohide"))
        self.set_allow_hyperlink(True)
        self.set_rewrap_on_resize(True)

        self.apply_config()
        self.apply_theme(themes.get(config.theme))
        self._install_url_matching()

        self.connect("button-press-event", self._on_button_press)

    # --- configuration ---------------------------------------------------
    def apply_config(self) -> None:
        cfg = self._config
        font = Pango.FontDescription.from_string(cfg.get("appearance", "font"))
        self.set_font(font)

        scroll = cfg.get_int("behavior", "scrollback_lines")
        self.set_scrollback_lines(scroll if scroll >= 0 else -1)

        self.set_audible_bell(cfg.get_bool("behavior", "audible_bell"))

        shape = _CURSOR_SHAPES.get(
            cfg.get("appearance", "cursor_shape"), Vte.CursorShape.BLOCK
        )
        self.set_cursor_shape(shape)
        blink = (
            Vte.CursorBlinkMode.ON
            if cfg.get_bool("appearance", "cursor_blink")
            else Vte.CursorBlinkMode.OFF
        )
        self.set_cursor_blink_mode(blink)

    def apply_theme(self, theme: themes.Theme) -> None:
        """Recolor the terminal. Background alpha tracks config opacity."""
        opacity = self._config.opacity
        palette = [rgba(c) for c in theme.palette]
        self.set_colors(
            rgba(theme.foreground),
            rgba(theme.background, opacity),
            palette,
        )
        self.set_color_cursor(rgba(theme.cursor))
        self.set_color_cursor_foreground(rgba(theme.cursor_foreground))
        self.set_color_highlight(rgba(theme.highlight))
        self.set_color_highlight_foreground(rgba(theme.highlight_foreground))
        self.set_color_bold(rgba(theme.bold))

    # --- zoom ------------------------------------------------------------
    def zoom_in(self) -> None:
        self._set_zoom(self._zoom + 0.1)

    def zoom_out(self) -> None:
        self._set_zoom(self._zoom - 0.1)

    def zoom_reset(self) -> None:
        self._set_zoom(1.0)

    def _set_zoom(self, value: float) -> None:
        self._zoom = max(0.4, min(4.0, value))
        self.set_font_scale(self._zoom)

    # --- shell -----------------------------------------------------------
    def spawn(self, working_directory=None, argv=None) -> None:
        cfg = self._config
        if argv is None:
            shell = _user_shell()
            argv = [shell]
            if cfg.get_bool("behavior", "login_shell"):
                argv.append("--login")

        cwd = working_directory or os.environ.get("HOME") or os.getcwd()

        env = dict(os.environ)
        env.setdefault("TERM", "xterm-256color")
        env["COLORTERM"] = "truecolor"
        envv = [f"{k}={v}" for k, v in env.items()]

        self.spawn_async(
            Vte.PtyFlags.DEFAULT,
            cwd,
            argv,
            envv,
            GLib.SpawnFlags.SEARCH_PATH,
            None,            # child_setup
            None,            # child_setup_data
            -1,              # timeout (no limit)
            None,            # cancellable
            self._on_spawned,
            None,            # user_data
        )

    def _on_spawned(self, terminal, pid, error, *_user_data) -> None:
        if error is not None:
            self.feed(
                ("\r\n\x1b[1;31mMoxTerminal: failed to start shell: "
                 f"{error.message}\x1b[0m\r\n").encode()
            )

    # --- helpers ---------------------------------------------------------
    def current_directory(self):
        uri = self.get_current_directory_uri()
        if not uri:
            return None
        path = GLib.filename_from_uri(uri)[0] if uri.startswith("file://") else None
        return path

    def title(self) -> str:
        return self.get_window_title() or ""

    # --- URL handling ----------------------------------------------------
    def _install_url_matching(self) -> None:
        try:
            regex = Vte.Regex.new_for_match(
                _URL_REGEX, len(_URL_REGEX.encode()), _PCRE2_MULTILINE
            )
            self._url_tag = self.match_add_regex(regex, 0)
            self.match_set_cursor_name(self._url_tag, "pointer")
        except Exception:
            self._url_tag = -1

    def _on_button_press(self, _widget, event) -> bool:
        # Ctrl+left-click opens a matched URL; otherwise let VTE handle it.
        if event.button != Gdk.BUTTON_PRIMARY:
            return False
        if not (event.state & Gdk.ModifierType.CONTROL_MASK):
            return False
        if self._url_tag < 0:
            return False
        match = self.match_check_event(event)
        uri = match[0] if match else None
        if not uri:
            return False
        if uri.startswith("www."):
            uri = "http://" + uri
        try:
            Gtk.show_uri_on_window(self.get_toplevel(), uri, Gdk.CURRENT_TIME)
        except Exception:
            Gio.AppInfo.launch_default_for_uri(uri, None)
        return True
