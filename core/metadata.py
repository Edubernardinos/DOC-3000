# -*- coding: utf-8 -*-
"""
Módulo de Metadados Reais (NTFS / Win32, PyMuPDF e EXIF)
"""

import os
import ctypes
from ctypes import wintypes
from datetime import datetime
import fitz  # PyMuPDF
from PIL.ExifTags import TAGS


def aplicar_metadados_e_tamanho_reais(caminho, autor=None, titulo=None, data_criacao=None, data_modificacao=None, tamanho_kb=None):
    """
    Grava metadados em PDF (PyMuPDF), faz padding binário para simular tamanho em KB
    e altera timestamps NTFS via kernel32 no Windows.
    """
    ext = os.path.splitext(caminho)[1].lower()
    if ext == ".pdf":
        try:
            doc = fitz.open(caminho)
            meta = doc.metadata or {}
            if autor: meta["author"] = autor
            if titulo: meta["title"] = titulo
            if data_criacao: meta["creationDate"] = data_criacao.strftime("D:%Y%m%d%H%M%S")
            if data_modificacao: meta["modDate"] = data_modificacao.strftime("D:%Y%m%d%H%M%S")
            meta["producer"] = "DOC_EDITOR_3000"
            doc.set_metadata(meta)
            doc.save(caminho, incremental=False, encryption=fitz.PDF_ENCRYPT_KEEP)
            doc.close()
        except Exception as e:
            print(f"Erro metadados PDF: {e}")

    if tamanho_kb and float(tamanho_kb) > 0:
        try:
            bytes_alvo = int(float(tamanho_kb) * 1024)
            bytes_atuais = os.path.getsize(caminho)
            if bytes_alvo > bytes_atuais:
                with open(caminho, "ab") as f:
                    f.write(b"\x00" * (bytes_alvo - bytes_atuais))
        except Exception as e:
            print(f"Erro padding tamanho: {e}")

    try:
        def dt_para_filetime(dt):
            EPOCH_AS_FILETIME = 116444736000000000
            HUNDREDS_OF_NANOSECONDS = 10000000
            ts = int(dt.timestamp() * HUNDREDS_OF_NANOSECONDS) + EPOCH_AS_FILETIME
            return wintypes.FILETIME(ts & 0xFFFFFFFF, ts >> 32)

        handle = ctypes.windll.kernel32.CreateFileW(caminho, 0x0100, 0, None, 3, 0x02000000, None)
        if handle != -1:
            ft_cria = dt_para_filetime(data_criacao) if data_criacao else None
            ft_mod = dt_para_filetime(data_modificacao) if data_modificacao else (ft_cria if ft_cria else None)
            p_cria = ctypes.byref(ft_cria) if ft_cria else None
            p_mod = ctypes.byref(ft_mod) if ft_mod else None
            ctypes.windll.kernel32.SetFileTime(handle, p_cria, p_mod, p_mod)
            ctypes.windll.kernel32.CloseHandle(handle)
    except Exception as e:
        print(f"Erro kernel32: {e}")


def obter_nome_tag_exif(tag_id):
    """Retorna o nome legível da tag EXIF."""
    return TAGS.get(tag_id, f"Tag {tag_id}")


def salvar_com_exif(caminho, metadados, img_salvar, logger=None):
    """Salva JPEG com EXIF editado usando piexif."""
    try:
        import piexif
        try:
            exif_dict = piexif.load(img_salvar)
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
                    if logger:
                        logger(f"Erro ao salvar {chave}: {e}")

        # Grava dimensões em pixels como inteiros no EXIF
        try:
            exif_dict["Exif"][40962] = int(img_salvar.width)
            exif_dict["Exif"][40963] = int(img_salvar.height)
        except Exception:
            pass

        exif_bytes = piexif.dump(exif_dict)
        img_salvar.save(caminho, "JPEG", quality=95, exif=exif_bytes)
        if logger:
            logger(f"Salvo com metadados EXIF: {caminho}")
    except Exception as e:
        if logger:
            logger(f"Aviso EXIF: {e}")
        img_salvar.save(caminho, quality=95)
