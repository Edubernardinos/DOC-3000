# -*- coding: utf-8 -*-
"""
Pacote Core do DOC_EDITOR_3000
"""

from .constants import FONTS_DIR, FAMILIAS_FONTES
from .fonts import resolver_fonte
from .metadata import (
    aplicar_metadados_e_tamanho_reais,
    salvar_com_exif,
    obter_nome_tag_exif
)
from .image_processing import (
    pdf_para_imagem,
    carregar_documento,
    obter_reader,
    detectar_texto,
    dividir_em_palavras,
    substituir_texto,
    processar_foto_sobreposta,
    _desenhar_grade_na_imagem
)

__all__ = [
    "FONTS_DIR",
    "FAMILIAS_FONTES",
    "resolver_fonte",
    "aplicar_metadados_e_tamanho_reais",
    "salvar_com_exif",
    "obter_nome_tag_exif",
    "pdf_para_imagem",
    "carregar_documento",
    "obter_reader",
    "detectar_texto",
    "dividir_em_palavras",
    "substituir_texto",
    "processar_foto_sobreposta",
    "_desenhar_grade_na_imagem"
]
