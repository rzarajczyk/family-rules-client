#!/bin/bash
echo "Clearing previous builds..."
rm -r build
rm -r dist

echo "Creating app..."
pyinstaller --log-level=WARN Family\ Rules.spec