#!/bin/bash

cd "$(dirname "$0")" || exit

if [ ! -f "./resources/AltServer" ]; then
   echo 'AltServer not exist'
   exit   
fi
if [ ! -f "./resources/AltStore.ipa" ]; then
    echo 'AltStore.ipa not exist'
    exit    
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
