#!/usr/bin/env python3
"""
Aplicação Web para extração de faturas de eletricidade (Coopérnico, EDP, etc.)

Esta aplicação usa Flask para criar uma interface web que permite:
- Upload de ficheiros PDF
- Processamento automático
- Visualização dos resultados
- Download dos ficheiros exportados (CSV, Excel, JSON)

Para executar:
    python app_web.py

A interface estará disponível em: http://localhost:5000
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

# Adicionar o diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session
from werkzeug.utils import secure_filename
from pdf_extractor import PDFExtractor

# Configuração da aplicação
app = Flask(__name__)
app.secret_key = 'pdf_extractor_secret_key_2024'

# Configurações
UPLOAD_FOLDER = Path('uploads')
OUTPUT_FOLDER = Path('output')
ALLOWED_EXTENSIONS = {'pdf', 'PDF'}

# Garantir que as pastas existem
UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['OUTPUT_FOLDER'] = str(OUTPUT_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max

# Inicializar extrator
extractor = PDFExtractor(use_ocr=False)


def allowed_file(filename):
    """Verificar se o ficheiro tem extensão permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(filename):
    """Gerar um nome de ficheiro único."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    ext = Path(filename).suffix
    return f"{timestamp}_{secure_filename(Path(filename).stem)}{ext}"


@app.route('/')
def index():
    """Página inicial."""
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Página de upload de ficheiros."""
    if request.method == 'POST':
        # Verificar se o pedido tem ficheiros
        if 'files' not in request.files:
            flash('Nenhum ficheiro selecionado', 'error')
            return redirect(request.url)
        
        files = request.files.getlist('files')
        
        if not files or all(f.filename == '' for f in files):
            flash('Nenhum ficheiro selecionado', 'error')
            return redirect(request.url)
        
        # Processar ficheiros
        uploaded_files = []
        results = []
        errors = []
        
        for file in files:
            if file and allowed_file(file.filename):
                # Guardar ficheiro
                filename = generate_unique_filename(file.filename)
                filepath = UPLOAD_FOLDER / filename
                file.save(str(filepath))
                uploaded_files.append(filename)
                
                # Processar ficheiro
                try:
                    data = extractor.extract_from_pdf(str(filepath))
                    results.append(data)
                except Exception as e:
                    errors.append({
                        'filename': file.filename,
                        'error': str(e)
                    })
            else:
                errors.append({
                    'filename': file.filename,
                    'error': 'Tipo de ficheiro não permitido'
                })
        
        # Guardar resultados na sessão
        session['results'] = results
        session['errors'] = errors
        session['uploaded_files'] = uploaded_files
        
        if results:
            return redirect(url_for('show_results'))
        else:
            flash('Nenhum ficheiro foi processado com sucesso', 'error')
            return redirect(request.url)
    
    return render_template('upload.html')


@app.route('/results')
def show_results():
    """Mostrar resultados da extração."""
    results = session.get('results', [])
    errors = session.get('errors', [])
    uploaded_files = session.get('uploaded_files', [])
    
    if not results:
        flash('Não há resultados para mostrar', 'error')
        return redirect(url_for('index'))
    
    # Preparar dados para o template
    processed_data = []
    for i, data in enumerate(results):
        processed_data.append({
            'index': i,
            'filename': uploaded_files[i] if i < len(uploaded_files) else 'desconhecido',
            'provider': data.get('provider', 'N/A'),
            'invoice_number': data.get('invoice_number', 'N/A'),
            'issue_date': data.get('issue_date', 'N/A'),
            'due_date': data.get('due_date', 'N/A'),
            'consumption_kwh': data.get('consumption_kwh', 'N/A'),
            'total_amount': data.get('total_amount', 'N/A'),
            'client_name': data.get('client_name', 'N/A'),
            'nif': data.get('nif', 'N/A'),
            'full_data': data
        })
    
    return render_template('results.html', 
                         results=processed_data, 
                         errors=errors,
                         count=len(results))


@app.route('/export', methods=['POST'])
def export_data():
    """Exportar dados para o formato selecionado."""
    results = session.get('results', [])
    export_format = request.form.get('format', 'csv')
    
    if not results:
        flash('Não há dados para exportar', 'error')
        return redirect(url_for('index'))
    
    # Gerar nome de ficheiro
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"faturas_{timestamp}.{export_format}"
    filepath = OUTPUT_FOLDER / filename
    
    # Exportar
    try:
        extractor.export(results, format=export_format, output_path=str(filepath))
        session['export_file'] = filename
        flash(f'Dados exportados para {filename}', 'success')
    except Exception as e:
        flash(f'Erro ao exportar: {e}', 'error')
        return redirect(url_for('show_results'))
    
    return redirect(url_for('download_file', filename=filename))


@app.route('/download/<filename>')
def download_file(filename):
    """Download do ficheiro exportado."""
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)


@app.route('/clear', methods=['POST'])
def clear_session():
    """Limpar dados da sessão."""
    session.clear()
    flash('Dados limpos', 'success')
    return redirect(url_for('index'))


@app.route('/about')
def about():
    """Página sobre."""
    return render_template('about.html')


@app.route('/test')
def test():
    """Página de teste com dados de exemplo."""
    # Dados de exemplo
    sample_data = [
        {
            'provider': 'coopernico',
            'invoice_number': 'COOP-2024-001234',
            'issue_date': '15-01-2024',
            'due_date': '30-01-2024',
            'consumption_kwh': 350.5,
            'total_amount': 73.41,
            'client_name': 'João Silva',
            'nif': '123456789',
            'consumption_period_start': '01-12-2023',
            'consumption_period_end': '31-12-2023',
            'power_contracted_kva': 6.9,
            'price_per_kwh': 0.14,
            'energy_cost': 49.07,
            'network_cost': 10.5,
            'iva_rate': 23.0,
            'iva_value': 13.84,
            'address': 'Rua da Cooperativa, 123',
            'postal_code': '1234-567',
            'city': 'Lisboa'
        }
    ]
    
    session['results'] = sample_data
    session['errors'] = []
    session['uploaded_files'] = ['exemplo_coopernico.pdf']
    
    return redirect(url_for('show_results'))


if __name__ == '__main__':
    # Limpar pastas temporárias
    if UPLOAD_FOLDER.exists():
        for f in UPLOAD_FOLDER.glob('*'):
            f.unlink()
    
    if OUTPUT_FOLDER.exists():
        for f in OUTPUT_FOLDER.glob('*'):
            f.unlink()
    
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║   PDF Invoice Extractor - Web Interface                        ║
    ║   A interface web está disponível em: http://localhost:5000    ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
