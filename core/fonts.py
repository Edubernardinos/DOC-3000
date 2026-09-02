# -*- coding: utf-8 -*-
"""
Módulo de Resolução e Manipulação de Fontes do Sistema
"""

import os
from .constants import FONTS_DIR, FAMILIAS_FONTES


def resolver_fonte(nome_familia, is_bold=False, is_italic=False):
    """Resolve o arquivo TTF apropriado dado o nome da família e flags de estilo."""
    if not nome_familia or nome_familia in ("auto", "Auto (Detectar)"):
        nome_familia = "Arial"
        
    variante = "regular"
    if is_bold and is_italic:
        variante = "bold_italic"
    elif is_bold:
        variante = "bold"
    elif is_italic:
        variante = "italic"
        
    fam_info = FAMILIAS_FONTES.get(nome_familia, FAMILIAS_FONTES["Arial"])
    arquivo = fam_info.get(variante, fam_info.get("regular", "arial.ttf"))
    
    if os.path.isabs(arquivo) and os.path.exists(arquivo):
        return arquivo
    
    caminho_win = os.path.join(FONTS_DIR, arquivo)
    if os.path.exists(caminho_win):
        return caminho_win
    
    caminho_regular = os.path.join(FONTS_DIR, fam_info.get("regular", "arial.ttf"))
    if os.path.exists(caminho_regular):
        return caminho_regular
        
    return arquivo
