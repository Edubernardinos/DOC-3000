@echo off
chcp 65001 >nul
title Instalador DOC_EDITOR_3000

cd /d "%~dp0"
echo ========================================================
echo         INSTALADOR OFICIAL DO DOC_EDITOR_3000
echo ========================================================
echo.

powershell -ExecutionPolicy Bypass -NoProfile -File "%~dp0criar_atalhos.ps1"

echo.
echo ========================================================
echo  [CONCLUÍDO] O aplicativo DOC_EDITOR_3000 foi instalado!
echo  Você pode abri-lo pelo atalho na sua Área de Trabalho.
echo ========================================================
echo.
pause
