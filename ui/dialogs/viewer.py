# -*- coding: utf-8 -*-
"""
Popup Dedicado: Visualizar Resultado Final (Apenas Imagem Pura com Zoom e Lupa)
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class JanelaVisualizarResultado(tk.Toplevel):
    def __init__(self, parent, img_resultado):
        super().__init__(parent)
        self.app = parent
        self.title("Visualizar - Resultado Final")
        self.geometry("1100x850")
        self.minsize(800, 600)

        # Imagem pura sem qualquer marcação ou retângulo
        self.img_base = img_resultado.copy() if img_resultado else None
        self.zoom = 1.0
        self.modo_lupa = False
        self.tk_img = None
        self.pan_start = None

        self._montar_ui()
        if self.img_base:
            self._ajustar_inicial()

    def _montar_ui(self):
        # Barra superior limpa: apenas Lupa, Zoom e Fechar
        bar = ttk.Frame(self, padding=(8, 4))
        bar.pack(side=tk.TOP, fill=tk.X)

        self.btn_lupa = tk.Button(
            bar, text="🔎 Ativar Lupa", font=("Segoe UI", 9, "bold"),
            bg="#f3f4f6", fg="#1f2937", activebackground="#e5e7eb",
            relief=tk.RAISED, cursor="hand2", command=self.toggle_lupa
        )
        self.btn_lupa.pack(side=tk.LEFT, padx=(0, 6))

        ttk.Separator(bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6)

        ttk.Button(bar, text="🔍 -", width=3, command=self.zoom_out).pack(side=tk.LEFT, padx=1)
        self.lbl_zoom = ttk.Label(bar, text="100%", font=("Segoe UI", 9, "bold"), width=6, anchor="center")
        self.lbl_zoom.pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="🔍 +", width=3, command=self.zoom_in).pack(side=tk.LEFT, padx=1)
        ttk.Button(bar, text="100%", width=4, command=self.zoom_100).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="Ajustar à Janela", command=self.ajustar_janela).pack(side=tk.LEFT, padx=4)

        ttk.Label(
            bar, text="💡 Dica: Role a rodinha do mouse para dar Zoom e arraste para mover a imagem.",
            font=("Segoe UI", 9), foreground="#666666"
        ).pack(side=tk.LEFT, padx=12)

        tk.Button(
            bar, text="✖ Fechar", font=("Segoe UI", 9, "bold"),
            bg="#ef4444", fg="white", activebackground="#dc2626",
            relief=tk.FLAT, cursor="hand2", command=self.destroy
        ).pack(side=tk.RIGHT, padx=4)

        # Canvas da imagem ocupando 100% do espaço restante
        f_canvas = ttk.Frame(self)
        f_canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(f_canvas, bg="#1e1e1e", cursor="fleur", highlightthickness=0)
        hbar = ttk.Scrollbar(f_canvas, orient=tk.HORIZONTAL, command=self.canvas.xview)
        vbar = ttk.Scrollbar(f_canvas, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)

        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Eventos de arraste (Pan) e Zoom com a rodinha
        self.canvas.bind("<ButtonPress-1>", self._on_pan_start)
        self.canvas.bind("<B1-Motion>", self._on_pan_drag)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Motion>", self._on_mouse_move)

    def _ajustar_inicial(self):
        self.zoom = 1.0
        self._redesenhar()

    def ajustar_janela(self):
        if not self.img_base: return
        cw = max(200, self.canvas.winfo_width())
        ch = max(200, self.canvas.winfo_height())
        iw, ih = self.img_base.size
        self.zoom = min(cw / iw, ch / ih)
        self._redesenhar()

    def zoom_in(self):
        self.zoom = min(5.0, self.zoom * 1.25)
        self._redesenhar()

    def zoom_out(self):
        self.zoom = max(0.1, self.zoom / 1.25)
        self._redesenhar()

    def zoom_100(self):
        self.zoom = 1.0
        self._redesenhar()

    def _on_mousewheel(self, event):
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def toggle_lupa(self):
        self.modo_lupa = not self.modo_lupa
        if self.modo_lupa:
            self.btn_lupa.config(bg="#f59e0b", fg="white", relief=tk.SUNKEN, text="🔎 Lupa Ativa (10x)")
            self.canvas.config(cursor="crosshair")
        else:
            self.btn_lupa.config(bg="#f3f4f6", fg="#1f2937", relief=tk.RAISED, text="🔎 Ativar Lupa")
            self.canvas.config(cursor="fleur")
            self.canvas.delete("lupa_view")

    def _redesenhar(self):
        if not self.img_base: return
        self.canvas.delete("img_final")
        self.canvas.delete("lupa_view")
        
        w, h = self.img_base.size
        vw = max(10, int(w * self.zoom))
        vh = max(10, int(h * self.zoom))

        img_scaled = self.img_base.resize((vw, vh), Image.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(img_scaled)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img, tags="img_final")
        self.canvas.config(scrollregion=(0, 0, vw, vh))
        self.lbl_zoom.config(text=f"{int(self.zoom * 100)}%")

    def _on_pan_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def _on_pan_drag(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def _on_mouse_move(self, event):
        if not self.modo_lupa or not self.img_base:
            return
        self.canvas.delete("lupa_view")
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)

        # Lupa HUD 10x sobre a imagem pura
        orig_x = int(cx / self.zoom)
        orig_y = int(cy / self.zoom)
        raio_amostra = 15
        
        x1 = max(0, orig_x - raio_amostra)
        y1 = max(0, orig_y - raio_amostra)
        x2 = min(self.img_base.width, orig_x + raio_amostra)
        y2 = min(self.img_base.height, orig_y + raio_amostra)

        if x2 > x1 and y2 > y1:
            try:
                amostra = self.img_base.crop((x1, y1, x2, y2))
                tam_hud = 150
                amostra_ampliada = amostra.resize((tam_hud, tam_hud), Image.NEAREST)
                self.tk_lupa = ImageTk.PhotoImage(amostra_ampliada)
                hx, hy = cx + 20, cy + 20
                self.canvas.create_image(hx, hy, anchor="nw", image=self.tk_lupa, tags="lupa_view")
                self.canvas.create_rectangle(hx, hy, hx + tam_hud, hy + tam_hud, outline="#ffcc00", width=2, tags="lupa_view")
            except Exception:
                pass
