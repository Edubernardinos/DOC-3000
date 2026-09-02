# -*- coding: utf-8 -*-
"""
Pacote de Diálogos e Janelas Modais do DOC_EDITOR_3000
"""

from .forensics import JanelaAnaliseVeracidade
from .viewer import JanelaVisualizarResultado
from .options import JanelaOpcoes
from .metadata_dialog import JanelaMetadados

__all__ = [
    "JanelaAnaliseVeracidade",
    "JanelaVisualizarResultado",
    "JanelaOpcoes",
    "JanelaMetadados"
]
