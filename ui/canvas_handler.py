# -*- coding: utf-8 -*-
"""
Mixin com toda a lógica de eventos do Canvas, Zoom, Pan, Lupa HUD e Handles de Foto
"""

import tkinter as tk
from PIL import Image, ImageTk
import numpy as np

from core.image_processing import (
    detectar_texto,
    _detectar_estilo,
    _bbox_bate
)


class CanvasHandlerMixin:
    """Mixin para App(tk.Tk) com gerenciamento de mouse e interações no Canvas."""

    def _obter_handles_foto(self):
        if not self.foto_ativa or self.foto_original is None:
            return {}
        
        fx = self.foto_x_var.get() * self.escala
        fy = self.foto_y_var.get() * self.escala
        fw = self.foto_w_var.get() * self.escala
        fh = self.foto_h_var.get() * self.escala
        raio = 6

        return {
            "nw": (fx - raio, fy - raio, fx + raio, fy + raio),
            "ne": (fx + fw - raio, fy - raio, fx + fw + raio, fy + raio),
            "se": (fx + fw - raio, fy + fh - raio, fx + fw + raio, fy + fh + raio),
            "sw": (fx - raio, fy + fh - raio, fx + raio, fy + fh + raio),
            "corpo": (fx + raio, fy + raio, fx + fw - raio, fy + fh - raio)
        }

    def _desenhar_lupa_hud(self, cx, cy, gx, gy):
        """Desenha uma lente de aumento de 10x ao lado do cursor mostrando os pixels e valores RGB/HEX."""
        self.canvas.delete("hud_lupa")
        if self.img_atual is None:
            return
            
        raio_amostra = 7  # 15x15 pixels
        xa = max(0, gx - raio_amostra)
        ya = max(0, gy - raio_amostra)
        xb = min(self.img_atual.width, gx + raio_amostra + 1)
        yb = min(self.img_atual.height, gy + raio_amostra + 1)
        
        roi = self.img_atual.crop((xa, ya, xb, yb))
        if roi.width == 0 or roi.height == 0:
            return
            
        fator = 9
        lupa_w = roi.width * fator
        lupa_h = roi.height * fator
        lupa_img = roi.resize((lupa_w, lupa_h), Image.NEAREST)
        
        cor_centro = self.img_atual.getpixel((gx, gy))[:3]
        hex_cor = f"#{cor_centro[0]:02x}{cor_centro[1]:02x}{cor_centro[2]:02x}"
        
        offset_x = 22 if (cx + lupa_w + 30) < self.canvas.winfo_width() else -(lupa_w + 22)
        offset_y = 22 if (cy + lupa_h + 45) < self.canvas.winfo_height() else -(lupa_h + 45)
        
        lx = cx + offset_x
        ly = cy + offset_y
        
        self._tk_lupa = ImageTk.PhotoImage(lupa_img)
        self.canvas.create_rectangle(lx - 2, ly - 2, lx + lupa_w + 2, ly + lupa_h + 20, fill="#11151a", outline="#00e5ff", width=2, tags="hud_lupa")
        self.canvas.create_image(lx, ly, anchor="nw", image=self._tk_lupa, tags="hud_lupa")
        
        # Pixel central destacado
        centro_rel_x = (gx - xa) * fator + fator // 2
        centro_rel_y = (gy - ya) * fator + fator // 2
        pm_x = lx + centro_rel_x
        pm_y = ly + centro_rel_y
        
        self.canvas.create_rectangle(pm_x - fator//2, pm_y - fator//2, pm_x + fator//2 + 1, pm_y + fator//2 + 1, outline="#ff0044", width=2, tags="hud_lupa")
        self.canvas.create_line(pm_x - 10, pm_y, pm_x - 3, pm_y, fill="#ffff00", width=2, tags="hud_lupa")
        self.canvas.create_line(pm_x + 3, pm_y, pm_x + 10, pm_y, fill="#ffff00", width=2, tags="hud_lupa")
        self.canvas.create_line(pm_x, pm_y - 10, pm_x, pm_y - 3, fill="#ffff00", width=2, tags="hud_lupa")
        self.canvas.create_line(pm_x, pm_y + 3, pm_x, pm_y + 10, fill="#ffff00", width=2, tags="hud_lupa")
        
        self.canvas.create_rectangle(lx + 4, ly + lupa_h + 3, lx + 16, ly + lupa_h + 15, fill=hex_cor, outline="#ffffff", tags="hud_lupa")
        self.canvas.create_text(lx + 20, ly + lupa_h + 9, anchor="w", text=f"{hex_cor} ({gx},{gy})", fill="#ffffff", font=("Consolas", 8, "bold"), tags="hud_lupa")

    def toggle_lupa(self):
        self.modo_lupa = not self.modo_lupa
        if self.modo_lupa:
            self.btn_lupa.config(bg="#f59e0b", fg="#ffffff", relief=tk.SUNKEN)
            self.canvas.config(cursor="tcross")
            self.status.config(text="🔎 LUPA HUD ATIVADA (10x): Passe o mouse pelo documento para inspecionar cada pixel.")
        else:
            if getattr(self, "tema_atual", "claro") == "vscode":
                self.btn_lupa.config(bg="#2d2d30", fg="#cccccc", relief=tk.RAISED)
            else:
                self.btn_lupa.config(bg="#f3f4f6", fg="#1f2937", relief=tk.RAISED)
            self.canvas.config(cursor="crosshair")
            self.canvas.delete("hud_lupa")
            self.status.config(text="Lupa desativada.")

    def zoom_in_doc(self):
        self.fator_zoom_manual = min(6.0, self.fator_zoom_manual * 1.25)
        self._mostrar_imagem()
        self.status.config(text=f"Zoom Documento: {int(self.fator_zoom_manual * 100)}%")

    def zoom_out_doc(self):
        self.fator_zoom_manual = max(0.25, self.fator_zoom_manual / 1.25)
        self._mostrar_imagem()
        self.status.config(text=f"Zoom Documento: {int(self.fator_zoom_manual * 100)}%")

    def zoom_100_doc(self):
        self.fator_zoom_manual = 1.0
        self._mostrar_imagem()
        self.status.config(text="Zoom Documento: 100% (Normal)")

    def on_ctrl_mousewheel(self, evento):
        if evento.delta > 0:
            self.zoom_in_doc()
        else:
            self.zoom_out_doc()

    def on_mouse_move(self, evento):
        cx = self.canvas.canvasx(evento.x)
        cy = self.canvas.canvasy(evento.y)

        # Se Pipeta ou Lupa estiver ativa, desenha a lente de aumento flutuante
        if getattr(self, "modo_pipeta", False) or getattr(self, "modo_lupa", False):
            self.canvas.config(cursor="tcross")
            if self.img_atual is not None:
                gx = int(cx / self.escala)
                gy = int(cy / self.escala)
                if 0 <= gx < self.img_atual.width and 0 <= gy < self.img_atual.height:
                    self._desenhar_lupa_hud(cx, cy, gx, gy)
                    return
        else:
            self.canvas.delete("hud_lupa")

        aba_atual = self.notebook.index(self.notebook.select())
        if aba_atual != 1 or not self.foto_ativa:
            self.canvas.config(cursor="crosshair")
            return

        handles = self._obter_handles_foto()
        if not handles:
            self.canvas.config(cursor="crosshair")
            return

        def dentro(box):
            return box[0] <= cx <= box[2] and box[1] <= cy <= box[3]

        if dentro(handles["nw"]) or dentro(handles["se"]):
            self.canvas.config(cursor="size_nw_se")
        elif dentro(handles["ne"]) or dentro(handles["sw"]):
            self.canvas.config(cursor="size_ne_sw")
        elif dentro(handles["corpo"]):
            self.canvas.config(cursor="fleur")
        else:
            self.canvas.config(cursor="crosshair")

    def on_mouse_down(self, evento):
        cx = self.canvas.canvasx(evento.x)
        cy = self.canvas.canvasy(evento.y)

        # Captura de Cor via Pipeta
        if getattr(self, "modo_pipeta", False):
            self.modo_pipeta = False
            self.btn_pipeta.config(bg="SystemButtonFace", relief=tk.GROOVE)
            self.canvas.config(cursor="crosshair")
            
            if self.img_original is not None:
                gx = int(cx / self.escala)
                gy = int(cy / self.escala)
                if 0 <= gx < self.img_original.width and 0 <= gy < self.img_original.height:
                    cor_rgb = self.img_original.getpixel((gx, gy))[:3]
                    self.cor_custom = cor_rgb
                    hex_cor = f"#{cor_rgb[0]:02x}{cor_rgb[1]:02x}{cor_rgb[2]:02x}"
                    self.btn_cor.config(bg=hex_cor)
                    self.log(f"Pipeta capturou cor: RGB{cor_rgb} ({hex_cor})")
                    self.status.config(text=f"Cor capturada da imagem: {hex_cor}")
                    self._on_param_alterado()
            return

        self.drag_start = (cx, cy)
        self.drag_moved = False

        aba_atual = self.notebook.index(self.notebook.select())
        if aba_atual == 1 and self.foto_ativa and self.foto_original is not None:
            handles = self._obter_handles_foto()
            def dentro(box):
                return box[0] <= cx <= box[2] and box[1] <= cy <= box[3]

            self.foto_box_inicial = (
                self.foto_x_var.get(), self.foto_y_var.get(),
                self.foto_w_var.get(), self.foto_h_var.get()
            )
            self.foto_drag_start = (cx, cy)

            if dentro(handles["nw"]):
                self.modo_arraste = "handle_nw"
                return
            elif dentro(handles["ne"]):
                self.modo_arraste = "handle_ne"
                return
            elif dentro(handles["se"]):
                self.modo_arraste = "handle_se"
                return
            elif dentro(handles["sw"]):
                self.modo_arraste = "handle_sw"
                return
            elif dentro(handles["corpo"]):
                self.modo_arraste = "mover_foto"
                return

        self.modo_arraste = None
        if self.rect_id:
            self.canvas.delete(self.rect_id)
            self.rect_id = None

    def on_mouse_drag(self, evento):
        if self.drag_start is None:
            return
        cx = self.canvas.canvasx(evento.x)
        cy = self.canvas.canvasy(evento.y)

        if self.modo_arraste is not None:
            ox, oy, ow, oh = self.foto_box_inicial
            sx, sy = self.foto_drag_start
            dx = (cx - sx) / self.escala
            dy = (cy - sy) / self.escala

            if self.modo_arraste == "mover_foto":
                self.foto_x_var.set(int(ox + dx))
                self.foto_y_var.set(int(oy + dy))
            elif self.modo_arraste == "handle_se":
                self.foto_w_var.set(max(15, int(ow + dx)))
                self.foto_h_var.set(max(15, int(oh + dy)))
            elif self.modo_arraste == "handle_sw":
                nw = max(15, int(ow - dx))
                self.foto_x_var.set(int(ox + (ow - nw)))
                self.foto_w_var.set(nw)
                self.foto_h_var.set(max(15, int(oh + dy)))
            elif self.modo_arraste == "handle_ne":
                nh = max(15, int(oh - dy))
                self.foto_y_var.set(int(oy + (oh - nh)))
                self.foto_w_var.set(max(15, int(ow + dx)))
                self.foto_h_var.set(nh)
            elif self.modo_arraste == "handle_nw":
                nw = max(15, int(ow - dx))
                nh = max(15, int(oh - dy))
                self.foto_x_var.set(int(ox + (ow - nw)))
                self.foto_y_var.set(int(oy + (oh - nh)))
                self.foto_w_var.set(nw)
                self.foto_h_var.set(nh)

            self._renderizar_documento()
            return

        x1, y1 = self.drag_start
        if abs(cx - x1) > 4 or abs(cy - y1) > 4:
            self.drag_moved = True
            if self.rect_id is None:
                self.rect_id = self.canvas.create_rectangle(
                    x1, y1, cx, cy, outline="#ffcc00", width=2, dash=(4, 2)
                )
            else:
                self.canvas.coords(self.rect_id, x1, y1, cx, cy)

    def on_mouse_up(self, evento):
        if self.modo_arraste is not None:
            self.modo_arraste = None
            self.drag_start = None
            return

        if self.drag_start is None:
            return

        x1c, y1c = self.drag_start
        x2c = self.canvas.canvasx(evento.x)
        y2c = self.canvas.canvasy(evento.y)
        self.drag_start = None

        if self.rect_id:
            self.canvas.delete(self.rect_id)
            self.rect_id = None

        dx = abs(x2c - x1c)
        dy = abs(y2c - y1c)

        if dx < 6 and dy < 6:
            self._tratar_clique(x1c, y1c)
            return

        if self.img_original is None:
            return

        xa, ya = int(min(x1c, x2c) / self.escala), int(min(y1c, y2c) / self.escala)
        xb, yb = int(max(x1c, x2c) / self.escala), int(max(y1c, y2c) / self.escala)

        if (xb - xa) < 6 or (yb - ya) < 6:
            return

        aba_atual = self.notebook.index(self.notebook.select())
        if aba_atual == 1 and self.foto_ativa:
            self.foto_x_var.set(xa)
            self.foto_y_var.set(ya)
            self.foto_w_var.set(xb - xa)
            self.foto_h_var.set(yb - ya)
            self._renderizar_documento()
            self.log(f"Foto 3x4 posicionada na área: ({xa},{ya}) {xb-xa}x{yb-ya}px")
            self.status.config(text=f"Foto ajustada à área selecionada ({xb-xa}x{yb-ya}px).")
            return

        self.log(f"OCR na área selecionada: ({xa},{ya}) → ({xb},{yb})")
        self.status.config(text="Detectando texto na área...")
        self.update()

        try:
            recortada = self.img_original.crop((xa, ya, xb, yb))
            caixas_rec = detectar_texto(recortada)
            
            if not caixas_rec:
                caixas_rec = [{
                    "bbox": (0, 0, xb - xa, yb - ya),
                    "texto": "",
                    "conf": 1.0
                }]

            novas_estruturadas = []
            for c in caixas_rec:
                cx1, cy1, cx2, cy2 = c["bbox"]
                gx1, gy1, gx2, gy2 = cx1 + xa, cy1 + ya, cx2 + xa, cy2 + ya
                
                arr_orig = np.array(self.img_original)
                det_bold, det_italic = _detectar_estilo(arr_orig, (gx1, gy1, gx2, gy2))
                alt_cx = max(8, gy2 - gy1)

                novas_estruturadas.append({
                    "bbox": (gx1, gy1, gx2, gy2),
                    "texto_original": c["texto"],
                    "novo_texto": c["texto"],
                    "ativo": False,
                    "fonte": "Auto (Detectar)",
                    "is_bold": det_bold,
                    "is_italic": det_italic,
                    "traco": 0.4 if det_bold else 0.0,
                    "espacamento": 0.0,
                    "nitidez": 1.0,
                    "rotacao": 0,
                    "cor_custom": None,
                    "escuridao": 20,
                    "tamanho": int(alt_cx * 0.9),
                    "ajuste_x": 0,
                    "ajuste_y": 2,
                    "blur": float(self.blur_var.get()),
                    "ruido": int(self.ruido_var.get()),
                    "arco_iris": float(self.arco_iris_var.get()),
                    "qualidade_jpg": self._obter_qualidade_jpg()
                })

            self.caixas = [c for c in self.caixas if not _bbox_bate(c["bbox"], (xa, ya, xb, yb))] + novas_estruturadas

            if novas_estruturadas:
                idx_novo = self.caixas.index(novas_estruturadas[0])
                self._selecionar_caixa(idx_novo)
            else:
                self._renderizar_documento()

            self.log(f"{len(novas_estruturadas)} caixa(s) de texto adicionada(s).")
            self.status.config(text=f"{len(novas_estruturadas)} caixa(s) prontas para edição.")
        except Exception as e:
            self.log("Erro no OCR:", str(e))
            self.status.config(text=f"Falha no OCR: {e}")
