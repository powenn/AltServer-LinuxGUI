#!/bin/bash

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root."
    exit
fi

SCRIPT_DIR=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)

cat <<EOF | tee AltServer.desktop >/dev/null
[Desktop Entry]
Name=AltServer
GenericName=AltServer for AltStore
Exec="$SCRIPT_DIR/AltServerGUI"
Terminal=false
Type=Application
X-GNOME-Autostart-enabled=true
EOF

sudo cp AltServer.desktop /home/*/.config/autostart/
sudo rm AltServer.desktop
