@echo off
echo ========================================
echo  KiCad MCP Server - Setup completo
echo ========================================
echo.
echo [1/3] Instalando dependencias con Python de KiCad...
"C:\Program Files\KiCad\9.0\bin\python.exe" -m pip install mcp --quiet
echo      OK

echo.
echo [2/3] Verificando MCP...
"C:\Program Files\KiCad\9.0\bin\python.exe" -c "import mcp; print('     MCP version:', mcp.__version__)"

echo.
echo [3/3] Verificando kicad-cli...
"C:\Program Files\KiCad\9.0\bin\kicad-cli.exe" --version 2>nul && echo "     kicad-cli OK" || echo "     ERROR: kicad-cli no encontrado"

echo.
echo ========================================
echo  Listo! Agrega esto a:
echo  %%APPDATA%%\Claude\claude_desktop_config.json
echo.
echo  {
echo    "mcpServers": {
echo      "kicad-maykhol": {
echo        "command": "C:\\Program Files\\KiCad\\9.0\\bin\\python.exe",
echo        "args": ["%~dp0server.py"]
echo      }
echo    }
echo  }
echo ========================================
pause
