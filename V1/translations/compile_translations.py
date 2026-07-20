#!/usr/bin/env python3
"""
Script para compilar os ficheiros de traducao (.po -> .mo).

Uso:
    python compile_translations.py
"""

import os
import subprocess
from pathlib import Path

# Diretorio das traducoes
LOCALE_DIR = Path(__file__).parent / 'locales'

def compile_translations():
    """Compilar todos os ficheiros .po para .mo."""
    print("Compilando traducoes...")
    
    # Encontrar todos os ficheiros .po
    po_files = list(LOCALE_DIR.rglob('*.po'))
    
    if not po_files:
        print("Nenhum ficheiro .po encontrado!")
        return
    
    print(f"Encontrados {len(po_files)} ficheiros .po")
    
    # Compilar cada ficheiro .po
    for po_file in po_files:
        mo_file = po_file.with_suffix('.mo')
        locale_dir = mo_file.parent
        
        # Criar diretorio se nao existir
        locale_dir.mkdir(parents=True, exist_ok=True)
        
        # Compilar
        try:
            # Usar msgfmt para compilar
            result = subprocess.run(
                ['msgfmt', '-o', str(mo_file), str(po_file)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"  ✅ {po_file.name} -> {mo_file.name}")
            else:
                print(f"  ❌ Erro a compilar {po_file}: {result.stderr}")
        except FileNotFoundError:
            print("  ⚠️  msgfmt nao encontrado. A instalar gettext...")
            try:
                import gettext
                print("  gettext ja esta instalado")
            except ImportError:
                print("  A instalar gettext...")
                subprocess.run(['pip', 'install', 'gettext'], check=True)
            
            # Tentar novamente
            result = subprocess.run(
                ['msgfmt', '-o', str(mo_file), str(po_file)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"  ✅ {po_file.name} -> {mo_file.name}")
            else:
                print(f"  ❌ Erro a compilar {po_file}: {result.stderr}")
    
    print("\nConcluido!")


def create_pot_template():
    """Criar ficheiro .pot template a partir dos ficheiros .po."""
    print("Criando ficheiro .pot template...")
    
    # Usar xgettext para criar .pot
    try:
        result = subprocess.run(
            ['xgettext', '--output=messages.pot', '--keyword=_', '--keyword=ngettext:1,2'] + 
            [str(f) for f in Path(__file__).parent.parent.rglob('*.py')],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent)
        )
        
        if result.returncode == 0:
            print("  ✅ messages.pot criado")
        else:
            print(f"  ❌ Erro: {result.stderr}")
    except FileNotFoundError:
        print("  ⚠️  xgettext nao encontrado")


if __name__ == '__main__':
    compile_translations()
    # create_pot_template()  # Opcional
