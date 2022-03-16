#!/bin/bash

cd "$(dirname "$0")" || exit

cat <<EOF | tee AltServer.desktop >/dev/null
[Desktop Entry]
Name=AltServer
GenericName=AltServer for Linux
Path=/usr/lib/altserver
Exec="/usr/lib/altserver/altserver"
Terminal=false
Type=Application
X-GNOME-Autostart-enabled=true
EOF

cp AltServer.desktop /home/*/.config/autostart/
rm AltServer.desktop
