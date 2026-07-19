#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicacao Web para TREINO do extrator de faturas com suporte multi-lingue.

Esta aplicacao permite:
- Carregar faturas PDF
- Selecionar texto manualmente
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

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session, jsonify, gettext
from werkzeug.utils import secure_filename
from training.trainer import InvoiceTrainer
from training.patterns import PatternManager
from pdf_extractor import PDFExtractor
from translations import set_language, get_language, SUPPORTED_LANGUAGES
import json

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

# Configurar idioma padrao
set_language('pt')  # Portugues por omissao


def get_translated_text(text: str) -> str:
    """Obter texto traduzido."""
    try:
        return gettext(text)
    except Exception:
        return text


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
                         supported_languages=SUPPORTED_LANGUAGES)


@app.route('/set_language/<lang>')
def set_language_route(lang):
    """Mudar idioma."""
    if lang in SUPPORTED_LANGUAGES:
        set_language(lang)
        session['language'] = lang
        flash(get_translated_text('Language changed successfully!'), 'success')
    else:
        flash(get_translated_text('Invalid language!'), 'error')
    
    return redirect(request.referrer or url_for('index'))


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Carregar ficheiro PDF para treino."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash(get_translated_text('No file selected'), 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash(get_translated_text('No file selected'), 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Guardar ficheiro
            filename = secure_filename(file.filename)
            filepath = UPLOAD_FOLDER / filename
            file.save(str(filepath))
            
            # Carregar texto
            try:
                text, filename = trainer.load_pdf(str(filepath))
                session['current_file'] = filename
                session['current_text'] = text
                session['current_provider'] = trainer.current_provider
                
                # Limpar anotacoes anteriores
                trainer.clear_annotations()
                
                flash(get_translated_text('File uploaded successfully!'), 'success')
                return redirect(url_for('train'))
            except Exception as e:
                flash(f"{get_translated_text('Error loading file')}: {e}", 'error')
                return redirect(request.url)
        else:
            flash(get_translated_text('Invalid file type. Only PDF allowed.'), 'error')
            return redirect(request.url)
    
    return render_template('training/upload.html',
                         current_language=get_language(),
                         supported_languages=SUPPORTED_LANGUAGES)


@app.route('/train', methods=['GET', 'POST'])
def train():
    """Pagina de treino."""
    if 'current_text' not in session:
        flash(get_translated_text('No file loaded. Please upload a file first.'), 'error')
        return redirect(url_for('upload_file'))
    
    # Atualizar treinador com texto da sessao
    trainer.current_text = session['current_text']
    trainer.current_filename = session.get('current_file', 'desconhecido')
    trainer.current_provider = session.get('current_provider', 'coopernico')
    
    if request.method == 'POST':
        # Processar anotacoes
        action = request.form.get('action')
        
        if action == 'add_annotation':
            field_name = request.form.get('field_name')
            start = int(request.form.get('start'))
            end = int(request.form.get('end'))
            text = request.form.get('text')
            
            if field_name and start >= 0 and end > start:
                trainer.add_annotation(field_name, start, end, text)
                session['annotations'] = trainer.current_annotations
                flash(get_translated_text('Annotation added!'), 'success')
        
        elif action == 'remove_annotation':
            field_name = request.form.get('field_name')
            index = int(request.form.get('index'))
            
            if field_name and trainer.remove_annotation(field_name, index):
                session['annotations'] = trainer.current_annotations
                flash(get_translated_text('Annotation removed!'), 'success')
        
        elif action == 'clear_annotations':
            trainer.clear_annotations()
            session.pop('annotations', None)
            flash(get_translated_text('All annotations cleared!'), 'success')
        
        elif action == 'learn':
            learned = trainer.learn_from_annotations()
            trainer.save_training_example()
            flash(get_translated_text('Patterns learned and saved!'), 'success')
            return redirect(url_for('train'))
        
        elif action == 'test_extraction':
            results = trainer.extract_with_learned_patterns(
                trainer.current_text, trainer.current_provider
            )
            session['extraction_results'] = results
            return redirect(url_for('test_extraction'))
    
    # Obter sugestoes para campos nao anotados
    fields = trainer.get_fields()
    annotated_fields = set(trainer.current_annotations.keys())
    
    suggestions = {}
    for field in fields:
        if field.field_name not in annotated_fields:
            suggestions[field.field_name] = trainer.get_field_suggestions(
                trainer.current_text, field.field_name
            )
    
    return render_template('training/train.html',
                         text=trainer.current_text,
                         filename=trainer.current_filename,
                         provider=trainer.current_provider,
                         fields=fields,
                         annotations=trainer.current_annotations,
                         suggestions=suggestions,
                         highlighted_text=trainer.get_text_with_highlights(),
                         current_language=get_language(),
                         supported_languages=SUPPORTED_LANGUAGES)


@app.route('/test_extraction')
def test_extraction():
    """Testar extracao com padroes aprendidos."""
    if 'current_text' not in session:
        flash(get_translated_text('No file loaded.'), 'error')
        return redirect(url_for('upload_file'))
    
    # Atualizar treinador
    trainer.current_text = session['current_text']
    trainer.current_provider = session.get('current_provider', 'coopernico')
    
    # Extrair dados
    results = trainer.extract_with_learned_patterns(
        trainer.current_text, trainer.current_provider
    )
    
    # Guardar na sessao
    session['extraction_results'] = results
    
    return render_template('training/test_extraction.html',
                         results=results,
                         fields=trainer.get_fields(),
                         current_language=get_language(),
                         supported_languages=SUPPORTED_LANGUAGES)


