# Guia Rápido para Faturas da Coopérnico

Este guia explica como processar faturas da **Coopérnico** usando o sistema de extração.

## 🚀 Começar em 5 Minutos

### Passo 1: Abrir o Terminal

- **Windows**: Prima `Win + R`, digite `cmd` e prima Enter
- **Mac**: Abra o Terminal (em Aplicações > Utilitários)
- **Linux**: Abra o Terminal (Ctrl+Alt+T)

### Passo 2: Navegar até à pasta do projeto

```bash
cd /caminho/para/PDFtools
```

Substitua `/caminho/para/PDFtools` pelo caminho real onde guardou o projeto.

Exemplo:
```bash
cd C:\Users\Joao\Documents\PDFtools
# ou
cd /Users/joao/Documents/PDFtools
# ou
cd ~/Documentos/PDFtools
```

### Passo 3: Criar ambiente virtual

```bash
python -m venv venv
```

### Passo 4: Ativar ambiente virtual

- **Windows**:
  ```bash
  venv\Scripts\activate
  ```

- **Mac/Linux**:
  ```bash
  source venv/bin/activate
  ```

Deve ver `(venv)` no início do prompt.

### Passo 5: Instalar dependências

```bash
pip install -r requirements.txt
```

### Passo 6: Testar com uma fatura de exemplo

```bash
python process_coopernico.py test
```

Isto mostra um exemplo de extração com dados da Coopérnico.

---

## 📁 Processar as Suas Faturas

### Opção A: Processar uma fatura individual

1. Coloque a sua fatura PDF na pasta do projeto ou num subdiretório
2. Execute:

```bash
python process_coopernico.py single sua_fatura.pdf
```

Isto cria um ficheiro `sua_fatura.csv` com os dados extraídos.

### Opção B: Processar todas as faturas numa pasta

1. Crie uma pasta para as faturas:
   ```bash
   mkdir faturas_coopernico
   ```

2. Copie todas as suas faturas PDF para esta pasta

3. Execute:
   ```bash
   python process_coopernico.py directory faturas_coopernico/
   ```

Isto cria um ficheiro `faturas_coopernico.csv` com todos os dados.

### Opção C: Exportar para Excel

```bash
python process_coopernico.py directory faturas_coopernico/ --format excel --output resultado.xlsx
```

---

## 📊 O que é Extraído das Faturas Coopérnico

O sistema extrai automaticamente os seguintes dados:

### 📄 Informações da Fatura
- Número da fatura
- Data de emissão
- Data de vencimento

### ⚡ Dados de Consumo
- Período de consumo (de/até)
- Consumo em kWh
- Potência contratada em kVA
- Preço por kWh

### 💰 Valores Monetários
- Custo da energia
- Custo de acesso à rede
- Taxa de IVA
- Valor do IVA
- **Total a pagar**

### 👤 Informações do Cliente
- Número do cliente/sócio
- Nome do cliente
- NIF
- Morada
- Código postal
- Localidade

### 📏 Informações do Contador
- Número do contador
- Leitura atual
- Leitura anterior
- Data da leitura

### 💳 Informações de Pagamento
- Método de pagamento
- Referência de pagamento

---

## 📝 Exemplos Práticos

### Exemplo 1: Processar uma fatura e obter CSV

```bash
python process_coopernico.py single fatura_jan2024.pdf
```

Resultado: `fatura_jan2024.csv`

### Exemplo 2: Processar todas as faturas e obter Excel

```bash
python process_coopernico.py directory ./faturas/ --format excel --output todas_faturas.xlsx
```

Resultado: `todas_faturas.xlsx` (pronto para abrir no Excel)

### Exemplo 3: Processar faturas com OCR (se forem scans)

Se as suas faturas são scans (imagens), use a opção `--ocr`:

```bash
python process_coopernico.py directory ./scans/ --ocr --format csv --output scans.csv
```

> ⚠️ **Nota**: Para usar OCR, precisa de instalar o Tesseract. Veja o guia em [INSTALL.md](INSTALL.md).

---

## 🎯 Dicas para Melhorar os Resultados

### 1. Qualidade dos PDFs

- **Melhor**: PDFs com texto (pode selecionar e copiar texto)
- **Bom**: PDFs com boa qualidade de imagem
- **Problema**: PDFs com baixa resolução ou texto muito pequeno

### 2. Organizar as Faturas

Crie uma estrutura como esta:
```
PDFtools/
├── faturas_coopernico/
│   ├── 2024/
│   │   ├── janeiro.pdf
│   │   ├── fevereiro.pdf
│   │   └── ...
│   └── 2023/
│       ├── janeiro.pdf
│       └── ...
└── saida/
    ├── 2024.csv
    └── 2023.csv
```

