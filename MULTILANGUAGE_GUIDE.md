# Guia: Sistema Multi-Lingue

O PDF Invoice Extractor agora suporta **múltiplos idiomas** para a interface de utilizador!

## 🌍 Idiomas Suportados

| Código | Idioma | Estado |
|--------|--------|--------|
| `pt` | Português | ✅ Completo |
| `en` | English | ✅ Completo |
| `es` | Español | ✅ Completo |
| `fr` | Français | ✅ Completo |

---

## 🚀 Como Usar

### Mudar de Idioma

1. **Na interface web**, clique no seletor de idioma no canto superior direito
2. **Selecione o idioma** que prefere (Português, English, Español, Français)
3. **A interface muda automaticamente** para o idioma selecionado

### Atalhos

- **Português**: `/set_language/pt`
- **English**: `/set_language/en`
- **Español**: `/set_language/es`
- **Français**: `/set_language/fr`

---

## 📁 Estrutura dos Ficheiros de Tradução

```
translations/
├── __init__.py           # Sistema de tradução
├── compile_translations.py  # Script para compilar .po -> .mo (alternativo)
├── build_translations.py  # Script para compilar com polib
└── locales/              # Ficheiros de tradução
    ├── en/               # Inglês
    │   └── LC_MESSAGES/
    │       ├── messages.po  # Ficheiro fonte
    │       └── messages.mo  # Ficheiro compilado
    ├── pt/               # Português
    │   └── LC_MESSAGES/
    │       ├── messages.po
    │       └── messages.mo
    ├── es/               # Espanhol
    │   └── LC_MESSAGES/
    │       ├── messages.po
    │       └── messages.mo
    └── fr/               # Francês
        └── LC_MESSAGES/
            ├── messages.po
            └── messages.mo
```

---

## 🔧 Como Adicionar um Novo Idioma

### Passo 1: Criar a Estrutura de Diretórios

```bash
mkdir -p translations/locales/<lang>/LC_MESSAGES
```

Substitua `<lang>` pelo código do idioma (ex: `de` para Alemão, `it` para Italiano).

### Passo 2: Criar o Ficheiro .po

1. Copie um ficheiro .po existente como template:
```bash
cp translations/locales/en/LC_MESSAGES/messages.po translations/locales/<lang>/LC_MESSAGES/messages.po
```

2. Edite o ficheiro e traduza todas as strings:
```po
msgid "Upload"
msgstr "<sua traducao>"
```

3. Atualize o cabeçalho do ficheiro:
```po
"Language: <lang>\n"
"Language-Team: <Nome da equipa>\n"
```

### Passo 3: Adicionar ao Sistema

1. Adicione o idioma ao dicionário `SUPPORTED_LANGUAGES` em `translations/__init__.py`:
```python
SUPPORTED_LANGUAGES = {
    'pt': 'Portugues',
    'en': 'English',
    'es': 'Espanol',
    'fr': 'Francais',
    '<lang>': '<Nome do Idioma>',  # Adicione aqui
}
```

### Passo 4: Compilar as Traduções

Execute:
```bash
python translations/build_translations.py
```

Isto cria os ficheiros .mo a partir dos .po.

### Passo 5: Testar

Inicie a aplicação e mude para o novo idioma:
```bash
python app_train_multi.py
```

---

## 📝 Formato dos Ficheiros .po

Os ficheiros .po seguem o formato padrão do gettext:

```po
msgid ""
msgstr ""
"Project-Id-Version: PDF Invoice Extractor 1.0\n"
"Language: pt\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"

# Comentário (opcional)
msgid "Hello"
msgstr "Ola"

# Com plural
msgid "One file"
msgid_plural "%d files"
msgstr[0] "Um ficheiro"
msgstr[1] "%d ficheiros"
```

### Regras Importantes:

1. **msgid** - A string original em Inglês (ou a string de referência)
2. **msgstr** - A tradução para o idioma
3. **Comentários** - Iniciam com `#`
4. **Strings vazias** - O cabeçalho deve ter msgid e msgstr vazios

---

## 🔄 Atualizar Traduções Existentes

### Adicionar Novas Strings

1. Adicione a nova string ao ficheiro `messages.po` em Inglês:
```po
msgid "New Feature"
msgstr "New Feature"
```

