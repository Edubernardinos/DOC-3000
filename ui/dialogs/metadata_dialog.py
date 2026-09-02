# -*- coding: utf-8 -*-
"""
Janela Dedicada de Metadados & Propriedades Reais do Documento
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime


class JanelaMetadados(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.app = parent
        self.title("🏷️ Propriedades do Documento, Metadados Reais & Tamanho")
        self.geometry("860x600")
        self.minsize(750, 480)

        # Segue o tema atual do app sem sobrescrever o tema global
        if getattr(self.app, "tema_atual", "claro") == "vscode":
            self.configure(bg="#1e1e1e")
        else:
            self.configure(bg="#ffffff")

        self._montar_ui()
        self.app.tree_metas = self.tree
        self.atualizar_tabela()

    def _montar_ui(self):
        f_top = ttk.LabelFrame(self, text=" Propriedades Reais do Documento & Sistema Operacional ", padding=10)
        f_top.pack(side=tk.TOP, fill=tk.X, padx=10, pady=8)

        # Linha 0: Criado em / Modificado em
        ttk.Label(f_top, text="Criado em:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        ttk.Entry(f_top, textvariable=self.app.meta_criado_var, width=22).grid(row=0, column=1, sticky="w", padx=4, pady=4)
        ttk.Button(f_top, text="Agora", width=6, command=lambda: self.app.meta_criado_var.set(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))).grid(row=0, column=2, padx=2)

        ttk.Label(f_top, text="Modificado em:").grid(row=0, column=3, sticky="w", padx=(14, 4), pady=4)
        ttk.Entry(f_top, textvariable=self.app.meta_mod_var, width=22).grid(row=0, column=4, sticky="w", padx=4, pady=4)
        ttk.Button(f_top, text="Agora", width=6, command=lambda: self.app.meta_mod_var.set(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))).grid(row=0, column=5, padx=2)

        # Linha 1: Autor / Título
        ttk.Label(f_top, text="Autor / Criador:").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        ttk.Entry(f_top, textvariable=self.app.meta_autor_var, width=22).grid(row=1, column=1, sticky="w", padx=4, pady=4)

        ttk.Label(f_top, text="Título do Doc:").grid(row=1, column=3, sticky="w", padx=(14, 4), pady=4)
        ttk.Entry(f_top, textvariable=self.app.meta_titulo_var, width=22).grid(row=1, column=4, sticky="w", padx=4, pady=4)

        # Linha 2: Tamanho KB / Resolução Pixels
        ttk.Label(f_top, text="Tamanho do Arquivo:").grid(row=2, column=0, sticky="w", padx=4, pady=4)
        f_tam = ttk.Frame(f_top)
        f_tam.grid(row=2, column=1, columnspan=2, sticky="w", padx=4, pady=4)
        ttk.Entry(f_tam, textvariable=self.app.meta_tamanho_var, width=9).pack(side=tk.LEFT)
        ttk.Label(f_tam, text=" KB (0 = normal)").pack(side=tk.LEFT, padx=4)

        ttk.Label(f_top, text="Resolução (Pixels):").grid(row=2, column=3, sticky="w", padx=(14, 4), pady=4)
        f_px = ttk.Frame(f_top)
        f_px.grid(row=2, column=4, columnspan=2, sticky="w", padx=4, pady=4)
        ttk.Entry(f_px, textvariable=self.app.meta_largura_px_var, width=6).pack(side=tk.LEFT)
        ttk.Label(f_px, text=" x ").pack(side=tk.LEFT)
        ttk.Entry(f_px, textvariable=self.app.meta_altura_px_var, width=6).pack(side=tk.LEFT)
        ttk.Label(f_px, text=" px").pack(side=tk.LEFT, padx=2)
        tk.Button(f_px, text="📐 Aplicar", bg="#0066cc", fg="white", font=("Segoe UI", 8, "bold"),
                  activebackground="#004499", activeforeground="white", relief=tk.RAISED, cursor="hand2",
                  command=self.aplicar_res).pack(side=tk.LEFT, padx=6)

        # Linha 3: NTFS Checkbox
        ttk.Checkbutton(f_top, text="Gravar datas de Criação/Modificação nos Atributos Reais do Windows (NTFS)",
                        variable=self.app.meta_aplicar_ntfs).grid(row=3, column=0, columnspan=6, sticky="w", padx=4, pady=(6, 2))

        # Painel da Tabela / EXIF
        f_bot = ttk.LabelFrame(self, text=" Tabela Completa de Metadados & EXIF ", padding=8)
        f_bot.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

        f_bar = ttk.Frame(f_bot)
        f_bar.pack(fill=tk.X, pady=(0, 4))
        ttk.Button(f_bar, text="🔄 Atualizar Leitura", command=self.atualizar_tabela).pack(side=tk.LEFT, padx=2)
        ttk.Button(f_bar, text="🗑️ Limpar Todos os Metadados", command=self.app.remover_metadados).pack(side=tk.LEFT, padx=4)
        ttk.Label(f_bar, text="💡 Clique duas vezes em qualquer linha para editar o valor.", foreground="#666666").pack(side=tk.LEFT, padx=10)

        f_tree = ttk.Frame(f_bot)
        f_tree.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(f_tree, columns=("chave", "valor"), show="headings")
        self.tree.heading("chave", text="Chave / Atributo")
        self.tree.heading("valor", text="Valor")
        self.tree.column("chave", width=220)
        self.tree.column("valor", width=550)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrl = ttk.Scrollbar(f_tree, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrl.set)
        scrl.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<Double-1>", self._on_double_click)

        f_rodape = ttk.Frame(self, padding=(10, 4))
        f_rodape.pack(side=tk.BOTTOM, fill=tk.X)
        tk.Button(f_rodape, text="OK / Fechar", width=14, font=("Segoe UI", 9, "bold"), command=self.destroy).pack(side=tk.RIGHT, padx=4)

    def aplicar_res(self):
        self.app.aplicar_resolucao_doc()
        self.atualizar_tabela()

    def atualizar_tabela(self):
        for it in self.tree.get_children():
            self.tree.delete(it)
        meta = self.app._ler_metadados()
        for k, v in meta.items():
            self.tree.insert("", tk.END, values=(k, str(v)))

    def _on_double_click(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        item = sel[0]
        k, v = self.tree.item(item, "values")
        self.app._popup_edit_meta(k, v, item, tree_alvo=self.tree)
