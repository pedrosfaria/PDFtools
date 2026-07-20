# Guia de Instalação - Passo a Passo

Este guia explica como instalar todas as dependências necessárias para executar o sistema de extração de faturas de eletricidade.

## 📋 Requisitos do Sistema

- **Sistema Operativo**: Windows 10/11, macOS, ou Linux (Ubuntu, Debian, etc.)
- **Python**: Versão 3.8 ou superior
- **Espaço em disco**: Aproximadamente 500MB (para o Tesseract OCR)

---

## 🐍 Passo 1: Instalar Python

### Verificar se já tem Python instalado

Abra um terminal (ou Command Prompt no Windows) e execute:

```bash
python --version
# ou
python3 --version
```

Se vir algo como `Python 3.8.XX` ou superior, já tem Python instalado. Caso contrário, instale:

### Windows

1. Vá a [python.org/downloads](https://www.python.org/downloads/)
2. Desça até "Python 3.11.X" (ou a versão mais recente 3.8+)
3. Clique em "Download Python 3.11.X"
4. Execute o instalador
5. **IMPORTANTE**: Marque a opção "Add Python to PATH" durante a instalação
6. Clique em "Install Now"

### macOS

```bash
# Usando Homebrew (recomendado)
brew install python

# Ou baixar do site
# Vá a python.org e baixe o instalador para Mac
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

---

## 🌐 Passo 2: Criar um Ambiente Virtual (Recomendado)

Um ambiente virtual permite isolar as dependências do projeto do resto do seu sistema.

### Navegar até à pasta do projeto

```bash
cd /caminho/para/PDFtools
```

Substitua `/caminho/para/PDFtools` pelo caminho real onde guardou o projeto.

### Criar o ambiente virtual

#### Windows
```bash
python -m venv venv
```

#### macOS/Linux
```bash
python3 -m venv venv
```

Isto cria uma pasta chamada `venv` com todas as dependências isoladas.

### Ativar o ambiente virtual

#### Windows (Command Prompt)
```bash
venv\Scripts\activate
```

#### Windows (PowerShell)
```bash
.\venv\Scripts\Activate.ps1
```

#### macOS/Linux
```bash
source venv/bin/activate
```

**Sabe que o ambiente está ativo quando vir `(venv)` no início do prompt do terminal.**

---

## 📦 Passo 3: Instalar as Dependências Python

Com o ambiente virtual ativo, execute:

```bash
pip install -r requirements.txt
```

Isto instala as dependências básicas:
- `pdfplumber` - Para ler ficheiros PDF
- `pandas` - Para manipular dados tabulares
- `openpyxl` - Para criar ficheiros Excel
- `python-dotenv` - Para gerir variáveis de ambiente

### Verificar instalação

```bash
pip list
```

Deve ver algo como:
```
Package         Version
--------------  -------
openpyxl        3.1.2
pandas          2.1.4
pdfplumber      0.10.3
pip             23.3.1
python-dotenv   1.0.0
setuptools      68.2.2
```

---

## 🔍 Passo 4: Instalar Tesseract OCR (Opcional)

**Só é necessário se as suas faturas forem scans (imagens) em vez de PDFs com texto.**

Se as suas faturas são PDFs com texto (pode selecionar e copiar texto), **pode saltar este passo**.

### O que é Tesseract?

Tesseract é um motor de OCR (Optical Character Recognition) que permite extrair texto de imagens. É necessário para processar faturas que são scans (fotografias ou digitalizações).

### Instalação por Sistema Operativo

#### Windows

1. **Baixar o instalador**:
   - Vá a [UB Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
   - Desça até "Download" e baixe o instalador mais recente (ex: `tesseract-ocr-w64-setup-5.3.3.20231005.exe`)

2. **Executar o instalador**:
   - Execute o ficheiro .exe que baixou
   - Siga os passos do instalador
   - **IMPORTANTE**: Marque a opção para adicionar ao PATH

3. **Instalar linguagens**:
   - Abra o Command Prompt como administrador
   - Execute:
     ```bash
     tesseract --list-langs
     ```
   - Se não vir `por` e `eng`, instale-as:
     ```bash
     # Baixar pacote de linguagens
     # Pode ser necessário baixar manualmente de:
     # https://github.com/tesseract-ocr/tessdata
     ```

4. **Instalar pytesseract**:
   ```bash
   pip install pytesseract pillow
   ```

#### macOS

```bash
# Instalar Tesseract
brew install tesseract

# Instalar linguagens (Português e Inglês)
brew install tesseract-lang

# Instalar biblioteca Python
pip install pytesseract pillow
```

#### Linux (Ubuntu/Debian)

```bash
# Instalar Tesseract
sudo apt update
sudo apt install tesseract-ocr

# Instalar linguagens
sudo apt install tesseract-ocr-por tesseract-ocr-eng

# Instalar biblioteca Python
pip install pytesseract pillow
```

### Verificar instalação do Tesseract

```bash
tesseract --version
```

Deve ver algo como:
```
tesseract 5.3.3
 leptonica-1.83.1
  libgif 5.2.1 : libjpeg 8d (libjpeg-turbo 2.1.5) : libpng 1.6.39 : libtiff 4.5.1 : zlib 1.2.13 : libwebp 1.3.2 : libopenjp2 2.5.0
 Found AVX512BW
 Found AVX512CD
 Found AVX512ER
 Found AVX512F
 Found AVX512PF
 Found AVX2
 Found FMA
 Found SSE4.1
 Found SSE4.2
```

E para verificar as linguagens:

```bash
tesseract --list-langs
```

Deve ver:
```
List of available languages (4):
eng
osd
por
... (outros)
```

---

## 🧪 Passo 5: Testar a Instalação

### Testar com o script de exemplo

```bash
python example_usage.py
```

Isto executa os exemplos e mostra se tudo está a funcionar.

### Testar com uma fatura real

1. Coloque uma fatura PDF na pasta `data/input/`
2. Execute:

```bash
python main.py extract data/input/sua_fatura.pdf --format csv --output saida.csv
```

### Testar com OCR (se instalou Tesseract)

```bash
python main.py extract sua_fatura_scan.pdf --ocr --format csv --output saida.csv
```

---

## 📁 Passo 6: Processar Faturas da Coopérnico

### Se tem faturas em PDF

1. Coloque as faturas na pasta `data/input/` ou crie uma pasta própria:
   ```bash
   mkdir faturas_coopernico
   # Copie as faturas para esta pasta
   ```

2. Processar todas as faturas num diretório:
   ```bash
   python main.py directory faturas_coopernico/ --format excel --output faturas_coopernico.xlsx
   ```

3. Ou processar ficheiros individuais:
   ```bash
   python main.py extract fatura1.pdf fatura2.pdf fatura3.pdf --format csv --output resultado.csv
   ```

### Se tem faturas em papel (scans)

1. Digitalize as faturas e guarde como PDF
2. Use a opção `--ocr`:
   ```bash
   python main.py directory faturas_scans/ --ocr --format excel --output resultado.xlsx
   ```

---

## ❓ Resolução de Problemas

### Problema: "python: command not found"

**Solução**: Python não está instalado ou não está no PATH.
- Verifique se instalou Python corretamente
- No Windows, certifique-se que marcou "Add Python to PATH" durante a instalação

### Problema: "pip: command not found"

**Solução**:
- Tente `python -m pip` em vez de `pip`
- Ou `python3 -m pip` no macOS/Linux

### Problema: "No module named 'pdfplumber'"

**Solução**: O ambiente virtual não está ativo ou não instalou as dependências.
```bash
# Ativar ambiente virtual
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
```

### Problema: "Tesseract not found"

**Solução**: Tesseract não está instalado ou não está no PATH.
- Verifique se instalou o Tesseract corretamente
- No Windows, certifique-se que marcou "Add to PATH" durante a instalação
- Teste com: `tesseract --version`

### Problema: "pytesseract.pytesseract.TesseractNotFoundError"

**Solução**: A biblioteca pytesseract não consegue encontrar o Tesseract.

No Windows, pode precisar de especificar o caminho:
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

Ou no código, adicione ao `main.py` ou crie um ficheiro `config.py`:
```python
# No main.py, antes de usar OCR
import pytesseract
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Linux/macOS
# ou
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
```

---

## 📝 Resumo dos Comandos Importantes

| Ação | Comando |
|------|---------|
| Criar ambiente virtual | `python -m venv venv` |
| Ativar ambiente (Windows) | `venv\Scripts\activate` |
| Ativar ambiente (macOS/Linux) | `source venv/bin/activate` |
| Instalar dependências | `pip install -r requirements.txt` |
| Instalar Tesseract (macOS) | `brew install tesseract` |
| Instalar Tesseract (Linux) | `sudo apt install tesseract-ocr tesseract-ocr-por` |
| Processar uma fatura | `python main.py extract fatura.pdf` |
| Processar diretório | `python main.py directory ./faturas/` |
| Usar OCR | `python main.py extract fatura.pdf --ocr` |
| Exportar para Excel | `python main.py extract fatura.pdf --format excel` |

---

## 🎯 Próximos Passos

1. ✅ Instalar Python
2. ✅ Criar ambiente virtual
3. ✅ Instalar dependências Python
4. ✅ (Opcional) Instalar Tesseract OCR
5. ✅ Testar com uma fatura
6. 🔄 **Processar as suas faturas da Coopérnico!**

Se tiver problemas, por favor partilhe:
- O erro exato que está a receber
- O seu sistema operativo
- Se está a usar ambiente virtual

Estou aqui para ajudar! 🚀
