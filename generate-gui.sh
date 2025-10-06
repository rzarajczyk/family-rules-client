#!/bin/bash

# Generate Python files from Qt Designer UI files
echo "Generating Python files from Qt Designer UI files..."
for FILE in qtdesigner/*.ui; do
  echo "Processing $FILE..."
  FILENAME=$(basename "$FILE" .ui)
  pyside6-uic "$FILE" -o "src/gen/$FILENAME.py"
done

# Compile translation files from .ts to .qm
echo "Compiling translation files..."
for FILE in translation_files/*.ts; do
  if [ -f "$FILE" ]; then
    echo "Compiling $FILE..."
    FILENAME=$(basename "$FILE" .ts)
    pyside6-lrelease "$FILE" -qm "src/gen/translation_files/${FILENAME}.qm"
  fi
done

echo "GUI generation and translation compilation completed!"