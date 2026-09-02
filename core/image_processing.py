# -*- coding: utf-8 -*-
"""
Motor de Processamento de Imagem, OCR, Tipografia e Filtros Forenses
"""

import os
import io
import fitz  # PyMuPDF
import easyocr
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import cv2

from .fonts import resolver_fonte


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
    """OCR reader (lazy singleton)."""
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
                     blur=0.5, ruido=0, arco_iris=0.0, opacidade=95, qualidade_jpg=75):
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


def processar_foto_sobreposta(img_foto_pil, largura, altura, angulo=0, blur=0.0, ruido=0, arco_iris=0.0,
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
