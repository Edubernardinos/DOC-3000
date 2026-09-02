# -*- coding: utf-8 -*-
"""
Gerenciador de Temas e Estilos da Interface (Claro e VS Code Dark)
"""

import tkinter as tk
from tkinter import ttk


def aplicar_tema_app(app, tema):
    """Aplica o tema (claro ou vscode) na aplicação e em seus widgets ttk/tk."""
    app.tema_atual = tema
    style = ttk.Style()

    if tema == "vscode":
        # Paleta VS Code (Cinza Grafite Suave)
        BG_BASE = "#1e1e1e"
        BG_SIDE = "#252526"
        BG_HOVER = "#2d2d30"
        BORDER = "#3e3e42"
        ACCENT = "#007acc"
        FG_TEXT = "#cccccc"
        FG_MUTED = "#858585"

        app.configure(bg=BG_BASE)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(".", background=BG_BASE, foreground=FG_TEXT, font=("Segoe UI", 9))
        style.configure("TFrame", background=BG_BASE)
        style.configure("TLabelframe", background=BG_SIDE, foreground="#38bdf8", relief="solid", borderwidth=1)
        style.configure("TLabelframe.Label", background=BG_SIDE, foreground="#38bdf8", font=("Segoe UI", 9, "bold"))
        style.configure("TLabel", background=BG_SIDE, foreground=FG_TEXT)
        style.configure("TNotebook", background=BG_BASE, borderwidth=0, tabmargins=[2, 4, 2, 0])
        style.configure("TNotebook.Tab", background=BG_SIDE, foreground=FG_MUTED, padding=[12, 4], font=("Segoe UI", 9, "bold"))
        style.map("TNotebook.Tab", background=[("selected", ACCENT)], foreground=[("selected", "#ffffff")])
        style.configure("TEntry", fieldbackground=BG_BASE, foreground="#ffffff")
        style.configure("TSpinbox", fieldbackground=BG_BASE, foreground="#ffffff")
        style.configure("TCombobox", fieldbackground=BG_BASE, foreground="#ffffff")
        style.configure("TCheckbutton", background=BG_SIDE, foreground=FG_TEXT)
        style.configure("TRadiobutton", background=BG_SIDE, foreground=FG_TEXT)

        if hasattr(app, "canvas"): app.canvas.config(bg="#1e1e1e")
        if hasattr(app, "canvas_preview"): app.canvas_preview.config(bg="#252526")
        if hasattr(app, "texto_log"): app.texto_log.config(bg="#1e1e1e", fg="#858585", insertbackground="#ffffff")
        if hasattr(app, "btn_lupa"): app.btn_lupa.config(bg="#2d2d30", fg="#cccccc")
        if hasattr(app, "overlay_aviso_texto"):
            app.overlay_aviso_texto.config(bg="#222226")
            for w in app.overlay_aviso_texto.winfo_children():
                try: w.config(bg="#222226")
                except Exception: pass
        if hasattr(app, "status"): app.status.config(background=BG_SIDE, foreground=FG_TEXT)
        if hasattr(app, "status"): app.status.config(text="Tema: Tema escuro/cinza")

    else:
        # Tema Padrão 100% BRANCO / Claro Original
        BG_WHITE = "#ffffff"
        FG_DARK = "#18181b"

        app.configure(bg=BG_WHITE)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(".", background=BG_WHITE, foreground=FG_DARK, font=("Segoe UI", 9))
        style.configure("TFrame", background=BG_WHITE)
        style.configure("TLabelframe", background=BG_WHITE, foreground="#1f2937", borderwidth=1, relief="solid")
        style.configure("TLabelframe.Label", background=BG_WHITE, foreground="#1f2937", font=("Segoe UI", 9, "bold"))
        style.configure("TLabel", background=BG_WHITE, foreground=FG_DARK)
        style.configure("TButton", background="#f3f4f6", foreground=FG_DARK, padding=(4, 2))
        style.configure("TNotebook", background=BG_WHITE, borderwidth=0, tabmargins=[2, 4, 2, 0])
        style.configure("TNotebook.Tab", background="#f3f4f6", foreground="#4b5563", padding=[10, 2], font=("Segoe UI", 8, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#0066cc")], foreground=[("selected", "#ffffff")])
        style.configure("TEntry", fieldbackground="#ffffff", foreground=FG_DARK)
        style.configure("TSpinbox", fieldbackground="#ffffff", foreground=FG_DARK)
        style.configure("TCombobox", fieldbackground="#ffffff", foreground=FG_DARK)
        style.configure("TCheckbutton", background=BG_WHITE, foreground=FG_DARK)
        style.configure("TRadiobutton", background=BG_WHITE, foreground=FG_DARK)

        if hasattr(app, "canvas"): app.canvas.config(bg="#e5e7eb")
        if hasattr(app, "canvas_preview"): app.canvas_preview.config(bg="#f4f4f5")
        if hasattr(app, "texto_log"): app.texto_log.config(bg="#ffffff", fg="#000000", insertbackground="#000000")
        if hasattr(app, "btn_lupa"): app.btn_lupa.config(bg="#f3f4f6", fg="#1f2937", relief=tk.RAISED)
        if hasattr(app, "overlay_aviso_texto"):
            app.overlay_aviso_texto.config(bg="#f8fafc")
            for w in app.overlay_aviso_texto.winfo_children():
                try: w.config(bg="#f8fafc")
                except Exception: pass
        if hasattr(app, "status"): app.status.config(background="#f4f4f5", foreground="#1f2937")
        if hasattr(app, "status"): app.status.config(text="Tema: Branco / Claro (Padrão Original)")
