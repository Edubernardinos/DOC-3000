# -*- coding: utf-8 -*-
"""
DOC_EDITOR_3000 - Editor de Documentos & Fotos (Ponto de Entrada Principal)
--------------------------------------------------------------------------
Arquitetura Modular:
- core/: Processamento de imagem, OCR, tipografia, filtros e metadados reais
- ui/: Interface gráfica moderna, temas, canvas responsivo e janelas modais

Compatível com execução direta, scripts .bat, .vbs e compilação PyInstaller.
"""

from core.constants import FONTS_DIR, FAMILIAS_FONTES
from core.fonts import resolver_fonte
from core.metadata import (
    aplicar_metadados_e_tamanho_reais,
    salvar_com_exif,
    obter_nome_tag_exif
)
from core.image_processing import (
    pdf_para_imagem,
    carregar_documento,
    obter_reader,
    detectar_texto,
    dividir_em_palavras,
    substituir_texto,
    processar_foto_sobreposta,
    _desenhar_grade_na_imagem
)
from ui.main_window import App
from ui.dialogs import (
    JanelaAnaliseVeracidade,
    JanelaVisualizarResultado,
    JanelaOpcoes,
    JanelaMetadados
)


def main():
    """Função de inicialização do aplicativo."""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
