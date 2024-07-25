#!/bin/bash
echo "Clearing previous builds..."
rm -r build
rm -r dist

echo "Creating app..."
pyinstaller --log-level=WARN Family\ Rules.spec

#echo "Creating dmg..."
#mkdir -p dist/dmg
#cp -r "dist/Family Rules.app" dist/dmg
#test -f "dist/Family Rules.dmg" && rm "dist/Family Rules.dmg"
#create-dmg \
#  --volname "Family Rules" \
#  --volicon "src/resources/foaf.icns" \
#  --window-pos 200 120 \
#  --window-size 600 300 \
#  --icon-size 100 \
#  --icon "Family Rules.app" 175 120 \
#  --hide-extension "Family Rules.app" \
#  --app-drop-link 425 120 \
#  "dist/Family Rules.dmg" \
#  "dist/dmg/"