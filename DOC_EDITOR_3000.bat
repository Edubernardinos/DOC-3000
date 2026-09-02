@echo off
chcp 65001 >nul
title DOC_EDITOR_3000

cd /d "%~dp0"
echo ========================================================
echo               INICIANDO DOC_EDITOR_3000
echo ========================================================
echo.

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -W ignore doc_editor.py
) else (
    python -W ignore doc_editor.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Ocorreu um erro ao executar o DOC_EDITOR_3000.
    pause
)
