# -*- coding: utf-8 -*-
"""
Pacote de Interface Gráfica do DOC_EDITOR_3000
"""

from .main_window import App
from .themes import aplicar_tema_app
from .dialogs import (
    JanelaAnaliseVeracidade,
    JanelaVisualizarResultado,
    JanelaOpcoes,
    JanelaMetadados
)

__all__ = [
    "App",
    "aplicar_tema_app",
    "JanelaAnaliseVeracidade",
    "JanelaVisualizarResultado",
    "JanelaOpcoes",
    "JanelaMetadados"
]
