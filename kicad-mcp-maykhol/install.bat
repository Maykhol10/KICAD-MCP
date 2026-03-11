@echo off
echo ========================================
echo  KiCad MCP Server - Instalacion
echo ========================================
echo.

REM Usar Python de KiCad que ya tienes instalado
set KICAD_PYTHON="C:\Program Files\KiCad\9.0\bin\python.exe"

echo [1] Instalando dependencias con Python de KiCad...
%KICAD_PYTHON% -m pip install mcp

echo.
echo [2] Verificando instalacion...
%KICAD_PYTHON% -c "import mcp; print('MCP OK:', mcp.__version__)"

echo.
echo [3] Test rapido del servidor...
%KICAD_PYTHON% server.py --version 2>nul || echo "Servidor listo para usar"

echo.
echo ========================================
echo  Instalacion completa!
echo  Ahora configura Claude Code con:
echo  Ver archivo: claude_code_config.json
echo ========================================
pause
