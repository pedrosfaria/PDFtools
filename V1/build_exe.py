#!/usr/bin/env python3
"""
Script para criar executável para Windows usando PyInstaller.

Este script gera um executável .exe que pode ser distribuído e executado
no Windows sem necessitar de ter Python instalado.

Uso:
    python build_exe.py

O executável será criado na pasta 'dist/'.
"""

import os
import sys
import subprocess
from pathlib import Path

# Caminho para o PyInstaller
PYINSTALLER = 'pyinstaller'

# Ficheiro principal da aplicação
MAIN_FILE = 'app_web.py'

# Nome do executável
EXE_NAME = 'PDF_Invoice_Extractor'

# Ícone (opcional - precisa de criar um ficheiro .ico)
ICON_FILE = None  # 'icon.ico' se tiver um ícone

# Opções do PyInstaller
PYINSTALLER_OPTS = [
    '--onefile',           # Criar um único ficheiro .exe
    '--windowed',          # Não mostrar consola (para aplicações GUI)
    '--name=' + EXE_NAME,  # Nome do executável
    '--clean',             # Limpar builds anteriores
    '--add-data=templates/*;templates',  # Incluir templates
    '--add-data=static/*;static',      # Incluir ficheiros estáticos
    '--add-data=pdf_extractor/*;pdf_extractor',  # Incluir o pacote
]

# Adicionar ícone se existir
if ICON_FILE and Path(ICON_FILE).exists():
    PYINSTALLER_OPTS.append('--icon=' + ICON_FILE)

# Adicionar ficheiro principal
PYINSTALLER_OPTS.append(MAIN_FILE)


def check_pyinstaller():
    """Verificar se o PyInstaller está instalado."""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False


def install_pyinstaller():
    """Instalar PyInstaller."""
    print("📦 A instalar PyInstaller...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    print("✅ PyInstaller instalado com sucesso!")


def build_executable():
    """Criar o executável."""
    print("🚀 A criar executável...")
    print(f"   Ficheiro principal: {MAIN_FILE}")
    print(f"   Nome do executável: {EXE_NAME}")
    
    # Comando do PyInstaller
    cmd = [sys.executable, '-m', PYINSTALLER] + PYINSTALLER_OPTS
    
    print(f"   Comando: {' '.join(cmd)}")
    
    # Executar
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Executável criado com sucesso!")
        print(f"   Localização: dist/{EXE_NAME}.exe")
    else:
        print("❌ Erro ao criar executável:")
        print(result.stderr)
        sys.exit(1)


def create_spec_file():
    """Criar ficheiro .spec para build personalizado."""
    spec_content = f"""
# {EXE_NAME}.spec

from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import os

# Paths
main_path = os.path.join(os.path.dirname(__file__), '{MAIN_FILE}')

# Collect data files
data_files = []

# Add templates
data_files += collect_data_files('templates', include_py_files=False)

# Add static files
data_files += collect_data_files('static', include_py_files=False)

# Add pdf_extractor package
data_files += collect_data_files('pdf_extractor', include_py_files=False)

# Create spec
a = Analysis(
    ['{MAIN_FILE}'],
    pathex=[os.path.dirname(__file__)],
    binaries=[],
    datas=data_files,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{EXE_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon=None
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{EXE_NAME}'
)
"""
    
    spec_path = Path(f'{EXE_NAME}.spec')
    with open(spec_path, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"✅ Ficheiro .spec criado: {spec_path}")
    return spec_path


def main():
    """Função principal."""
    print("=" * 60)
    print("PDF Invoice Extractor - Build Executável")
    print("=" * 60)
    print()
    
    # Verificar se PyInstaller está instalado
    if not check_pyinstaller():
        install_pyinstaller()
    
    # Criar executável
    build_executable()
    
    print()
    print("=" * 60)
    print("Build concluído!")
    print("=" * 60)
    print()
    print("Para executar:")
    print(f"   1. Vá à pasta 'dist/'")
    print(f"   2. Execute: {EXE_NAME}.exe")
    print()
    print("A aplicação web estará disponível em: http://localhost:5000")
    print()


if __name__ == '__main__':
    main()
