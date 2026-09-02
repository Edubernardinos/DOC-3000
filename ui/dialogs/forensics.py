# -*- coding: utf-8 -*-
"""
Janela de Análise Forense & Veracidade
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import cv2
from PIL import Image, ImageTk


class JanelaAnaliseVeracidade(tk.Toplevel):
    def __init__(self, parent, img_original, img_modificada, caixas_modificadas, foto_info=None):
        super().__init__(parent)
        self.title("🔬 Análise de Veracidade Forense - Inspeção Antes vs Depois")
        self.geometry("1100x780")
        self.minsize(900, 650)

        self.img_original = img_original
        self.img_modificada = img_modificada
        self.caixas = caixas_modificadas
        self.foto_info = foto_info

        self.regioes = self._extrair_regioes()
        self.regiao_idx = 0
        self.overlay_val = tk.IntVar(value=100)
        self.modo_view = tk.StringVar(value="overlay")
        self.tk_img_view = None

        self._montar_ui()
        self._calcular_metricas_e_atualizar()

    def _extrair_regioes(self):
        regs = []
        for i, c in enumerate(self.caixas):
            if c.get("ativo") and c.get("novo_texto"):
                regs.append({
                    "tipo": "texto",
                    "nome": f"Texto #{i+1}: '{c.get('texto_original', '')}' → '{c.get('novo_texto', '')}'",
                    "bbox": c["bbox"]
                })
        if self.foto_info and self.foto_info.get("ativa"):
            fx, fy, fw, fh = self.foto_info["x"], self.foto_info["y"], self.foto_info["w"], self.foto_info["h"]
            regs.append({
                "tipo": "foto",
                "nome": f"Foto 3x4 Sobreposta ({fw}x{fh}px)",
                "bbox": (fx, fy, fx + fw, fy + fh)
            })

        if not regs:
            regs.append({
                "tipo": "geral",
                "nome": "Documento Completo",
                "bbox": (0, 0, self.img_original.width, self.img_original.height)
            })
        return regs

    def _montar_ui(self):
        topo = ttk.Frame(self, padding=8)
        topo.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(topo, text="Selecione o Trecho Modificado:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.combo_reg = ttk.Combobox(
            topo, values=[r["nome"] for r in self.regioes], state="readonly", width=45
        )
        self.combo_reg.current(0)
        self.combo_reg.pack(side=tk.LEFT, padx=(0, 12))
        self.combo_reg.bind("<<ComboboxSelected>>", self._on_troca_regiao)

        ttk.Label(topo, text="Modo de Inspeção:").pack(side=tk.LEFT, padx=(0, 4))
        ttk.Radiobutton(topo, text="Transparência (Overlay)", value="overlay", variable=self.modo_view, command=self._atualizar_visualizacao).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(topo, text="Lado a Lado", value="lado", variable=self.modo_view, command=self._atualizar_visualizacao).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(topo, text="Mapa de Ruído / ELA", value="ela", variable=self.modo_view, command=self._atualizar_visualizacao).pack(side=tk.LEFT, padx=2)

        f_slider = ttk.Frame(self, padding=(8, 2))
        f_slider.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(f_slider, text="Antes (Original) 0%").pack(side=tk.LEFT)
        self.scale_overlay = ttk.Scale(f_slider, from_=0, to=100, variable=self.overlay_val, command=lambda e: self._atualizar_visualizacao())
        self.scale_overlay.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        ttk.Label(f_slider, text="100% Depois (Modificado)").pack(side=tk.LEFT)

        corpo = ttk.Frame(self, padding=6)
        corpo.pack(fill=tk.BOTH, expand=True)

        f_canvas = ttk.Frame(corpo)
        f_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas_view = tk.Canvas(f_canvas, bg="#222222")
        self.canvas_view.pack(fill=tk.BOTH, expand=True)

        f_diag = ttk.LabelFrame(corpo, text="📊 Relatório Forense & Métricas", padding=8)
        f_diag.pack(side=tk.RIGHT, fill=tk.Y, padx=(6, 0))

        self.lbl_score = ttk.Label(f_diag, text="Score de Veracidade: 96%", font=("Segoe UI", 14, "bold"), foreground="#008800")
        self.lbl_score.pack(anchor="w", pady=(0, 6))

        self.txt_metricas = tk.Text(f_diag, width=42, height=22, wrap=tk.WORD, font=("Consolas", 9), bg="#f8f9fa")
        self.txt_metricas.pack(fill=tk.BOTH, expand=True)

    def _on_troca_regiao(self, event=None):
        self.regiao_idx = self.combo_reg.current()
        self._calcular_metricas_e_atualizar()

    def _calcular_metricas_e_atualizar(self):
        reg = self.regioes[self.regiao_idx]
        x1, y1, x2, y2 = reg["bbox"]
        pad = 20
        xa = max(0, x1 - pad)
        ya = max(0, y1 - pad)
        xb = min(self.img_original.width, x2 + pad)
        yb = min(self.img_original.height, y2 + pad)

        roi_orig = self.img_original.crop((xa, ya, xb, yb))
        roi_mod = self.img_modificada.crop((xa, ya, xb, yb))

        cinza_orig = cv2.cvtColor(np.array(roi_orig), cv2.COLOR_RGB2GRAY)
        cinza_mod = cv2.cvtColor(np.array(roi_mod), cv2.COLOR_RGB2GRAY)
        
        lap_orig = cv2.Laplacian(cinza_orig, cv2.CV_32F).var()
        lap_mod = cv2.Laplacian(cinza_mod, cv2.CV_32F).var()
        
        diff_ruido = abs(lap_orig - lap_mod)
        compat_ruido = max(0, min(100, int(100 - (diff_ruido / (lap_orig + 1e-5)) * 40)))

        bordas_mod = cv2.Canny(cinza_mod, 50, 150)
        densidade_borda = (bordas_mod > 0).mean() * 100
        compat_borda = max(70, min(100, int(100 - densidade_borda * 0.8)))

        lum_orig = cinza_orig.mean()
        lum_mod = cinza_mod.mean()
        diff_lum = abs(lum_orig - lum_mod)
        compat_lum = max(0, min(100, int(100 - (diff_lum / 255.0) * 100)))

        score_final = int(compat_ruido * 0.4 + compat_borda * 0.35 + compat_lum * 0.25)
        score_final = max(60, min(99, score_final))

        if score_final >= 90:
            cor = "#008800"
            veredito = "EXCELENTE (Imperceptível a olho nu)"
        elif score_final >= 80:
            cor = "#aa7700"
            veredito = "BOM (Muito consistente, pequenas variações)"
        else:
            cor = "#cc0000"
            veredito = "ATENÇÃO (Possível nitidez ou ruído em excesso)"

        self.lbl_score.config(text=f"Score: {score_final}% - {veredito}", foreground=cor)

        relatorio = (
            f"=== DIAGNÓSTICO DO TRECHO ===\n"
            f"Região: {reg['nome']}\n"
            f"Dimensões: {xb-xa} x {yb-ya} pixels\n\n"
            f"--- MÉTRICAS FORENSES ---\n"
            f"• Grão/Ruído do Papel:  {compat_ruido}%\n"
            f"• Suavidade das Bordas: {compat_borda}%\n"
            f"• Coerência Luminosa:   {compat_lum}%\n"
            f"• Índice de Camuflagem: {score_final}%\n\n"
            f"--- RECOMENDAÇÃO INTELIGENTE ---\n"
        )

        if compat_ruido < 85:
            relatorio += "💡 Dica: Ajuste o 'Ruído (Grão)' em +2 a +4 para igualar perfeitamente ao grão do scanner.\n"
        elif compat_borda < 85:
            relatorio += "💡 Dica: Aumente o 'Blur (Foco)' em +0.1 para suavizar as arestas das letras.\n"
        else:
            relatorio += "✅ A textura e o contraste estão perfeitamente harmonizados com o documento original.\n"

        self.txt_metricas.delete("1.0", tk.END)
        self.txt_metricas.insert(tk.END, relatorio)

        self._atualizar_visualizacao()

    def _atualizar_visualizacao(self):
        reg = self.regioes[self.regiao_idx]
        x1, y1, x2, y2 = reg["bbox"]
        pad = 20
        xa = max(0, x1 - pad)
        ya = max(0, y1 - pad)
        xb = min(self.img_original.width, x2 + pad)
        yb = min(self.img_original.height, y2 + pad)

        roi_orig = self.img_original.crop((xa, ya, xb, yb))
        roi_mod = self.img_modificada.crop((xa, ya, xb, yb))

        modo = self.modo_view.get()

        if modo == "overlay":
            alpha = self.overlay_val.get() / 100.0
            img_final = Image.blend(roi_orig.convert("RGBA"), roi_mod.convert("RGBA"), alpha).convert("RGB")
        elif modo == "lado":
            w = roi_orig.width
            h = roi_orig.height
            img_final = Image.new("RGB", (w * 2 + 8, h), (40, 40, 40))
            img_final.paste(roi_orig, (0, 0))
            img_final.paste(roi_mod, (w + 8, 0))
        elif modo == "ela":
            arr_orig = np.array(roi_orig, dtype=np.int16)
            arr_mod = np.array(roi_mod, dtype=np.int16)
            diff = np.abs(arr_mod - arr_orig).astype(np.uint8)
            diff_ampliada = np.clip(diff * 4, 0, 255)
            img_final = Image.fromarray(diff_ampliada)

        self.canvas_view.update()
        cw = max(200, self.canvas_view.winfo_width())
        ch = max(200, self.canvas_view.winfo_height())
        iw, ih = img_final.size
        escala = min(cw / iw, ch / ih, 3.0)
        img_view = img_final.resize((max(1, int(iw * escala)), max(1, int(ih * escala))), Image.LANCZOS)

        self.tk_img_view = ImageTk.PhotoImage(img_view)
        self.canvas_view.delete("all")
        self.canvas_view.create_image(cw // 2, ch // 2, anchor="center", image=self.tk_img_view)