### 3. Processar por Ano

```bash
# Processar faturas de 2024
python process_coopernico.py directory faturas_coopernico/2024/ --format csv --output saida/2024.csv

# Processar faturas de 2023
python process_coopernico.py directory faturas_coopernico/2023/ --format csv --output saida/2023.csv
```

---

## ❓ Resolução de Problemas Comuns

### Problema: "Ficheiro não encontrado"

**Causa**: O caminho para o ficheiro está errado.

**Solução**:
- Verifique se o ficheiro existe
- Use o caminho completo:
  ```bash
  python process_coopernico.py single C:\Users\Joao\faturas\fatura.pdf
  ```

### Problema: "Não foi possível detetar o fornecedor"

**Causa**: A fatura pode ter um formato diferente.

**Solução**:
- Verifique se a fatura é realmente da Coopérnico
- Abra o PDF e confirme que tem "Coopérnico" ou "Cooperativa de Energia"
- Se for um scan, use a opção `--ocr`

### Problema: "Dados em falta"

**Causa**: O formato da fatura pode ser diferente do esperado.

**Solução**:
- Abra o ficheiro CSV/Excel gerado e verifique o que foi extraído
- Se algum campo importante está em falta, pode ser necessário ajustar o parser
- Contacte-me com um exemplo da fatura para eu ajustar o código

### Problema: "Tesseract not found" (ao usar --ocr)

**Causa**: O Tesseract OCR não está instalado.

**Solução**:
- Instale o Tesseract seguindo as instruções em [INSTALL.md](INSTALL.md)
- Ou não use a opção `--ocr` se as faturas já têm texto

---

## 📊 O que Fazer com os Dados Extraídos

### 1. Abrir no Excel

Simplesmente abra o ficheiro `.csv` ou `.xlsx` no Excel:
- Dados organizados em colunas
- Fácil de filtrar, ordenar e analisar

### 2. Importar para o Google Sheets

1. Vá a [sheets.google.com](https://sheets.google.com)
2. Crie uma nova folha
3. Clique em "Ficheiro > Importar"
4. Selecione o ficheiro CSV
5. Escolha "Substituir folha de cálculo"

### 3. Analisar os Dados

Pode criar gráficos de:
- Evolução do consumo ao longo do tempo
- Custo médio por kWh
- Comparação entre meses/anos

### 4. Integração com Outras Aplicações

Os ficheiros CSV/Excel podem ser importados para:
- Contabilidade (Sage, PHC, etc.)
- Aplicações de gestão
- Bases de dados
- Sistemas de business intelligence

---

## 🔧 Personalização

### Adicionar Campos Específicos

Se precisar de extrair campos adicionais das faturas da Coopérnico, pode modificar o parser:

1. Abra o ficheiro: `pdf_extractor/parsers/coopernico_parser.py`
2. Adicione novos métodos de extração
3. Atualize o método `parse()` para incluir os novos campos

### Exemplo: Extrair campo personalizado

```python
# No coopernico_parser.py
def _extract_custom_field(self, text: str) -> Optional[str]:
    """Extrair um campo personalizado."""
    pattern = r"Campo\s*Personalizado\s*:?\s*([A-Za-z0-9\s]+)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

# No método parse()
data["custom_field"] = self._extract_custom_field(text)
```

---

## 📞 Suporte

Se tiver problemas ou dúvidas:

1. **Verifique o guia de instalação**: [INSTALL.md](INSTALL.md)
2. **Teste com o exemplo**: `python process_coopernico.py test`
3. **Verifique o log**: O sistema cria um ficheiro `pdf_extractor.log` com detalhes

Se o problema persistir, por favor forneça:
- O erro exato que está a receber
- O tipo de ficheiro (PDF com texto ou scan)
- Uma amostra da fatura (se possível)

---

## 🎉 Pronto!

Agora já pode processar todas as suas faturas da Coopérnico automaticamente! 🚀

**Resumo dos comandos mais úteis:**

| Ação | Comando |
|------|---------|
| Testar | `python process_coopernico.py test` |
| Processar uma fatura | `python process_coopernico.py single fatura.pdf` |
| Processar pasta | `python process_coopernico.py directory ./faturas/` |
| Exportar para Excel | `python process_coopernico.py directory ./faturas/ --format excel` |
| Usar OCR | `python process_coopernico.py single fatura.pdf --ocr` |

Boa sorte com a extração dos seus dados! 💡
