#!/usr/bin/env bash
# MoxTerminal — one-shot install script for PMX OS / Debian.
# Usage:  sudo bash install.sh
#         sudo bash install.sh uninstall
set -euo pipefail

RED='\033[0;31m'; CYAN='\033[0;36m'; PINK='\033[0;35m'
BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'

PREFIX=/usr
PKGDIR="$PREFIX/share/moxterminal"
BINDIR="$PREFIX/bin"
APPDIR="$PREFIX/share/applications"
ICONDIR="$PREFIX/share/icons/hicolor/scalable/apps"
APPID="org.panmox.MoxTerminal"

require_root() {
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}Please run with sudo.${NC}"
        exit 1
    fi
}

banner() {
    echo -e ""
    echo -e "${CYAN}${BOLD}  // MOXTERMINAL${NC} ${PINK}●${NC}"
    echo -e "${DIM}  The PANMOX terminal for PMX OS${NC}"
    echo -e ""
}

install_deps() {
    echo -e "${CYAN}→ Installing system dependencies…${NC}"
    apt-get install -y --no-install-recommends \
        python3 \
        python3-gi \
        gir1.2-gtk-3.0 \
        gir1.2-vte-2.91 \
        fonts-jetbrains-mono 2>/dev/null \
        || apt-get install -y --no-install-recommends \
               python3 python3-gi gir1.2-gtk-3.0 gir1.2-vte-2.91
}

do_install() {
    require_root
    banner
    install_deps

    echo -e "${CYAN}→ Installing MoxTerminal files…${NC}"
    install -d "$PKGDIR/moxterminal"
    install -m644 moxterminal/*.py "$PKGDIR/moxterminal/"

    install -d "$APPDIR" "$ICONDIR" "$BINDIR"
    install -m644 "data/$APPID.desktop" "$APPDIR/"
    install -m644 "data/icons/$APPID.svg" "$ICONDIR/"

    cat > "$BINDIR/moxterminal" << 'LAUNCHER'
#!/usr/bin/env python3
import sys
sys.path.insert(0, '/usr/share/moxterminal')
from moxterminal.__main__ import main
sys.exit(main())
LAUNCHER
    chmod 755 "$BINDIR/moxterminal"

    update-desktop-database -q "$PREFIX/share/applications" 2>/dev/null || true
    gtk-update-icon-cache -q -t -f "$PREFIX/share/icons/hicolor" 2>/dev/null || true

    echo -e ""
    echo -e "${CYAN}${BOLD}  MoxTerminal installed.${NC}  Run: ${PINK}moxterminal${NC}"
    echo -e ""
}

do_uninstall() {
    require_root
    echo -e "${CYAN}→ Removing MoxTerminal…${NC}"
    rm -rf "$PKGDIR"
    rm -f  "$BINDIR/moxterminal"
    rm -f  "$APPDIR/$APPID.desktop"
    rm -f  "$ICONDIR/$APPID.svg"
    update-desktop-database -q "$PREFIX/share/applications" 2>/dev/null || true
    gtk-update-icon-cache -q -t -f "$PREFIX/share/icons/hicolor" 2>/dev/null || true
    echo -e "${CYAN}  Done.${NC}"
}

case "${1:-install}" in
    install)   do_install ;;
    uninstall) do_uninstall ;;
    *)
        echo "Usage: sudo bash install.sh [install|uninstall]"
        exit 1
        ;;
esac
