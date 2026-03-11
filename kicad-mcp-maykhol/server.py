#!/usr/bin/env python3
"""
KiCad MCP Server - Liviano y eficiente para Claude Code
Autor: Para Maykhol - ESP32-RS485 project
Usa kicad-cli de KiCad 9.0 sin cargar archivos en RAM
"""

import json
import subprocess
import os
import re
import sys
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("kicad-maykhol")

# ─── Configuración ────────────────────────────────────────────────
KICAD_CLI = r"C:\Program Files\KiCad\9.0\bin\kicad-cli.exe"

def run_cli(args: list, timeout=60) -> dict:
    """Ejecuta kicad-cli y retorna stdout/stderr"""
    try:
        result = subprocess.run(
            [KICAD_CLI] + args,
            capture_output=True, text=True, timeout=timeout,
            encoding='utf-8', errors='replace'
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": "Timeout", "returncode": -1}
    except FileNotFoundError:
        return {"success": False, "stdout": "", "stderr": f"kicad-cli no encontrado en: {KICAD_CLI}", "returncode": -1}

# ─── HERRAMIENTA 1: DRC ───────────────────────────────────────────
@mcp.tool()
def run_drc(pcb_path: str) -> str:
    """
    Corre DRC en un archivo .kicad_pcb y retorna errores parseados.
    Args:
        pcb_path: Ruta completa al archivo .kicad_pcb
    """
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w') as f:
        report_path = f.name

    result = run_cli(["pcb", "drc", "--output", report_path, pcb_path])
    
    try:
        with open(report_path, 'r', encoding='utf-8', errors='replace') as f:
            report = f.read()
        os.unlink(report_path)
    except:
        report = result["stderr"]

    # Parsear resumen
    lines = result["stdout"] + result["stderr"]
    violations = re.search(r'(\d+) infracciones?|(\d+) violation', lines, re.IGNORECASE)
    unconnected = re.search(r'(\d+) (?:elementos? no conectados?|unconnected)', lines, re.IGNORECASE)

    summary = {
        "violations": int(violations.group(1) or violations.group(2)) if violations else "?",
        "unconnected": int(unconnected.group(1)) if unconnected else "?",
        "report_preview": report[:3000] if report else lines[:3000]
    }
    return json.dumps(summary, ensure_ascii=False, indent=2)


# ─── HERRAMIENTA 2: ERC ───────────────────────────────────────────
@mcp.tool()
def run_erc(sch_path: str) -> str:
    """
    Corre ERC en un archivo .kicad_sch y retorna errores parseados.
    Args:
        sch_path: Ruta completa al archivo .kicad_sch
    """
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w') as f:
        report_path = f.name

    result = run_cli(["sch", "erc", "--output", report_path, sch_path])

    try:
        with open(report_path, 'r', encoding='utf-8', errors='replace') as f:
            report = f.read()
        os.unlink(report_path)
    except:
        report = result["stderr"]

    return json.dumps({
        "success": result["success"],
        "report": report[:4000] if report else result["stdout"][:4000]
    }, ensure_ascii=False, indent=2)


# ─── HERRAMIENTA 3: LEER PCB (eficiente, sin cargar todo) ─────────
@mcp.tool()
def analyze_pcb(pcb_path: str) -> str:
    """
    Analiza un .kicad_pcb leyendo solo lo esencial: componentes, nets, capas.
    NO carga el archivo completo en RAM — parsea línea a línea.
    Args:
        pcb_path: Ruta completa al archivo .kicad_pcb
    """
    stats = {
        "footprints": [],
        "nets": [],
        "layers": [],
        "board_size": None,
        "file_size_kb": 0
    }

    try:
        stats["file_size_kb"] = round(os.path.getsize(pcb_path) / 1024, 1)
        
        with open(pcb_path, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                # Footprints
                if line.startswith('(footprint '):
                    m = re.search(r'\(footprint "([^"]+)"', line)
                    if m:
                        stats["footprints"].append(m.group(1))
                # Nets
                elif line.startswith('(net '):
                    m = re.search(r'\(net \d+ "([^"]+)"\)', line)
                    if m and m.group(1):
                        stats["nets"].append(m.group(1))
                # Capas
                elif '(layer "' in line and '(layers' not in line:
                    m = re.search(r'\(layer "([^"]+)"\)', line)
                    if m and m.group(1) not in stats["layers"]:
                        stats["layers"].append(m.group(1))
                # Board size
                elif '(page ' in line:
                    stats["board_size"] = line.strip()

        stats["total_footprints"] = len(stats["footprints"])
        stats["total_nets"] = len(stats["nets"])
        # Limitar listas para no saturar contexto
        stats["footprints"] = stats["footprints"][:50]
        stats["nets"] = stats["nets"][:50]
        stats["layers"] = list(set(stats["layers"]))[:30]

    except Exception as e:
        return json.dumps({"error": str(e)})

    return json.dumps(stats, ensure_ascii=False, indent=2)


# ─── HERRAMIENTA 4: EXPORTAR GERBERS ─────────────────────────────
@mcp.tool()
def export_gerbers(pcb_path: str, output_dir: str) -> str:
    """
    Exporta Gerbers listos para JLCPCB/PCBWay.
    Args:
        pcb_path: Ruta al .kicad_pcb
        output_dir: Carpeta de salida para los Gerbers
    """
    os.makedirs(output_dir, exist_ok=True)
    result = run_cli(["pcb", "export", "gerbers", "--output", output_dir, pcb_path], timeout=120)
    
    # Listar archivos generados
    files = []
    try:
        files = os.listdir(output_dir)
    except:
        pass

    return json.dumps({
        "success": result["success"],
        "output_dir": output_dir,
        "files_generated": files,
        "stderr": result["stderr"][:500] if not result["success"] else ""
    }, ensure_ascii=False, indent=2)


# ─── HERRAMIENTA 5: EXPORTAR BOM ──────────────────────────────────
@mcp.tool()
def export_bom(sch_path: str, output_path: str) -> str:
    """
    Exporta BOM (Bill of Materials) desde el esquemático.
    Args:
        sch_path: Ruta al .kicad_sch
        output_path: Ruta de salida del CSV
    """
    result = run_cli(["sch", "export", "bom", "--output", output_path, sch_path], timeout=60)
    
    preview = ""
    try:
        with open(output_path, 'r', encoding='utf-8', errors='replace') as f:
            preview = f.read(2000)
    except:
        pass

    return json.dumps({
        "success": result["success"],
        "output": output_path,
        "preview": preview,
        "stderr": result["stderr"][:300]
    }, ensure_ascii=False, indent=2)


# ─── HERRAMIENTA 6: LEER DRC.TXT EXISTENTE ────────────────────────
@mcp.tool()
def read_drc_report(report_path: str, max_errors: int = 50) -> str:
    """
    Lee y parsea un reporte DRC/ERC ya generado (ej: drc.txt del escritorio).
    Args:
        report_path: Ruta al archivo de reporte
        max_errors: Máximo de errores a retornar (default 50)
    """
    try:
        with open(report_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception as e:
        return json.dumps({"error": str(e)})

    # Parsear errores por categoría
    errors = []
    current_error = []
    for line in content.split('\n'):
        if line.startswith('[') or line.startswith('Error') or line.startswith('Warning'):
            if current_error:
                errors.append(' '.join(current_error))
            current_error = [line.strip()]
        elif line.strip() and current_error:
            current_error.append(line.strip())
    if current_error:
        errors.append(' '.join(current_error))

    # Agrupar por tipo
    categories = {}
    for e in errors:
        key = re.match(r'\[([^\]]+)\]', e)
        key = key.group(1) if key else "General"
        categories.setdefault(key, []).append(e)

    return json.dumps({
        "total_errors": len(errors),
        "categories": {k: len(v) for k, v in categories.items()},
        "errors_sample": errors[:max_errors],
        "raw_preview": content[:1000]
    }, ensure_ascii=False, indent=2)


# ─── HERRAMIENTA 7: EXPORTAR SVG (preview liviano) ────────────────
@mcp.tool()
def export_svg(pcb_path: str, output_path: str, layers: str = "F.Cu,B.Cu,F.SilkS,Edge.Cuts") -> str:
    """
    Exporta el PCB como SVG para previsualización (sin cargar en RAM).
    Args:
        pcb_path: Ruta al .kicad_pcb
        output_path: Ruta de salida .svg
        layers: Capas separadas por coma (default: F.Cu,B.Cu,F.SilkS,Edge.Cuts)
    """
    result = run_cli([
        "pcb", "export", "svg",
        "--output", output_path,
        "--layers", layers,
        "--mode-single",
        pcb_path
    ], timeout=60)

    return json.dumps({
        "success": result["success"],
        "output": output_path,
        "exists": os.path.exists(output_path),
        "size_kb": round(os.path.getsize(output_path)/1024, 1) if os.path.exists(output_path) else 0,
        "stderr": result["stderr"][:300]
    }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    print("KiCad MCP Server iniciando...", file=sys.stderr)
    mcp.run(transport='stdio')
