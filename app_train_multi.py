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
import re

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

# Variavel global para guardar o ficheiro atual e anotacoes
CURRENT_FILE_INFO = {
    'filename': None,
    'filepath': None,
    'text': None,
    'annotations': {}  # {field_name: [(start, end, text), ...]}
}


@app.before_request
def before_request():
    """Inicializar idioma da sessao antes de cada request."""
    if TRANSLATION_AVAILABLE:
        # Verificar se ha idioma na sessao
        lang = session.get('language', 'pt')
        if lang != get_language():
            set_language(lang)


def allowed_file(filename):
    """Verificar se o ficheiro tem extensao permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_current_text():
    """Obter texto do ficheiro atual."""
    if CURRENT_FILE_INFO['text']:
        return CURRENT_FILE_INFO['text']
    
    if CURRENT_FILE_INFO['filepath'] and Path(CURRENT_FILE_INFO['filepath']).exists():
        try:
            CURRENT_FILE_INFO['text'] = extract_text_from_pdf(CURRENT_FILE_INFO['filepath'])
            return CURRENT_FILE_INFO['text']
        except:
            pass
    
    return ''


def get_current_annotations():
    """Obter anotacoes atuais."""
    return CURRENT_FILE_INFO.get('annotations', {})


def clear_current_file():
    """Limpar informacao do ficheiro atual."""
    CURRENT_FILE_INFO['filename'] = None
    CURRENT_FILE_INFO['filepath'] = None
    CURRENT_FILE_INFO['text'] = None
    CURRENT_FILE_INFO['annotations'] = {}


def generate_highlighted_text(text, annotations):
    """
    Gerar HTML com texto e destaques das anotacoes.
    
    Args:
        text: Texto original
        annotations: Dicionario {field_name: [(start, end, text), ...]}
        
    Returns:
        HTML com texto e destaques
    """
    if not text:
        return "<p>Nenhum texto carregado</p>"
    
    # Cores para diferentes campos
    field_colors = {
        "invoice_number": "#FFD700",  # Amarelo
        "issue_date": "#87CEFA",      # Azul claro
        "due_date": "#87CEFA",        # Azul claro
        "consumption_kwh": "#98FB98", # Verde claro
        "total_amount": "#F08080",    # Vermelho claro
        "client_name": "#DDA0DD",     # Roxo claro
        "nif": "#FFA07A",            # Laranja claro
    }
    
    # Criar uma lista de todos os destaques com suas posicoes
    highlights = []
    for ann_field, field_annotations in annotations.items():
        color = field_colors.get(ann_field, "#FFFF99")  # Amarelo claro
        for start, end, ann_text in field_annotations:
            highlights.append({
                'start': start,
                'end': end,
                'text': ann_text,
                'field': ann_field,
                'color': color
            })
    
    # Ordenar por posicao inicial
    highlights.sort(key=lambda h: h['start'])
    
    # Processar o texto e aplicar destaques
    result_parts = []
    last_pos = 0
    
    for highlight in highlights:
        start = highlight['start']
        end = highlight['end']
        
        # Adicionar texto antes do destaque
        if last_pos < start:
            result_parts.append(text[last_pos:start])
        
        # Adicionar o destaque
        selected_text = text[start:end]
        highlight_span = (f"<span class='highlight' style='background-color: {highlight['color']}; "
                        f"padding: 2px 4px; border-radius: 3px;' "
                        f"data-field='{highlight['field']}' data-start='{start}' data-end='{end}'>"
                        f"{selected_text}</span>")
        result_parts.append(highlight_span)
        
        last_pos = end
    
    # Adicionar texto restante
    if last_pos < len(text):
        result_parts.append(text[last_pos:])
    
    # Dividir em linhas preservando os destaques
    html_text = ''.join(result_parts)
    lines = html_text.split('\n')
    html_lines = [f"<div style='white-space: pre-wrap; margin-bottom: 5px;'>{line}</div>" for line in lines]
    
    return '\n'.join(html_lines)


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
                
                # Guardar informacao global
                CURRENT_FILE_INFO['filename'] = filename
                CURRENT_FILE_INFO['filepath'] = str(filepath)
                CURRENT_FILE_INFO['text'] = text
                CURRENT_FILE_INFO['annotations'] = {}  # Limpar anotacoes para novo ficheiro
                
                # Guardar tambem na sessao para compatibilidade
                session['current_file'] = filename
                session['filepath'] = str(filepath)
                session['extracted_text'] = text
                session['current_filename'] = filename
                session['annotations'] = {}
                
                # Ir diretamente para treino
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


@app.route('/train', methods=['GET', 'POST'])
def train():
    """Pagina de treino com padroes guardados."""
    # Obter todos os campos com os seus padroes
    fields = pattern_manager.get_all_fields()
    
    # Obter texto (tentar global primeiro, depois sessao)
    extracted_text = get_current_text()
    current_filename = CURRENT_FILE_INFO.get('filename', '') or session.get('current_filename', '')
    
    # Obter anotacoes atuais
    annotations = get_current_annotations()
    
    # Se nao houver texto, mostrar mensagem
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
                    start = int(start) if start else 0
                    end = int(end) if end else 0
                    
                    # Adicionar anotacao
                    if field_name not in annotations:
                        annotations[field_name] = []
                    annotations[field_name].append((start, end, text))
                    CURRENT_FILE_INFO['annotations'] = annotations
                    
                    # Guardar na sessao
                    session['annotations'] = annotations
                    
                    flash(_('Annotation added successfully!'), 'success')
                except Exception as e:
                    flash(_('Error adding annotation: ') + str(e), 'error')
            else:
                flash(_('Field and text are required'), 'error')
            
            return redirect(url_for('train'))
        
        elif action == 'remove_annotation':
            field_name = request.form.get('field_name')
            index = request.form.get('index')
            
            if field_name and index is not None:
                try:
                    index = int(index)
                    if field_name in annotations and 0 <= index < len(annotations[field_name]):
                        del annotations[field_name][index]
                        if not annotations[field_name]:
                            del annotations[field_name]
                        CURRENT_FILE_INFO['annotations'] = annotations
                        session['annotations'] = annotations
                        flash(_('Annotation removed successfully!'), 'success')
                except Exception as e:
                    flash(_('Error removing annotation: ') + str(e), 'error')
            else:
                flash(_('Invalid annotation data'), 'error')
            
            return redirect(url_for('train'))
        
        elif action == 'clear_annotations':
            # Limpar anotacoes
            CURRENT_FILE_INFO['annotations'] = {}
            session['annotations'] = {}
            annotations = {}
            flash(_('All annotations cleared!'), 'success')
            return redirect(url_for('train'))
        
        elif action == 'learn':
            # Aprender padroes a partir das anotacoes
            learned_count = 0
            for field_name, field_annotations in annotations.items():
                for start, end, text in field_annotations:
                    try:
                        pattern = Pattern(
                            field_name=field_name,
                            pattern=text,
                            pattern_type="contains",
                            provider="coopernico"
                        )
                        pattern_manager.add_pattern(field_name, pattern)
                        learned_count += 1
                    except Exception as e:
                        flash(_('Error saving pattern for ') + field_name + ": " + str(e), 'error')
            
            if learned_count > 0:
                flash(_('Patterns learned and saved successfully! ') + str(learned_count) + _(' patterns created.'), 'success')
            else:
                flash(_('No annotations to learn from.'), 'info')
            
            return redirect(url_for('train'))
        
        elif action == 'test_extraction':
            # Redirecionar para pagina de teste
            return redirect(url_for('test_extraction'))
    
    # Obter sugestoes para campos nao anotados
    suggestions = {}
    annotated_fields = set(annotations.keys())
    for field in fields:
        if field.field_name not in annotated_fields:
            # Obter sugestoes do pattern_manager
            field_patterns = pattern_manager.get_field(field.field_name)
            if field_patterns and field_patterns.patterns:
                suggestions[field.field_name] = []
                for pattern in field_patterns.patterns:
                    # Tentar encontrar match no texto
                    if pattern.pattern_type == "regex":
                        try:
                            for match in re.finditer(pattern.pattern, extracted_text, re.IGNORECASE):
                                start, end = match.span()
                                value = match.group(1) if match.groups() else match.group(0)
                                suggestions[field.field_name].append({
                                    "start": start,
                                    "end": end,
                                    "text": value,
                                    "confidence": pattern.confidence,
                                    "pattern": pattern.pattern
                                })
                                break  # Apenas uma sugestao por campo
                        except:
                            pass
    
    return render_template('training/train.html',
                         filename=current_filename,
                         provider="coopernico",
                         highlighted_text=generate_highlighted_text(extracted_text, annotations),
                         suggestions=suggestions,
                         fields=fields,
                         annotations=annotations,
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
    # Obter campos
    fields = pattern_manager.get_all_fields()
    
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
                
                # Converter result para results (dicionario com valores)
                # O template espera 'results' como dict de campo: valor
                results = result if isinstance(result, dict) else {}
                
                return render_template('training/test_extraction.html',
                                     results=results,
                                     fields=fields,
                                     filename=filename,
                                     current_language=get_language(),
                                     supported_languages=SUPPORTED_LANGUAGES,
                                     _=_)
            except Exception as e:
                flash(_('Error extracting data: ') + str(e), 'error')
                # Devolver template com results vazio
                return render_template('training/test_extraction.html',
                                     results={},
                                     fields=fields,
                                     filename=None,
                                     current_language=get_language(),
                                     supported_languages=SUPPORTED_LANGUAGES,
                                     _=_)
        else:
            flash(_('Invalid file type'), 'error')
    
    # Para GET, mostrar pagina com resultados vazios
    return render_template('training/test_extraction.html',
                         results={},
                         fields=fields,
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
            # Guardar global
            CURRENT_FILE_INFO['filename'] = filename
            CURRENT_FILE_INFO['filepath'] = str(dest_path)
            CURRENT_FILE_INFO['text'] = text
            CURRENT_FILE_INFO['annotations'] = {}
            
            # Guardar na sessao tambem
            session['extracted_text'] = text
            session['current_filename'] = filename
            session['annotations'] = {}
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
        
        # Limpar ficheiro atual
        clear_current_file()
        
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
        
        # Limpar ficheiro atual
        clear_current_file()
        
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
