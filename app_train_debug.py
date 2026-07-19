#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicacao Web DEBUG para TREINO do extrator de faturas.

Esta aplicacao permite:
- Carregar faturas PDF
- Ver texto extraido em bruto
- Ver dados estruturados extraidos
- Comparar resultados de diferentes parsers
- Depurar padroes de extracao

Uso:
    python app_train_debug.py

A interface estara disponivel em: http://localhost:5002
"""

import os
import sys
import json
from pathlib import Path

# Adicionar o diretorio ao path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session, jsonify
from werkzeug.utils import secure_filename
from pdf_extractor import PDFExtractor
from pdf_extractor.utils.pdf_utils import extract_text_from_pdf
from pdf_extractor.parsers import PARSERS
from training.trainer import InvoiceTrainer
from training.patterns import PatternManager
import traceback

# Configuracao da aplicacao
app = Flask(__name__)
app.secret_key = 'debug_training_secret_key_2024'

# Configuracoes
UPLOAD_FOLDER = Path('training/uploads')
OUTPUT_FOLDER = Path('training/output')
DEBUG_FOLDER = Path('training/debug')
ALLOWED_EXTENSIONS = {'pdf', 'PDF'}

# Garantir que as pastas existem
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
DEBUG_FOLDER.mkdir(parents=True, exist_ok=True)

app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['OUTPUT_FOLDER'] = str(OUTPUT_FOLDER)
app.config['DEBUG_FOLDER'] = str(DEBUG_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Inicializar treinador e extrator
trainer = InvoiceTrainer()
pattern_manager = PatternManager()

def allowed_file(filename):
    """Verifica se o ficheiro e permitido."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_human_readable_text(text, max_length=5000):
    """Torna o texto legivel para visualizacao."""
    if not text:
        return ""
    
    # Substituir multiplos espacos por um so
    text = ' '.join(text.split())
    
    # Limitar comprimento
    if len(text) > max_length:
        return text[:max_length] + f"\n\n... (texto truncado, total: {len(text)} caracteres)"
    
    return text

def get_available_parsers():
    """Retorna a lista de parsers disponiveis."""
    return list(PARSERS.keys())

def get_parser(parser_name):
    """Retorna uma instancia do parser."""
    parser_class = PARSERS.get(parser_name)
    if parser_class:
        return parser_class()
    return None

@app.route('/')
def index():
    """Pagina inicial."""
    return render_template('training/debug_upload.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Carrega um ficheiro PDF."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nenhum ficheiro selecionado', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('Nenhum ficheiro selecionado', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = UPLOAD_FOLDER / filename
            file.save(str(filepath))
            
            # Guardar nome do ficheiro na sessao
            session['current_file'] = filename
            session['filepath'] = str(filepath)
            
            return redirect(url_for('debug_extraction', filename=filename))
        else:
            flash('Ficheiro nao permitido. Apenas PDF.', 'error')
    
    return render_template('training/debug_upload.html')

@app.route('/debug/<filename>')
def debug_extraction(filename):
    """Pagina de debug da extracao."""
    filepath = UPLOAD_FOLDER / filename
    
    if not filepath.exists():
        flash('Ficheiro nao encontrado', 'error')
        return redirect(url_for('index'))
    
    try:
        # Extrair texto bruto
        raw_text = extract_text_from_pdf(str(filepath))
        
        # Extrair com o extrator principal
        extractor = PDFExtractor(use_ocr=False)
        extracted_data = extractor.extract_from_pdf(str(filepath))
        
        # Tentar com todos os parsers disponiveis
        available_parsers = get_available_parsers()
        parsers_results = {}
        
        for parser_name in available_parsers:
            try:
                parser = get_parser(parser_name)
                if parser:
                    # Extrair texto primeiro para o parser
                    text = extract_text_from_pdf(str(filepath))
                    result = parser.parse(text)
                    parsers_results[parser_name] = {
                        'success': True,
                        'result': result
                    }
            except Exception as e:
                parsers_results[parser_name] = {
                    'success': False,
                    'error': str(e)
                }
        
        # Informacoes do ficheiro
        file_info = {
            'filename': filename,
            'size': filepath.stat().st_size,
            'path': str(filepath)
        }
        
        return render_template('training/debug_results.html',
                             file_info=file_info,
                             raw_text=get_human_readable_text(raw_text),
                             extracted_data=extracted_data,
                             parsers_results=parsers_results,
                             available_parsers=available_parsers)
        
    except Exception as e:
        error_msg = f"Erro ao processar ficheiro: {str(e)}"
        traceback_str = traceback.format_exc()
        return render_template('training/debug_results.html',
                             file_info={'filename': filename},
                             error=error_msg,
                             traceback=traceback_str)

@app.route('/download/<path:filename>')
def download_file(filename):
    """Descarrega um ficheiro."""
    return send_from_directory(str(UPLOAD_FOLDER), filename, as_attachment=True)

@app.route('/api/extract', methods=['POST'])
def api_extract():
    """API para extracao rapida."""
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum ficheiro fornecido'}), 400
    
    file = request.files['file']
    
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Ficheiro invalido'}), 400
    
    try:
        # Guardar ficheiro temporariamente
        filename = secure_filename(file.filename)
        filepath = DEBUG_FOLDER / filename
        file.save(str(filepath))
        
        # Extrair
        extractor = PDFExtractor(use_ocr=False)
        result = extractor.extract_from_pdf(str(filepath))
        
        # Limpar ficheiro temporario
        filepath.unlink(missing_ok=True)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/clear', methods=['POST'])
def clear_uploads():
    """Limpa os ficheiros carregados."""
    try:
        for f in UPLOAD_FOLDER.glob('*'):
            if f.is_file():
                f.unlink()
        for f in DEBUG_FOLDER.glob('*'):
            if f.is_file():
                f.unlink()
        flash('Ficheiros temporarios apagados com sucesso', 'success')
    except Exception as e:
        flash(f'Erro ao apagar ficheiros: {e}', 'error')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    print("="*60)
    print("DEBUG TRAINING APP - Extrator de Faturas")
    print("="*60)
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Debug folder: {DEBUG_FOLDER}")
    print("\nA aplicacao estara disponivel em: http://localhost:5002")
    print("Pressione Ctrl+C para parar o servidor")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5002, debug=True)
