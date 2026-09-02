# -*- coding: utf-8 -*-
"""
Janela Principal da Aplicação DOC_EDITOR_3000
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from datetime import datetime
from PIL import Image, ImageDraw, ImageTk, ImageFont
import numpy as np

from core.constants import FAMILIAS_FONTES
from core.metadata import aplicar_metadados_e_tamanho_reais
from core.image_processing import (
    carregar_documento,
    substituir_texto,
    processar_foto_sobreposta,
    _desenhar_grade_na_imagem
)
from .canvas_handler import CanvasHandlerMixin
from .dialogs import (
    JanelaAnaliseVeracidade,
    JanelaVisualizarResultado,
    JanelaOpcoes,
    JanelaMetadados
)
from .themes import aplicar_tema_app


class App(tk.Tk, CanvasHandlerMixin):
    def __init__(self):
        super().__init__()
        self.title("DOC_EDITOR_3000 - Editor Profissional de Documentos & Fotos")
        self.geometry("1460x950")
        try:
            self.state("zoomed")
        except Exception:
            pass
        
        # Carrega o ícone oficial se disponível
        if os.path.exists("app_icon.ico"):
            try:
                self.iconbitmap("app_icon.ico")
            except Exception:
                pass

        self.img_original = None
        self.img_atual = None
        self.caixas = []
        self.selecionada = None
        
        # Foto sobreposta (3x4)
        self.foto_original = None
        self.foto_ativa = False
        
        # Manipulação direta por alças / handles
        self.modo_arraste = None
        self.handle_hover = None
        self.foto_drag_start = (0, 0)
        self.foto_box_inicial = (0, 0, 0, 0)

        self.escala = 1.0
        self.fator_zoom_manual = 1.0
        self.tk_img = None
        self.tk_preview_img = None
        self._tk_lupa = None
        self.drag_start = None
        self.drag_moved = False
        self.rect_id = None
        self._preview_job = None
        self.modo_pipeta = False
        self.modo_lupa = False

        self.caminho_documento = None
        self.meta_criado_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        self.meta_mod_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        self.meta_autor_var = tk.StringVar(value="")
        self.meta_titulo_var = tk.StringVar(value="")
        self.meta_tamanho_var = tk.StringVar(value="0")
        self.meta_largura_px_var = tk.StringVar(value="")
        self.meta_altura_px_var = tk.StringVar(value="")
        self.meta_aplicar_ntfs = tk.BooleanVar(value=True)

        self.dock_visivel = True
        self.log_visivel = True
        self.tema_atual = "claro"

        self._criar_menu_opcoes()
        self._montar_ui()
        self.aplicar_tema("claro")
        self.atualizar_estado_edicao_texto()

    def _montar_ui(self):
        top = ttk.Frame(self, padding=(4, 2))
        top.pack(side=tk.TOP, fill=tk.X)

        frame_arq = ttk.LabelFrame(top, text=" Painel ", padding=(4, 2))
        frame_arq.pack(side=tk.LEFT, padx=(2, 4), fill=tk.Y)

        # 1. Abrir e Salvar (50% / 50%)
        f_btns_top = ttk.Frame(frame_arq)
        f_btns_top.pack(side=tk.TOP, fill=tk.X, pady=1)
        tk.Button(f_btns_top, text="Abrir", font=("Segoe UI", 8, "bold"), bg="#3b82f6", fg="white",
                  activebackground="#2563eb", relief=tk.FLAT, cursor="hand2", command=self.abrir).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        tk.Button(f_btns_top, text="Salvar", font=("Segoe UI", 8, "bold"), bg="#10b981", fg="white",
                  activebackground="#059669", relief=tk.FLAT, cursor="hand2", command=self.salvar).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)

        # 2. Zoom e Comparador
        f_zm = ttk.Frame(frame_arq)
        f_zm.pack(side=tk.TOP, fill=tk.X, pady=1)
        ttk.Button(f_zm, text="-", width=3, command=self.zoom_out_doc).pack(side=tk.LEFT, padx=1)
        ttk.Button(f_zm, text="100%", width=4, command=self.zoom_100_doc).pack(side=tk.LEFT, padx=1)
        ttk.Button(f_zm, text="+", width=3, command=self.zoom_in_doc).pack(side=tk.LEFT, padx=1)
        self.btn_toggle_dock = tk.Button(f_zm, text="Comparador (On)", font=("Segoe UI", 8, "bold"), bg="#2563eb", fg="white",
                                         relief=tk.FLAT, cursor="hand2", command=self.toggle_dock_comparador)
        self.btn_toggle_dock.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)

        # 3. Forense, Metadados e Opções (33% cada)
        f_ferramentas = ttk.Frame(frame_arq)
        f_ferramentas.pack(side=tk.TOP, fill=tk.X, pady=1)
        tk.Button(f_ferramentas, text="Forense", font=("Segoe UI", 8, "bold"), bg="#0284c7", fg="white",
                  activebackground="#0369a1", relief=tk.FLAT, cursor="hand2", command=self.abrir_analise_veracidade).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        tk.Button(f_ferramentas, text="Metadados", font=("Segoe UI", 8, "bold"), bg="#059669", fg="white",
                  activebackground="#047857", relief=tk.FLAT, cursor="hand2", command=self.abrir_janela_metadados).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        tk.Button(f_ferramentas, text="Opções", font=("Segoe UI", 8, "bold"), bg="#4b5563", fg="white",
                  activebackground="#374151", relief=tk.FLAT, cursor="hand2", command=self.abrir_janela_opcoes).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)

        # 4. Lupa HUD (10x)
        self.btn_lupa = tk.Button(
            frame_arq, text="Lupa HUD (10x)", font=("Segoe UI", 8, "bold"),
            bg="#f3f4f6", fg="#1f2937", activebackground="#e5e7eb", relief=tk.RAISED, borderwidth=1, cursor="hand2", command=self.toggle_lupa
        )
        self.btn_lupa.pack(side=tk.TOP, fill=tk.X, pady=1)

        # 5. Histórico e Limpar (50% / 50%)
        f_baixo_arq = ttk.Frame(frame_arq)
        f_baixo_arq.pack(side=tk.TOP, fill=tk.X, pady=1)
        self.btn_toggle_log = tk.Button(f_baixo_arq, text="Histórico", font=("Segoe UI", 8, "bold"), bg="#4b5563", fg="white",
                                        activebackground="#374151", relief=tk.FLAT, cursor="hand2", command=self.toggle_painel_log)
        self.btn_toggle_log.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        tk.Button(f_baixo_arq, text="Limpar", font=("Segoe UI", 8, "bold"), bg="#dc2626", fg="white",
                  activebackground="#b91c1c", relief=tk.FLAT, cursor="hand2", command=self.limpar_tudo).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)

        self.notebook = ttk.Notebook(top)
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_mudou)
        self.notebook.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        # ==========================================
        # ABA 1: EDIÇÃO DE TEXTO
        # ==========================================
        tab_texto = ttk.Frame(self.notebook, padding=(4, 2))
        self.notebook.add(tab_texto, text=" 1. Editar Texto (OCR / Substituição) ")

        self.tab_texto = tab_texto
        # Escudo transparente que intercepta qualquer clique enquanto desativado
        self.escudo_clique = tk.Frame(tab_texto, cursor="no")
        self.escudo_clique.bind("<Button-1>", lambda e: self._clicou_quando_desativado())

        # Linha 1 da aba de texto: Busca, Substituição e Ações
        l1 = ttk.Frame(tab_texto)
        l1.pack(fill=tk.X, pady=(1, 2))

        ttk.Label(l1, text="Buscar:").pack(side=tk.LEFT, padx=(0, 2))
        self.busca = ttk.Entry(l1, width=12)
        self.busca.pack(side=tk.LEFT, padx=(0, 6))
        self.busca.bind("<KeyRelease>", self.on_busca)

        ttk.Label(l1, text="Original:").pack(side=tk.LEFT, padx=(0, 2))
        self.lbl_orig = ttk.Label(l1, text="(nenhum)", font=("Segoe UI", 9, "italic"), foreground="#0055aa")
        self.lbl_orig.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Label(l1, text="Novo:").pack(side=tk.LEFT, padx=(0, 2))
        self.entrada = ttk.Entry(l1, width=18)
        self.entrada.pack(side=tk.LEFT, padx=(0, 8))
        self.entrada.bind("<KeyRelease>", lambda e: self._on_param_alterado())

        self.cor_custom = None
        self.btn_cor = tk.Button(l1, text="Cor", font=("Segoe UI", 8, "bold"), bg="#f3f4f6", fg="#1f2937", relief=tk.RAISED, borderwidth=1, cursor="hand2", command=self.escolher_cor_texto)
        self.btn_cor.pack(side=tk.LEFT, padx=2)

        self.btn_pipeta = tk.Button(l1, text="Pipeta", font=("Segoe UI", 8, "bold"), bg="#f3f4f6", fg="#1f2937", relief=tk.RAISED, borderwidth=1, cursor="hand2", command=self.ativar_pipeta)
        self.btn_pipeta.pack(side=tk.LEFT, padx=2)

        ttk.Button(l1, text="Restaurar", command=self.restaurar_caixa).pack(side=tk.LEFT, padx=3)
        ttk.Button(l1, text="Excluir", command=self.excluir_caixa).pack(side=tk.LEFT, padx=3)

        # Linha 2 da aba de texto: Tipografia, Transformação e Posição Justificada
        l2 = ttk.Frame(tab_texto)
        l2.pack(fill=tk.X, pady=(1, 2))

        # Bloco Fonte
        ttk.Label(l2, text="Fonte:").pack(side=tk.LEFT, padx=(0, 2))
        self.fonte_var = tk.StringVar(value="Auto (Detectar)")
        self.combo_fontes = ttk.Combobox(
            l2, textvariable=self.fonte_var, values=list(FAMILIAS_FONTES.keys()),
            state="readonly", width=13
        )
        self.combo_fontes.pack(side=tk.LEFT, padx=(0, 4))
        self.combo_fontes.bind("<<ComboboxSelected>>", lambda e: self._on_param_alterado())

        self.bold_var = tk.BooleanVar(value=False)
        self.check_bold = ttk.Checkbutton(l2, text="Negrito", variable=self.bold_var, command=self._on_param_alterado)
        self.check_bold.pack(side=tk.LEFT, padx=(0, 2))

        self.italic_var = tk.BooleanVar(value=False)
        self.check_italic = ttk.Checkbutton(l2, text="Itálico", variable=self.italic_var, command=self._on_param_alterado)
        self.check_italic.pack(side=tk.LEFT, padx=(0, 6))

        # Traço: [-] [val] [+]
        f_traco = ttk.Frame(l2)
        f_traco.pack(side=tk.LEFT, padx=3)
        ttk.Label(f_traco, text="Traço:").pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(f_traco, text="-", width=2, command=self.diminuir_traco).pack(side=tk.LEFT, padx=1)
        self.traco_var = tk.DoubleVar(value=0.0)
        self.spin_traco = ttk.Entry(f_traco, width=4, textvariable=self.traco_var, justify="center")
        self.spin_traco.pack(side=tk.LEFT, padx=1)
        self.spin_traco.bind("<KeyRelease>", lambda e: self._on_param_alterado())
        ttk.Button(f_traco, text="+", width=2, command=self.aumentar_traco).pack(side=tk.LEFT, padx=1)

        # Espaço: [-] [val] [+]
        f_esp = ttk.Frame(l2)
        f_esp.pack(side=tk.LEFT, padx=3)
        ttk.Label(f_esp, text="Espaço:").pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(f_esp, text="-", width=2, command=self.diminuir_espacamento).pack(side=tk.LEFT, padx=1)
        self.espacamento_var = tk.DoubleVar(value=0.0)
        self.spin_esp = ttk.Entry(f_esp, width=4, textvariable=self.espacamento_var, justify="center")
        self.spin_esp.pack(side=tk.LEFT, padx=1)
        self.spin_esp.bind("<KeyRelease>", lambda e: self._on_param_alterado())
        ttk.Button(f_esp, text="+", width=2, command=self.aumentar_espacamento).pack(side=tk.LEFT, padx=1)

        # Tam: [-] [val] [+]
        f_tam = ttk.Frame(l2)
        f_tam.pack(side=tk.LEFT, padx=3)
        ttk.Label(f_tam, text="Tam:").pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(f_tam, text="-", width=2, command=self.diminuir_fonte).pack(side=tk.LEFT, padx=1)
        self.tamanho_var = tk.IntVar(value=24)
        self.spin_tam = ttk.Entry(f_tam, width=3, textvariable=self.tamanho_var, justify="center")
        self.spin_tam.pack(side=tk.LEFT, padx=1)
        self.spin_tam.bind("<KeyRelease>", lambda e: self._on_param_alterado())
        ttk.Button(f_tam, text="+", width=2, command=self.aumentar_fonte).pack(side=tk.LEFT, padx=1)

        # Girar: [-] [val] [+]
        f_rot = ttk.Frame(l2)
        f_rot.pack(side=tk.LEFT, padx=3)
        ttk.Label(f_rot, text="Girar:").pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(f_rot, text="-", width=2, command=self.diminuir_rotacao).pack(side=tk.LEFT, padx=1)
        self.rotacao_var = tk.IntVar(value=0)
        ent_rot = ttk.Entry(f_rot, width=3, textvariable=self.rotacao_var, justify="center")
        ent_rot.pack(side=tk.LEFT, padx=1)
        ent_rot.bind("<KeyRelease>", lambda e: self._on_param_alterado())
        ttk.Button(f_rot, text="+", width=2, command=self.aumentar_rotacao).pack(side=tk.LEFT, padx=1)
        ttk.Label(f_rot, text="°").pack(side=tk.LEFT)

        # X: [-] [val] [+]
        f_x = ttk.Frame(l2)
        f_x.pack(side=tk.LEFT, padx=3)
        ttk.Label(f_x, text="X:").pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(f_x, text="-", width=2, command=self.diminuir_x).pack(side=tk.LEFT, padx=1)
        self.ajuste_x_var = tk.IntVar(value=0)
        ent_x = ttk.Entry(f_x, width=3, textvariable=self.ajuste_x_var, justify="center")
        ent_x.pack(side=tk.LEFT, padx=1)
        ent_x.bind("<KeyRelease>", lambda e: self._on_param_alterado())
        ttk.Button(f_x, text="+", width=2, command=self.aumentar_x).pack(side=tk.LEFT, padx=1)

        # Y: [-] [val] [+]
        f_y = ttk.Frame(l2)
        f_y.pack(side=tk.LEFT, padx=3)
        ttk.Label(f_y, text="Y:").pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(f_y, text="-", width=2, command=self.diminuir_y).pack(side=tk.LEFT, padx=1)
        self.ajuste_y_var = tk.IntVar(value=2)
        ent_y = ttk.Entry(f_y, width=3, textvariable=self.ajuste_y_var, justify="center")
        ent_y.pack(side=tk.LEFT, padx=1)
        ent_y.bind("<KeyRelease>", lambda e: self._on_param_alterado())
        ttk.Button(f_y, text="+", width=2, command=self.aumentar_y).pack(side=tk.LEFT, padx=1)

        # Linha 3 da aba de texto: Efeitos de Realismo e Presets Justificados
        l3 = ttk.Frame(tab_texto)
        l3.pack(fill=tk.X, pady=(1, 2))

        ttk.Label(l3, text="Realismo:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 4))

        # Nitidez: [-] [val] [+]
        f_nit = ttk.Frame(l3)
        f_nit.pack(side=tk.LEFT, padx=3)
        ttk.Label(f_nit, text="Nitidez:").pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(f_nit, text="-", width=2, command=self.diminuir_nitidez).pack(side=tk.LEFT, padx=1)
        self.nitidez_var = tk.DoubleVar(value=1.0)
        self.spin_nit = ttk.Entry(f_nit, width=4, textvariable=self.nitidez_var, justify="center")
        self.spin_nit.pack(side=tk.LEFT, padx=1)
        self.spin_nit.bind("<KeyRelease>", lambda e: self._on_param_alterado())
        ttk.Button(f_nit, text="+", width=2, command=self.aumentar_nitidez).pack(side=tk.LEFT, padx=1)

        # Escuro: [-] [val] [+]
        f_esc = ttk.Frame(l3)
        f_esc.pack(side=tk.LEFT, padx=3)
        ttk.Label(f_esc, text="Escuro:").pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(f_esc, text="-", width=2, command=self.diminuir_escuridao).pack(side=tk.LEFT, padx=1)
        self.escuridao_var = tk.IntVar(value=20)
        self.spin_esc = ttk.Entry(f_esc, width=3, textvariable=self.escuridao_var, justify="center")
        self.spin_esc.pack(side=tk.LEFT, padx=1)
        self.spin_esc.bind("<KeyRelease>", lambda e: self._on_param_alterado())
        ttk.Button(f_esc, text="+", width=2, command=self.aumentar_escuridao).pack(side=tk.LEFT, padx=1)

        # Blur: [-] [val] [+]
        f_blur = ttk.Frame(l3)
        f_blur.pack(side=tk.LEFT, padx=3)
        ttk.Label(f_blur, text="Blur:").pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(f_blur, text="-", width=2, command=self.diminuir_blur).pack(side=tk.LEFT, padx=1)
        self.blur_var = tk.DoubleVar(value=0.5)
        self.spin_blur = ttk.Entry(f_blur, width=4, textvariable=self.blur_var, justify="center")
        self.spin_blur.pack(side=tk.LEFT, padx=1)
        self.spin_blur.bind("<KeyRelease>", lambda e: self._on_param_alterado())
        ttk.Button(f_blur, text="+", width=2, command=self.aumentar_blur).pack(side=tk.LEFT, padx=1)

        # Grão: [-] [val] [+]
        f_ruido = ttk.Frame(l3)
        f_ruido.pack(side=tk.LEFT, padx=3)
        ttk.Label(f_ruido, text="Grão:").pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(f_ruido, text="-", width=2, command=self.diminuir_ruido).pack(side=tk.LEFT, padx=1)
        self.ruido_var = tk.IntVar(value=0)
        self.spin_ruido = ttk.Entry(f_ruido, width=3, textvariable=self.ruido_var, justify="center")
        self.spin_ruido.pack(side=tk.LEFT, padx=1)
        self.spin_ruido.bind("<KeyRelease>", lambda e: self._on_param_alterado())
        ttk.Button(f_ruido, text="+", width=2, command=self.aumentar_ruido).pack(side=tk.LEFT, padx=1)

        # Arco-Íris: [-] [val] [+]
        f_arco = ttk.Frame(l3)
        f_arco.pack(side=tk.LEFT, padx=3)
        ttk.Label(f_arco, text="Arco-Íris:").pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(f_arco, text="-", width=2, command=self.diminuir_arco_iris).pack(side=tk.LEFT, padx=1)
        self.arco_iris_var = tk.DoubleVar(value=0.0)
        self.spin_arco = ttk.Entry(f_arco, width=4, textvariable=self.arco_iris_var, justify="center")
        self.spin_arco.pack(side=tk.LEFT, padx=1)
        self.spin_arco.bind("<KeyRelease>", lambda e: self._on_param_alterado())
        ttk.Button(f_arco, text="+", width=2, command=self.aumentar_arco_iris).pack(side=tk.LEFT, padx=1)

        # JPG Combobox
        ttk.Label(l3, text="JPG:").pack(side=tk.LEFT, padx=(4, 2))
        self.jpg_var = tk.StringVar(value="Leve (75%)")
        self.combo_jpg = ttk.Combobox(
            l3, textvariable=self.jpg_var,
            values=["Desativado (100%)", "Leve (75%)", "Médio (50%)", "Forte (30%)", "Muito Forte (15%)"],
            state="readonly", width=14
        )
        self.combo_jpg.pack(side=tk.LEFT, padx=(0, 4))
        self.combo_jpg.bind("<<ComboboxSelected>>", lambda e: self._on_param_alterado())

        # Presets Rápidos
        f_presets = ttk.Frame(l3)
        f_presets.pack(side=tk.LEFT, padx=(4, 0))
        ttk.Button(f_presets, text="Nítido", command=self.preset_nitido).pack(side=tk.LEFT, padx=2)
        ttk.Button(f_presets, text="Foto / Scan", command=self.preset_scan).pack(side=tk.LEFT, padx=2)
        ttk.Button(f_presets, text="WhatsApp", command=self.preset_whatsapp).pack(side=tk.LEFT, padx=2)

        # ==========================================
        # ABA 2: FOTO 3x4 Sobreposta
        # ==========================================
        tab_foto = ttk.Frame(self.notebook, padding=(4, 2))
        self.notebook.add(tab_foto, text=" 2. Inserir e Editar Imagem ")

        f1 = ttk.Frame(tab_foto)
        f1.pack(fill=tk.X, pady=1)

        ttk.Button(f1, text="Carregar Foto (3x4)", command=self.carregar_foto).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(f1, text="Remover Foto", command=self.remover_foto).pack(side=tk.LEFT, padx=(0, 6))

        self.lbl_foto_status = ttk.Label(f1, text="(Nenhuma foto 3x4 carregada)", font=("Segoe UI", 9, "italic"), foreground="#888888")
        self.lbl_foto_status.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Label(f1, text="Arraste o corpo da foto para mover ou puxe os cantos para redimensionar!", foreground="#007700", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=4)

        # Linha 2: Posição, Dimensões e Giro Justificados [-] [val] [+]
        f2 = ttk.Frame(tab_foto)
        f2.pack(fill=tk.X, pady=(1, 2))

        # Posição X
        f_fx = ttk.Frame(f2)
        f_fx.pack(side=tk.LEFT, padx=3)
        ttk.Label(f_fx, text="Posição X:").pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(f_fx, text="-", width=2, command=lambda: self.mudar_foto_x(-5)).pack(side=tk.LEFT, padx=1)
        self.foto_x_var = tk.IntVar(value=50)
        ent_fx = ttk.Entry(f_fx, width=4, textvariable=self.foto_x_var, justify="center")
        ent_fx.pack(side=tk.LEFT, padx=1)
        ent_fx.bind("<KeyRelease>", lambda e: self._on_foto_alterada())
        ttk.Button(f_fx, text="+", width=2, command=lambda: self.mudar_foto_x(5)).pack(side=tk.LEFT, padx=1)

        # Posição Y
        f_fy = ttk.Frame(f2)
        f_fy.pack(side=tk.LEFT, padx=3)
        ttk.Label(f_fy, text="Y:").pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(f_fy, text="-", width=2, command=lambda: self.mudar_foto_y(-5)).pack(side=tk.LEFT, padx=1)
        self.foto_y_var = tk.IntVar(value=50)
        ent_fy = ttk.Entry(f_fy, width=4, textvariable=self.foto_y_var, justify="center")
        ent_fy.pack(side=tk.LEFT, padx=1)
        ent_fy.bind("<KeyRelease>", lambda e: self._on_foto_alterada())
        ttk.Button(f_fy, text="+", width=2, command=lambda: self.mudar_foto_y(5)).pack(side=tk.LEFT, padx=1)

        # Largura
        f_fw = ttk.Frame(f2)
        f_fw.pack(side=tk.LEFT, padx=3)
        ttk.Label(f_fw, text="Largura:").pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(f_fw, text="-", width=2, command=lambda: self.mudar_foto_w(-5)).pack(side=tk.LEFT, padx=1)
        self.foto_w_var = tk.IntVar(value=180)
        ent_fw = ttk.Entry(f_fw, width=4, textvariable=self.foto_w_var, justify="center")
        ent_fw.pack(side=tk.LEFT, padx=1)
        ent_fw.bind("<KeyRelease>", lambda e: self._on_foto_alterada())
        ttk.Button(f_fw, text="+", width=2, command=lambda: self.mudar_foto_w(5)).pack(side=tk.LEFT, padx=1)

        # Altura
        f_fh = ttk.Frame(f2)
        f_fh.pack(side=tk.LEFT, padx=3)
        ttk.Label(f_fh, text="Altura:").pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(f_fh, text="-", width=2, command=lambda: self.mudar_foto_h(-5)).pack(side=tk.LEFT, padx=1)
        self.foto_h_var = tk.IntVar(value=240)
        ent_fh = ttk.Entry(f_fh, width=4, textvariable=self.foto_h_var, justify="center")
        ent_fh.pack(side=tk.LEFT, padx=1)
        ent_fh.bind("<KeyRelease>", lambda e: self._on_foto_alterada())
        ttk.Button(f_fh, text="+", width=2, command=lambda: self.mudar_foto_h(5)).pack(side=tk.LEFT, padx=1)

        # Girar
        f_frot = ttk.Frame(f2)
        f_frot.pack(side=tk.LEFT, padx=3)
        ttk.Label(f_frot, text="Girar:").pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(f_frot, text="-", width=2, command=lambda: self.mudar_foto_rot(-15)).pack(side=tk.LEFT, padx=1)
        self.foto_rot_var = tk.IntVar(value=0)
        ent_frot = ttk.Entry(f_frot, width=3, textvariable=self.foto_rot_var, justify="center")
        ent_frot.pack(side=tk.LEFT, padx=1)
        ent_frot.bind("<KeyRelease>", lambda e: self._on_foto_alterada())
        ttk.Button(f_frot, text="+", width=2, command=lambda: self.mudar_foto_rot(15)).pack(side=tk.LEFT, padx=1)
        ttk.Label(f_frot, text="°").pack(side=tk.LEFT)

        # Presets Foto
        f_fpresets = ttk.Frame(f2)
        f_fpresets.pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(f_fpresets, text="3x4 Carteirinha", command=self.preset_foto_3x4).pack(side=tk.LEFT, padx=2)
        ttk.Button(f_fpresets, text="Tamanho Original", command=self.preset_foto_orig).pack(side=tk.LEFT, padx=2)

        # Linha 3: Efeitos de Realismo da Foto Justificados [-] [val] [+]
        f3 = ttk.Frame(tab_foto)
        f3.pack(fill=tk.X, pady=(1, 2))

        ttk.Label(f3, text="Realismo Foto:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 4))

        # Nitidez
        f_fnit = ttk.Frame(f3)
        f_fnit.pack(side=tk.LEFT, padx=3)
        ttk.Label(f_fnit, text="Nitidez:").pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(f_fnit, text="-", width=2, command=lambda: self.mudar_foto_nitidez(-0.1)).pack(side=tk.LEFT, padx=1)
        self.foto_nitidez_var = tk.DoubleVar(value=1.0)
        ent_fnit = ttk.Entry(f_fnit, width=4, textvariable=self.foto_nitidez_var, justify="center")
        ent_fnit.pack(side=tk.LEFT, padx=1)
        ent_fnit.bind("<KeyRelease>", lambda e: self._on_foto_alterada())
        ttk.Button(f_fnit, text="+", width=2, command=lambda: self.mudar_foto_nitidez(0.1)).pack(side=tk.LEFT, padx=1)

        # Blur
        f_fblur = ttk.Frame(f3)
        f_fblur.pack(side=tk.LEFT, padx=3)
        ttk.Label(f_fblur, text="Foco/Blur:").pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(f_fblur, text="-", width=2, command=lambda: self.mudar_foto_blur(-0.1)).pack(side=tk.LEFT, padx=1)
        self.foto_blur_var = tk.DoubleVar(value=0.4)
        ent_fblur = ttk.Entry(f_fblur, width=4, textvariable=self.foto_blur_var, justify="center")
        ent_fblur.pack(side=tk.LEFT, padx=1)
        ent_fblur.bind("<KeyRelease>", lambda e: self._on_foto_alterada())
        ttk.Button(f_fblur, text="+", width=2, command=lambda: self.mudar_foto_blur(0.1)).pack(side=tk.LEFT, padx=1)

        # Grão
        f_fruido = ttk.Frame(f3)
        f_fruido.pack(side=tk.LEFT, padx=3)
        ttk.Label(f_fruido, text="Grão:").pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(f_fruido, text="-", width=2, command=lambda: self.mudar_foto_ruido(-2)).pack(side=tk.LEFT, padx=1)
        self.foto_ruido_var = tk.IntVar(value=0)
        ent_fruido = ttk.Entry(f_fruido, width=3, textvariable=self.foto_ruido_var, justify="center")
        ent_fruido.pack(side=tk.LEFT, padx=1)
        ent_fruido.bind("<KeyRelease>", lambda e: self._on_foto_alterada())
        ttk.Button(f_fruido, text="+", width=2, command=lambda: self.mudar_foto_ruido(2)).pack(side=tk.LEFT, padx=1)

        # Arco-Íris
        f_farco = ttk.Frame(f3)
        f_farco.pack(side=tk.LEFT, padx=3)
        ttk.Label(f_farco, text="Arco-Íris:").pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(f_farco, text="-", width=2, command=lambda: self.mudar_foto_arco_iris(-0.2)).pack(side=tk.LEFT, padx=1)
        self.foto_arco_iris_var = tk.DoubleVar(value=0.0)
        ent_farco = ttk.Entry(f_farco, width=4, textvariable=self.foto_arco_iris_var, justify="center")
        ent_farco.pack(side=tk.LEFT, padx=1)
        ent_farco.bind("<KeyRelease>", lambda e: self._on_foto_alterada())
        ttk.Button(f_farco, text="+", width=2, command=lambda: self.mudar_foto_arco_iris(0.2)).pack(side=tk.LEFT, padx=1)

        # Brilho
        f_fbrilho = ttk.Frame(f3)
        f_fbrilho.pack(side=tk.LEFT, padx=3)
        ttk.Label(f_fbrilho, text="Brilho:").pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(f_fbrilho, text="-", width=2, command=lambda: self.mudar_foto_brilho(-0.05)).pack(side=tk.LEFT, padx=1)
        self.foto_brilho_var = tk.DoubleVar(value=1.0)
        ent_fbrilho = ttk.Entry(f_fbrilho, width=4, textvariable=self.foto_brilho_var, justify="center")
        ent_fbrilho.pack(side=tk.LEFT, padx=1)
        ent_fbrilho.bind("<KeyRelease>", lambda e: self._on_foto_alterada())
        ttk.Button(f_fbrilho, text="+", width=2, command=lambda: self.mudar_foto_brilho(0.05)).pack(side=tk.LEFT, padx=1)

        # Contraste
        f_fcontr = ttk.Frame(f3)
        f_fcontr.pack(side=tk.LEFT, padx=3)
        ttk.Label(f_fcontr, text="Contraste:").pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(f_fcontr, text="-", width=2, command=lambda: self.mudar_foto_contraste(-0.05)).pack(side=tk.LEFT, padx=1)
        self.foto_contraste_var = tk.DoubleVar(value=1.0)
        ent_fcontr = ttk.Entry(f_fcontr, width=4, textvariable=self.foto_contraste_var, justify="center")
        ent_fcontr.pack(side=tk.LEFT, padx=1)
        ent_fcontr.bind("<KeyRelease>", lambda e: self._on_foto_alterada())
        ttk.Button(f_fcontr, text="+", width=2, command=lambda: self.mudar_foto_contraste(0.05)).pack(side=tk.LEFT, padx=1)

        # JPG
        ttk.Label(f3, text="JPG:").pack(side=tk.LEFT, padx=(4, 2))
        self.foto_jpg_var = tk.StringVar(value="Leve (75%)")
        self.combo_foto_jpg = ttk.Combobox(
            f3, textvariable=self.foto_jpg_var,
            values=["Desativado (100%)", "Leve (75%)", "Médio (50%)", "Forte (30%)", "Muito Forte (15%)"],
            state="readonly", width=14
        )
        self.combo_foto_jpg.pack(side=tk.LEFT, padx=(0, 4))
        self.combo_foto_jpg.bind("<<ComboboxSelected>>", lambda e: self._on_foto_alterada())

        # ==========================================
        # ABA 3: VISUALIZAR (POPUP DEDICADO APENAS A IMAGEM)
        # ==========================================
        tab_resultado = ttk.Frame(self.notebook, padding=(4, 2))
        self.notebook.add(tab_resultado, text=" Visualizar ")

        f_res = ttk.Frame(tab_resultado)
        f_res.pack(fill=tk.BOTH, expand=True, pady=2)

        tk.Button(
            f_res, text="Abrir Visualização Limpa (Apenas a Imagem)", font=("Segoe UI", 9, "bold"),
            bg="#2563eb", fg="white", activebackground="#1d4ed8", relief=tk.RAISED, cursor="hand2",
            command=self.abrir_popup_visualizar
        ).pack(side=tk.LEFT, padx=(4, 8), pady=1)

        ttk.Label(
            f_res, text="Abre uma janela dedicada apenas com a imagem final pura, com opção de Lupa HUD e Zoom livre.",
            font=("Segoe UI", 8, "italic"), foreground="#4b5563"
        ).pack(side=tk.LEFT)

        # ---- Layout principal com GRID ROBUSTO ----
        centro = ttk.Frame(self)
        centro.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)
        centro.columnconfigure(1, weight=1)
        centro.rowconfigure(0, weight=1)

        # 1. Coluna 0: Log / Histórico (sempre à esquerda)
        self.frame_log = ttk.LabelFrame(centro, text="Histórico", padding=4)
        self.frame_log.grid(row=0, column=0, sticky="ns", padx=(0, 4))
        self.texto_log = tk.Text(self.frame_log, bg="#ffffff", fg="#18181b", width=22, height=22, wrap=tk.WORD, font=("Consolas", 8))
        self.texto_log.pack(side=tk.LEFT, fill=tk.Y)
        scrol = ttk.Scrollbar(self.frame_log, command=self.texto_log.yview)
        scrol.pack(side=tk.RIGHT, fill=tk.Y)
        self.texto_log.configure(yscrollcommand=scrol.set)

        # 2. Coluna 1: Canvas do Documento Principal (expande 100%)
        self.frame_canvas = ttk.Frame(centro)
        self.frame_canvas.grid(row=0, column=1, sticky="nsew")
        self.canvas = tk.Canvas(self.frame_canvas, bg="#e5e7eb", cursor="crosshair")
        hbar = ttk.Scrollbar(self.frame_canvas, orient=tk.HORIZONTAL, command=self.canvas.xview)
        vbar = ttk.Scrollbar(self.frame_canvas, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 3. Coluna 2: Comparador Lado a Lado (sempre à direita)
        self.frame_preview_dock = ttk.LabelFrame(centro, text="Visualização Lado a Lado (Ao Vivo)", padding=6)
        self.frame_preview_dock.grid(row=0, column=2, sticky="ns", padx=(4, 0))

        bar_dock = ttk.Frame(self.frame_preview_dock)
        bar_dock.pack(side=tk.TOP, fill=tk.X, pady=(0, 4))

        ttk.Label(bar_dock, text="Zoom:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 2))
        self.preview_zoom_var = tk.DoubleVar(value=2.5)
        for z_label, z_val in [("1x", 1.0), ("1.5x", 1.5), ("2x", 2.0), ("2.5x", 2.5), ("3x", 3.0), ("4x", 4.0)]:
            ttk.Radiobutton(bar_dock, text=z_label, value=z_val, variable=self.preview_zoom_var, command=self._atualizar_preview_lado_a_lado).pack(side=tk.LEFT, padx=1)

        self.preview_grid_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(bar_dock, text="Grade", variable=self.preview_grid_var, command=self._atualizar_preview_lado_a_lado).pack(side=tk.LEFT, padx=(6, 2))

        self.preview_grid_passo_var = tk.IntVar(value=14)
        ttk.Spinbox(bar_dock, from_=6, to=50, width=3, textvariable=self.preview_grid_passo_var, command=self._atualizar_preview_lado_a_lado).pack(side=tk.LEFT, padx=1)
        ttk.Label(bar_dock, text="px").pack(side=tk.LEFT, padx=(0, 2))
        tk.Button(bar_dock, text="X", font=("Segoe UI", 7, "bold"), bg="#f3f4f6", fg="#ef4444", relief=tk.FLAT, cursor="hand2", command=self.toggle_dock_comparador).pack(side=tk.RIGHT, padx=2)

        self.lbl_dock_info = ttk.Label(self.frame_preview_dock, text="Selecione qualquer palavra no documento.", foreground="#0066cc", font=("Segoe UI", 9))
        self.lbl_dock_info.pack(side=tk.TOP, fill=tk.X, pady=(0, 4))

        f_cp = ttk.Frame(self.frame_preview_dock)
        f_cp.pack(fill=tk.BOTH, expand=True)

        self.canvas_preview = tk.Canvas(f_cp, bg="#1e1e1e", width=460, highlightthickness=0)
        h_prev_scrol = ttk.Scrollbar(f_cp, orient=tk.HORIZONTAL, command=self.canvas_preview.xview)
        v_prev_scrol = ttk.Scrollbar(f_cp, orient=tk.VERTICAL, command=self.canvas_preview.yview)
        self.canvas_preview.configure(xscrollcommand=h_prev_scrol.set, yscrollcommand=v_prev_scrol.set)

        h_prev_scrol.pack(side=tk.BOTTOM, fill=tk.X)
        v_prev_scrol.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas_preview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.status = ttk.Label(
            self,
            text="Abra um documento para começar. Ao selecionar qualquer caixa, ela aparecerá ampliada ao vivo no painel direito.",
            relief=tk.SUNKEN, anchor="w", padding=4
        )
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Control-MouseWheel>", self.on_ctrl_mousewheel)
        self.bind("<Control-z>", lambda e: self.desfazer())

        self.log("App iniciado com Réguas, Lupa HUD (10x), Pipeta e Fontes Serifadas.")

    def log(self, *msgs):
        if not hasattr(self, "texto_log"):
            return
        self.texto_log.insert(tk.END, " ".join(map(str, msgs)) + "\n")
        self.texto_log.see(tk.END)

    def escolher_cor_texto(self):
        cor = colorchooser.askcolor(title="Escolher Cor do Texto")[0]
        if cor:
            self.cor_custom = tuple(int(c) for c in cor)
            self.btn_cor.config(bg=f"#{self.cor_custom[0]:02x}{self.cor_custom[1]:02x}{self.cor_custom[2]:02x}")
            self._on_param_alterado()

    def ativar_pipeta(self):
        if self.modo_pipeta:
            self.modo_pipeta = False
            self.btn_pipeta.config(bg="SystemButtonFace", relief=tk.GROOVE)
            self.canvas.config(cursor="crosshair")
            self.status.config(text="Pipeta desativada.")
        else:
            self.modo_pipeta = True
            self.btn_pipeta.config(bg="#ffcc00", relief=tk.SUNKEN)
            self.canvas.config(cursor="tcross")
            self.status.config(text="PIPETA ATIVA: Clique em qualquer letra ou pixel do documento para puxar a cor exata.")

    def abrir_popup_visualizar(self):
        """Abre a janela popup dedicada exclusivamente para inspecionar a imagem final com zoom e lupa."""
        if self.img_atual is None:
            messagebox.showwarning("Sem documento", "Abra um documento primeiro para visualizar.")
            return
        self._renderizar_documento()
        JanelaVisualizarResultado(self, self.img_atual)

    def abrir_janela_opcoes(self):
        JanelaOpcoes(self)

    def abrir_janela_metadados(self):
        JanelaMetadados(self)

    def abrir_analise_veracidade(self):
        if self.img_original is None or self.img_atual is None:
            messagebox.showwarning("Sem documento", "Abra um documento e faça modificações primeiro.")
            return

        foto_info = None
        if self.foto_ativa and self.foto_original is not None:
            foto_info = {
                "ativa": True,
                "x": self.foto_x_var.get(),
                "y": self.foto_y_var.get(),
                "w": self.foto_w_var.get(),
                "h": self.foto_h_var.get()
            }

        JanelaAnaliseVeracidade(
            self,
            self.img_original,
            self.img_atual,
            self.caixas,
            foto_info=foto_info
        )

    def _obter_qualidade_jpg(self):
        val = self.jpg_var.get()
        if "75" in val:
            return 75
        elif "50" in val:
            return 50
        elif "30" in val:
            return 30
        elif "15" in val:
            return 15
        return 100

    def _obter_qualidade_foto_jpg(self):
        val = self.foto_jpg_var.get()
        if "75" in val:
            return 75
        elif "50" in val:
            return 50
        elif "30" in val:
            return 30
        elif "15" in val:
            return 15
        return 100

    def _on_param_alterado(self):
        if self.selecionada is None or self.selecionada >= len(self.caixas):
            return
        
        cx = self.caixas[self.selecionada]
        novo_texto = self.entrada.get()
        cx["novo_texto"] = novo_texto
        cx["ativo"] = bool(novo_texto.strip() != "" and novo_texto != cx.get("texto_original"))
        cx["fonte"] = self.fonte_var.get()
        cx["is_bold"] = self.bold_var.get()
        cx["is_italic"] = self.italic_var.get()
        cx["traco"] = float(self.traco_var.get())
        cx["espacamento"] = float(self.espacamento_var.get())
        cx["nitidez"] = float(self.nitidez_var.get())
        cx["rotacao"] = int(self.rotacao_var.get())
        cx["cor_custom"] = self.cor_custom
        cx["escuridao"] = self.escuridao_var.get()
        cx["tamanho"] = self.tamanho_var.get()
        cx["ajuste_y"] = self.ajuste_y_var.get()
        cx["ajuste_x"] = self.ajuste_x_var.get()
        cx["blur"] = float(self.blur_var.get())
        cx["ruido"] = int(self.ruido_var.get())
        cx["arco_iris"] = float(self.arco_iris_var.get())
        cx["qualidade_jpg"] = self._obter_qualidade_jpg()

        if self._preview_job:
            self.after_cancel(self._preview_job)
        self._preview_job = self.after(30, self._renderizar_documento)

    def _on_foto_alterada(self):
        if self._preview_job:
            self.after_cancel(self._preview_job)
        self._preview_job = self.after(30, self._renderizar_documento)

    def _renderizar_documento(self):
        if self.img_original is None:
            return

        img_resultado = self.img_original.copy()

        # 1. Renderiza substituições de texto
        for cx in self.caixas:
            if cx.get("ativo") and cx.get("novo_texto"):
                img_resultado = substituir_texto(
                    img_resultado,
                    cx["bbox"],
                    cx["novo_texto"],
                    nome_fonte=cx.get("fonte", "Arial"),
                    is_bold=cx.get("is_bold", False),
                    is_italic=cx.get("is_italic", False),
                    espessura_traco=cx.get("traco", 0.0),
                    espacamento_letras=cx.get("espacamento", 0),
                    nitidez=cx.get("nitidez", 1.0),
                    rotacao=cx.get("rotacao", 0),
                    cor_custom=cx.get("cor_custom", None),
                    escuridao=cx.get("escuridao", 20),
                    tamanho_fonte=cx.get("tamanho", None),
                    ajuste_x=cx.get("ajuste_x", 0),
                    ajuste_y=cx.get("ajuste_y", 2),
                    blur=cx.get("blur", 0.5),
                    ruido=cx.get("ruido", 0),
                    arco_iris=cx.get("arco_iris", 0.0),
                    opacidade=95,
                    qualidade_jpg=cx.get("qualidade_jpg", 75)
                )

        # 2. Renderiza foto sobreposta (3x4)
        if self.foto_ativa and self.foto_original is not None:
            fx = self.foto_x_var.get()
            fy = self.foto_y_var.get()
            fw = self.foto_w_var.get()
            fh = self.foto_h_var.get()
            frot = self.foto_rot_var.get()
            fblur = float(self.foto_blur_var.get())
            fruido = int(self.foto_ruido_var.get())
            farco = float(self.foto_arco_iris_var.get())
            fnit = float(self.foto_nitidez_var.get())
            fbrilho = float(self.foto_brilho_var.get())
            fcontraste = float(self.foto_contraste_var.get())
            fjpg = self._obter_qualidade_foto_jpg()

            foto_proc = processar_foto_sobreposta(
                self.foto_original,
                fw, fh, angulo=frot, blur=fblur, ruido=fruido, arco_iris=farco,
                brilho=fbrilho, contraste=fcontraste, nitidez=fnit,
                qualidade_jpg=fjpg, opacidade=100
            )

            if foto_proc is not None:
                img_rgba = img_resultado.convert("RGBA")
                camada_foto = Image.new("RGBA", img_rgba.size, (0, 0, 0, 0))
                camada_foto.paste(foto_proc, (fx, fy), mask=foto_proc)
                img_resultado = Image.alpha_composite(img_rgba, camada_foto).convert("RGB")

        self.img_atual = img_resultado
        self._mostrar_imagem()
        self._atualizar_preview_lado_a_lado()

    def _atualizar_preview_lado_a_lado(self):
        """Atualiza a telinha lateral com a visualização ampliada Antes vs Depois com grade milimétrica."""
        if not hasattr(self, "canvas_preview"):
            return
        if self.img_original is None or self.img_atual is None:
            self.canvas_preview.delete("all")
            cw = max(200, self.canvas_preview.winfo_width())
            self.canvas_preview.create_text(
                cw // 2, 50,
                text="Abra um documento para ativar o comparador lado a lado.",
                fill="#777777", font=("Segoe UI", 10, "italic")
            )
            return

        box = None
        titulo_info = ""
        if self.selecionada is not None and self.selecionada < len(self.caixas):
            cx = self.caixas[self.selecionada]
            box = cx["bbox"]
            titulo_info = f"Texto: '{cx.get('texto_original', '')}'"
        elif self.foto_ativa and self.foto_original is not None:
            fx, fy = self.foto_x_var.get(), self.foto_y_var.get()
            fw, fh = self.foto_w_var.get(), self.foto_h_var.get()
            box = (fx, fy, fx + fw, fy + fh)
            titulo_info = f"Foto 3x4 ({fw}x{fh}px)"
        else:
            for cx in reversed(self.caixas):
                if cx.get("ativo"):
                    box = cx["bbox"]
                    titulo_info = f"Texto: '{cx.get('texto_original', '')}'"
                    break

        if not box:
            self.canvas_preview.delete("all")
            cw = max(200, self.canvas_preview.winfo_width())
            self.canvas_preview.create_text(
                cw // 2, 50,
                text="Selecione qualquer palavra no documento acima para ver o comparador Lado a Lado aqui.",
                fill="#999999", font=("Segoe UI", 10, "italic")
            )
            return

        x1, y1, x2, y2 = box
        pad_x = max(10, int((x2 - x1) * 0.1))
        pad_y = max(8, int((y2 - y1) * 0.15))
        xa = max(0, x1 - pad_x)
        ya = max(0, y1 - pad_y)
        xb = min(self.img_original.width, x2 + pad_x)
        yb = min(self.img_original.height, y2 + pad_y)

        roi_orig = self.img_original.crop((xa, ya, xb, yb))
        roi_mod = self.img_atual.crop((xa, ya, xb, yb))

        w, h = roi_orig.size
        if w <= 0 or h <= 0:
            return

        zoom = float(self.preview_zoom_var.get())
        zw, zh = max(10, int(w * zoom)), max(10, int(h * zoom))

        view_orig = roi_orig.resize((zw, zh), Image.LANCZOS)
        view_mod = roi_mod.resize((zw, zh), Image.LANCZOS)

        # Aplica Régua Milimétrica com Pixels Anotados
        if getattr(self, "preview_grid_var", None) and self.preview_grid_var.get():
            passo = max(10, int(self.preview_grid_passo_var.get()))
            view_orig = _desenhar_grade_na_imagem(view_orig, zoom_escala=zoom, passo_px=passo)
            view_mod = _desenhar_grade_na_imagem(view_mod, zoom_escala=zoom, passo_px=passo)

        margem = 12
        cabecalho = 26
        espaco_entre = 16

        cw = max(380, self.canvas_preview.winfo_width())
        modo_lado_a_lado = (zw * 2 + margem * 3) <= max(cw, 460)

        if modo_lado_a_lado:
            total_w = zw * 2 + margem * 3
            total_h = zh + cabecalho + margem * 2

            prancha = Image.new("RGB", (total_w, total_h), (25, 25, 25))
            draw_p = ImageDraw.Draw(prancha)
            fonte_p = ImageFont.load_default()

            draw_p.text((margem + 2, 7), f"ORIGINAL ({titulo_info})", fill=(140, 200, 255), font=fonte_p)
            draw_p.text((margem * 2 + zw + 2, 7), "MODIFICADO (AO VIVO)", fill=(130, 255, 140), font=fonte_p)

            prancha.paste(view_orig, (margem, cabecalho + margem))
            prancha.paste(view_mod, (margem * 2 + zw, cabecalho + margem))

            draw_p.rectangle([margem - 1, cabecalho + margem - 1, margem + zw, cabecalho + margem + zh], outline=(60, 120, 180), width=2)
            draw_p.rectangle([margem * 2 + zw - 1, cabecalho + margem - 1, margem * 2 + zw * 2, cabecalho + margem + zh], outline=(40, 160, 70), width=2)
        else:
            total_w = max(zw + margem * 2, 360)
            total_h = (zh + cabecalho + margem) * 2 + margem

            prancha = Image.new("RGB", (total_w, total_h), (25, 25, 25))
            draw_p = ImageDraw.Draw(prancha)
            fonte_p = ImageFont.load_default()

            draw_p.text((margem + 2, 6), f"ORIGINAL: {titulo_info}", fill=(140, 200, 255), font=fonte_p)
            prancha.paste(view_orig, (margem, cabecalho + 4))
            draw_p.rectangle([margem - 1, cabecalho + 3, margem + zw, cabecalho + 4 + zh], outline=(60, 120, 180), width=2)

            y_bloco2 = cabecalho + 4 + zh + espaco_entre
            draw_p.text((margem + 2, y_bloco2), "MODIFICADO (AO VIVO):", fill=(130, 255, 140), font=fonte_p)
            prancha.paste(view_mod, (margem, y_bloco2 + cabecalho))
            draw_p.rectangle([margem - 1, y_bloco2 + cabecalho - 1, margem + zw, y_bloco2 + cabecalho + zh], outline=(40, 160, 70), width=2)

        self.tk_preview_img = ImageTk.PhotoImage(prancha)
        self.canvas_preview.delete("all")
        self.canvas_preview.config(scrollregion=(0, 0, total_w, total_h))
        pos_x = max(0, (cw - total_w) // 2)
        self.canvas_preview.create_image(pos_x, 0, anchor="nw", image=self.tk_preview_img)
        self.lbl_dock_info.config(text=f"Comparando: {titulo_info} (Zoom: {zoom:.1f}x)")

    # --- Controles de Foto 3x4 ---

    def carregar_foto(self):
        caminho = filedialog.askopenfilename(
            title="Escolha a Foto 3x4 ou Imagem",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp *.webp *.tif *.tiff"), ("Todos", "*.*")]
        )
        if not caminho:
            return
        try:
            self.foto_original = Image.open(caminho).convert("RGB")
            self.foto_ativa = True
            
            orig_w, orig_h = self.foto_original.size
            if orig_w > 0 and orig_h > 0:
                proporcao = orig_h / orig_w
                sug_w = 200
                sug_h = int(sug_w * proporcao)
                self.foto_w_var.set(sug_w)
                self.foto_h_var.set(sug_h)

            self.lbl_foto_status.config(
                text=f"Foto: {os.path.basename(caminho)} ({self.foto_original.width}x{self.foto_original.height}px)",
                foreground="#0055aa"
            )
            self._renderizar_documento()
            self.log(f"Foto 3x4 carregada: {os.path.basename(caminho)}")
            self.status.config(text="Foto carregada. Arraste-a na tela ou puxe os cantos/alças para redimensionar!")
        except Exception as e:
            messagebox.showerror("Erro ao carregar foto", str(e))

    def remover_foto(self):
        self.foto_original = None
        self.foto_ativa = False
        self.lbl_foto_status.config(text="(Nenhuma foto carregada)", foreground="#888888")
        self._renderizar_documento()
        self.log("Foto sobreposta removida.")
        self.status.config(text="Foto removida.")

    def aumentar_tam_foto(self):
        self.foto_w_var.set(int(self.foto_w_var.get() * 1.05) + 2)
        self.foto_h_var.set(int(self.foto_h_var.get() * 1.05) + 2)
        self._on_foto_alterada()

    def mudar_foto_x(self, delta):
        self.foto_x_var.set(self.foto_x_var.get() + delta)
        self._on_foto_alterada()

    def mudar_foto_y(self, delta):
        self.foto_y_var.set(self.foto_y_var.get() + delta)
        self._on_foto_alterada()

    def mudar_foto_w(self, delta):
        novo_w = max(10, self.foto_w_var.get() + delta)
        self.foto_w_var.set(novo_w)
        self._on_foto_alterada()

    def mudar_foto_h(self, delta):
        novo_h = max(10, self.foto_h_var.get() + delta)
        self.foto_h_var.set(novo_h)
        self._on_foto_alterada()

    def mudar_foto_rot(self, delta):
        self.foto_rot_var.set((self.foto_rot_var.get() + delta) % 360)
        self._on_foto_alterada()

    def mudar_foto_nitidez(self, delta):
        v = round(max(0.0, min(3.0, self.foto_nitidez_var.get() + delta)), 1)
        self.foto_nitidez_var.set(v)
        self._on_foto_alterada()

    def mudar_foto_blur(self, delta):
        v = round(max(0.0, min(5.0, self.foto_blur_var.get() + delta)), 1)
        self.foto_blur_var.set(v)
        self._on_foto_alterada()

    def mudar_foto_ruido(self, delta):
        v = max(0, min(60, self.foto_ruido_var.get() + delta))
        self.foto_ruido_var.set(v)
        self._on_foto_alterada()

    def mudar_foto_arco_iris(self, delta):
        v = round(max(0.0, min(4.0, self.foto_arco_iris_var.get() + delta)), 1)
        self.foto_arco_iris_var.set(v)
        self._on_foto_alterada()

    def mudar_foto_brilho(self, delta):
        v = round(max(0.2, min(2.5, self.foto_brilho_var.get() + delta)), 2)
        self.foto_brilho_var.set(v)
        self._on_foto_alterada()

    def mudar_foto_contraste(self, delta):
        v = round(max(0.2, min(2.5, self.foto_contraste_var.get() + delta)), 2)
        self.foto_contraste_var.set(v)
        self._on_foto_alterada()

    def diminuir_tam_foto(self):
        self.foto_w_var.set(max(10, int(self.foto_w_var.get() * 0.95) - 2))
        self.foto_h_var.set(max(10, int(self.foto_h_var.get() * 0.95) - 2))
        self._on_foto_alterada()

    def preset_foto_3x4(self):
        self.foto_w_var.set(180)
        self.foto_h_var.set(240)
        self._on_foto_alterada()
        self.status.config(text="Dimensões ajustadas para padrão 3x4 (180x240px)")

    def preset_foto_orig(self):
        if self.foto_original:
            self.foto_w_var.set(self.foto_original.width)
            self.foto_h_var.set(self.foto_original.height)
            self._on_foto_alterada()

    # --- Controles de Texto ---

    def aumentar_rotacao(self):
        self.rotacao_var.set(self.rotacao_var.get() + 1)
        self._on_param_alterado()

    def diminuir_rotacao(self):
        self.rotacao_var.set(self.rotacao_var.get() - 1)
        self._on_param_alterado()

    def aumentar_y(self):
        self.ajuste_y_var.set(self.ajuste_y_var.get() + 1)
        self._on_param_alterado()

    def diminuir_y(self):
        self.ajuste_y_var.set(self.ajuste_y_var.get() - 1)
        self._on_param_alterado()

    def aumentar_x(self):
        self.ajuste_x_var.set(self.ajuste_x_var.get() + 1)
        self._on_param_alterado()

    def diminuir_x(self):
        self.ajuste_x_var.set(self.ajuste_x_var.get() - 1)
        self._on_param_alterado()

    def aumentar_fonte(self):
        tam = self.tamanho_var.get()
        self.tamanho_var.set(min(300, tam + 2))
        self._on_param_alterado()

    def diminuir_fonte(self):
        tam = self.tamanho_var.get()
        self.tamanho_var.set(max(6, tam - 2))
        self._on_param_alterado()

    def aumentar_traco(self):
        t = round(self.traco_var.get() + 0.2, 1)
        self.traco_var.set(min(5.0, t))
        self._on_param_alterado()

    def diminuir_traco(self):
        t = round(self.traco_var.get() - 0.2, 1)
        self.traco_var.set(max(0.0, t))
        self._on_param_alterado()

    def aumentar_espacamento(self):
        e = round(float(self.espacamento_var.get()) + 0.2, 1)
        self.espacamento_var.set(min(40.0, e))
        self._on_param_alterado()

    def diminuir_espacamento(self):
        e = round(float(self.espacamento_var.get()) - 0.2, 1)
        self.espacamento_var.set(max(-10.0, e))
        self._on_param_alterado()

    def aumentar_nitidez(self):
        n = round(self.nitidez_var.get() + 0.2, 1)
        self.nitidez_var.set(min(3.0, n))
        self._on_param_alterado()

    def diminuir_nitidez(self):
        n = round(self.nitidez_var.get() - 0.2, 1)
        self.nitidez_var.set(max(0.5, n))
        self._on_param_alterado()

    def aumentar_escuridao(self):
        e = self.escuridao_var.get() + 5
        self.escuridao_var.set(min(100, e))
        self._on_param_alterado()

    def diminuir_escuridao(self):
        e = self.escuridao_var.get() - 5
        self.escuridao_var.set(max(0, e))
        self._on_param_alterado()

    def aumentar_blur(self):
        b = round(self.blur_var.get() + 0.1, 1)
        self.blur_var.set(min(4.0, b))
        self._on_param_alterado()

    def diminuir_blur(self):
        b = round(self.blur_var.get() - 0.1, 1)
        self.blur_var.set(max(0.0, b))
        self._on_param_alterado()

    def aumentar_ruido(self):
        r = self.ruido_var.get() + 2
        self.ruido_var.set(min(60, r))
        self._on_param_alterado()

    def diminuir_ruido(self):
        r = self.ruido_var.get() - 2
        self.ruido_var.set(max(0, r))
        self._on_param_alterado()

    def aumentar_arco_iris(self):
        a = round(self.arco_iris_var.get() + 0.2, 1)
        self.arco_iris_var.set(min(4.0, a))
        self._on_param_alterado()

    def diminuir_arco_iris(self):
        a = round(self.arco_iris_var.get() - 0.2, 1)
        self.arco_iris_var.set(max(0.0, a))
        self._on_param_alterado()

    def preset_nitido(self):
        self.blur_var.set(0.0)
        self.nitidez_var.set(1.4)
        self.ruido_var.set(0)
        self.arco_iris_var.set(0.0)
        self.jpg_var.set("Desativado (100%)")
        self._on_param_alterado()

    def preset_scan(self):
        self.blur_var.set(0.5)
        self.nitidez_var.set(1.1)
        self.ruido_var.set(12)
        self.arco_iris_var.set(1.2)
        self.jpg_var.set("Leve (75%)")
        self._on_param_alterado()

    def preset_whatsapp(self):
        self.blur_var.set(0.8)
        self.nitidez_var.set(1.2)
        self.ruido_var.set(18)
        self.arco_iris_var.set(1.6)
        self.jpg_var.set("Médio (50%)")
        self._on_param_alterado()

    # --- Metadados e Propriedades do Documento ---

    def _exif_tag_nome(self, tag_id):
        from PIL.ExifTags import TAGS
        return TAGS.get(tag_id, f"Tag {tag_id}")

    def _ler_metadados(self):
        """Retorna dict com metadados do documento e da imagem atual."""
        if self.img_atual is None:
            return {}
        dados = {}
        
        formato = "Desconhecido"
        if getattr(self, "caminho_documento", None):
            formato = os.path.splitext(self.caminho_documento)[1].upper().replace(".", "")
        elif self.img_atual.format:
            formato = self.img_atual.format
        dados["Formato"] = formato

        w = self.meta_largura_px_var.get().strip() if hasattr(self, "meta_largura_px_var") and self.meta_largura_px_var.get().strip() else str(self.img_atual.width)
        h = self.meta_altura_px_var.get().strip() if hasattr(self, "meta_altura_px_var") and self.meta_altura_px_var.get().strip() else str(self.img_atual.height)
        dados["Tamanho (Pixels)"] = f"{w} x {h}"
        dados["Modo"] = self.img_atual.mode

        if hasattr(self, "meta_criado_var") and self.meta_criado_var.get():
            dados["Data de Criação"] = self.meta_criado_var.get()
        if hasattr(self, "meta_mod_var") and self.meta_mod_var.get():
            dados["Data de Modificação"] = self.meta_mod_var.get()
        if hasattr(self, "meta_autor_var") and self.meta_autor_var.get():
            dados["Autor"] = self.meta_autor_var.get()
        if hasattr(self, "meta_titulo_var") and self.meta_titulo_var.get():
            dados["Título"] = self.meta_titulo_var.get()
        if hasattr(self, "meta_tamanho_var") and self.meta_tamanho_var.get() and self.meta_tamanho_var.get() != "0":
            dados["Tamanho Alvo (KB)"] = f"{self.meta_tamanho_var.get()} KB"

        try:
            import piexif
            exif_dict = piexif.load(self.img_atual)
            for ifd, tags in exif_dict.items():
                for k, v in tags.items():
                    nome_tag = self._exif_tag_nome(k)
                    if nome_tag not in dados:
                        dados[nome_tag] = v
        except Exception:
            pass

        return dados

    def atualizar_metadados(self):
        """Atualiza lista EXIF no treeview. Se vazio, mostra info do arquivo."""
        if not hasattr(self, "tree_metas") or self.tree_metas is None:
            return
        meta = self._ler_metadados()
        for item in self.tree_metas.get_children():
            self.tree_metas.delete(item)
        if not meta:
            if self.img_atual is not None:
                self.tree_metas.insert("", tk.END, values=("Formato", self.img_atual.format or "Desconhecido"))
                self.tree_metas.insert("", tk.END, values=("Tamanho", f"{self.img_atual.width} x {self.img_atual.height} px"))
                self.tree_metas.insert("", tk.END, values=("Modo", self.img_atual.mode))
                self.tree_metas.insert("", tk.END, values=("DPI", self.img_atual.info.get('dpi', 'N/A')))
                self.tree_metas.insert("", tk.END, values=("(Nota)", "Sem EXIF (WhatsApp remove na compressão)"))
            else:
                self.tree_metas.insert("", tk.END, values=("(Info)", "Abra um documento primeiro"))
        else:
            for chave, valor in meta.items():
                self.tree_metas.insert("", tk.END, values=(chave, str(valor)))

    def remover_metadados(self):
        """Remove EXIF e marca img para salvar limpo."""
        self._sem_metadados = True
        self.log("Metadados marcados para remoção. Salve para gerar imagem limpa.")
        self.status.config(text="Metadados serão removidos ao salvar.")

    def _obter_metadados_editados(self):
        dados = getattr(self, "metas_custom_editados", {}).copy()
        alvo = getattr(self, "tree_metas", None)
        if alvo is not None:
            try:
                for item in alvo.get_children():
                    vals = alvo.item(item, "values")
                    if vals and len(vals) >= 2:
                        k, v = vals[0], vals[1]
                        if k and k not in ("(Nota)", "(Info)", "Status"):
                            dados[k] = v
            except Exception:
                pass
        return dados

    def _editar_meta(self, evento):
        item = self.tree_metas.selection()[0]
        chave, valor = self.tree_metas.item(item, "values")
        self._popup_edit_meta(chave, valor, item)

    def _popup_edit_meta(self, chave, valor, item, tree_alvo=None):
        dialog = tk.Toplevel(self)
        dialog.title(f"Editar {chave}")
        dialog.geometry("420x130")
        dialog.resizable(False, False)

        ttk.Label(dialog, text=f"{chave}:", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=12, pady=(12, 4))
        ent = ttk.Entry(dialog, width=45)
        ent.pack(padx=12, pady=4, fill=tk.X)
        ent.insert(0, valor)
        ent.focus_set()

        def ok():
            novo_val = ent.get().strip()
            alvo = tree_alvo if tree_alvo is not None else getattr(self, "tree_metas", None)
            if alvo is not None:
                try:
                    alvo.item(item, values=(chave, novo_val))
                except Exception:
                    pass

            if not hasattr(self, "metas_custom_editados"):
                self.metas_custom_editados = {}
            self.metas_custom_editados[chave] = novo_val

            self.log(f"{chave} editado para '{novo_val}'")
            dialog.destroy()

        f_btn = ttk.Frame(dialog)
        f_btn.pack(side=tk.BOTTOM, fill=tk.X, padx=12, pady=10)
        ttk.Button(f_btn, text="OK", command=ok).pack(side=tk.RIGHT, padx=4)
        ttk.Button(f_btn, text="Cancelar", command=dialog.destroy).pack(side=tk.RIGHT)

    # --- Seleção e Manipulação de Caixas de Texto ---

    def _tratar_clique(self, canvas_x, canvas_y):
        if not self.caixas:
            return

        x = canvas_x / self.escala
        y = canvas_y / self.escala
        tolerancia = 4

        for i, cx in enumerate(self.caixas):
            x1, y1, x2, y2 = cx["bbox"]
            if (x1 - tolerancia) <= x <= (x2 + tolerancia) and (y1 - tolerancia) <= y <= (y2 + tolerancia):
                self._selecionar_caixa(i)
                return

        self.selecionada = None
        self.lbl_orig.config(text="(nenhum)")
        self.atualizar_estado_edicao_texto()
        self._mostrar_imagem()
        self._atualizar_preview_lado_a_lado()

    def _definir_estado_widgets(self, container, habilitar=True):
        """Desativa ou ativa recursivamente todos os controles para ficarem cinzas e não-clicáveis."""
        novo_estado = "normal" if habilitar else "disabled"
        for w in container.winfo_children():
            if w == getattr(self, "escudo_clique", None):
                continue
            if w.winfo_children():
                self._definir_estado_widgets(w, habilitar)
            if isinstance(w, (ttk.Entry, tk.Entry, ttk.Spinbox, tk.Spinbox, ttk.Button, tk.Button, ttk.Checkbutton, tk.Checkbutton)):
                try: w.config(state=novo_estado)
                except Exception: pass
            elif isinstance(w, ttk.Combobox):
                try: w.config(state="readonly" if habilitar else "disabled")
                except Exception: pass

    def _clicou_quando_desativado(self):
        """Disparado quando o usuário tenta clicar nos controles cinzas."""
        self.status.config(text="Selecione primeiro o quadrado com o mouse e a palavra que é para ser alterada.")
        messagebox.showinfo(
            "Seleção Necessária",
            "Selecione primeiro o quadrado com o mouse e a palavra que é para ser alterada no documento!"
        )

    def atualizar_estado_edicao_texto(self):
        """Deixa tudo cinza e não clicável se não houver palavra selecionada."""
        if not hasattr(self, "tab_texto") or not hasattr(self, "escudo_clique"):
            return
        tem_sel = (self.selecionada is not None and 0 <= self.selecionada < len(self.caixas))
        if tem_sel:
            self._definir_estado_widgets(self.tab_texto, habilitar=True)
            self.escudo_clique.place_forget()
        else:
            self._definir_estado_widgets(self.tab_texto, habilitar=False)
            self.escudo_clique.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.escudo_clique.lift()

    def _selecionar_caixa(self, indice):
        if indice < 0 or indice >= len(self.caixas):
            return
        self.selecionada = indice
        cx = self.caixas[indice]

        # 1. Habilita imediatamente a barra de texto (remove o cinza e o bloqueio de cliques)
        self.atualizar_estado_edicao_texto()

        # 2. Preenche os campos da palavra selecionada
        self.lbl_orig.config(text=cx.get("texto_original", ""))
        self.entrada.delete(0, tk.END)
        self.entrada.insert(0, cx.get("novo_texto", cx.get("texto_original", "")))

        self.fonte_var.set(cx.get("fonte", "Auto (Detectar)"))
        self.bold_var.set(cx.get("is_bold", False))
        self.italic_var.set(cx.get("is_italic", False))
        self.traco_var.set(float(cx.get("traco", 0.0)))
        self.espacamento_var.set(float(cx.get("espacamento", 0.0)))
        self.nitidez_var.set(float(cx.get("nitidez", 1.0)))
        self.rotacao_var.set(int(cx.get("rotacao", 0)))
        self.cor_custom = cx.get("cor_custom", None)
        if self.cor_custom:
            self.btn_cor.config(bg=f"#{self.cor_custom[0]:02x}{self.cor_custom[1]:02x}{self.cor_custom[2]:02x}")
        else:
            self.btn_cor.config(bg="SystemButtonFace")

        self.escuridao_var.set(cx.get("escuridao", 20))
        self.tamanho_var.set(cx.get("tamanho", 24))
        self.ajuste_y_var.set(cx.get("ajuste_y", 2))
        self.ajuste_x_var.set(cx.get("ajuste_x", 0))
        self.blur_var.set(cx.get("blur", 0.5))
        self.ruido_var.set(cx.get("ruido", 0))
        self.arco_iris_var.set(cx.get("arco_iris", 0.0))

        jpg_val = cx.get("qualidade_jpg", 75)
        for opt in ["Desativado (100%)", "Leve (75%)", "Médio (50%)", "Forte (30%)", "Muito Forte (15%)"]:
            if str(jpg_val) in opt:
                self.jpg_var.set(opt)
                break

        self.notebook.select(0)
        self._mostrar_imagem()
        self._atualizar_preview_lado_a_lado()
        self.status.config(text=f"Editando '{cx.get('texto_original', '')}'.")
        self.entrada.focus_set()
        self.entrada.selection_range(0, tk.END)

    def _obter_abas_metadados(self):
        """Retorna dict com abas por tipo: 'Imagem' (EXIF), 'PDF' (pymupdf), 'DOCX'."""
        return {"EXIF": self._ler_metadados()}

    def restaurar_caixa(self):
        if self.selecionada is None or self.selecionada >= len(self.caixas):
            return
        cx = self.caixas[self.selecionada]
        cx["novo_texto"] = cx.get("texto_original", "")
        cx["ativo"] = False
        self.entrada.delete(0, tk.END)
        self.entrada.insert(0, cx["novo_texto"])
        self._renderizar_documento()
        self.status.config(text="Caixa restaurada ao estado original.")

    def excluir_caixa(self):
        if self.selecionada is None or self.selecionada >= len(self.caixas):
            return
        self.caixas.pop(self.selecionada)
        self.selecionada = None
        self.lbl_orig.config(text="(nenhum)")
        self.entrada.delete(0, tk.END)
        self._renderizar_documento()
        self.status.config(text="Caixa excluída.")

    # --- Menu de Opções, Temas e Tamanho da Tela ---

    def _criar_menu_opcoes(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Menu Arquivo
        menu_arq = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=menu_arq)
        menu_arq.add_command(label="Abrir Documento...", command=self.abrir)
        menu_arq.add_command(label="Salvar Imagem...", command=self.salvar)
        menu_arq.add_separator()
        menu_arq.add_command(label="Propriedades / Metadados...", command=self.abrir_janela_metadados)
        menu_arq.add_command(label="Análise Forense...", command=self.abrir_analise_veracidade)
        menu_arq.add_separator()
        menu_arq.add_command(label="Sair", command=self.destroy)

        # Menu Opções
        menu_opcoes = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Opções", menu=menu_opcoes)

        # Submenu Temas
        menu_temas = tk.Menu(menu_opcoes, tearoff=0)
        menu_opcoes.add_cascade(label="Tema da Interface", menu=menu_temas)
        menu_temas.add_command(label="Claro (Padrão Original)", command=lambda: (self.aplicar_tema("claro"), self.atualizar_estado_edicao_texto()))
        menu_temas.add_command(label="Tema escuro/cinza", command=lambda: self.aplicar_tema("vscode"))

        # Submenu Tamanho da Tela
        menu_tela = tk.Menu(menu_opcoes, tearoff=0)
        menu_opcoes.add_cascade(label="Tamanho da Tela", menu=menu_tela)
        menu_tela.add_command(label="HD Compacto (1280 x 720)", command=lambda: self.redimensionar_janela(1280, 720))
        menu_tela.add_command(label="Padrão Médio (1460 x 950)", command=lambda: self.redimensionar_janela(1460, 950))
        menu_tela.add_command(label="Full HD (1920 x 1080)", command=lambda: self.redimensionar_janela(1920, 1080))
        menu_tela.add_separator()
        menu_tela.add_command(label="Maximizar / Tela Cheia", command=self.toggle_maximizar)
        menu_tela.add_command(label="Tamanho Personalizado...", command=self.popup_tamanho_personalizado)

        # Menu Exibir
        menu_exibir = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Exibir", menu=menu_exibir)
        menu_exibir.add_command(label="Alternar Comparador Lado a Lado", command=self.toggle_dock_comparador)
        menu_exibir.add_command(label="Alternar Histórico / Log", command=self.toggle_painel_log)
        menu_exibir.add_command(label="Lupa HUD (10x)", command=self.toggle_lupa)

    def redimensionar_janela(self, w, h):
        self.state("normal")
        self.geometry(f"{w}x{h}")
        self.status.config(text=f"Resolução da janela ajustada para {w}x{h}.")

    def toggle_maximizar(self):
        try:
            if self.state() == "zoomed":
                self.state("normal")
            else:
                self.state("zoomed")
        except Exception:
            pass

    def popup_tamanho_personalizado(self):
        diag = tk.Toplevel(self)
        diag.title("Tamanho Personalizado")
        diag.geometry("320x150")
        diag.resizable(False, False)
        
        ttk.Label(diag, text="Largura (px):").grid(row=0, column=0, padx=10, pady=10)
        ent_w = ttk.Entry(diag, width=10)
        ent_w.insert(0, str(self.winfo_width()))
        ent_w.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(diag, text="Altura (px):").grid(row=1, column=0, padx=10, pady=6)
        ent_h = ttk.Entry(diag, width=10)
        ent_h.insert(0, str(self.winfo_height()))
        ent_h.grid(row=1, column=1, padx=10, pady=6)

        def aplicar():
            try:
                pw = int(ent_w.get().strip())
                ph = int(ent_h.get().strip())
                self.redimensionar_janela(pw, ph)
                diag.destroy()
            except Exception as e:
                messagebox.showerror("Valor Inválido", str(e))

        ttk.Button(diag, text="Aplicar", command=aplicar).grid(row=2, column=0, columnspan=2, pady=10)

    def aplicar_tema(self, tema):
        aplicar_tema_app(self, tema)

    def toggle_dock_comparador(self):
        if self.dock_visivel:
            self.frame_preview_dock.grid_remove()
            self.dock_visivel = False
            self.btn_toggle_dock.config(text="Comparador (Off)", bg="#e5e7eb" if getattr(self, "tema_atual", "claro") == "claro" else "#27272a")
            self.status.config(text="Comparador lateral ocultado. Documento expandido!")
        else:
            self.frame_preview_dock.grid()
            self.dock_visivel = True
            self.btn_toggle_dock.config(text="Comparador (On)", bg="#2563eb", fg="white")
            self._atualizar_preview_lado_a_lado()
            self.status.config(text="Comparador lateral exibido à direita.")

    def toggle_painel_log(self):
        if self.log_visivel:
            self.frame_log.grid_remove()
            self.log_visivel = False
            self.btn_toggle_log.config(text="Histórico (Off)", bg="#9ca3af", fg="white")
            self.status.config(text="Painel de Histórico ocultado.")
        else:
            self.frame_log.grid()
            self.log_visivel = True
            self.btn_toggle_log.config(text="Histórico", bg="#4b5563", fg="white")
            self.status.config(text="Painel de Histórico restaurado à esquerda.")

    # --- Operações de Arquivo e Ciclo de Vida ---

    def abrir(self):
        caminho = filedialog.askopenfilename(
            title="Escolha o documento",
            filetypes=[("Documentos", "*.pdf *.docx *.doc *.png *.jpg *.jpeg *.bmp *.tif *.tiff"),
                       ("Todos", "*.*")],
        )
        if not caminho:
            return
        try:
            self.img_original = carregar_documento(caminho)
        except Exception as e:
            messagebox.showerror("Erro ao abrir", str(e))
            return
        self.img_atual = self.img_original.copy()
        self.caixas = []
        self.selecionada = None
        self.atualizar_estado_edicao_texto()
        self.remover_foto()
        self._mostrar_imagem()
        self._atualizar_preview_lado_a_lado()
        self.atualizar_estado_edicao_texto()
        self.status.config(text=f"Documento carregado: {os.path.basename(caminho)}")
        self.log(f"Carregado: {os.path.basename(caminho)}")
        self.caminho_documento = caminho
        try:
            st = os.stat(caminho)
            self.meta_criado_var.set(datetime.fromtimestamp(st.st_ctime).strftime("%d/%m/%Y %H:%M:%S"))
            self.meta_mod_var.set(datetime.fromtimestamp(st.st_mtime).strftime("%d/%m/%Y %H:%M:%S"))
            self.meta_tamanho_var.set(str(int(st.st_size / 1024)))
            self.meta_largura_px_var.set(str(self.img_atual.width))
            self.meta_altura_px_var.set(str(self.img_atual.height))
        except Exception:
            pass
        self.atualizar_metadados()

    def _on_tab_mudou(self, event=None):
        try:
            aba = self.notebook.index(self.notebook.select())
            if aba == 2:  # Aba: Visualizar
                self.abrir_popup_visualizar()
                self.status.config(text="Visualizar: janela popup de inspeção aberta com a imagem final.")
            else:
                if hasattr(self, "frame_log") and getattr(self, "log_visivel", True):
                    self.frame_log.grid()
                if hasattr(self, "frame_preview_dock") and getattr(self, "dock_visivel", True):
                    self.frame_preview_dock.grid()
                self._mostrar_imagem(mostrar_caixas=True)
                self.atualizar_estado_edicao_texto()
        except Exception:
            pass

    def _mostrar_imagem(self, mostrar_caixas=None):
        if self.img_atual is None:
            return
        self.canvas.delete("all")
        w, h = self.img_atual.size
        maxlado = 1600
        escala_base = min(maxlado / w, maxlado / h, 3.5) if max(w, h) > maxlado else 1.0
        self.escala = escala_base * float(getattr(self, "fator_zoom_manual", 1.0))
        vw = max(10, int(w * self.escala))
        vh = max(10, int(h * self.escala))
        img_view = self.img_atual.resize((vw, vh), Image.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(img_view)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
        self.canvas.config(scrollregion=(0, 0, vw, vh))

        for i, cx in enumerate(self.caixas):
            x1, y1, x2, y2 = cx["bbox"]
            is_sel = (i == self.selecionada)
            is_ativo = cx.get("ativo", False)
            
            if is_sel:
                cor = "#ff0000"
                largura = 3
            elif is_ativo:
                cor = "#00ff66"
                largura = 2
            else:
                cor = "#00bfff"
                largura = 1

            self.canvas.create_rectangle(
                x1 * self.escala, y1 * self.escala, x2 * self.escala, y2 * self.escala,
                outline=cor, width=largura, tags=f"box{i}"
            )

        if self.foto_ativa and self.foto_original is not None:
            fx = self.foto_x_var.get() * self.escala
            fy = self.foto_y_var.get() * self.escala
            fw = self.foto_w_var.get() * self.escala
            fh = self.foto_h_var.get() * self.escala
            r = 5

            self.canvas.create_rectangle(
                fx, fy, fx + fw, fy + fh,
                outline="#ffaa00", width=2, dash=(6, 3), tags="foto_3x4_border"
            )

            cantos = [
                (fx, fy), (fx + fw, fy), (fx + fw, fy + fh), (fx, fy + fh)
            ]
            for cx_canto, cy_canto in cantos:
                self.canvas.create_rectangle(
                    cx_canto - r, cy_canto - r, cx_canto + r, cy_canto + r,
                    fill="#ffffff", outline="#ff6600", width=2, tags="foto_handle"
                )

    def on_busca(self, evento):
        termo = self.busca.get().strip()
        if not termo:
            return
        for i, cx in enumerate(self.caixas):
            if termo.lower() in cx.get("texto_original", "").lower() or termo.lower() in cx.get("novo_texto", "").lower():
                self._selecionar_caixa(i)
                return

    def desfazer(self):
        if not self.caixas:
            self.status.config(text="Nada para desfazer.")
            return
        for cx in reversed(self.caixas):
            if cx.get("ativo"):
                cx["ativo"] = False
                cx["novo_texto"] = cx.get("texto_original", "")
                break
        self._renderizar_documento()
        self.status.config(text="Desfeito!")

    def limpar_tudo(self):
        self.caixas = []
        self.selecionada = None
        self.atualizar_estado_edicao_texto()
        self.lbl_orig.config(text="(nenhum)")
        self.entrada.delete(0, tk.END)
        self.remover_foto()
        if self.img_original is not None:
            self.img_atual = self.img_original.copy()
        self._mostrar_imagem()
        self._atualizar_preview_lado_a_lado()
        self.log("Todas as caixas e fotos foram limpas.")
        self.status.config(text="Limpo!")

    def aplicar_resolucao_doc(self):
        """Redimensiona o documento na tela e na memória imediatamente para a resolução digitada."""
        if self.img_atual is None:
            messagebox.showwarning("Sem documento", "Abra um documento primeiro.")
            return
        try:
            pw = int(self.meta_largura_px_var.get().strip())
            ph = int(self.meta_altura_px_var.get().strip())
            if pw < 20 or ph < 20 or pw > 15000 or ph > 15000:
                messagebox.showwarning("Dimensões inválidas", "Digite valores entre 20 e 15000 pixels.")
                return

            escala_x = pw / max(1, self.img_atual.width)
            escala_y = ph / max(1, self.img_atual.height)

            self.img_atual = self.img_atual.resize((pw, ph), Image.LANCZOS)
            if self.img_original is not None:
                self.img_original = self.img_original.resize((pw, ph), Image.LANCZOS)

            for cx in self.caixas:
                x1, y1, x2, y2 = cx["bbox"]
                cx["bbox"] = (int(x1 * escala_x), int(y1 * escala_y), int(x2 * escala_x), int(y2 * escala_y))

            self._mostrar_imagem()
            self._atualizar_preview_lado_a_lado()
            self.atualizar_metadados()
            self.log(f"Resolução alterada com sucesso para: {pw} x {ph} px")
            self.status.config(text=f"Resolução alterada para {pw}x{ph} px.")
        except Exception as e:
            messagebox.showerror("Erro ao redimensionar", str(e))

    def salvar(self):
        if self.img_atual is None:
            messagebox.showwarning("Nada para salvar", "Abra e edite um documento primeiro.")
            return
        caminho = filedialog.asksaveasfilename(
            title="Salvar resultado",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg *.jpeg"), ("PDF", "*.pdf")],
        )
        if not caminho:
            return
        
        ext = os.path.splitext(caminho)[1].lower()
        
        # Redimensiona pixels se o usuário alterou a resolução na aba de metadados
        img_para_salvar = self.img_atual.copy()
        try:
            pw = int(self.meta_largura_px_var.get().strip())
            ph = int(self.meta_altura_px_var.get().strip())
            if pw > 10 and ph > 10 and (pw != img_para_salvar.width or ph != img_para_salvar.height):
                img_para_salvar = img_para_salvar.resize((pw, ph), Image.LANCZOS)
        except Exception:
            pass

        if ext == ".pdf":
            img_para_salvar.save(caminho, "PDF", resolution=100.0)
        elif ext in (".jpg", ".jpeg"):
            metadados_editados = self._obter_metadados_editados()
            if metadados_editados:
                self._salvar_com_exif(caminho, metadados_editados, img_salvar=img_para_salvar)
            else:
                img_para_salvar.save(caminho, "JPEG", quality=95)
        else:
            img_para_salvar.save(caminho)

        try:
            dt_cria = datetime.strptime(self.meta_criado_var.get().strip(), "%d/%m/%Y %H:%M:%S")
        except Exception:
            dt_cria = datetime.now()

        try:
            dt_mod = datetime.strptime(self.meta_mod_var.get().strip(), "%d/%m/%Y %H:%M:%S")
        except Exception:
            dt_mod = datetime.now()

        try:
            tam_kb = float(self.meta_tamanho_var.get().strip().replace(",", "."))
        except Exception:
            tam_kb = 0.0

        aplicar_metadados_e_tamanho_reais(
            caminho=caminho,
            autor=self.meta_autor_var.get().strip(),
            titulo=self.meta_titulo_var.get().strip(),
            data_criacao=dt_cria if self.meta_aplicar_ntfs.get() else None,
            data_modificacao=dt_mod if self.meta_aplicar_ntfs.get() else None,
            tamanho_kb=tam_kb
        )

        tam_final_kb = os.path.getsize(caminho) / 1024
        self.log(f"Salvo com sucesso: {caminho} ({tam_final_kb:.1f} KB)")
        self.status.config(text=f"Documento salvo em: {caminho}")

    def _salvar_com_exif(self, caminho, metadados, img_salvar=None):
        """Salva JPEG com EXIF editado usando piexif."""
        alvo_img = img_salvar if img_salvar is not None else self.img_atual
        try:
            import piexif
            try:
                exif_dict = piexif.load(alvo_img)
            except Exception:
                exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}}

            if "0th" not in exif_dict: exif_dict["0th"] = {}
            if "Exif" not in exif_dict: exif_dict["Exif"] = {}

            tag_map = {
                "Make": ("0th", 271),
                "Model": ("0th", 272),
                "Software": ("0th", 305),
                "DateTime": ("0th", 306),
                "Artist": ("0th", 315),
                "Copyright": ("0th", 33432),
            }

            for chave, valor in metadados.items():
                if chave in tag_map:
                    ifd, tag = tag_map[chave]
                    try:
                        exif_dict[ifd][tag] = str(valor).encode('utf-8')
                    except Exception as e:
                        self.log(f"Erro ao salvar {chave}: {e}")

            try:
                exif_dict["Exif"][40962] = int(alvo_img.width)
                exif_dict["Exif"][40963] = int(alvo_img.height)
            except Exception:
                pass

            exif_bytes = piexif.dump(exif_dict)
            alvo_img.save(caminho, "JPEG", quality=95, exif=exif_bytes)
            self.log(f"Salvo com metadados EXIF: {caminho}")
        except Exception as e:
            self.log(f"Aviso EXIF: {e}")
            alvo_img.save(caminho, quality=95)
