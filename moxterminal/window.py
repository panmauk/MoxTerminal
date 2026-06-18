"""The MoxTerminal window: header bar, tabs, transparency and KDE blur."""

from gi.repository import Gdk, Gio, GLib, Gtk

from . import __app_id__, __app_name__, __version__, themes
from .config import CONFIG_PATH, Config
from .terminal import MoxTerminal
from .util import set_kde_blur


class MoxWindow(Gtk.ApplicationWindow):
    """A single window holding one or more terminal tabs."""

    def __init__(self, app, config: Config, cwd=None, argv=None):
        super().__init__(application=app)
        self._config = config
        self._theme = themes.get(config.theme)
        self._terminals = {}   # page box -> MoxTerminal
        self._labels = {}      # page box -> Gtk.Label

        self.set_default_size(920, 580)
        self.set_icon_name(__app_id__)
        self.get_style_context().add_class("moxterminal")

        self._enable_transparency()

        self._build_headerbar()

        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.notebook.set_show_border(False)
        self.notebook.set_show_tabs(False)
        self.notebook.connect("switch-page", self._on_switch_page)
        self.add(self.notebook)

        self.connect("realize", self._on_realize)
        self.connect("screen-changed", lambda w, _s: self._enable_transparency())
        self.connect("key-press-event", self._on_key_press)

        self.new_tab(cwd=cwd, argv=argv)

    # --- transparency / blur --------------------------------------------
    def _enable_transparency(self) -> None:
        screen = self.get_screen()
        visual = screen.get_rgba_visual() if screen else None
        if visual is not None and screen.is_composited():
            self.set_visual(visual)
        self.set_app_paintable(True)

    def _on_realize(self, *_):
        set_kde_blur(self.get_window(), self._config.blur)

    # --- header bar ------------------------------------------------------
    def _build_headerbar(self) -> None:
        bar = Gtk.HeaderBar()
        bar.set_show_close_button(True)

        new_tab_btn = Gtk.Button.new_from_icon_name(
            "list-add-symbolic", Gtk.IconSize.MENU
        )
        new_tab_btn.set_tooltip_text("New tab  (Ctrl+Shift+T)")
        new_tab_btn.connect("clicked", lambda _b: self.new_tab())
        bar.pack_start(new_tab_btn)

        menu_btn = Gtk.MenuButton()
        menu_btn.set_image(
            Gtk.Image.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.MENU)
        )
        menu_btn.set_tooltip_text("Menu")
        menu_btn.set_popup(self._build_menu())
        bar.pack_end(menu_btn)

        # Centered PANMOX branding: "// MOXTERMINAL ●"
        title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        tag = Gtk.Label(label="// MOXTERMINAL")
        tag.get_style_context().add_class("brand-tag")
        dot = Gtk.Label(label="●")
        dot.get_style_context().add_class("brand-dot")
        title.pack_start(tag, False, False, 0)
        title.pack_start(dot, False, False, 0)
        bar.set_custom_title(title)

        self.set_titlebar(bar)

    def _build_menu(self) -> Gtk.Menu:
        menu = Gtk.Menu()
        menu.get_style_context().add_class("mox-menu")

        def item(label, accel, handler):
            mi = Gtk.MenuItem()
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=18)
            lbl = Gtk.Label(label=label, xalign=0)
            box.pack_start(lbl, True, True, 0)
            if accel:
                ak = Gtk.Label(label=accel)
                ak.get_style_context().add_class("dim-label")
                box.pack_end(ak, False, False, 0)
            mi.add(box)
            mi.connect("activate", handler)
            menu.append(mi)
            return mi

        def sep():
            menu.append(Gtk.SeparatorMenuItem())

        item("New Tab", "Ctrl+Shift+T", lambda _m: self.new_tab())
        item("New Window", "Ctrl+Shift+N",
             lambda _m: self.get_application().new_window())
        item("Close Tab", "Ctrl+Shift+W",
             lambda _m: self.close_tab(self._current_box()))
        sep()
        item("Copy", "Ctrl+Shift+C", lambda _m: self._copy())
        item("Paste", "Ctrl+Shift+V", lambda _m: self._paste())
        sep()
        item("Switch Theme", "Ctrl+Shift+P", lambda _m: self.toggle_theme())
        item("Toggle Blur", "", lambda _m: self.toggle_blur())
        item("More Transparent", "Ctrl+Shift+−",
             lambda _m: self.adjust_opacity(-0.06))
        item("Less Transparent", "Ctrl+Shift++",
             lambda _m: self.adjust_opacity(+0.06))
        sep()
        item("Reload Config", "", lambda _m: self.reload_config())
        item("Edit Preferences…", "", lambda _m: self._edit_config())
        item("About MoxTerminal", "", lambda _m: self._about())

        menu.show_all()
        return menu

    # --- tabs ------------------------------------------------------------
    def new_tab(self, cwd=None, argv=None) -> MoxTerminal:
        term = MoxTerminal(self._config)
        term.apply_theme(self._theme)
        term.connect("child-exited", self._on_child_exited)
        term.connect("window-title-changed", self._on_title_changed)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        box.pack_start(term, True, True, 0)
        scrollbar = Gtk.Scrollbar(
            orientation=Gtk.Orientation.VERTICAL, adjustment=term.get_vadjustment()
        )
        box.pack_start(scrollbar, False, False, 0)

        self._terminals[box] = term
        label_widget, label = self._make_tab_label(box)
        self._labels[box] = label

        page = self.notebook.append_page(box, label_widget)
        self.notebook.set_tab_reorderable(box, True)
        box.show_all()

        self.notebook.set_show_tabs(self.notebook.get_n_pages() > 1)
        self.notebook.set_current_page(page)

        term.spawn(working_directory=cwd or self._inherit_cwd())
        term.grab_focus()
        return term

    def _make_tab_label(self, box):
        wrap = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        label = Gtk.Label(label="Terminal")
        label.set_ellipsize(3)  # Pango.EllipsizeMode.END
        label.set_max_width_chars(22)
        close = Gtk.Button.new_from_icon_name(
            "window-close-symbolic", Gtk.IconSize.MENU
        )
        close.set_relief(Gtk.ReliefStyle.NONE)
        close.set_focus_on_click(False)
        close.connect("clicked", lambda _b: self.close_tab(box))
        wrap.pack_start(label, True, True, 0)
        wrap.pack_end(close, False, False, 0)
        wrap.show_all()
        return wrap, label

    def close_tab(self, box) -> None:
        if box is None:
            return
        page = self.notebook.page_num(box)
        if page < 0:
            return
        self.notebook.remove_page(page)
        self._terminals.pop(box, None)
        self._labels.pop(box, None)
        if self.notebook.get_n_pages() == 0:
            self.destroy()
        else:
            self.notebook.set_show_tabs(self.notebook.get_n_pages() > 1)

    def _current_box(self):
        idx = self.notebook.get_current_page()
        return self.notebook.get_nth_page(idx) if idx >= 0 else None

    def current_terminal(self):
        return self._terminals.get(self._current_box())

    def _inherit_cwd(self):
        term = self.current_terminal()
        return term.current_directory() if term else None

    # --- signal handlers -------------------------------------------------
    def _on_switch_page(self, _nb, box, _num):
        term = self._terminals.get(box)
        if term:
            GLib.idle_add(term.grab_focus)
            self._sync_window_title(term)

    def _on_child_exited(self, term, _status):
        for box, t in list(self._terminals.items()):
            if t is term:
                self.close_tab(box)
                break

    def _on_title_changed(self, term):
        for box, t in self._terminals.items():
            if t is term:
                label = self._labels.get(box)
                if label:
                    label.set_text(term.title() or "Terminal")
                if box is self._current_box():
                    self._sync_window_title(term)
                break

    def _sync_window_title(self, term):
        title = term.title()
        self.set_title(f"{title} — {__app_name__}" if title else __app_name__)

    # --- copy / paste ----------------------------------------------------
    def _copy(self):
        term = self.current_terminal()
        if term and term.get_has_selection():
            term.copy_clipboard_format(2)  # Vte.Format.TEXT

    def _paste(self):
        term = self.current_terminal()
        if term:
            term.paste_clipboard()

    # --- appearance actions ---------------------------------------------
    def toggle_theme(self):
        name = themes.next_theme(self._theme.name)
        self._theme = themes.get(name)
        self._config.theme = name
        self._config.save()
        for term in self._terminals.values():
            term.apply_theme(self._theme)
        self.get_application().reload_style(self._theme, self._config.opacity)

    def toggle_blur(self):
        self._config.blur = not self._config.blur
        self._config.save()
        set_kde_blur(self.get_window(), self._config.blur)

    def adjust_opacity(self, delta):
        self._config.opacity = self._config.opacity + delta
        self._config.save()
        for term in self._terminals.values():
            term.apply_theme(self._theme)
        self.get_application().reload_style(self._theme, self._config.opacity)

    def reload_config(self):
        self._config = Config()
        self._theme = themes.get(self._config.theme)
        for term in self._terminals.values():
            term._config = self._config
            term.apply_config()
            term.apply_theme(self._theme)
        set_kde_blur(self.get_window(), self._config.blur)
        self.get_application().reload_style(self._theme, self._config.opacity)

    def _edit_config(self):
        try:
            Gtk.show_uri_on_window(self, "file://" + CONFIG_PATH, Gdk.CURRENT_TIME)
        except Exception:
            Gio.AppInfo.launch_default_for_uri("file://" + CONFIG_PATH, None)

    def _about(self):
        dlg = Gtk.AboutDialog(transient_for=self, modal=True)
        dlg.set_program_name(__app_name__)
        dlg.set_version(__version__)
        dlg.set_comments(
            "The PANMOX terminal for PMX OS.\n"
            "Transparent. Blue. Blurry. No cloud. No telemetry. No boss."
        )
        dlg.set_website("https://panmox.org/pmxos")
        dlg.set_website_label("panmox.org/pmxos")
        dlg.set_logo_icon_name(__app_id__)
        dlg.connect("response", lambda d, _r: d.destroy())
        dlg.present()

    # --- keyboard --------------------------------------------------------
    def _on_key_press(self, _widget, event):
        mask = Gtk.accelerator_get_default_mod_mask()
        state = event.state & mask
        ctrl = bool(state & Gdk.ModifierType.CONTROL_MASK)
        shift = bool(state & Gdk.ModifierType.SHIFT_MASK)
        kv = Gdk.keyval_to_lower(event.keyval)
        term = self.current_terminal()

        if ctrl and shift:
            if kv == Gdk.KEY_t:
                self.new_tab(); return True
            if kv == Gdk.KEY_n:
                self.get_application().new_window(); return True
            if kv == Gdk.KEY_w:
                self.close_tab(self._current_box()); return True
            if kv == Gdk.KEY_c:
                self._copy(); return True
            if kv == Gdk.KEY_v:
                self._paste(); return True
            if kv == Gdk.KEY_p:
                self.toggle_theme(); return True

        if ctrl and not shift:
            if event.keyval in (Gdk.KEY_plus, Gdk.KEY_equal, Gdk.KEY_KP_Add):
                if term: term.zoom_in()
                return True
            if event.keyval in (Gdk.KEY_minus, Gdk.KEY_KP_Subtract):
                if term: term.zoom_out()
                return True
            if event.keyval in (Gdk.KEY_0, Gdk.KEY_KP_0):
                if term: term.zoom_reset()
                return True
            if event.keyval == Gdk.KEY_Page_Down:
                self.notebook.next_page(); return True
            if event.keyval == Gdk.KEY_Page_Up:
                self.notebook.prev_page(); return True

        return False
