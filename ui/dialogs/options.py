# -*- coding: utf-8 -*-
"""
Janela de Opções, Temas e Resolução de Tela
"""

import tkinter as tk
from tkinter import ttk


class JanelaOpcoes(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.app = parent
        self.title("Opções - DOC_EDITOR_3000")
        self.geometry("450x360")
        self.resizable(False, False)

        f_tema = ttk.LabelFrame(self, text=" Tema da Interface ", padding=10)
        f_tema.pack(fill=tk.X, padx=12, pady=(10, 6))

        ttk.Label(f_tema, text="Escolha a aparência do programa:").pack(anchor="w", pady=(0, 6))
        
        f_btns_tema = ttk.Frame(f_tema)
        f_btns_tema.pack(fill=tk.X)
        
        tk.Button(f_btns_tema, text="Branco / Claro (Padrão)", font=("Segoe UI", 9, "bold"),
                  bg="#f4f4f5", fg="#18181b", relief=tk.RAISED, cursor="hand2", padx=10, pady=6,
                  command=lambda: self.app.aplicar_tema("claro")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        tk.Button(f_btns_tema, text="Tema escuro/cinza", font=("Segoe UI", 9, "bold"),
                  bg="#252526", fg="#cccccc", activebackground="#007acc", activeforeground="#ffffff",
                  relief=tk.RAISED, cursor="hand2", padx=10, pady=6,
                  command=lambda: self.app.aplicar_tema("vscode")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        f_tela = ttk.LabelFrame(self, text=" Tamanho da Janela (Resolução da Tela) ", padding=10)
        f_tela.pack(fill=tk.X, padx=12, pady=6)

        f_grid_res = ttk.Frame(f_tela)
        f_grid_res.pack(fill=tk.X, pady=(0, 8))

        ttk.Button(f_grid_res, text="1280 x 720 (HD)", command=lambda: self.app.redimensionar_janela(1280, 720)).grid(row=0, column=0, padx=3, pady=2, sticky="ew")
        ttk.Button(f_grid_res, text="1460 x 950 (Padrão)", command=lambda: self.app.redimensionar_janela(1460, 950)).grid(row=0, column=1, padx=3, pady=2, sticky="ew")
        ttk.Button(f_grid_res, text="1920 x 1080 (Full HD)", command=lambda: self.app.redimensionar_janela(1920, 1080)).grid(row=1, column=0, padx=3, pady=2, sticky="ew")
        ttk.Button(f_grid_res, text="Maximizar Tela", command=self.app.toggle_maximizar).grid(row=1, column=1, padx=3, pady=2, sticky="ew")
        f_grid_res.columnconfigure(0, weight=1)
        f_grid_res.columnconfigure(1, weight=1)

        f_cust = ttk.Frame(f_tela)
        f_cust.pack(fill=tk.X)
        ttk.Label(f_cust, text="Personalizado:").pack(side=tk.LEFT, padx=2)
        ent_w = ttk.Entry(f_cust, width=6)
        ent_w.insert(0, str(self.app.winfo_width()))
        ent_w.pack(side=tk.LEFT, padx=2)
        ttk.Label(f_cust, text="x").pack(side=tk.LEFT)
        ent_h = ttk.Entry(f_cust, width=6)
        ent_h.insert(0, str(self.app.winfo_height()))
        ent_h.pack(side=tk.LEFT, padx=2)

        def aplicar_cust():
            try:
                self.app.redimensionar_janela(int(ent_w.get()), int(ent_h.get()))
            except Exception:
                pass

        ttk.Button(f_cust, text="Aplicar", command=aplicar_cust).pack(side=tk.LEFT, padx=4)

        f_fechar = ttk.Frame(self, padding=(12, 6))
        f_fechar.pack(side=tk.BOTTOM, fill=tk.X)
        tk.Button(f_fechar, text="Fechar", width=12, font=("Segoe UI", 9, "bold"), command=self.destroy).pack(side=tk.RIGHT)
