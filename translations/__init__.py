"""
Sistema de traducao multi-lingue para o PDF Invoice Extractor.

Suporta:
- Portugues (pt)
- Ingles (en)
- Espanhol (es)
- Frances (fr)

Uso:
    from translations import gettext as _
    print(_("Hello"))  # Imprime "Ola" se o idioma for pt
"""

import gettext as gettext_module
import os
from pathlib import Path

# Diretorio das traducoes
LOCALE_DIR = Path(__file__).parent / 'locales'

# Idiomas suportados
SUPPORTED_LANGUAGES = {
    'pt': 'Portugues',
    'en': 'English',
    'es': 'Espanol',
    'fr': 'Francais'
}

# Idioma padrao
DEFAULT_LANGUAGE = 'pt'

# Variavel global para o idioma atual
_current_language = DEFAULT_LANGUAGE
_current_translation = None


def set_language(lang: str):
    """
    Definir o idioma atual.
    
    Args:
        lang: Codigo do idioma (ex: 'pt', 'en', 'es', 'fr')
    """
    global _current_language, _current_translation
    
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
    
    _current_language = lang
    
    try:
        # Tentar carregar traducao
        translation = gettext_module.translation(
            'messages',
            localedir=str(LOCALE_DIR),
            languages=[lang],
            fallback=True
        )
        _current_translation = translation
    except Exception:
        # Se nao encontrar traducao, usar gettext nulo
        _current_translation = gettext_module.NullTranslations()


def get_language() -> str:
    """Obter o idioma atual."""
    return _current_language


def gettext(text: str) -> str:
    """
    Traduzir texto para o idioma atual.
    
    Args:
        text: Texto a traduzir
        
    Returns:
        Texto traduzido
    """
    global _current_translation
    
    if _current_translation is None:
        set_language(_current_language)
    
    return _current_translation.gettext(text)


def ngettext(singular: str, plural: str, n: int) -> str:
    """
    Traduzir texto com plural.
    
    Args:
        singular: Forma singular
        plural: Forma plural
        n: Numero
        
    Returns:
        Texto traduzido
    """
    global _current_translation
    
    if _current_translation is None:
        set_language(_current_language)
    
    return _current_translation.ngettext(singular, plural, n)


# Inicializar com idioma padrao
set_language(DEFAULT_LANGUAGE)

# Funcoes de conveniencia
_ = gettext
n_ = ngettext
