"""The GTK application: owns config, global CSS, and window creation."""

from gi.repository import Gdk, Gio, Gtk

from . import __app_id__, themes
from .config import Config
from .style import build_css
from .window import MoxWindow


class MoxApplication(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id=__app_id__,
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
        )
        self._config = Config()
        self._provider = Gtk.CssProvider()

    # --- lifecycle -------------------------------------------------------
    def do_startup(self):
        Gtk.Application.do_startup(self)
        screen = Gdk.Screen.get_default()
        if screen is not None:
            Gtk.StyleContext.add_provider_for_screen(
                screen,
                self._provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )
        self.reload_style(themes.get(self._config.theme), self._config.opacity)

    def do_command_line(self, command_line):
        args = command_line.get_arguments()[1:]
        cwd = None
        argv = None
        i = 0
        while i < len(args):
            a = args[i]
            if a in ("-e", "-x", "--command"):
                rest = args[i + 1:]
                argv = rest if rest else None
                break
            if a in ("-w", "--working-directory") and i + 1 < len(args):
                cwd = args[i + 1]
                i += 2
                continue
            if a == "--theme" and i + 1 < len(args):
                name = args[i + 1]
                if name in themes.THEMES:
                    self._config.theme = name
                    self.reload_style(themes.get(name), self._config.opacity)
                i += 2
                continue
            i += 1

        self.new_window(cwd=cwd, argv=argv)
        return 0

    # --- windows ---------------------------------------------------------
    def new_window(self, cwd=None, argv=None):
        win = MoxWindow(self, self._config, cwd=cwd, argv=argv)
        win.show_all()
        win.present()
        return win

    # --- styling ---------------------------------------------------------
    def reload_style(self, theme: themes.Theme, opacity: float):
        css = build_css(theme, opacity)
        self._provider.load_from_data(css.encode("utf-8"))
