#!/bin/bash

# Package variables
PACKAGE_NAME="altserver-linuxgui"

# Path variables
SCRIPT_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
REPO_ROOT_DIR="$SCRIPT_DIR/../.."
SOURCE_DIR="$REPO_ROOT_DIR/src"
TEMP_DIR=$(mktemp -d)
PACKAGE_DEB_DIR="$SCRIPT_DIR/deb"
DEB_ROOT_DIR="$TEMP_DIR/$PACKAGE_NAME"
DEB_USR_LIB_DIR="$DEB_ROOT_DIR/usr/lib"
BUILD_ROOT_DIR="$TEMP_DIR/build"
DIST_ROOT_DIR="$TEMP_DIR/dist"
PROGRAM_MAIN="$SOURCE_DIR/main.py"
PROGRAM_RESOURCES_DIR="$SOURCE_DIR/resources"
OUTPUT_DEB_PATH="$REPO_ROOT_DIR/$PACKAGE_NAME.deb"

# Create directories
mkdir -p "$DEB_ROOT_DIR"
mkdir -p "$DEB_USR_LIB_DIR"
mkdir -p "$BUILD_ROOT_DIR"
mkdir -p "$DIST_ROOT_DIR"

# Generate a distributable copy of the program
pyinstaller --distpath "$DIST_ROOT_DIR" --workpath "$BUILD_ROOT_DIR" --name "$PACKAGE_NAME" "$PROGRAM_MAIN"

# Copy packaging files into deb root
cp -R "$PACKAGE_DEB_DIR/"* "$DEB_ROOT_DIR"

# Copy program into deb root
cp -R "$DIST_ROOT_DIR/$PACKAGE_NAME/"* "$DEB_USR_LIB_DIR"

# Copy program resources into deb root
cp -R "$PROGRAM_RESOURCES_DIR" "$DEB_USR_LIB_DIR"

# Build deb package
dpkg-deb --build --root-owner-group AltServer "$OUTPUT_DEB_PATH"