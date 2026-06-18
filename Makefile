PREFIX  ?= /usr
DESTDIR ?=
APPID    = org.panmox.MoxTerminal

PKGDIR  = $(DESTDIR)$(PREFIX)/share/moxterminal
BINDIR  = $(DESTDIR)$(PREFIX)/bin
APPDIR  = $(DESTDIR)$(PREFIX)/share/applications
ICONDIR = $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps

.PHONY: all install uninstall run check clean

all:
	@echo "Targets: install, uninstall, run, check"

install:
	install -d "$(PKGDIR)/moxterminal"
	install -m644 moxterminal/*.py "$(PKGDIR)/moxterminal/"
	install -d "$(APPDIR)" "$(ICONDIR)" "$(BINDIR)"
	install -m644 data/$(APPID).desktop "$(APPDIR)/"
	install -m644 data/icons/$(APPID).svg "$(ICONDIR)/"
	printf '#!/usr/bin/env python3\nimport sys\nsys.path.insert(0, "$(PREFIX)/share/moxterminal")\nfrom moxterminal.__main__ import main\nsys.exit(main())\n' > "$(BINDIR)/moxterminal"
	chmod 755 "$(BINDIR)/moxterminal"
ifeq ($(strip $(DESTDIR)),)
	-update-desktop-database -q $(PREFIX)/share/applications 2>/dev/null || true
	-gtk-update-icon-cache -q -t -f $(PREFIX)/share/icons/hicolor 2>/dev/null || true
endif
	@echo "MoxTerminal installed. Run: moxterminal"

uninstall:
	rm -rf "$(PKGDIR)"
	rm -f "$(BINDIR)/moxterminal"
	rm -f "$(APPDIR)/$(APPID).desktop"
	rm -f "$(ICONDIR)/$(APPID).svg"
	@echo "MoxTerminal removed."

run:
	python3 -m moxterminal

check:
	python3 -m py_compile moxterminal/*.py

clean:
	rm -rf moxterminal/__pycache__ build *.egg-info
