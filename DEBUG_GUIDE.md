# 🐛 Guia de Debug - Extrator de Faturas PDF

Este guia explica como usar as ferramentas de debug para resolver problemas com a extracao de dados de faturas PDF.

---

## 📁 Ficheiros de Debug Disponiveis

### 1. `test_upload.py` - Script de Teste Rapido
Script simples para testar extracao de um ficheiro PDF individual.

**Uso:**
```bash
python test_upload.py "caminho/para/fatura.pdf"
```

**Exemplo:**
```bash
python test_upload.py "faturas_fornecedores/coopernico/faturacoop.pdf"
```

**O que faz:**
- Extrai texto bruto do PDF
- Tenta extrair dados estruturados
- Mostra os primeiros 1000 caracteres do texto
- Mostra o resultado em formato JSON

**Saida esperada:**
```
============================================================
TESTANDO EXTRACAO: faturas_fornecedores/coopernico/faturacoop.pdf
============================================================

📄 A extrair texto do PDF...
✅ SUCESSO: Extraido 5432 caracteres

============================================================
TEXTO EXTRAIDO (primeiros 1000 caracteres):
============================================================
NIF: 500123456
Nome: Coopernico - Cooperativa de Consumidores
Morada: Rua das Faturas, 123
...

============================================================
A EXTRATIR DADOS ESTRUTURADOS...
============================================================

✅ Dados extraidos com sucesso:
{
  "emissor": {
    "nif": "500123456",
    "nome": "Coopernico - Cooperativa de Consumidores",
    ...
  },
  "cliente": {...},
  "itens": [...],
  "totais": {...}
}
```

---

### 2. `app_train_debug.py` - Aplicacao Web de Debug
Aplicacao Flask para debug interativo com interface web.

**Uso:**
```bash
python app_train_debug.py
```

**A interface estara disponivel em:** `http://localhost:5002`

**Funcionalidades:**
- 📤 Upload de ficheiros PDF
- 👁️ Visualizacao de texto bruto extraido
- 📊 Visualizacao de dados estruturados
- 🔧 Comparacao de resultados de todos os parsers disponiveis
- 💾 Descarregar ficheiros carregados
- 🗑️ Limpar ficheiros temporarios

**Paginas:**
- `/` ou `/upload` - Carregar ficheiro PDF
- `/debug/<filename>` - Ver resultados detalhados
- `/download/<filename>` - Descarregar ficheiro
- `/api/extract` - API para extracao rapida (POST)

---

## 🔍 Como Depurar Problemas Comuns

### Problema 1: Nenhum texto extraido

**Sintoma:** O script devolve `⚠️ AVISO: Nenhum texto extraido. O PDF pode ser uma imagem (scan).`

**Causa:** O PDF e uma imagem digitalizada (scan) e nao contem texto pesquisavel.

**Solucao:**
```python
# Usar OCR para extrair texto de PDFs digitalizados
extractor = PDFExtractor(use_ocr=True)
result = extractor.extract_from_pdf("fatura_scan.pdf")
```

**Requisitos para OCR:**
```bash
pip install pytesseract pillow
# E instalar Tesseract OCR no sistema
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
# Linux: sudo apt install tesseract-ocr
# Mac: brew install tesseract
```

---

### Problema 2: Dados estruturados vazios

**Sintoma:** O texto e extraido, mas nao ha dados estruturados (campos como NIF, nome, itens, etc.).

**Causas possiveis:**
1. O parser nao reconhece o formato da fatura
2. Os padroes de extracao nao estao treinados para este tipo de fatura
3. O texto extraido tem formato inesperado

**Solucoes:**

#### Opcao A: Verificar texto bruto
```bash
python test_upload.py "fatura.pdf"
```
Verifique se o texto contem as informacoes que espera (NIF, nome, valores, etc.).

#### Opcao B: Treinar o extrator
Use a aplicacao de treino para ensinar o sistema a reconhecer os campos:
```bash
python app_train.py
# Acesse http://localhost:5001
```

#### Opcao C: Criar um parser personalizado
Veja `pdf_extractor/parsers/` para exemplos de parsers e crie um novo para o seu formato de fatura.

---

### Problema 3: Erro ao processar PDF

**Sintoma:** Erro como `PdfReadError`, `FileNotFoundError`, etc.

**Solucoes:**

1. **Verificar se o ficheiro existe:**
   ```python
   from pathlib import Path
   Path("fatura.pdf").exists()  # Deve retornar True
   ```

2. **Verificar se o ficheiro e valido:**
   ```bash
   # Usar pdfinfo (parte do poppler-utils)
   pdfinfo fatura.pdf
   ```

3. **Verificar permissões:**
   ```bash
   # Linux/Mac
   ls -la fatura.pdf
   chmod +r fatura.pdf
   ```

