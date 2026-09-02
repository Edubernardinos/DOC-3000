# -*- coding: utf-8 -*-
"""
Editor de Documentos Interativo - Modo Dinâmico e Análise Forense
-----------------------------------------------------------------
Permite:
1. Aba de Texto: Substituir trechos de texto em tempo real (Live Preview) com fontes,
   estilos (Negrito, Itálico), peso/traço decimal, espaçamento entre letras (Tracking),
   nitidez, rotação, escuridão, aberração arco-íris (Laranja/Azul) e ruído cromático.
2. Aba de Foto 3x4: Adicionar fotos sobrepostas, mover e redimensionar interativamente
   pelas alças no canvas, ajustando foco, nitidez, brilho, contraste e franjas de cor.
3. 🔍 Comparador Lado a Lado Permanente (Live Split Dock): Exibe sempre embaixo a visualização
   ampliada do [ORIGINAL] vs [MODIFICADO AO VIVO] para cada seleção em tempo real!
4. 🔬 Análise de Veracidade: Comparador visual Antes vs Depois (Overlay 0-100%, ELA/Diferença)
   e cálculo de compatibilidade de ruído, luminância e score de camuflagem forense.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import os
import io
import fitz  # PyMuPDF
import easyocr
import numpy as np
from PIL import Image, ImageDraw, ImageTk, ImageFont, ImageFilter, ImageEnhance
import cv2


# ============================
# Constantes e Fontes do Sistema
# ============================

FONTS_DIR = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")

FAMILIAS_FONTES = {
    # --- Inteligente / Automático ---
    "Auto (Detectar)": {"regular": "arial.ttf", "bold": "arialbd.ttf", "italic": "ariali.ttf", "bold_italic": "arialbi.ttf"},
    
    # --- FONTES SERIFADAS (Clássicas, Cartórios, Carteirinhas, Diplomas e Documentos) ---
    "Times New Roman": {"regular": "times.ttf", "bold": "timesbd.ttf", "italic": "timesi.ttf", "bold_italic": "timesbi.ttf"},
    "Georgia": {"regular": "georgia.ttf", "bold": "georgiab.ttf", "italic": "georgiai.ttf", "bold_italic": "georgiaz.ttf"},
    "Garamond": {"regular": "GARA.TTF", "bold": "GARABD.TTF", "italic": "GARAIT.TTF", "bold_italic": "GARABD.TTF"},
    "Palatino Linotype": {"regular": "pala.ttf", "bold": "palab.ttf", "italic": "palai.ttf", "bold_italic": "palabi.ttf"},
    "Bookman Old Style": {"regular": "BOOKOS.TTF", "bold": "BOOKOSB.TTF", "italic": "BOOKOSI.TTF", "bold_italic": "BOOKOSBI.TTF"},
    "Century": {"regular": "CENTURY.TTF", "bold": "CENTURY.TTF", "italic": "CENTURY.TTF", "bold_italic": "CENTURY.TTF"},
    "Century Schoolbook": {"regular": "SCHLBKB.TTF", "bold": "SCHLBKB.TTF", "italic": "SCHLBKI.TTF", "bold_italic": "SCHLBKBI.TTF"},
    "Constantia": {"regular": "constan.ttf", "bold": "constanb.ttf", "italic": "constani.ttf", "bold_italic": "constanz.ttf"},
    "Cambria": {"regular": "cambriab.ttf", "bold": "cambriab.ttf", "italic": "cambriai.ttf", "bold_italic": "cambriaz.ttf"},
    "Baskerville": {"regular": "BASKVILL.TTF", "bold": "BASKVILL.TTF", "italic": "BASKVILL.TTF", "bold_italic": "BASKVILL.TTF"},
    "Bodoni MT": {"regular": "BOD_R.TTF", "bold": "BOD_B.TTF", "italic": "BOD_I.TTF", "bold_italic": "BOD_BI.TTF"},
    "Goudy Old Style": {"regular": "GOUDOS.TTF", "bold": "GOUDOSB.TTF", "italic": "GOUDOST.TTF", "bold_italic": "GOUDOSB.TTF"},
    "Rockwell": {"regular": "ROCK.TTF", "bold": "ROCKB.TTF", "italic": "ROCKI.TTF", "bold_italic": "ROCKBI.TTF"},
    "Caladea": {"regular": "Caladea-Regular.ttf", "bold": "Caladea-Bold.ttf", "italic": "Caladea-Italic.ttf", "bold_italic": "Caladea-BoldItalic.ttf"},
    "Amiri": {"regular": "Amiri-Regular.ttf", "bold": "Amiri-Bold.ttf", "italic": "Amiri-Italic.ttf", "bold_italic": "Amiri-BoldItalic.ttf"},
    
    # --- FONTES SEM SERIFA (Oficiais, Crachás, CNH e Identidades) ---
    "Arial": {"regular": "arial.ttf", "bold": "arialbd.ttf", "italic": "ariali.ttf", "bold_italic": "arialbi.ttf"},
    "Calibri": {"regular": "calibri.ttf", "bold": "calibrib.ttf", "italic": "calibrii.ttf", "bold_italic": "calibriz.ttf"},
    "Segoe UI": {"regular": "segoeui.ttf", "bold": "segoeuib.ttf", "italic": "segoeuii.ttf", "bold_italic": "segoeuiz.ttf"},
    "Tahoma": {"regular": "tahoma.ttf", "bold": "tahomabd.ttf", "italic": "tahoma.ttf", "bold_italic": "tahomabd.ttf"},
    "Verdana": {"regular": "verdana.ttf", "bold": "verdanab.ttf", "italic": "verdanai.ttf", "bold_italic": "verdanaz.ttf"},
    "Trebuchet MS": {"regular": "trebuc.ttf", "bold": "trebucbd.ttf", "italic": "trebucit.ttf", "bold_italic": "trebucbi.ttf"},
    "Bahnschrift": {"regular": "bahnschrift.ttf", "bold": "bahnschrift.ttf", "italic": "bahnschrift.ttf", "bold_italic": "bahnschrift.ttf"},
    "Century Gothic": {"regular": "GOTHIC.TTF", "bold": "GOTHICB.TTF", "italic": "GOTHICI.TTF", "bold_italic": "GOTHICBI.TTF"},
    "Franklin Gothic": {"regular": "framd.ttf", "bold": "framdit.ttf", "italic": "framdit.ttf", "bold_italic": "framdit.ttf"},
    "Corbel": {"regular": "corbel.ttf", "bold": "corbelb.ttf", "italic": "corbeli.ttf", "bold_italic": "corbelz.ttf"},
    "Candara": {"regular": "Candara.ttf", "bold": "Candarab.ttf", "italic": "Candarai.ttf", "bold_italic": "Candaraz.ttf"},
    "Arial Black": {"regular": "ariblk.ttf", "bold": "ariblk.ttf", "italic": "ariblk.ttf", "bold_italic": "ariblk.ttf"},
    "Impact": {"regular": "impact.ttf", "bold": "impact.ttf", "italic": "impact.ttf", "bold_italic": "impact.ttf"},
    "Comic Sans MS": {"regular": "comic.ttf", "bold": "comicbd.ttf", "italic": "comici.ttf", "bold_italic": "comicz.ttf"},
    
    # --- FONTES MONOESPAÇADAS (Datilografia, Carteirinhas e Códigos) ---
    "Courier New": {"regular": "cour.ttf", "bold": "courbd.ttf", "italic": "couri.ttf", "bold_italic": "courbi.ttf"},
    "Consolas": {"regular": "consola.ttf", "bold": "consolab.ttf", "italic": "consolai.ttf", "bold_italic": "consolaz.ttf"},
    "Lucida Console": {"regular": "lucon.ttf", "bold": "lucon.ttf", "italic": "lucon.ttf", "bold_italic": "lucon.ttf"}
}


def resolver_fonte(nome_familia, is_bold=False, is_italic=False):
    """Resolve o arquivo TTF apropriado dado o nome da família e flags de estilo."""
    if not nome_familia or nome_familia in ("auto", "Auto (Detectar)"):
        nome_familia = "Arial"
        
    variante = "regular"
    if is_bold and is_italic:
        variante = "bold_italic"
    elif is_bold:
        variante = "bold"
    elif is_italic:
        variante = "italic"
        
    fam_info = FAMILIAS_FONTES.get(nome_familia, FAMILIAS_FONTES["Arial"])
    arquivo = fam_info.get(variante, fam_info.get("regular", "arial.ttf"))
    
    if os.path.isabs(arquivo) and os.path.exists(arquivo):
        return arquivo
    
    caminho_win = os.path.join(FONTS_DIR, arquivo)
    if os.path.exists(caminho_win):
        return caminho_win
    
    caminho_regular = os.path.join(FONTS_DIR, fam_info.get("regular", "arial.ttf"))
    if os.path.exists(caminho_regular):
        return caminho_regular
        
    return arquivo


# ============================
# Núcleo de Processamento
# ============================

def pdf_para_imagem(caminho, zoom=3):
    """Converte a primeira página de um PDF em PIL.Image."""
    doc = fitz.open(caminho)
    pagina = doc[0]
    matriz = fitz.Matrix(zoom, zoom)
    pix = pagina.get_pixmap(matrix=matriz)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    doc.close()
    return img


def carregar_documento(caminho):
    """Carrega PDF, DOCX ou imagem e devolve PIL.Image RGB."""
    ext = os.path.splitext(caminho)[1].lower()
    if ext == ".pdf":
        return pdf_para_imagem(caminho)
    if ext in (".docx", ".doc"):
        resultado = _docx_para_pdf_tmp(caminho)
        if isinstance(resultado, Image.Image):
            return resultado
        return pdf_para_imagem(resultado)
    img = Image.open(caminho).convert("RGB")
    return img


def _docx_para_pdf_tmp(caminho):
    """Converte DOCX pra PDF."""
    import tempfile
    from pathlib import Path
    import subprocess

    try:
        from docx2pdf import convert
        convert(caminho, tempfile.gettempdir())
        return os.path.join(tempfile.gettempdir(), Path(caminho).stem + ".pdf")
    except Exception:
        pass

    soffice_candidates = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]
    for office in soffice_candidates:
        if os.path.exists(office):
            subprocess.run(
                [office, "--headless", "--convert-to", "pdf", caminho,
                 "--outdir", tempfile.gettempdir()],
                check=True, capture_output=True)
            return os.path.join(tempfile.gettempdir(), Path(caminho).stem + ".pdf")

    from docx import Document
    doc = Document(caminho)
    texto = [p.text for p in doc.paragraphs if p.text.strip()]
    if not texto:
        raise RuntimeError(
            "Pra abrir DOCX você precisa instalar LibreOffice:\n"
            "1. vá em https://www.libreoffice.org/download/download/\n"
            "2. instale e reinicie este app"
        )
    img = Image.new("RGB", (1200, 1600), "white")
    draw = ImageDraw.Draw(img)
    fonte = ImageFont.truetype("arial.ttf", 40)
    y = 60
    for linha in texto:
        draw.text((60, y), linha, fill="black", font=fonte)
        y += 60
    return img


_reader = None

def obter_reader():
    """OCR reader (lazy)."""
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(["pt"], gpu=False, verbose=False)
    return _reader


def _bbox_bate(box1, box2, limiar=0.25):
    """Verifica se duas caixas têm sobreposição significativa."""
    ax1, ay1, ax2, ay2 = box1
    bx1, by1, bx2, by2 = box2
    
    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)
    
    if ix2 <= ix1 or iy2 <= iy1:
        return False
        
    area_inter = (ix2 - ix1) * (iy2 - iy1)
    area_box1 = max(1, (ax2 - ax1) * (ay2 - ay1))
    
    return (area_inter / area_box1) >= limiar


def detectar_texto(pil_img):
    """Roda OCR e devolve lista de caixas: {bbox:(x1,y1,x2,y2), texto, conf}."""
    leitor = obter_reader()
    arr = np.array(pil_img)
    resultados = leitor.readtext(arr)
    caixas = []
    for pontos, texto, conf in resultados:
        pts = np.array(pontos)
        x1, y1 = pts[:, 0].min(), pts[:, 1].min()
        x2, y2 = pts[:, 0].max(), pts[:, 1].max()
        caixa = {
            "bbox": (int(x1), int(y1), int(x2), int(y2)),
            "texto": texto,
            "conf": float(conf),
        }
        caixas.extend(dividir_em_palavras(np.array(pil_img), caixa))
    return caixas


def dividir_em_palavras(arr, caixa):
    """Quebra caixas de múltiplas palavras em caixas por palavra."""
    x1, y1, x2, y2 = caixa["bbox"]
    texto = caixa["texto"]
    palavras = texto.split()
    if len(palavras) <= 1:
        return [caixa]

    roi = arr[y1:y2, x1:x2]
    if roi.size == 0:
        return [caixa]
        
    cinza = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
    _, binario = cv2.threshold(cinza, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    colunas = binario.sum(axis=0) > 0

    altura_char = y2 - y1
    gap_min = max(3, int(altura_char * 0.15))
    segmentos = []
    inicio = None
    gapista = 0
    for i, tem_tinta in enumerate(colunas):
        if tem_tinta:
            if inicio is None:
                inicio = i
            elif gapista >= gap_min:
                segmentos.append((inicio, i - gapista))
                inicio = i
            gapista = 0
        else:
            if inicio is not None:
                gapista += 1
    if inicio is not None:
        segmentos.append((inicio, len(colunas) - 1 if not tem_tinta else inicio))

    if len(segmentos) < len(palavras) or len(segmentos) != len(palavras):
        return _dividir_proporcional(x1, y1, x2, y2, palavras, caixa["conf"])

    caixas_pal = []
    for p, (s0, s1) in zip(palavras, segmentos):
        caixas_pal.append({
            "bbox": (int(x1 + s0), y1, int(x1 + s1), y2),
            "texto": p,
            "conf": caixa["conf"],
        })
    return caixas_pal


def _dividir_proporcional(x1, y1, x2, y2, palavras, conf):
    """Divide a caixa proporcionalmente ao tamanho das palavras."""
    total_chars = sum(len(p) for p in palavras)
    if total_chars == 0:
        return []
    pos = 0.0
    caixas_pal = []
    for p in palavras:
        frac = len(p) / total_chars
        pw = frac * (x2 - x1)
        caixas_pal.append({
            "bbox": (int(x1 + pos), y1, int(x1 + pos + pw), y2),
            "texto": p,
            "conf": conf,
        })
        pos += pw
    return caixas_pal


def _cor_fundo(arr, box):
    """Estima a cor de fundo ao redor da caixa de texto (mediana das bordas)."""
    x1, y1, x2, y2 = box
    pad = 4
    h, w = arr.shape[:2]
    xa, ya = max(x1 - pad, 0), max(y1 - pad, 0)
    xb, yb = min(x2 + pad, w - 1), min(y2 + pad, h - 1)
    regiao = []
    borda_cima = arr[ya:y1, xa:xb]
    borda_baixo = arr[y2:yb, xa:xb]
    for b in (borda_cima, borda_baixo):
        if b.size:
            regiao.append(b.reshape(-1, b.shape[-1]))
    if regiao:
        amostras = np.concatenate(regiao)
        cor = np.median(amostras, axis=0).astype(int)
        return tuple(int(c) for c in cor)
    return (255, 255, 255)


def _cor_texto(arr, box):
    """Cor média do texto (pixels escuros)."""
    x1, y1, x2, y2 = box
    roi = arr[y1:y2, x1:x2].reshape(-1, 3)
    if roi.size == 0:
        return (0, 0, 0)
    limi = roi.mean(axis=1)
    k = max(int(len(roi) * 0.15), 1)
    escuros = roi[np.argsort(limi)[:k]]
    cor = tuple(int(c) for c in np.median(escuros, axis=0).astype(int))
    return cor


def _detectar_estilo(arr, box):
    """Detecção de negrito e itálico: retorna (is_bold, is_italic)."""
    x1, y1, x2, y2 = box
    roi = arr[y1:y2, x1:x2]
    if roi.size == 0:
        return False, False
    cinza = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
    _, binario = cv2.threshold(cinza, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    hpfis = binario.mean(axis=1)
    valores = hpfis[hpfis > 0]
    med_len = np.median(valores) if valores.size else 0
    is_bold = bool(med_len > ((x2 - x1) * 0.06))
    is_italic = False
    return is_bold, is_italic


def _aplicar_aberracao_cromatica_subpixel(arr_rgb, deslocamento=1.2):
    """
    Desloca os canais R e B no espaço de cor RGB para criar franja Laranja na esquerda e Azul na direita.
    """
    if deslocamento <= 0.05:
        return arr_rgb
        
    h, w = arr_rgb.shape[:2]
    r = arr_rgb[:, :, 0]
    g = arr_rgb[:, :, 1]
    b = arr_rgb[:, :, 2]

    d = float(deslocamento)
    mat_r = np.float32([[1, 0, d], [0, 1, 0]])
    mat_b = np.float32([[1, 0, -d], [0, 1, 0]])

    r_shifted = cv2.warpAffine(r, mat_r, (w, h), borderMode=cv2.BORDER_REFLECT)
    b_shifted = cv2.warpAffine(b, mat_b, (w, h), borderMode=cv2.BORDER_REFLECT)

    return np.stack([r_shifted, g, b_shifted], axis=2)


def _comprimir_roi_jpg(roi_img, qualidade=75):
    """Simula artefatos de compressão JPEG real de scanners/câmeras/WhatsApp."""
    if qualidade >= 100 or qualidade <= 0:
        return roi_img
    buf = io.BytesIO()
    roi_img.save(buf, format="JPEG", quality=qualidade)
    buf.seek(0)
    return Image.open(buf).convert("RGB")


def _calcular_largura_com_espacamento(texto, font, espacamento_px=0):
    """Mede o comprimento total do texto considerando o espaçamento entre letras (tracking)."""
    if not texto:
        return 0
    if espacamento_px == 0:
        bbox = font.getbbox(texto)
        return bbox[2] - bbox[0]
        
    larg_total = 0
    for i, char in enumerate(texto):
        bbox = font.getbbox(char)
        cw = (bbox[2] - bbox[0]) if bbox else font.getlength(char)
        larg_total += cw
        if i < len(texto) - 1:
            larg_total += espacamento_px
    return larg_total


def _desenhar_texto_com_espacamento(draw, pos_inicial, texto, font, fill=255, anchor="ls", espacamento_4x=0, **kwargs):
    """Desenha texto caractere a caractere com avanço customizado de espaçamento."""
    if espacamento_4x == 0 or len(texto) <= 1:
        try:
            draw.text(pos_inicial, texto, fill=fill, font=font, anchor=anchor, **kwargs)
        except Exception:
            draw.text(pos_inicial, texto, fill=fill, font=font, **kwargs)
        return

    cur_x, cur_y = pos_inicial
    for char in texto:
        try:
            draw.text((cur_x, cur_y), char, fill=fill, font=font, anchor=anchor, **kwargs)
        except Exception:
            draw.text((cur_x, cur_y), char, fill=fill, font=font, **kwargs)
            
        bbox = font.getbbox(char)
        cw = (bbox[2] - bbox[0]) if bbox else font.getlength(char)
        cur_x += cw + espacamento_4x


def substituir_texto(pil_img, box, novo_texto, nome_fonte="Arial", is_bold=False, is_italic=False,
                     espessura_traco=0.0, escuridao=0, espacamento_letras=0, nitidez=1.0,
                     rotacao=0, cor_custom=None,
                     tamanho_fonte=None, ajuste_x=0, ajuste_y=2,
                     blur=0.5, ruido=10, arco_iris=1.2, opacidade=95, qualidade_jpg=75):
    """
    Substitui texto com espaçamento entre letras (tracking), nitidez, rotação,
    franjas subpixel cromáticas (arco-íris) e ruído cromático colorido.
    """
    img = pil_img.copy()
    arr_fundo = np.array(img)
    x1, y1, x2, y2 = box

    cor_fundo = _cor_fundo(arr_fundo, (x1, y1, x2, y2))
    cor_texto_original = _cor_texto(arr_fundo, (x1, y1, x2, y2))

    if cor_custom:
        cor_base = cor_custom
    else:
        fator_escuridao = max(0.0, min(1.0, float(escuridao) / 100.0))
        cor_base = tuple(
            max(0, min(255, int(c * (1.0 - fator_escuridao))))
            for c in cor_texto_original
        )

    # apaga o texto original na imagem
    arr_fundo[y1:y2, x1:x2] = cor_fundo
    img = Image.fromarray(arr_fundo)

    alvo_w, alvo_h = max(1, x2 - x1), max(1, y2 - y1)

    if nome_fonte in (None, "auto", "Auto (Detectar)"):
        det_bold, det_italic = _detectar_estilo(arr_fundo, (x1, y1, x2, y2))
        bold_final = is_bold or det_bold
        italic_final = is_italic or det_italic
        arquivo_fonte = resolver_fonte("Arial", is_bold=bold_final, is_italic=italic_final)
    else:
        arquivo_fonte = resolver_fonte(nome_fonte, is_bold=is_bold, is_italic=is_italic)

    if tamanho_fonte is not None and int(tamanho_fonte) > 0:
        tamanho = int(tamanho_fonte)
        try:
            fonte = ImageFont.truetype(arquivo_fonte, tamanho)
        except OSError:
            fonte = ImageFont.load_default()
    else:
        tamanho = max(alvo_h, 8)
        for _ in range(80):
            try:
                fonte = ImageFont.truetype(arquivo_fonte, tamanho)
            except OSError:
                fonte = ImageFont.load_default()
                break
            w = _calcular_largura_com_espacamento(novo_texto, fonte, espacamento_letras)
            if w <= alvo_w or tamanho <= 8:
                break
            tamanho -= 1

    w_float = _calcular_largura_com_espacamento(novo_texto, fonte, espacamento_letras)
    w = int(round(w_float))
    tx = int(round(x1 + max((alvo_w - w_float) / 2.0, 0.0) + ajuste_x if w_float <= alvo_w else x1 + ajuste_x))

    try:
        ascent, descent = fonte.getmetrics()
        baseline_y = int(round(y2 - max(descent, 0) + ajuste_y))
    except Exception:
        baseline_y = int(round(y1 + tamanho + ajuste_y))

    ESCALA = 4
    traco_float = float(espessura_traco or 0.0)
    desloc_arco = float(arco_iris or 0.0)
    esp_4x = float(espacamento_letras or 0.0) * ESCALA

    pad_box = int(max(30, int(tamanho * 0.7) + int(traco_float * 4) + int(desloc_arco * 4) + abs(int(rotacao * 2))))
    rx1 = int(max(0, min(x1, tx) - pad_box))
    ry1 = int(max(0, min(y1, baseline_y - tamanho) - pad_box))
    rx2 = int(min(img.width, max(x2, tx + w) + pad_box))
    ry2 = int(min(img.height, max(y2, baseline_y + 15) + pad_box))
    roi_w = int(max(1, rx2 - rx1))
    roi_h = int(max(1, ry2 - ry1))

    if roi_w > 0 and roi_h > 0:
        try:
            fonte_4x = ImageFont.truetype(arquivo_fonte, int(tamanho * ESCALA))
        except OSError:
            fonte_4x = ImageFont.load_default()

        rel_tx_4x = float((tx - rx1) * ESCALA)
        rel_base_y_4x = float((baseline_y - ry1) * ESCALA)

        stroke_kwargs = {}
        if traco_float > 0.01:
            stroke_px_4x = int(round(traco_float * ESCALA))
            if stroke_px_4x > 0:
                stroke_kwargs["stroke_width"] = stroke_px_4x
                stroke_kwargs["stroke_fill"] = 255

        dx_subpixel_4x = float(desloc_arco * ESCALA)

        img_mask_r = Image.new("L", (int(roi_w * ESCALA), int(roi_h * ESCALA)), 0)
        _desenhar_texto_com_espacamento(
            ImageDraw.Draw(img_mask_r),
            (rel_tx_4x + dx_subpixel_4x, rel_base_y_4x),
            novo_texto, fonte_4x, fill=255, anchor="ls", espacamento_4x=esp_4x, **stroke_kwargs
        )

        img_mask_g = Image.new("L", (int(roi_w * ESCALA), int(roi_h * ESCALA)), 0)
        _desenhar_texto_com_espacamento(
            ImageDraw.Draw(img_mask_g),
            (rel_tx_4x, rel_base_y_4x),
            novo_texto, fonte_4x, fill=255, anchor="ls", espacamento_4x=esp_4x, **stroke_kwargs
        )

        img_mask_b = Image.new("L", (int(roi_w * ESCALA), int(roi_h * ESCALA)), 0)
        _desenhar_texto_com_espacamento(
            ImageDraw.Draw(img_mask_b),
            (rel_tx_4x - dx_subpixel_4x, rel_base_y_4x),
            novo_texto, fonte_4x, fill=255, anchor="ls", espacamento_4x=esp_4x, **stroke_kwargs
        )

        mask_r_1x = img_mask_r.resize((roi_w, roi_h), Image.LANCZOS)
        mask_g_1x = img_mask_g.resize((roi_w, roi_h), Image.LANCZOS)
        mask_b_1x = img_mask_b.resize((roi_w, roi_h), Image.LANCZOS)

        if rotacao != 0:
            mask_r_1x = mask_r_1x.rotate(-rotacao, resample=Image.BICUBIC)
            mask_g_1x = mask_g_1x.rotate(-rotacao, resample=Image.BICUBIC)
            mask_b_1x = mask_b_1x.rotate(-rotacao, resample=Image.BICUBIC)

        if blur > 0.05:
            mask_r_1x = mask_r_1x.filter(ImageFilter.GaussianBlur(radius=blur))
            mask_g_1x = mask_g_1x.filter(ImageFilter.GaussianBlur(radius=blur))
            mask_b_1x = mask_b_1x.filter(ImageFilter.GaussianBlur(radius=blur))

        alpha_r = np.array(mask_r_1x, dtype=np.float32) / 255.0 * (opacidade / 100.0)
        alpha_g = np.array(mask_g_1x, dtype=np.float32) / 255.0 * (opacidade / 100.0)
        alpha_b = np.array(mask_b_1x, dtype=np.float32) / 255.0 * (opacidade / 100.0)

        roi_doc = np.array(img.crop((rx1, ry1, rx2, ry2)), dtype=np.float32)

        out_r = roi_doc[:, :, 0] * (1.0 - alpha_r) + cor_base[0] * alpha_r
        out_g = roi_doc[:, :, 1] * (1.0 - alpha_g) + cor_base[1] * alpha_g
        out_b = roi_doc[:, :, 2] * (1.0 - alpha_b) + cor_base[2] * alpha_b

        roi_composta = np.stack([out_r, out_g, out_b], axis=2)

        if ruido > 0:
            mascara_geral = (alpha_r + alpha_g + alpha_b) > 0.05
            if np.any(mascara_geral):
                noise_r = np.random.normal(0, ruido * 1.1, (roi_h, roi_w))
                noise_g = np.random.normal(0, ruido * 0.9, (roi_h, roi_w))
                noise_b = np.random.normal(0, ruido * 1.2, (roi_h, roi_w))

                roi_composta[:, :, 0] = np.clip(roi_composta[:, :, 0] + noise_r, 0, 255)
                roi_composta[:, :, 1] = np.clip(roi_composta[:, :, 1] + noise_g, 0, 255)
                roi_composta[:, :, 2] = np.clip(roi_composta[:, :, 2] + noise_b, 0, 255)

        img_roi_final = Image.fromarray(np.clip(roi_composta, 0, 255).astype(np.uint8))

        if nitidez != 1.0:
            img_roi_final = ImageEnhance.Sharpness(img_roi_final).enhance(nitidez)

        img.paste(img_roi_final, (rx1, ry1))

    if qualidade_jpg and 0 < qualidade_jpg < 100:
        pad_jpg = 10
        jx1 = int(max(0, min(x1, tx) - pad_jpg))
        jy1 = int(max(0, y1 - pad_jpg))
        jx2 = int(min(img.width, max(x2, tx + w) + pad_jpg))
        jy2 = int(min(img.height, y2 + pad_jpg))
        roi_final = img.crop((jx1, jy1, jx2, jy2))
        roi_jpg = _comprimir_roi_jpg(roi_final, qualidade=qualidade_jpg)
        img.paste(roi_jpg, (jx1, jy1))

    return img


def processar_foto_sobreposta(img_foto_pil, largura, altura, angulo=0, blur=0.0, ruido=0, arco_iris=0.8,
                              brilho=1.0, contraste=1.0, saturacao=1.0, nitidez=1.0,
                              qualidade_jpg=100, opacidade=100):
    """Processa a foto 3x4 com redimensionamento, foco, nitidez, ruído cromático e aberração."""
    if img_foto_pil is None or largura <= 4 or altura <= 4:
        return None
        
    foto = img_foto_pil.convert("RGBA")
    foto = foto.resize((int(largura), int(altura)), Image.LANCZOS)
    
    if angulo != 0:
        foto = foto.rotate(angulo, expand=True, resample=Image.BICUBIC)
        
    if brilho != 1.0:
        r, g, b, a = foto.split()
        rgb = Image.merge("RGB", (r, g, b))
        rgb = ImageEnhance.Brightness(rgb).enhance(brilho)
        nr, ng, nb = rgb.split()
        foto = Image.merge("RGBA", (nr, ng, nb, a))
        
    if contraste != 1.0:
        r, g, b, a = foto.split()
        rgb = Image.merge("RGB", (r, g, b))
        rgb = ImageEnhance.Contrast(rgb).enhance(contraste)
        nr, ng, nb = rgb.split()
        foto = Image.merge("RGBA", (nr, ng, nb, a))
        
    if saturacao != 1.0:
        r, g, b, a = foto.split()
        rgb = Image.merge("RGB", (r, g, b))
        rgb = ImageEnhance.Color(rgb).enhance(saturacao)
        nr, ng, nb = rgb.split()
        foto = Image.merge("RGBA", (nr, ng, nb, a))
        
    if nitidez != 1.0:
        r, g, b, a = foto.split()
        rgb = Image.merge("RGB", (r, g, b))
        rgb = ImageEnhance.Sharpness(rgb).enhance(nitidez)
        nr, ng, nb = rgb.split()
        foto = Image.merge("RGBA", (nr, ng, nb, a))
        
    if blur > 0.05:
        foto = foto.filter(ImageFilter.GaussianBlur(radius=blur))

    if arco_iris > 0.05:
        arr_rgba = np.array(foto)
        arr_rgb = arr_rgba[:, :, :3]
        arr_rgb_aberr = _aplicar_aberracao_cromatica_subpixel(arr_rgb, deslocamento=arco_iris)
        foto = Image.fromarray(np.dstack([arr_rgb_aberr, arr_rgba[:, :, 3]]), mode="RGBA")
        
    if ruido > 0:
        arr = np.array(foto, dtype=np.int16)
        noise_r = np.random.normal(0, ruido * 1.1, (arr.shape[0], arr.shape[1])).astype(np.int16)
        noise_g = np.random.normal(0, ruido * 0.9, (arr.shape[0], arr.shape[1])).astype(np.int16)
        noise_b = np.random.normal(0, ruido * 1.2, (arr.shape[0], arr.shape[1])).astype(np.int16)
        arr[:, :, 0] = np.clip(arr[:, :, 0] + noise_r, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] + noise_g, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] + noise_b, 0, 255)
        foto = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), mode="RGBA")
        
    if qualidade_jpg and 0 < qualidade_jpg < 100:
        buf = io.BytesIO()
        foto.convert("RGB").save(buf, format="JPEG", quality=qualidade_jpg)
        buf.seek(0)
        foto_jpg = Image.open(buf).convert("RGBA")
        foto_jpg.putalpha(foto.split()[3])
        foto = foto_jpg
        
    if opacidade < 100:
        arr = np.array(foto, dtype=np.float32)
        arr[:, :, 3] = arr[:, :, 3] * (max(0, opacidade) / 100.0)
        foto = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), mode="RGBA")
        
    return foto


def _desenhar_grade_na_imagem(img_pil, zoom_escala=1.0, passo_px=25):
    """
    Desenha linhas de réguas graduadas nos eixos X e Y com os valores de pixels
    anotados numericamente e linhas guias de referência (sem malha densa de quadradinhos).
    """
    w, h = img_pil.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_g = ImageDraw.Draw(overlay)
    fonte_px = ImageFont.load_default()

    h_regua = 16
    w_regua = 24
    
    # Faixas de fundo das réguas
    draw_g.rectangle([0, 0, w, h_regua], fill=(15, 20, 25, 220))
    draw_g.rectangle([0, 0, w_regua, h], fill=(15, 20, 25, 220))
    draw_g.rectangle([0, 0, w_regua, h_regua], fill=(10, 12, 16, 255))
    draw_g.text((2, 2), "px", fill=(0, 220, 255, 255), font=fonte_px)

    # Linhas e números do Eixo X (Superior)
    passo_x = max(20, int(passo_px))
    for x in range(w_regua, w, passo_x):
        # Linha guia vertical fina e sutil
        draw_g.line([(x, h_regua), (x, h)], fill=(0, 180, 255, 45), width=1)
        # Marcador na régua
        draw_g.line([(x, h_regua - 5), (x, h_regua)], fill=(0, 240, 255, 220), width=1)
        # Anotação numérica em pixels
        px_real = int(round((x - w_regua) / max(0.1, zoom_escala)))
        draw_g.text((x + 2, 2), f"{px_real}", fill=(200, 240, 255, 240), font=fonte_px)

    # Linhas e números do Eixo Y (Lateral)
    passo_y = max(18, int(passo_px * 0.85))
    for y in range(h_regua, h, passo_y):
        # Linha guia horizontal fina e sutil
        draw_g.line([(w_regua, y), (w, y)], fill=(0, 180, 255, 45), width=1)
        # Marcador na régua
        draw_g.line([(w_regua - 5, y), (w_regua, y)], fill=(0, 240, 255, 220), width=1)
        # Anotação numérica
        py_real = int(round((y - h_regua) / max(0.1, zoom_escala)))
        draw_g.text((2, y - 4), f"{py_real}", fill=(200, 240, 255, 240), font=fonte_px)

    # Linha Guia Central Horizontal (Dourada) com valor de pixel anotado
    mid_y = h_regua + (h - h_regua) // 2
    draw_g.line([(w_regua, mid_y), (w, mid_y)], fill=(255, 215, 0, 180), width=1)
    val_mid_y = int(round((mid_y - h_regua) / max(0.1, zoom_escala)))
    draw_g.text((w - 55, mid_y - 12), f"Y={val_mid_y}px", fill=(255, 225, 80, 255), font=fonte_px)

    # Linha Guia Central Vertical (Vermelha/Laranja) com valor de pixel anotado
    mid_x = w_regua + (w - w_regua) // 2
    draw_g.line([(mid_x, h_regua), (mid_x, h)], fill=(255, 90, 90, 170), width=1)
    val_mid_x = int(round((mid_x - w_regua) / max(0.1, zoom_escala)))
    draw_g.text((mid_x + 3, h - 14), f"X={val_mid_x}px", fill=(255, 120, 120, 255), font=fonte_px)

    return Image.alpha_composite(img_pil.convert("RGBA"), overlay).convert("RGB")


# ==========================================
# Janela de Análise Forense & Veracidade
# ==========================================

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


# ============================
# Interface gráfica Principal
# ============================

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DOC_EDITOR_3000 - Editor Profissional de Documentos & Fotos")
        self.geometry("1460x950")
        
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

        self._montar_ui()

    def _montar_ui(self):
        top = ttk.Frame(self, padding=6)
        top.pack(side=tk.TOP, fill=tk.X)

        frame_arq = ttk.LabelFrame(top, text="Documento", padding=4)
        frame_arq.pack(side=tk.LEFT, padx=4, fill=tk.Y)
        ttk.Button(frame_arq, text="Abrir Documento", command=self.abrir).pack(side=tk.TOP, fill=tk.X, pady=1)
        ttk.Button(frame_arq, text="Salvar Imagem", command=self.salvar).pack(side=tk.TOP, fill=tk.X, pady=1)
        ttk.Button(frame_arq, text="Limpar Tudo", command=self.limpar_tudo).pack(side=tk.TOP, fill=tk.X, pady=1)

        f_zm = ttk.Frame(frame_arq)
        f_zm.pack(side=tk.TOP, fill=tk.X, pady=1)
        ttk.Button(f_zm, text="🔍 -", width=3, command=self.zoom_out_doc).pack(side=tk.LEFT, padx=1)
        ttk.Button(f_zm, text="100%", width=4, command=self.zoom_100_doc).pack(side=tk.LEFT, padx=1)
        ttk.Button(f_zm, text="🔍 +", width=3, command=self.zoom_in_doc).pack(side=tk.LEFT, padx=1)

        self.btn_lupa = tk.Button(
            frame_arq, text="🔎 Lupa HUD (10x)", font=("Segoe UI", 8),
            relief=tk.GROOVE, command=self.toggle_lupa
        )
        self.btn_lupa.pack(side=tk.TOP, fill=tk.X, pady=1)

        btn_analise = tk.Button(
            frame_arq, text="🔬 Análise Forense", font=("Segoe UI", 8, "bold"),
            bg="#0066cc", fg="white", activebackground="#004499", activeforeground="white",
            relief=tk.RAISED, cursor="hand2", command=self.abrir_analise_veracidade
        )
        btn_analise.pack(side=tk.TOP, fill=tk.X, pady=2)

        self.notebook = ttk.Notebook(top)
        self.notebook.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        # ==========================================
        # ABA 1: EDIÇÃO DE TEXTO
        # ==========================================
        tab_texto = ttk.Frame(self.notebook, padding=4)
        self.notebook.add(tab_texto, text=" 📝 1. Editar Texto (OCR / Substituição) ")

        # Linha 1 da aba de texto
        l1 = ttk.Frame(tab_texto)
        l1.pack(fill=tk.X, pady=1)

        ttk.Label(l1, text="Buscar:").pack(side=tk.LEFT, padx=(0, 2))
        self.busca = ttk.Entry(l1, width=11)
        self.busca.pack(side=tk.LEFT, padx=(0, 4))
        self.busca.bind("<KeyRelease>", self.on_busca)

        ttk.Label(l1, text="Original:").pack(side=tk.LEFT, padx=(0, 2))
        self.lbl_orig = ttk.Label(l1, text="(nenhum)", font=("Segoe UI", 9, "italic"), foreground="#0055aa")
        self.lbl_orig.pack(side=tk.LEFT, padx=(0, 6))

        ttk.Label(l1, text="Novo:").pack(side=tk.LEFT, padx=(0, 2))
        self.entrada = ttk.Entry(l1, width=16)
        self.entrada.pack(side=tk.LEFT, padx=(0, 4))
        self.entrada.bind("<KeyRelease>", lambda e: self._on_param_alterado())

        self.cor_custom = None
        self.btn_cor = tk.Button(l1, text="🎨 Cor", width=5, relief=tk.GROOVE, command=self.escolher_cor_texto)
        self.btn_cor.pack(side=tk.LEFT, padx=1)

        self.btn_pipeta = tk.Button(l1, text="💉 Pipeta", width=7, relief=tk.GROOVE, command=self.ativar_pipeta)
        self.btn_pipeta.pack(side=tk.LEFT, padx=(1, 3))

        ttk.Button(l1, text="🔄 Restaurar", command=self.restaurar_caixa).pack(side=tk.LEFT, padx=2)
        ttk.Button(l1, text="🗑️ Excluir", command=self.excluir_caixa).pack(side=tk.LEFT, padx=2)

        # Linha 2 da aba de texto (Fonte, Estilo, Traço, Espaçamento, Tamanho e Rotação)
        l2 = ttk.Frame(tab_texto)
        l2.pack(fill=tk.X, pady=1)

        ttk.Label(l2, text="Fonte:").pack(side=tk.LEFT, padx=(0, 2))
        self.fonte_var = tk.StringVar(value="Auto (Detectar)")
        self.combo_fontes = ttk.Combobox(
            l2, textvariable=self.fonte_var, values=list(FAMILIAS_FONTES.keys()),
            state="readonly", width=12
        )
        self.combo_fontes.pack(side=tk.LEFT, padx=(0, 3))
        self.combo_fontes.bind("<<ComboboxSelected>>", lambda e: self._on_param_alterado())

        self.bold_var = tk.BooleanVar(value=False)
        self.check_bold = ttk.Checkbutton(l2, text="Negrito", variable=self.bold_var, command=self._on_param_alterado)
        self.check_bold.pack(side=tk.LEFT, padx=(0, 2))

        self.italic_var = tk.BooleanVar(value=False)
        self.check_italic = ttk.Checkbutton(l2, text="Itálico", variable=self.italic_var, command=self._on_param_alterado)
        self.check_italic.pack(side=tk.LEFT, padx=(0, 3))

        ttk.Label(l2, text="Traço:").pack(side=tk.LEFT, padx=(0, 2))
        self.traco_var = tk.DoubleVar(value=0.0)
        self.spin_traco = ttk.Spinbox(l2, from_=0.0, to=5.0, increment=0.2, width=3, textvariable=self.traco_var, command=self._on_param_alterado)
        self.spin_traco.pack(side=tk.LEFT, padx=1)
        ttk.Button(l2, text="-", width=2, command=self.diminuir_traco).pack(side=tk.LEFT, padx=1)
        ttk.Button(l2, text="+", width=2, command=self.aumentar_traco).pack(side=tk.LEFT, padx=(1, 3))

        # Espaçamento entre Letras (Tracking) Milimétrico (0.2 em 0.2px)
        ttk.Label(l2, text="Espaço:").pack(side=tk.LEFT, padx=(0, 2))
        self.espacamento_var = tk.DoubleVar(value=0.0)
        self.spin_esp = ttk.Spinbox(l2, from_=-10.0, to=40.0, increment=0.2, width=4, textvariable=self.espacamento_var, command=self._on_param_alterado)
        self.spin_esp.pack(side=tk.LEFT, padx=1)
        ttk.Button(l2, text="-", width=2, command=self.diminuir_espacamento).pack(side=tk.LEFT, padx=1)
        ttk.Button(l2, text="+", width=2, command=self.aumentar_espacamento).pack(side=tk.LEFT, padx=(1, 3))

        ttk.Label(l2, text="Tam:").pack(side=tk.LEFT, padx=(0, 2))
        self.tamanho_var = tk.IntVar(value=24)
        self.spin_tam = ttk.Spinbox(l2, from_=6, to=200, width=3, textvariable=self.tamanho_var, command=self._on_param_alterado)
        self.spin_tam.pack(side=tk.LEFT, padx=1)
        ttk.Button(l2, text="A-", width=2, command=self.diminuir_fonte).pack(side=tk.LEFT, padx=1)
        ttk.Button(l2, text="A+", width=2, command=self.aumentar_fonte).pack(side=tk.LEFT, padx=(1, 3))

        ttk.Label(l2, text="Girar:").pack(side=tk.LEFT, padx=(0, 1))
        self.rotacao_var = tk.IntVar(value=0)
        ttk.Spinbox(l2, from_=-90, to=90, increment=1, width=3, textvariable=self.rotacao_var, command=self._on_param_alterado).pack(side=tk.LEFT, padx=1)
        ttk.Label(l2, text="°").pack(side=tk.LEFT, padx=(0, 3))

        ttk.Label(l2, text="Y:").pack(side=tk.LEFT, padx=(0, 1))
        self.ajuste_y_var = tk.IntVar(value=2)
        ttk.Spinbox(l2, from_=-50, to=50, width=3, textvariable=self.ajuste_y_var, command=self._on_param_alterado).pack(side=tk.LEFT, padx=1)

        ttk.Label(l2, text="X:").pack(side=tk.LEFT, padx=(1, 1))
        self.ajuste_x_var = tk.IntVar(value=0)
        ttk.Spinbox(l2, from_=-50, to=50, width=3, textvariable=self.ajuste_x_var, command=self._on_param_alterado).pack(side=tk.LEFT, padx=1)

        # Linha 3 da aba de texto (Degradação, Nitidez, Ruído Cromático e Arco-Íris Subpixel)
        l3 = ttk.Frame(tab_texto)
        l3.pack(fill=tk.X, pady=1)

        ttk.Label(l3, text="🎨 Realismo:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 3))

        ttk.Label(l3, text="Nitidez:").pack(side=tk.LEFT, padx=(0, 2))
        self.nitidez_var = tk.DoubleVar(value=1.0)
        self.spin_nit = ttk.Spinbox(l3, from_=0.5, to=3.0, increment=0.1, width=3, textvariable=self.nitidez_var, command=self._on_param_alterado)
        self.spin_nit.pack(side=tk.LEFT, padx=1)
        ttk.Button(l3, text="-", width=2, command=self.diminuir_nitidez).pack(side=tk.LEFT, padx=1)
        ttk.Button(l3, text="+", width=2, command=self.aumentar_nitidez).pack(side=tk.LEFT, padx=(1, 3))

        ttk.Label(l3, text="Escuro:").pack(side=tk.LEFT, padx=(0, 2))
        self.escuridao_var = tk.IntVar(value=20)
        self.spin_esc = ttk.Spinbox(l3, from_=0, to=100, increment=5, width=3, textvariable=self.escuridao_var, command=self._on_param_alterado)
        self.spin_esc.pack(side=tk.LEFT, padx=1)
        ttk.Button(l3, text="-", width=2, command=self.diminuir_escuridao).pack(side=tk.LEFT, padx=1)
        ttk.Button(l3, text="+", width=2, command=self.aumentar_escuridao).pack(side=tk.LEFT, padx=(1, 3))

        ttk.Label(l3, text="Blur:").pack(side=tk.LEFT, padx=(0, 2))
        self.blur_var = tk.DoubleVar(value=0.5)
        self.spin_blur = ttk.Spinbox(l3, from_=0.0, to=4.0, increment=0.1, width=3, textvariable=self.blur_var, command=self._on_param_alterado)
        self.spin_blur.pack(side=tk.LEFT, padx=1)
        ttk.Button(l3, text="-", width=2, command=self.diminuir_blur).pack(side=tk.LEFT, padx=1)
        ttk.Button(l3, text="+", width=2, command=self.aumentar_blur).pack(side=tk.LEFT, padx=(1, 3))

        ttk.Label(l3, text="Grão:").pack(side=tk.LEFT, padx=(0, 2))
        self.ruido_var = tk.IntVar(value=10)
        self.spin_ruido = ttk.Spinbox(l3, from_=0, to=60, increment=2, width=3, textvariable=self.ruido_var, command=self._on_param_alterado)
        self.spin_ruido.pack(side=tk.LEFT, padx=1)
        ttk.Button(l3, text="-", width=2, command=self.diminuir_ruido).pack(side=tk.LEFT, padx=1)
        ttk.Button(l3, text="+", width=2, command=self.aumentar_ruido).pack(side=tk.LEFT, padx=(1, 3))

        ttk.Label(l3, text="🌈 Arco-Íris:").pack(side=tk.LEFT, padx=(0, 2))
        self.arco_iris_var = tk.DoubleVar(value=1.2)
        self.spin_arco = ttk.Spinbox(l3, from_=0.0, to=4.0, increment=0.2, width=3, textvariable=self.arco_iris_var, command=self._on_param_alterado)
        self.spin_arco.pack(side=tk.LEFT, padx=1)
        ttk.Button(l3, text="-", width=2, command=self.diminuir_arco_iris).pack(side=tk.LEFT, padx=1)
        ttk.Button(l3, text="+", width=2, command=self.aumentar_arco_iris).pack(side=tk.LEFT, padx=(1, 3))

        ttk.Label(l3, text="JPG:").pack(side=tk.LEFT, padx=(0, 2))
        self.jpg_var = tk.StringVar(value="Leve (75%)")
        self.combo_jpg = ttk.Combobox(
            l3, textvariable=self.jpg_var,
            values=["Desativado (100%)", "Leve (75%)", "Médio (50%)", "Forte (30%)", "Muito Forte (15%)"],
            state="readonly", width=11
        )
        self.combo_jpg.pack(side=tk.LEFT, padx=(0, 3))
        self.combo_jpg.bind("<<ComboboxSelected>>", lambda e: self._on_param_alterado())

        ttk.Button(l3, text="Nítido", width=5, command=self.preset_nitido).pack(side=tk.LEFT, padx=1)
        ttk.Button(l3, text="Foto/Scan", width=7, command=self.preset_scan).pack(side=tk.LEFT, padx=1)
        ttk.Button(l3, text="WhatsApp", width=7, command=self.preset_whatsapp).pack(side=tk.LEFT, padx=1)

        # ==========================================
        # ABA 3: METADADOS (EXIF)
        # ==========================================
        tab_meta = ttk.Frame(self.notebook, padding=4)
        self.notebook.add(tab_meta, text=" 📊 3. Metadados (EXIF) ")

        m1 = ttk.Frame(tab_meta)
        m1.pack(fill=tk.BOTH, expand=True)

        ttk.Button(m1, text="🔄 Atualizar", command=self.atualizar_metadados).pack(side=tk.LEFT, padx=2)
        ttk.Button(m1, text="🗑️ Remover Todos", command=self.remover_metadados).pack(side=tk.LEFT, padx=2)

        self.tree_metas = ttk.Treeview(m1, columns=("chave", "valor"), show="headings", height=15)
        self.tree_metas.heading("chave", text="Chave")
        self.tree_metas.heading("valor", text="Valor")
        self.tree_metas.column("chave", width=180)
        self.tree_metas.column("valor", width=400)
        self.tree_metas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrl_meta = ttk.Scrollbar(m1, command=self.tree_metas.yview)
        self.tree_metas.configure(yscrollcommand=scrl_meta.set)
        scrl_meta.pack(side=tk.LEFT, fill=tk.Y)

        f_edit = ttk.Frame(tab_meta)
        f_edit.pack(side=tk.BOTTOM, fill=tk.X)
        tk.Label(f_edit, text="💡 Clique duplo na lista pra editar. Remover limpa EXIF ao salvar.").pack(anchor="w")
        self.tree_metas.bind("<Double-1>", self._editar_meta)
        self.atualizar_metadados()

        # ==========================================
        # ABA 2: FOTO 3x4 Sobreposta
        # ==========================================
        tab_foto = ttk.Frame(self.notebook, padding=4)
        self.notebook.add(tab_foto, text=" 🖼️ 2. Foto 3x4 / Imagem Sobreposta ")

        f1 = ttk.Frame(tab_foto)
        f1.pack(fill=tk.X, pady=1)

        ttk.Button(f1, text="📂 Carregar Foto (3x4)", command=self.carregar_foto).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(f1, text="🗑️ Remover Foto", command=self.remover_foto).pack(side=tk.LEFT, padx=(0, 6))

        self.lbl_foto_status = ttk.Label(f1, text="(Nenhuma foto 3x4 carregada)", font=("Segoe UI", 9, "italic"), foreground="#888888")
        self.lbl_foto_status.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Label(f1, text="💡 Arraste o corpo da foto para mover ou puxe os cantos para redimensionar!", foreground="#007700", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=4)

        f2 = ttk.Frame(tab_foto)
        f2.pack(fill=tk.X, pady=1)

        ttk.Label(f2, text="Posição X:").pack(side=tk.LEFT, padx=(0, 2))
        self.foto_x_var = tk.IntVar(value=50)
        ttk.Spinbox(f2, from_=-500, to=4000, width=5, textvariable=self.foto_x_var, command=self._on_foto_alterada).pack(side=tk.LEFT, padx=1)

        ttk.Label(f2, text="Y:").pack(side=tk.LEFT, padx=(4, 2))
        self.foto_y_var = tk.IntVar(value=50)
        ttk.Spinbox(f2, from_=-500, to=4000, width=5, textvariable=self.foto_y_var, command=self._on_foto_alterada).pack(side=tk.LEFT, padx=(1, 6))

        ttk.Label(f2, text="Largura:").pack(side=tk.LEFT, padx=(0, 2))
        self.foto_w_var = tk.IntVar(value=180)
        ttk.Spinbox(f2, from_=10, to=2000, width=4, textvariable=self.foto_w_var, command=self._on_foto_alterada).pack(side=tk.LEFT, padx=1)

        ttk.Label(f2, text="Altura:").pack(side=tk.LEFT, padx=(4, 2))
        self.foto_h_var = tk.IntVar(value=240)
        ttk.Spinbox(f2, from_=10, to=2000, width=4, textvariable=self.foto_h_var, command=self._on_foto_alterada).pack(side=tk.LEFT, padx=(1, 4))

        ttk.Button(f2, text="Tam -", width=5, command=self.diminuir_tam_foto).pack(side=tk.LEFT, padx=1)
        ttk.Button(f2, text="Tam +", width=5, command=self.aumentar_tam_foto).pack(side=tk.LEFT, padx=(1, 6))

        ttk.Label(f2, text="Girar:").pack(side=tk.LEFT, padx=(0, 2))
        self.foto_rot_var = tk.IntVar(value=0)
        ttk.Spinbox(f2, from_=-360, to=360, increment=90, width=4, textvariable=self.foto_rot_var, command=self._on_foto_alterada).pack(side=tk.LEFT, padx=1)
        ttk.Label(f2, text="°").pack(side=tk.LEFT, padx=(0, 6))

        ttk.Button(f2, text="3x4 Carteirinha", command=self.preset_foto_3x4).pack(side=tk.LEFT, padx=2)
        ttk.Button(f2, text="Tamanho Original", command=self.preset_foto_orig).pack(side=tk.LEFT, padx=2)

        f3 = ttk.Frame(tab_foto)
        f3.pack(fill=tk.X, pady=1)

        ttk.Label(f3, text="🎨 Realismo Foto:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 4))

        ttk.Label(f3, text="Nitidez:").pack(side=tk.LEFT, padx=(0, 2))
        self.foto_nitidez_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(f3, from_=0.5, to=3.0, increment=0.1, width=3, textvariable=self.foto_nitidez_var, command=self._on_foto_alterada).pack(side=tk.LEFT, padx=1)

        ttk.Label(f3, text="Foco/Blur:").pack(side=tk.LEFT, padx=(3, 2))
        self.foto_blur_var = tk.DoubleVar(value=0.4)
        ttk.Spinbox(f3, from_=0.0, to=5.0, increment=0.1, width=3, textvariable=self.foto_blur_var, command=self._on_foto_alterada).pack(side=tk.LEFT, padx=1)

        ttk.Label(f3, text="Grão:").pack(side=tk.LEFT, padx=(3, 2))
        self.foto_ruido_var = tk.IntVar(value=8)
        ttk.Spinbox(f3, from_=0.0, to=60, increment=2, width=3, textvariable=self.foto_ruido_var, command=self._on_foto_alterada).pack(side=tk.LEFT, padx=1)

        ttk.Label(f3, text="🌈 Arco-Íris:").pack(side=tk.LEFT, padx=(2, 2))
        self.foto_arco_iris_var = tk.DoubleVar(value=0.8)
        ttk.Spinbox(f3, from_=0.0, to=4.0, increment=0.2, width=3, textvariable=self.foto_arco_iris_var, command=self._on_foto_alterada).pack(side=tk.LEFT, padx=1)

        ttk.Label(f3, text="Brilho:").pack(side=tk.LEFT, padx=(3, 2))
        self.foto_brilho_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(f3, from_=0.4, to=1.8, increment=0.05, width=4, textvariable=self.foto_brilho_var, command=self._on_foto_alterada).pack(side=tk.LEFT, padx=1)

        ttk.Label(f3, text="Contraste:").pack(side=tk.LEFT, padx=(3, 2))
        self.foto_contraste_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(f3, from_=0.4, to=2.0, increment=0.05, width=4, textvariable=self.foto_contraste_var, command=self._on_foto_alterada).pack(side=tk.LEFT, padx=1)

        ttk.Label(f3, text="JPG:").pack(side=tk.LEFT, padx=(3, 2))
        self.foto_jpg_var = tk.StringVar(value="Leve (75%)")
        self.combo_foto_jpg = ttk.Combobox(
            f3, textvariable=self.foto_jpg_var,
            values=["Desativado (100%)", "Leve (75%)", "Médio (50%)", "Forte (30%)", "Muito Forte (15%)"],
            state="readonly", width=11
        )
        self.combo_foto_jpg.pack(side=tk.LEFT, padx=(0, 4))
        self.combo_foto_jpg.bind("<<ComboboxSelected>>", lambda e: self._on_foto_alterada())

        # ---- Layout principal: esquerda log, centro documento, DIREITA comparador ao vivo ----
        centro = ttk.Frame(self)
        centro.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)

        # 1. Esquerda: Log / Histórico (compacto)
        frame_log = ttk.LabelFrame(centro, text="Histórico", padding=4)
        frame_log.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 4))
        self.texto_log = tk.Text(frame_log, width=20, height=22, wrap=tk.WORD, font=("Consolas", 8))
        self.texto_log.pack(side=tk.LEFT, fill=tk.Y)
        scrol = ttk.Scrollbar(frame_log, command=self.texto_log.yview)
        scrol.pack(side=tk.RIGHT, fill=tk.Y)
        self.texto_log.configure(yscrollcommand=scrol.set)

        # 2. Direita: Painel Lateral Fixo de Comparação Lado a Lado em Tempo Real (>>>)
        self.frame_preview_dock = ttk.LabelFrame(centro, text="🔍 Visualização Lado a Lado (Ao Vivo)", padding=6)
        self.frame_preview_dock.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(4, 0))

        bar_dock = ttk.Frame(self.frame_preview_dock)
        bar_dock.pack(side=tk.TOP, fill=tk.X, pady=(0, 4))

        ttk.Label(bar_dock, text="Zoom:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 2))
        self.preview_zoom_var = tk.DoubleVar(value=2.5)
        for z_label, z_val in [("1x", 1.0), ("1.5x", 1.5), ("2x", 2.0), ("2.5x", 2.5), ("3x", 3.0), ("4x", 4.0)]:
            ttk.Radiobutton(bar_dock, text=z_label, value=z_val, variable=self.preview_zoom_var, command=self._atualizar_preview_lado_a_lado).pack(side=tk.LEFT, padx=1)

        self.preview_grid_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(bar_dock, text="📐 Grade", variable=self.preview_grid_var, command=self._atualizar_preview_lado_a_lado).pack(side=tk.LEFT, padx=(6, 2))

        self.preview_grid_passo_var = tk.IntVar(value=14)
        ttk.Spinbox(bar_dock, from_=6, to=50, width=3, textvariable=self.preview_grid_passo_var, command=self._atualizar_preview_lado_a_lado).pack(side=tk.LEFT, padx=1)
        ttk.Label(bar_dock, text="px").pack(side=tk.LEFT, padx=(0, 2))

        self.lbl_dock_info = ttk.Label(self.frame_preview_dock, text="💡 Selecione qualquer palavra no documento.", foreground="#0066cc", font=("Segoe UI", 9))
        self.lbl_dock_info.pack(side=tk.TOP, fill=tk.X, pady=(0, 4))

        # Canvas do Preview Lateral com Scrollbars dedicadas
        f_cp = ttk.Frame(self.frame_preview_dock)
        f_cp.pack(fill=tk.BOTH, expand=True)

        self.canvas_preview = tk.Canvas(f_cp, bg="#1e1e1e", width=460, highlightthickness=0)
        h_prev_scrol = ttk.Scrollbar(f_cp, orient=tk.HORIZONTAL, command=self.canvas_preview.xview)
        v_prev_scrol = ttk.Scrollbar(f_cp, orient=tk.VERTICAL, command=self.canvas_preview.yview)
        self.canvas_preview.configure(xscrollcommand=h_prev_scrol.set, yscrollcommand=v_prev_scrol.set)

        h_prev_scrol.pack(side=tk.BOTTOM, fill=tk.X)
        v_prev_scrol.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas_preview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 3. Centro: Canvas do Documento Principal
        frame_canvas = ttk.Frame(centro)
        frame_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(frame_canvas, bg="#333333", cursor="crosshair")
        hbar = ttk.Scrollbar(frame_canvas, orient=tk.HORIZONTAL, command=self.canvas.xview)
        vbar = ttk.Scrollbar(frame_canvas, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

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
            self.status.config(text="💉 PIPETA ATIVA: Clique em qualquer letra ou pixel do documento para puxar a cor exata.")

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
                    ruido=cx.get("ruido", 10),
                    arco_iris=cx.get("arco_iris", 1.2),
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
                text="💡 Selecione qualquer palavra no documento acima para ver o comparador Lado a Lado aqui.",
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

        # Decide se coloca lado a lado ou empilhado com base na largura do painel
        cw = max(380, self.canvas_preview.winfo_width())
        modo_lado_a_lado = (zw * 2 + margem * 3) <= max(cw, 460)

        if modo_lado_a_lado:
            total_w = zw * 2 + margem * 3
            total_h = zh + cabecalho + margem * 2

            prancha = Image.new("RGB", (total_w, total_h), (25, 25, 25))
            draw_p = ImageDraw.Draw(prancha)
            fonte_p = ImageFont.load_default()

            draw_p.text((margem + 2, 7), f"⬅️ ORIGINAL ({titulo_info})", fill=(140, 200, 255), font=fonte_p)
            draw_p.text((margem * 2 + zw + 2, 7), "➡️ MODIFICADO (AO VIVO)", fill=(130, 255, 140), font=fonte_p)

            prancha.paste(view_orig, (margem, cabecalho + margem))
            prancha.paste(view_mod, (margem * 2 + zw, cabecalho + margem))

            draw_p.rectangle([margem - 1, cabecalho + margem - 1, margem + zw, cabecalho + margem + zh], outline=(60, 120, 180), width=2)
            draw_p.rectangle([margem * 2 + zw - 1, cabecalho + margem - 1, margem * 2 + zw * 2, cabecalho + margem + zh], outline=(40, 160, 70), width=2)
        else:
            # Empilhado verticalmente
            total_w = max(zw + margem * 2, 360)
            total_h = (zh + cabecalho + margem) * 2 + margem

            prancha = Image.new("RGB", (total_w, total_h), (25, 25, 25))
            draw_p = ImageDraw.Draw(prancha)
            fonte_p = ImageFont.load_default()

            # Bloco 1: Original
            draw_p.text((margem + 2, 6), f"⬅️ ORIGINAL: {titulo_info}", fill=(140, 200, 255), font=fonte_p)
            prancha.paste(view_orig, (margem, cabecalho + 4))
            draw_p.rectangle([margem - 1, cabecalho + 3, margem + zw, cabecalho + 4 + zh], outline=(60, 120, 180), width=2)

            # Bloco 2: Modificado
            y_bloco2 = cabecalho + 4 + zh + espaco_entre
            draw_p.text((margem + 2, y_bloco2), "➡️ MODIFICADO (AO VIVO):", fill=(130, 255, 140), font=fonte_p)
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

    # --- Mouse, Canvas & Manipulação Direta por Alças (Handles) ---

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
            self.btn_lupa.config(bg="#ffcc00", relief=tk.SUNKEN)
            self.canvas.config(cursor="tcross")
            self.status.config(text="🔎 LUPA HUD ATIVADA (10x): Passe o mouse pelo documento para inspecionar cada pixel.")
        else:
            self.btn_lupa.config(bg="SystemButtonFace", relief=tk.GROOVE)
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

    def _exif_tag_nome(self, tag_id):
        from PIL.ExifTags import TAGS
        return TAGS.get(tag_id, f"Tag {tag_id}")

    def _ler_metadados(self):
        """Retorna dict do EXIF da imagem atual."""
        if self.img_atual is None:
            return {}
        try:
            exif = self.img_atual.getexif()
            return {self._exif_tag_nome(k): v for k, v in exif.items()}
        except Exception:
            return {}

    def atualizar_metadados(self):
        """Atualiza lista EXIF no treeview."""
        meta = self._ler_metadados()
        for item in self.tree_metas.get_children():
            self.tree_metas.delete(item)
        for chave, valor in meta.items():
            self.tree_metas.insert("", tk.END, values=(chave, str(valor)))

    def remover_metadados(self):
        """Remove EXIF e marca img para salvar limpo."""
        self._sem_metadados = True
        self.log("Metadados marcados para remoção. Salve para gerar imagem limpa.")
        self.status.config(text="Metadados serão removidos ao salvar.")

    def _editar_meta(self, evento):
        item = self.tree_metas.selection()[0]
        chave, valor = self.tree_metas.item(item, "values")
        self._popup_edit_meta(chave, valor, item)

    def _popup_edit_meta(self, chave, valor, item):
        dialog = tk.Toplevel(self)
        dialog.title(f"Editar {chave}")
        tk.Label(dialog, text=f"{chave}:").pack(side=tk.LEFT)
        ent = tk.Entry(dialog, width=50)
        ent.pack(side=tk.LEFT)
        ent.insert(0, valor)
        def ok():
            self.tree_metas.item(item, values=(chave, ent.get()))
            self.log(f"{chave} editado na visualização (EXIF só se salvar com piexif)")
            dialog.destroy()
        tk.Button(dialog, text="OK", command=ok).pack(side=tk.RIGHT)

    def abrir_analise_veracidade(self):
        if not hasattr(self, "img_atual") or self.img_atual is None:
            messagebox.showwarning("Sem documento", "Carregue um documento primeiro.")
            return
        JanelaAnaliseVeracidade(
            self, self.img_original, self.img_atual, self.caixas,
            foto_info={"ativa": self.foto_ativa, "x": self.foto_x_var.get(), "y": self.foto_y_var.get(),
                       "w": self.foto_w_var.get(), "h": self.foto_h_var.get()} if self.foto_ativa else None
        )

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
        self._mostrar_imagem()
        self._atualizar_preview_lado_a_lado()

    def _selecionar_caixa(self, indice):
        if indice < 0 or indice >= len(self.caixas):
            return
        self.selecionada = indice
        cx = self.caixas[indice]

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
        self.ruido_var.set(cx.get("ruido", 10))
        self.arco_iris_var.set(cx.get("arco_iris", 1.2))

        jpg_val = cx.get("qualidade_jpg", 75)
        for opt in ["Desativado (100%)", "Leve (75%)", "Médio (50%)", "Forte (30%)", "Muito Forte (15%)"]:
            if str(jpg_val) in opt:
                self.jpg_var.set(opt)
                break

        self.notebook.select(0)
        self._mostrar_imagem()

    def _obter_abas_metadados(self):
        """Retorna dict com abas por tipo: 'Imagem' (EXIF), 'PDF' (pymupdf), 'DOCX'."""
        self._atualizar_preview_lado_a_lado()
        self.status.config(text=f"Editando '{cx.get('texto_original', '')}'.")
        self.entrada.focus_set()
        self.entrada.selection_range(0, tk.END)

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
        self.remover_foto()
        self._mostrar_imagem()
        self._atualizar_preview_lado_a_lado()
        self.status.config(text=f"Documento carregado: {os.path.basename(caminho)}")
        self.log(f"Carregado: {os.path.basename(caminho)}")

    def _mostrar_imagem(self):
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
        self.lbl_orig.config(text="(nenhum)")
        self.entrada.delete(0, tk.END)
        self.remover_foto()
        if self.img_original is not None:
            self.img_atual = self.img_original.copy()
        self._mostrar_imagem()
        self._atualizar_preview_lado_a_lado()
        self.log("Todas as caixas e fotos foram limpas.")
        self.status.config(text="Limpo!")

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
        if ext == ".pdf":
            self.img_atual.save(caminho, "PDF", resolution=100.0)
        else:
            self.img_atual.save(caminho)
            
        self.log(f"Salvo em: {caminho}")
        self.status.config(text=f"Documento salvo em: {caminho}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
