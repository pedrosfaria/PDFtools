#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicacao Web para TREINO do extrator de faturas com suporte multi-lingue.

Esta aplicacao permite:
- Carregar faturas PDF
- Ver texto extraido
- Associar texto a campos
- Guardar padroes aprendidos
- Testar a extracao com padroes aprendidos
- Mudar de idioma

Uso:
    python app_train_multi.py

A interface estara disponivel em: http://localhost:5001
"""

import os
import sys
from pathlib import Path

# Adicionar o diretorio ao path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session, jsonify
from werkzeug.utils import secure_filename
from training.trainer import InvoiceTrainer
from training.patterns import PatternManager, Pattern
from pdf_extractor import PDFExtractor
from pdf_extractor.utils.pdf_utils import extract_text_from_pdf

# Importar sistema de traducao com fallback
try:
    from translations import set_language, get_language, gettext as _, SUPPORTED_LANGUAGES
    TRANSLATION_AVAILABLE = True
except Exception as e:
    print(f"Aviso: Sistema de traducao nao disponivel: {e}")
    print("A usar traducao simples (Portugues)")
    TRANSLATION_AVAILABLE = False
    
    # Funcao de fallback simples
    def _(text):
        """Funcao de traducao simples - devolve o texto original."""
        return text
    
    def get_language():
        return 'pt'
    
    def set_language(lang):
        pass
    
    SUPPORTED_LANGUAGES = {'pt': 'Portugues', 'en': 'English'}

import json
import shutil

# Configuracao da aplicacao
app = Flask(__name__)
app.secret_key = 'training_secret_key_2024'

# Configuracoes
UPLOAD_FOLDER = Path('training/uploads')
OUTPUT_FOLDER = Path('training/output')
ALLOWED_EXTENSIONS = {'pdf', 'PDF'}

# Garantir que as pastas existem
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['OUTPUT_FOLDER'] = str(OUTPUT_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Inicializar treinador e extrator
trainer = InvoiceTrainer()
extractor = PDFExtractor()
pattern_manager = PatternManager()

# Configurar idioma padrao
set_language('pt')  # Portugues por omissao


def allowed_file(filename):
    """Verificar se o ficheiro tem extensao permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Pagina inicial do treino."""
    # Obter exemplos de treino
    examples = trainer.get_training_examples()
    
    return render_template('training/index.html', 
                         examples=examples,
                         fields=trainer.get_fields(),
                         current_language=get_language(),
                         supported_languages=SUPPORTED_LANGUAGES,
                         _=_)  # Passar funcao de traducao para template


@app.route('/set_language/<lang>')
def set_language_route(lang):
    """Mudar idioma."""
    if lang in SUPPORTED_LANGUAGES:
        set_language(lang)
        session['language'] = lang
        flash(_('Language changed successfully!'), 'success')
    else:
        flash(_('Invalid language!'), 'error')
    
    return redirect(request.referrer or url_for('index'))


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Carregar ficheiro PDF para treino."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash(_('No file selected'), 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash(_('No file selected'), 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = UPLOAD_FOLDER / filename
            file.save(str(filepath))
            
            # Extrair texto do PDF imediatamente
            try:
                text = extract_text_from_pdf(str(filepath))
                
                if not text:
                    flash(_('No text could be extracted from the PDF. The file may be a scanned image.'), 'error')
                    return redirect(url_for('upload_file'))
                
                # Guardar informacao na sessao
                session['current_file'] = filename
                session['filepath'] = str(filepath)
                session['extracted_text'] = text
                session['current_filename'] = filename
                
                # Ir diretamente para treino com o texto
                flash(_('File uploaded successfully! Text extracted.'), 'success')
                return redirect(url_for('train'))
                
            except Exception as e:
                flash(_('Error processing PDF: ') + str(e), 'error')
                return redirect(url_for('upload_file'))
        else:
            flash(_('Invalid file type. Only PDF files are allowed.'), 'error')
    
    return render_template('training/upload.html',
                         current_language=get_language(),
                         supported_languages=SUPPORTED_LANGUAGES,
                         _=_)


@app.route('/view_text/<filename>')
def view_text(filename):
    """Visualizar texto extraido do PDF."""
    filepath = UPLOAD_FOLDER / filename
    
    if not filepath.exists():
        flash(_('File not found'), 'error')
        return redirect(url_for('upload_file'))
    
    # Obter texto da sessao
    extracted_text = session.get('extracted_text', '')
    
    if not extracted_text:
        # Se nao tiver na sessao, extrair novamente
        try:
            extracted_text = extract_text_from_pdf(str(filepath))
            session['extracted_text'] = extracted_text
        except Exception as e:
            flash(_('Error reading file: ') + str(e), 'error')
            return redirect(url_for('upload_file'))
    
    # Obter campos
    fields = trainer.get_fields()
    
    return render_template('training/view_text.html',
                         filename=filename,
                         text=extracted_text,
                         fields=fields,
                         current_language=get_language(),
                         supported_languages=SUPPORTED_LANGUAGES,
                         _=_)


@app.route('/train', methods=['GET', 'POST'])
def train():
    """Pagina de treino com padroes guardados."""
    # Obter todos os campos com os seus padroes
    fields = pattern_manager.get_all_fields()
    
    # Obter texto da sessao OU do ficheiro mais recente
    extracted_text = session.get('extracted_text', '')
    current_filename = session.get('current_filename', '')
    
    # Se nao houver texto na sessao, tentar obter do ficheiro mais recente
    if not extracted_text and current_filename:
        filepath = UPLOAD_FOLDER / current_filename
        if filepath.exists():
            try:
                extracted_text = extract_text_from_pdf(str(filepath))
                session['extracted_text'] = extracted_text
            except:
                pass
    
    # Se ainda nao houver texto, mostrar mensagem
    if not extracted_text:
        flash(_('Please upload a PDF file first.'), 'info')
        return redirect(url_for('upload_file'))
    
    # Criar lista de padroes para o template
    patterns = []
    for field in fields:
        for pattern in field.patterns:
            patterns.append({
                'field_name': field.field_name,
                'display_name': field.display_name,
                'pattern': pattern.pattern,
                'pattern_type': pattern.pattern_type,
                'provider': pattern.provider
            })
    
    # Handle POST actions from the form
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_annotation':
            field_name = request.form.get('field_name')
            text = request.form.get('text')
            start = request.form.get('start')
            end = request.form.get('end')
            
            if field_name and text:
                try:
                    # Criar padrao e guardar
                    pattern = Pattern(
                        field_name=field_name,
                        pattern=text,
                        pattern_type="contains",
                        provider="coopernico"
                    )
                    pattern_manager.add_pattern(field_name, pattern)
                    flash(_('Pattern saved successfully!'), 'success')
                except Exception as e:
                    flash(_('Error saving pattern: ') + str(e), 'error')
            else:
                flash(_('Field and text are required'), 'error')
            
            return redirect(url_for('train'))
        
        elif action == 'remove_annotation':
            field_name = request.form.get('field_name')
            index = request.form.get('index')
            # Implementar remocao se necessario
            flash(_('Annotation removed'), 'info')
            return redirect(url_for('train'))
        
        elif action == 'test_extraction':
            # Redirecionar para pagina de teste
            return redirect(url_for('test_extraction'))
        
        elif action == 'clear_annotations':
            # Limpar anotacoes
            flash(_('All annotations cleared'), 'info')
            return redirect(url_for('train'))
    
    return render_template('training/train.html',
                         filename=current_filename,
                         provider="coopernico",
                         highlighted_text=extracted_text,
                         suggestions={},  # Vazio por agora
                         fields=fields,
                         annotations={},  # Vazio por agora
                         patterns=patterns,
                         current_language=get_language(),
                         supported_languages=SUPPORTED_LANGUAGES,
                         _=_)


@app.route('/save_pattern', methods=['POST'])
def save_pattern():
    """Guardar padrao de extracao (rota alternativa)."""
    if request.method == 'POST':
        field = request.form.get('field')
        text = request.form.get('text')
        filename = session.get('current_filename')
        
        if not field or not text:
            flash(_('Field and text are required'), 'error')
            return redirect(url_for('train'))
        
        try:
            # Criar padrao e guardar
            pattern = Pattern(
                field_name=field,
                pattern=text,
                pattern_type="contains",
                provider="coopernico"
            )
            pattern_manager.add_pattern(field, pattern)
            
            flash(_('Pattern saved successfully!'), 'success')
            return redirect(url_for('train'))
        except Exception as e:
            flash(_('Error saving pattern: ') + str(e), 'error')
    
    return redirect(url_for('index'))


@app.route('/test_extraction', methods=['GET', 'POST'])
def test_extraction():
    """Testar extracao com padroes aprendidos."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash(_('No file selected'), 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = UPLOAD_FOLDER / filename
            file.save(str(filepath))
            
            try:
                # Extrair com padroes aprendidos
                result = extractor.extract_from_pdf(str(filepath))
                
                return render_template('training/test_extraction.html',
                                     result=result,
                                     filename=filename,
                                     current_language=get_language(),
                                     supported_languages=SUPPORTED_LANGUAGES,
                                     _=_)
            except Exception as e:
                flash(_('Error extracting data: ') + str(e), 'error')
        else:
            flash(_('Invalid file type'), 'error')
    
    return render_template('training/test_extraction.html',
                         result=None,
                         filename=None,
                         current_language=get_language(),
                         supported_languages=SUPPORTED_LANGUAGES,
                         _=_)