---

### Problema 4: Parser especifico falha

**Sintoma:** Um parser (ex: `coopernico_parser`) falha com erro.

**Solucao:**

1. **Ver o erro detalhado na aplicacao debug:**
   - Acesse `http://localhost:5002`
   - Carregue o ficheiro
   - Veja a secao "Resultados por Parser"

2. **Testar o parser diretamente:**
   ```python
   from pdf_extractor.parsers import get_parser
   
   parser = get_parser('coopernico_parser')
   try:
       result = parser.parse("fatura.pdf")
       print(result)
   except Exception as e:
       print(f"Erro: {e}")
       import traceback
       traceback.print_exc()
   ```

3. **Verificar o codigo do parser:**
   - Abra `pdf_extractor/parsers/coopernico_parser.py`
   - Verifique se os padroes regex correspondem ao seu PDF

---

## 🛠️ API de Debug

### Endpoint: `/api/extract` (POST)

Envia um PDF e recebe os dados extraidos em JSON.

**Request:**
```bash
curl -X POST -F "file=@fatura.pdf" http://localhost:5002/api/extract
```

**Response (sucesso):**
```json
{
    "success": true,
    "filename": "fatura.pdf",
    "result": {
        "emissor": {
            "nif": "123456789",
            "nome": "Empresa SA"
        },
        "cliente": {...},
        "itens": [...],
        "totais": {...}
    }
}
```

**Response (erro):**
```json
{
    "success": false,
    "error": "Mensagem de erro",
    "traceback": "Traceback completo..."
}
```

---

## 📊 Comparacao de Parsers

A aplicacao debug mostra resultados de todos os parsers disponiveis. Isto e util para:

1. **Ver qual parser funciona melhor** para o seu tipo de fatura
2. **Identificar padroes** que estao a falhar
3. **Comparar formatos** de saida

**Parsers disponiveis:**
- `coopernico_parser` - Para faturas Coopernico
- `edp_parser` - Para faturas EDP
- `galp_parser` - Para faturas Galp
- `ibersol_parser` - Para faturas Ibersol
- `base_parser` - Parser generico (fallback)

---

## 💡 Dicas de Debug

### 1. Comece com PDFs simples
Teste com faturas que sabe que tem texto pesquisavel (nao scans).

### 2. Verifique o texto bruto
Muitas vezes o problema nao e no parser, mas na extracao de texto.

### 3. Teste com diferentes parsers
Alguns parsers sao especificos para determinados formatos.

### 4. Use OCR para scans
Se o PDF e uma imagem, ative OCR.

### 5. Treine o sistema
Use a aplicacao de treino para ensinar o sistema a reconhecer os seus padroes de faturas.

### 6. Verifique o encoding
Alguns PDFs tem problemas de encoding. Tente:
```python
text = extract_text_from_pdf("fatura.pdf", encoding='utf-8')
# ou
text = extract_text_from_pdf("fatura.pdf", encoding='latin-1')
```

---

## 📞 Suporte

Se encontrar problemas que nao consegue resolver:

1. **Guarde o PDF problematico** em `faturas_fornecedores/`
2. **Execute o script de teste:**
   ```bash
   python test_upload.py "faturas_fornecedores/fatura_problematica.pdf"
   ```
3. **Guarde a saida** (texto e erros)
4. **Abra uma issue** no GitHub com:
   - O PDF (ou descricao do formato)
   - A saida do script de teste
   - O que espera que aconteca
   - O que realmente acontece

---

## 🔧 Configuracao Avançada

### Aumentar limite de upload
Por padrao, o limite e 50MB. Para aumentar:

```python
# Em app_train_debug.py
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
```

### Mudar porta do servidor
```python
# Em app_train_debug.py
app.run(host='0.0.0.0', port=5003, debug=True)  # Porta 5003
```

### Ativar OCR por padrao
```python
# Em app_train_debug.py
extractor = PDFExtractor(use_ocr=True)  # Usar OCR
```

---

## 📝 Historico de Alteracoes

| Data | Alteracao | Autor |
|------|-----------|-------|
| 2024-XX-XX | Criacao inicial dos ficheiros de debug | Vibe Code |
| 2024-XX-XX | Adicionada comparacao de parsers | Vibe Code |
| 2024-XX-XX | Adicionada API de extracao | Vibe Code |

---

## 🎯 Resumo Rapido

| Ferramenta | Uso | Porta |
|-----------|-----|-------|
| `test_upload.py` | Teste rapido por linha de comandos | - |
| `app_train_debug.py` | Interface web de debug | 5002 |
| `app_train.py` | Interface web de treino | 5001 |
| `app_train_multi.py` | Interface web de treino multi-lingue | 5001 |
| `app_web.py` | Aplicacao web principal | 5000 |
