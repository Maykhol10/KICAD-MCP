# KiCad MCP Server — Maykhol Edition
MCP liviano para Claude Code. Sin crashes de RAM. Usa kicad-cli de KiCad 9.0.

## Instalación

### 1. Copiar archivos
```
C:\Users\DELL\kicad-mcp\
  server.py
  install.bat
```

### 2. Instalar dependencias
Doble click en `install.bat`
O desde KiCad 9.0 Command Prompt:
```cmd
pip install mcp
```

### 3. Configurar Claude Code
Edita `%APPDATA%\Claude\claude_desktop_config.json` y agrega:
```json
{
  "mcpServers": {
    "kicad-maykhol": {
      "command": "C:\\Program Files\\KiCad\\9.0\\bin\\python.exe",
      "args": ["C:\\Users\\DELL\\kicad-mcp\\server.py"]
    }
  }
}
```

### 4. Reiniciar Claude Code
```cmd
claude
```

## Herramientas disponibles

| Herramienta | Descripción |
|-------------|-------------|
| `run_drc` | Corre DRC en .kicad_pcb |
| `run_erc` | Corre ERC en .kicad_sch |
| `analyze_pcb` | Lee componentes/nets sin explotar RAM |
| `export_gerbers` | Exporta Gerbers para JLCPCB |
| `export_bom` | Exporta BOM como CSV |
| `read_drc_report` | Parsea reporte DRC existente |
| `export_svg` | Preview del PCB como SVG |

## Ventajas vs MCP original
- ✅ Sin crashes de RAM (no carga todo en memoria)
- ✅ Usa Python de KiCad (ya instalado)
- ✅ Sin Bun, sin Node.js
- ✅ Parseo línea a línea de archivos grandes
- ✅ Compatible con KiCad 9.0

## Tu proyecto
PCB: `C:\Users\DELL\Downloads\ESP32-RS485-2026-03-10_235502\ESP32-RS485.kicad_pcb`

Ejemplo en Claude Code:
```
Corre DRC en C:\Users\DELL\Downloads\ESP32-RS485-2026-03-10_235502\ESP32-RS485.kicad_pcb
```