@app.route('/examples')
def examples():
    """Pagina com exemplos de faturas."""
    examples = trainer.get_training_examples()
    
    return render_template('training/examples.html',
                         examples=examples,
                         current_language=get_language(),
                         supported_languages=SUPPORTED_LANGUAGES,
                         _=_)


@app.route('/load_example/<filename>')
def load_example(filename):
    """Carregar um exemplo de fatura para treino."""
    filepath = Path('training/examples') / filename
    
    if not filepath.exists():
        flash(_('Example file not found'), 'error')
        return redirect(url_for('examples'))
    
    try:
        # Copiar ficheiro para uploads
        dest_path = UPLOAD_FOLDER / filename
        shutil.copy(str(filepath), str(dest_path))
        
        # Extrair texto
        text = extract_text_from_pdf(str(dest_path))
        if text:
            session['extracted_text'] = text
            session['current_filename'] = filename
            flash(_('Example loaded successfully!'), 'success')
        
        return redirect(url_for('train'))
    except Exception as e:
        flash(_('Error loading example: ') + str(e), 'error')
        return redirect(url_for('examples'))


@app.route('/delete_example/<filename>')
def delete_example(filename):
    """Apagar um exemplo de fatura."""
    filepath = Path('training/examples') / filename
    
    if filepath.exists():
        try:
            filepath.unlink()
            flash(_('Example deleted successfully!'), 'success')
        except Exception as e:
            flash(_('Error deleting example: ') + str(e), 'error')
    
    return redirect(url_for('examples'))


