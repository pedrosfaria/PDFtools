#!/usr/bin/env python3
"""
Script para criar ficheiros .mo a partir de .po sem depender de ferramentas externas.
"""

import polib
from pathlib import Path

# Diretorio das traducoes
LOCALE_DIR = Path(__file__).parent / 'locales'

def compile_po_to_mo():
    """Compilar todos os ficheiros .po para .mo."""
    print("Compilando traducoes .po -> .mo...")
    
    # Encontrar todos os ficheiros .po
    po_files = list(LOCALE_DIR.rglob('*.po'))
    
    if not po_files:
        print("Nenhum ficheiro .po encontrado!")
        return
    
    print(f"Encontrados {len(po_files)} ficheiros .po")
    
    for po_file in po_files:
        mo_file = po_file.with_suffix('.mo')
        mo_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Carregar .po
            po = polib.pofile(str(po_file))
            
            # Guardar .mo
            po.save_as_mofile(str(mo_file))
            
            print(f"  ✅ {po_file.name} -> {mo_file.name}")
        except ImportError:
            print("  ❌ polib nao instalado. A instalar...")
            import subprocess
            subprocess.run(['pip', 'install', 'polib'], check=True)
            
            # Tentar novamente
            po = polib.pofile(str(po_file))
            po.save_as_mofile(str(mo_file))
            print(f"  ✅ {po_file.name} -> {mo_file.name}")
        except Exception as e:
            print(f"  ❌ Erro a compilar {po_file}: {e}")
    
    print("\nConcluido!")


if __name__ == '__main__':
    compile_po_to_mo()
