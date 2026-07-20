# Guia: Criar Aplicação Web Executável para Windows

Este guia explica como transformar o sistema de extração de faturas numa **aplicação web executável** que pode ser executada no Windows com um simples duplo clique, usando o browser como interface.

## 🎯 Solução Recomendada: Flask + PyInstaller

Vamos usar:
- **Flask**: Framework web leve para criar a interface
- **PyInstaller**: Para criar o executável .exe
- **Browser**: A interface será acessível via `http://localhost:5000`

---

## 📋 Arquitetura da Solução

```
PDFtools/
├── app_web.py              # Aplicação Flask (servidor web)
├── templates/              # Páginas HTML (interface)
│   ├── base.html           # Template base
│   ├── index.html          # Página inicial
│   ├── upload.html         # Página de upload
│   ├── results.html        # Página de resultados
│   └── about.html          # Página sobre
├── static/                 # CSS, JS, imagens
│   └── style.css           # Estilos personalizados
├── build_exe.py            # Script para criar executável
├── requirements_web.txt    # Dependências para versão web
├── pdf_extractor/          # (já existe) - Lógica de extração
└── dist/                   # (gerado) - Executável .exe
```

---

## 🚀 Passo a Passo para Criar o Executável

### Passo 1: Instalar Dependências Adicionais

```bash
# Ativar ambiente virtual (se não estiver ativo)
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# Instalar dependências para a versão web
pip install -r requirements_web.txt
```

### Passo 2: Testar a Aplicação Web

Antes de criar o executável, teste a aplicação web para garantir que tudo funciona:

```bash
python app_web.py
```

Abra o browser e vá para: **http://localhost:5000**

Deve ver a interface web com:
- Página inicial com opções
- Página de upload de ficheiros
- Página de resultados
- Página sobre

**Teste o upload de uma fatura** para confirmar que tudo funciona.

Para parar o servidor: `Ctrl + C`

### Passo 3: Criar o Executável

Execute o script de build:

```bash
python build_exe.py
```

Isto vai:
1. Verificar se o PyInstaller está instalado
2. Criar o executável na pasta `dist/`
3. Incluir todos os ficheiros necessários (templates, static, etc.)

### Passo 4: Verificar o Executável

Após o build, verifique a pasta `dist/`:
```
PDFtools/
└── dist/
    └── PDF_Invoice_Extractor.exe  # O executável
```

---

## 🎉 Como Usar o Executável

### No Windows:

1. **Navegue até à pasta `dist/`**
2. **Faça duplo clique em `PDF_Invoice_Extractor.exe`**
3. **Aguarde alguns segundos** (o servidor web está a iniciar)
4. **O browser deve abrir automaticamente** em `http://localhost:5000`

Se o browser não abrir automaticamente, abra manualmente e vá para `http://localhost:5000`

### Funcionalidades da Interface Web:

| Página | Descrição |
|-------|-----------|
| **Início** | Visão geral do sistema e fornecedores suportados |
| **Upload** | Carregar ficheiros PDF para processar |
| **Resultados** | Ver dados extraídos e exportar |
| **Teste** | Testar com dados de exemplo |
| **Sobre** | Informações sobre o sistema |

---

## 📦 Distribuir a Aplicação

Para distribuir a aplicação para outros utilizadores:

1. **Crie uma pasta ZIP** com o conteúdo da pasta `dist/`:
   ```bash
   # No Windows (usando PowerShell):
   Compress-Archive -Path dist\* -DestinationPath PDF_Invoice_Extractor.zip
   
   # Ou manualmente:
   # - Selecione todos os ficheiros na pasta dist/
   # - Clique com o botão direito e selecione "Enviar para > Pasta compactada"
   ```

2. **Partilhe o ficheiro ZIP** com os utilizadores

3. **Instruções para os utilizadores**:
   - Descompactar o ZIP
   - Executar `PDF_Invoice_Extractor.exe`
   - A interface web abre automaticamente no browser

---

## ⚙️ Personalização

### Mudar o Nome do Executável

Edite o ficheiro `build_exe.py` e mude a variável:
```python
EXE_NAME = 'PDF_Invoice_Extractor'
```

### Adicionar um Ícone

1. Crie um ficheiro `.ico` (ícone do Windows)
2. Coloque-o na pasta raiz do projeto
3. Em `build_exe.py`, descomente e mude:
```python
ICON_FILE = 'icon.ico'  # ou o nome do seu ficheiro
```

### Mudar a Porta do Servidor

