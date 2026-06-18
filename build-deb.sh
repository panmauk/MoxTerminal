#!/usr/bin/env bash
# Build a moxterminal .deb from the project root.
# Usage (on a Debian/PMX OS machine):
#   sudo apt-get install -y devscripts debhelper
#   bash build-deb.sh
set -euo pipefail

command -v dpkg-buildpackage >/dev/null 2>&1 || {
    echo "dpkg-buildpackage not found. Install: sudo apt-get install devscripts debhelper"
    exit 1
}

dpkg-buildpackage -us -uc -b
DEB=$(ls -1t ../moxterminal_*.deb 2>/dev/null | head -1)
if [[ -n "$DEB" ]]; then
    echo ""
    echo "Built: $DEB"
    echo "Install: sudo dpkg -i $DEB"
    echo "Or:      sudo apt-get install $DEB"
fi
