#!/bin/bash
echo "Clearing previous builds..."
rm -r build
rm -r dist

echo "Creating app..."
pyinstaller --log-level=WARN app-macos.spec
echo "Zipping..."
zip -q -r "Family Rules.zip" dist/*