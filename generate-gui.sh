#!/bin/bash
pyside6-uic qtdesigner/MainWindow.ui -o src/gen/MainWindow.py
pyside6-uic qtdesigner/InitialSetup.ui -o src/gen/InitialSetup.py