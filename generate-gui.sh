#!/bin/bash
for FILE in qtdesigner/*.ui; do
  echo "Processing $FILE..."
  FILENAME=$(basename "$FILE" .ui)
  pyside6-uic "$FILE" -o "src/gen/$FILENAME.py"
done