Em `app_web.py`, mude a última linha:
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```
Para:
```python
app.run(host='0.0.0.0', port=8080, debug=True)  # ou outra porta
```

---

## 🔧 Resolução de Problemas

### Problema: "PyInstaller not found"

**Solução**: Instale o PyInstaller:
```bash
pip install pyinstaller
```

### Problema: "ModuleNotFoundError: No module named 'flask'"

**Solução**: Instale as dependências:
```bash
pip install -r requirements_web.txt
```

### Problema: O executável é muito grande

**Causa**: O PyInstaller empacota todas as dependências, incluindo o Python.

**Solução**: Isto é normal. O executável tem cerca de 50-100MB.

### Problema: O executável não abre o browser automaticamente

**Solução**: O utilizador tem de abrir manualmente o browser e ir para `http://localhost:5000`

Para abrir automaticamente, pode modificar `app_web.py`:
```python
import webbrowser

if __name__ == '__main__':
    # ... código existente ...
    
    # Abrir browser automaticamente
    webbrowser.open('http://localhost:5000')
    
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### Problema: O servidor demora a iniciar

**Causa**: O PyInstaller demora a extrair os ficheiros na primeira execução.

**Solução**: Isto é normal. Na primeira execução, o executável demora alguns segundos a extrair os ficheiros temporários.

### Problema: "Failed to execute script app_web"

**Causa**: Pode ser falta de dependências ou problema com o PyInstaller.

**Solução**:
1. Verifique que todas as dependências estão instaladas
2. Tente criar o executável novamente
3. Verifique o log de erros

---

## 📊 Alternativas ao PyInstaller

### 1. Auto PY to EXE

[Auto PY to EXE](https://pypi.org/project/auto-py-to-exe/) é uma interface gráfica para o PyInstaller.

**Vantagens**:
- Interface gráfica fácil de usar
- Não precisa de saber comandos

**Desvantagens**:
- Menos controle sobre as opções

### 2. cx_Freeze

[cx_Freeze](https://cx-freeze.readthedocs.io/) é outra opção para criar executáveis.

**Vantagens**:
- Suporta múltiplas plataformas
- Boa documentação

**Desvantagens**:
- Configuração mais complexa

### 3. Nuitka

[Nuitka](https://nuitka.net/) compila Python para código nativo.

**Vantagens**:
- Melhor performance
- Executáveis mais rápidos

**Desvantagens**:
- Processo de build mais lento
- Configuração complexa

---

## 🌐 Alternativa: Usar Web2Py

Como mencionou o **web2py**, aqui está como o poderia usar:

### Passo 1: Instalar web2py

```bash
pip install web2py
```

### Passo 2: Criar uma aplicação web2py

1. Crie uma pasta para a aplicação:
```bash
mkdir web2py_app
cd web2py_app
```

2. Inicie o web2py:
```bash
python -m web2py
```

3. Crie uma nova aplicação no interface web do web2py

4. Adicione o código do extrator de PDFs

**Vantagens do web2py**:
- Framework completo com ORM, autenticação, etc.
- Fácil de deployar
- Não precisa de criar executável (acede-se via browser)

**Desvantagens**:
- Mais complexo para um projeto simples
- Requer mais configuração

---

## 🎯 Comparação das Opções

| Opção | Complexidade | Executável | Interface Web | Dependências |
|-------|-------------|------------|---------------|--------------|
| **Flask + PyInstaller** | ⭐⭐ | ✅ Sim | ✅ Sim | ⭐⭐ |
| **web2py** | ⭐⭐⭐ | ❌ Não | ✅ Sim | ⭐⭐⭐ |
| **Django + PyInstaller** | ⭐⭐⭐⭐ | ✅ Sim | ✅ Sim | ⭐⭐⭐⭐ |
| **FastAPI + PyInstaller** | ⭐⭐ | ✅ Sim | ✅ Sim | ⭐⭐ |

**Recomendação**: **Flask + PyInstaller** é a melhor opção para o seu caso.

---

## 📝 Resumo dos Comandos

| Ação | Comando |
|------|---------|
| Instalar dependências | `pip install -r requirements_web.txt` |
| Testar aplicação web | `python app_web.py` |
| Criar executável | `python build_exe.py` |
| Executar | Duplo clique em `dist/PDF_Invoice_Extractor.exe` |

---

## 🎉 Conclusão

Agora tem tudo o que precisa para:

1. ✅ **Criar uma aplicação web** com Flask
2. ✅ **Testar localmente** em `http://localhost:5000`
3. ✅ **Criar um executável** para Windows
4. ✅ **Distribuir** para outros utilizadores

A aplicação web permite:
- Upload de ficheiros PDF via browser
- Processamento automático
- Visualização dos resultados
- Exportação para CSV, Excel ou JSON
- Interface intuitiva e moderna

**Próximos passos:**
1. Instale as dependências: `pip install -r requirements_web.txt`
2. Teste a aplicação: `python app_web.py`
3. Crie o executável: `python build_exe.py`
4. Distribua o executável na pasta `dist/`

Se tiver dúvidas ou problemas, não hesite em perguntar! 🚀
