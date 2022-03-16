#!/bin/bash

cd "$(dirname "$0")" || exit

pyinstaller -w -n altserver UI.py
cp -R ./resources ./dist/altserver
cp -R ./dist/altserver ./AltServer/usr/lib
dpkg -b AltServer AltServer.deb