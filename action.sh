#!/bin/bash

cd "$(dirname "$0")" || exit

ALTSERVER_VERSION="v0.0.4"
ALTSTORE_VERSION="1_4_9"

if [ ! -f "./resources/AltServer" ]; then
    curl -L "https://github.com/NyaMisty/AltServer-Linux/releases/download/$ALTSERVER_VERSION/AltServer-x86_64" > "./resources/AltServer"
fi
if [ ! -f "./resources/AltStore.ipa" ]; then
    curl -L "https://cdn.altstore.io/file/altstore/apps/altstore/$ALTSTORE_VERSION.ipa" > "./resources/AltStore.ipa"
fi
if [ -d "./AltServer/usr/lib" ]; then
    rm -rf "./AltServer/usr/lib"
fi
if [ -d "./dist" ]; then
    rm -rf "./dist"
fi

pyinstaller -w -n altserver UI.py
cp -R ./resources ./dist/altserver
if [ ! -d "./AltServer/usr/lib" ]; then
    mkdir "./AltServer/usr/lib"
fi

cp -R ./dist/altserver ./AltServer/usr/lib
dpkg-deb --build --root-owner-group AltServer AltServer.deb
