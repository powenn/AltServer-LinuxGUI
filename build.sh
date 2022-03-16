#!/bin/bash

cd "$(dirname "$0")" || exit

pyinstaller -w -n altserver UI.py
cp -R ./resources ./dist/altserver
if [ ! -d "./AltServer/usr/lib" ]; then
    mkdir "./AltServer/usr/lib"
fi

cp -R ./dist/altserver ./AltServer/usr/lib
dpkg -b AltServer AltServer.deb