2. Traduza para os outros idiomas:
```po
# Em pt/LC_MESSAGES/messages.po
msgid "New Feature"
msgstr "Nova Funcionalidade"

# Em es/LC_MESSAGES/messages.po
msgid "New Feature"
msgstr "Nueva Funcionalidad"
```

3. Compile as traduções:
```bash
python translations/build_translations.py
```

### Ferramentas Úteis

#### Extrair Strings do Código

Para extrair todas as strings do código Python:

```bash
# Instalar xgettext (faz parte do gettext)
# No Ubuntu: sudo apt install gettext
# No Mac: brew install gettext

# Extrair strings
xgettext --output=messages.pot --keyword=_ --keyword=ngettext:1,2 -L Python *.py
```

#### Atualizar Ficheiros .po

```bash
# Atualizar um ficheiro .po com novas strings do .pot
msgmerge --update translations/locales/pt/LC_MESSAGES/messages.po messages.pot
```

---

## 💡 Dicas para Tradutores

### 1. Mantenha a Formatação
- Não mude a formatação das strings (ex: `{variable}` deve manter-se)
- Mantenha os mesmos placeholders

### 2. Teste as Traduções
- Depois de traduzir, teste a interface para verificar que tudo cabe
- Algumas strings podem ser longas e não caber no design

### 3. Contextualize
- Pense no contexto onde a string aparece
- Algumas palavras podem ter múltiplos significados

### 4. Consistência
- Use a mesma tradução para a mesma palavra em todo o ficheiro
- Mantenha consistência com outras aplicações

---

## 📊 Strings Traduzidas

Atualmente, os seguintes tipos de strings estão traduzidos:

### Interface
- Nomes das páginas (Início, Carregar, Treinar, Testar, Sobre)
- Títulos e descrições

### Mensagens
- Mensagens de sucesso, erro, aviso
- Mensagens de confirmação

### Campos de Faturas
- Todos os campos de faturas (Nº Fatura, Data Emissão, etc.)
- Tipos de dados (texto, número, data, valor)

### Fornecedores
- Nomes dos fornecedores (EDP, Galp, Ibersol, Coopérnico)

### Botões e Ações
- Todos os botões da interface
- Todas as ações disponíveis

### Dicas e Estatísticas
- Dicas para o utilizador
- Estatísticas de treino

---

## ❓ Perguntas Frequentes

### Q: Como sei que idioma está ativo?
**R:** O idioma ativo é guardado na sessão. Pode ver no canto superior direito da interface.

### Q: Posso mudar de idioma sem reiniciar a aplicação?
**R:** Sim! Basta clicar no seletor de idioma e a interface muda automaticamente.

### Q: O que acontece se um texto não estiver traduzido?
**R:** Se um texto não tiver tradução, é mostrado o texto original (em Inglês).

### Q: Como adiciono um novo idioma?
**R:** Siga os passos na secção "Como Adicionar um Novo Idioma" acima.

### Q: Os ficheiros .mo são necessários?
**R:** Sim, os ficheiros .mo são a versão compilada que o gettext usa. São mais rápidos de carregar.

### Q: Posso editar os ficheiros .mo diretamente?
**R:** Não recomendado. Edite os ficheiros .po e depois compile para .mo.

---

## 🎯 Boas Práticas

1. **Teste sempre** as traduções antes de fazer commit
2. **Mantenha os ficheiros .po atualizados** com as últimas strings
3. **Use ferramentas** como Poedit para editar ficheiros .po
4. **Documente** as traduções com comentários quando necessário
5. **Mantenha consistência** entre os diferentes idiomas

---

## 📚 Recursos Úteis

- [Gettext Documentation](https://docs.python.org/3/library/gettext.html)
- [Poedit](https://poedit.net/) - Editor de ficheiros .po
- [Transifex](https://www.transifex.com/) - Plataforma de tradução colaborativa
- [Crowdin](https://crowdin.com/) - Outra plataforma de tradução

---

## 🚀 Próximos Passos

1. ✅ **Testar os idiomas existentes** (pt, en, es, fr)
2. ✅ **Adicionar mais idiomas** se necessário
3. ✅ **Atualizar traduções** quando adicionar novas funcionalidades
4. ✅ **Manter consistência** entre todos os idiomas

O sistema multi-língue está pronto a usar! 🌍
