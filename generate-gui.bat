@echo off
setlocal enabledelayedexpansion

REM Generate Python files from Qt Designer UI files
echo Generating Python files from Qt Designer UI files...

REM Process all .ui files in qtdesigner directory
for %%f in (qtdesigner\*.ui) do (
    echo Processing %%f...
    for %%n in ("%%f") do (
        set "filename=%%~nn"
        pyside6-uic "%%f" -o "src\gen\!filename!.py"
    )
)

REM Compile translation files from .ts to .qm
echo Compiling translation files...
for %%f in (translation_files\*.ts) do (
    if exist "%%f" (
        echo Compiling %%f...
        for %%n in ("%%f") do (
            set "filename=%%~nn"
            pyside6-lrelease "%%f" -qm "src\gen\translation_files\!filename!.qm"
        )
    )
)

echo GUI generation and translation compilation completed!
pause
