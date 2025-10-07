#!/bin/bash
echo "Clearing previous builds..."
rm -r build
rm -r dist

echo "Creating app..."
pyinstaller --log-level=WARN app-macos.spec

echo "Ad hoc code signing the app..."
codesign --force --deep --sign - dist/FamilyRules.app

echo "Verifying signature..."
codesign --verify --verbose dist/FamilyRules.app