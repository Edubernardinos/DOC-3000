# -*- coding: utf-8 -*-
"""
Constantes e Mapeamento Tipográfico do DOC_EDITOR_3000
"""

import os

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
