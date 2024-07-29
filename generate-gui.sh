#!/bin/bash
pyside6-uic qtdesigner/MainWindow.ui -o src/gen/MainWindow.py
pyside6-uic qtdesigner/InitialSetup.ui -o src/gen/InitialSetup.py
pyside6-uic qtdesigner/SettingsWindow.ui -o src/gen/SettingsWindow.py
pyside6-uic qtdesigner/ParentConfirm.ui -o src/gen/ParentConfirm.py