@app.route('/export_patterns')
def export_patterns():
    """Exportar padroes para ficheiro JSON."""
    try:
        fields = pattern_manager.get_all_fields()
        patterns_data = []
        for field in fields:
            for pattern in field.patterns:
                patterns_data.append(pattern.to_dict())
        
        return jsonify(patterns_data)
    except Exception as e:
        flash(_('Error exporting patterns: ') + str(e), 'error')
        return redirect(url_for('train'))


@app.route('/import_patterns', methods=['POST'])
def import_patterns():
    """Importar padroes de ficheiro JSON."""
    if 'file' not in request.files:
        flash(_('No file selected'), 'error')
        return redirect(url_for('train'))
    
    file = request.files['file']
    
    if file and file.filename.endswith('.json'):
        try:
            patterns_data = json.loads(file.read())
            for pattern_data in patterns_data:
                pattern = Pattern.from_dict(pattern_data)
                pattern_manager.add_pattern(pattern.field_name, pattern)
            
            flash(_('Patterns imported successfully!'), 'success')
        except Exception as e:
            flash(_('Error importing patterns: ') + str(e), 'error')
    else:
        flash(_('Invalid file type. Only JSON files are allowed.'), 'error')
    
    return redirect(url_for('train'))


@app.route('/clear_all', methods=['POST'])
def clear_all():
    """Apagar todos os dados de treino."""
    try:
        # Apagar ficheiro de padroes
        patterns_file = Path('training/patterns.json')
        if patterns_file.exists():
            patterns_file.unlink()
        
        # Recriar PatternManager para apagar da memoria
        global pattern_manager
        pattern_manager = PatternManager()
        
        # Apagar ficheiros de exemplos
        examples_dir = Path('training/examples')
        if examples_dir.exists():
            for f in examples_dir.glob('*'):
                if f.is_file():
                    f.unlink()
        
        # Apagar ficheiros temporarios
        for f in UPLOAD_FOLDER.glob('*'):
            if f.is_file():
                f.unlink()
        for f in OUTPUT_FOLDER.glob('*'):
            if f.is_file():
                f.unlink()
        
        flash(_('All training data cleared successfully!'), 'success')
    except Exception as e:
        flash(_('Error clearing all data: ') + str(e), 'error')
    
    return redirect(url_for('index'))


@app.route('/download/<path:filename>')
def download_file(filename):
    """Descarregar ficheiro."""
    return send_from_directory(str(UPLOAD_FOLDER), filename, as_attachment=True)


@app.route('/clear', methods=['POST'])
def clear_uploads():
    """Limpar ficheiros carregados."""
    try:
        for f in UPLOAD_FOLDER.glob('*'):
            if f.is_file():
                f.unlink()
        for f in OUTPUT_FOLDER.glob('*'):
            if f.is_file():
                f.unlink()
        flash(_('Temporary files cleared successfully!'), 'success')
    except Exception as e:
        flash(_('Error clearing files: ') + str(e), 'error')
    
    return redirect(url_for('index'))


if __name__ == '__main__':
    print("="*60)
    print("TRAINING APP - Extrator de Faturas (Multi-lingue)")
    print("="*60)
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Output folder: {OUTPUT_FOLDER}")
    print("\nA aplicacao estara disponivel em: http://localhost:5001")
    print("Pressione Ctrl+C para parar o servidor")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5001, debug=False)