@app.route('/get_suggestions/<field_name>')
def get_suggestions(field_name):
    """API para obter sugestoes para um campo."""
    if 'current_text' not in session:
        return jsonify({"suggestions": []})
    
    trainer.current_text = session['current_text']
    suggestions = trainer.get_field_suggestions(trainer.current_text, field_name)
    
    return jsonify({
        "suggestions": [
            {
                "start": s["start"],
                "end": s["end"],
                "text": s["text"],
                "confidence": s["confidence"]
            }
            for s in suggestions
        ]
    })


@app.route('/api/extract_text', methods=['POST'])
def api_extract_text():
    """API para extrair texto de uma posicao."""
    data = request.json
    start = data.get('start', 0)
    end = data.get('end', 0)
    text = session.get('current_text', '')
    
    if start >= 0 and end > start and end <= len(text):
        extracted = text[start:end].strip()
        return jsonify({"text": extracted, "start": start, "end": end})
    
    return jsonify({"error": get_translated_text("Invalid position")}), 400


@app.route('/api/annotate', methods=['POST'])
def api_annotate():
    """API para adicionar anotacao."""
    data = request.json
    field_name = data.get('field_name')
    start = data.get('start', 0)
    end = data.get('end', 0)
    text = data.get('text', '')
    
    if field_name and start >= 0 and end > start:
        trainer.current_text = session.get('current_text', '')
        trainer.add_annotation(field_name, start, end, text)
        session['annotations'] = trainer.current_annotations
        
        return jsonify({
            "success": True,
            "annotations": {
                field: [{"start": s, "end": e, "text": t} for s, e, t in anns]
                for field, anns in trainer.current_annotations.items()
            }
        })
    
    return jsonify({"success": False, "error": get_translated_text("Invalid data")}), 400


@app.route('/api/learn', methods=['POST'])
def api_learn():
    """API para aprender padroes."""
    trainer.current_text = session.get('current_text', '')
    trainer.current_filename = session.get('current_file', 'desconhecido')
    trainer.current_provider = session.get('current_provider', 'coopernico')
    
    learned = trainer.learn_from_annotations()
    trainer.save_training_example()
    
    return jsonify({
        "success": True,
        "learned_patterns": {field: p.to_dict() for field, p in learned.items()}
    })


@app.route('/api/extract', methods=['POST'])
def api_extract():
    """API para extrair dados."""
    trainer.current_text = session.get('current_text', '')
    trainer.current_provider = session.get('current_provider', 'coopernico')
    
    results = trainer.extract_with_learned_patterns(
        trainer.current_text, trainer.current_provider
    )
    
    session['extraction_results'] = results
    
    return jsonify({
        "success": True,
        "results": results
    })


@app.route('/list_examples')
def list_examples():
    """Listar todos os exemplos de treino."""
    examples = trainer.get_training_examples()
    
    return render_template('training/examples.html', 
                         examples=examples,
                         current_language=get_language(),
                         supported_languages=SUPPORTED_LANGUAGES)


@app.route('/load_example/<filename>')
def load_example(filename):
    """Carregar um exemplo de treino."""
    example = trainer.load_training_example(filename)
    
    if example:
        session['current_text'] = example.text
        session['current_file'] = example.filename
        session['current_provider'] = example.provider
        session['annotations'] = example.field_annotations
        
        flash(get_translated_text('Example loaded!'), 'success')
        return redirect(url_for('train'))
    else:
        flash(get_translated_text('Example not found!'), 'error')
        return redirect(url_for('list_examples'))


@app.route('/delete_example/<filename>')
def delete_example(filename):
    """Apagar um exemplo de treino."""
    example_path = Path('training/training_data') / f"{filename}.json"
    
    if example_path.exists():
        example_path.unlink()
        flash(get_translated_text('Example deleted!'), 'success')
    else:
        flash(get_translated_text('Example not found!'), 'error')
    
    return redirect(url_for('list_examples'))


@app.route('/export_patterns')
def export_patterns():
    """Exportar padroes aprendidos."""
    patterns_file = Path('training/patterns.json')
    
    if patterns_file.exists():
        return send_from_directory('training', 'patterns.json', as_attachment=True)
    else:
        flash(get_translated_text('No patterns to export!'), 'error')
        return redirect(url_for('index'))


@app.route('/import_patterns', methods=['POST'])
def import_patterns():
    """Importar padroes."""
    if 'file' not in request.files:
        flash(get_translated_text('No file selected!'), 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash(get_translated_text('No file selected!'), 'error')
        return redirect(url_for('index'))
    
    if file and file.filename.endswith('.json'):
        # Guardar ficheiro
        filepath = Path('training/patterns_backup.json')
        file.save(str(filepath))
        
        # Carregar padroes
        global trainer
        trainer = InvoiceTrainer(patterns_file=str(filepath))
        
        flash(get_translated_text('Patterns imported successfully!'), 'success')
        return redirect(url_for('index'))
    else:
        flash(get_translated_text('Invalid file!'), 'error')
        return redirect(url_for('index'))


@app.route('/clear_all')
def clear_all():
    """Limpar todos os dados de treino."""
    # Apagar ficheiros de treino
    training_data_dir = Path('training/training_data')
    if training_data_dir.exists():
        for f in training_data_dir.glob('*.json'):
            f.unlink()
    
    # Apagar padroes
    patterns_file = Path('training/patterns.json')
    if patterns_file.exists():
        patterns_file.unlink()
    
    # Reiniciar treinador
    global trainer
    trainer = InvoiceTrainer()
    
    flash(get_translated_text('All training data deleted!'), 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    print("""
    +-----------------------------------------------------+
    |  PDF Invoice Extractor - Training Mode (Multi-Lang)  |
    |  A interface estara disponivel em:                 |
    |  http://localhost:5001                              |
    |                                                     |
    |  Idiomas suportados: pt, en, es, fr                 |
    +-----------------------------------------------------+
    """)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
