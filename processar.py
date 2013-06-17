#!/usr/bin/env python
# coding: utf-8

"""
Script descartável para processar scans de um livro.

Linhas comentadas na função ``main`` invocam funções que
foram usadas em diferentes momentos do processamento.
"""

import shutil
import time
import os
import glob
import re
from PIL import Image

#PATH = 'testes/'
PATH = 'scans/'
PATH_THUMBS = 'thumbs/'
PADRAO_PAGINA = re.compile(r'p\d\d\d\.png')
SUFIXO_VERSAO = re.compile(r'.*-(\d+)')
DIM_ORIG = (4091, 2962)
DIM_CROP = (3800, 2900)
MARGENS = [
    (1775,    0, 1900, 1450),
    (1775, 1450, 1900, 2900),
    (1900,    0, 2025, 1450),
    (1900, 1450, 2025, 2900),
]
AREAS_AMOSTRAS = [
    (1775,  200, 1825, 1400),
    (1775, 1500, 1825, 2700),
    (1950,  200, 2000, 1400),
    (1950, 1500, 2000, 2700),
]
DIM_THUMBS = {'1000'  : (1006, 768),
              '300' : (314, 240)}


def extrair_num_copia(nome_orig):
    """
        >>> extrair_num_copia('a')
        0
        >>> extrair_num_copia('a-3')
        3
        >>> extrair_num_copia('p123.png')
        0
        >>> extrair_num_copia('p123-7.png')
        7
        >>> extrair_num_copia('p123-.png')
        0
    """
    prefixo_orig, ext = os.path.splitext(nome_orig)
    pos_sufixo = prefixo_orig.rfind('-')
    if pos_sufixo == -1:
        return 0
    try:
        num = int(prefixo_orig[pos_sufixo+1:])
    except ValueError:
        return 0
    return num

def gerar_nome_copia(nome_orig):
    prefixo_orig, ext = os.path.splitext(nome_orig)
    nomes = glob.glob(prefixo_orig+'*'+ext)
    versoes = [extrair_num_copia(nome) for nome in nomes]
    num_copia = max(versoes)+1
    return prefixo_orig + ('-%d'%num_copia) + ext

def backup(nome_orig):
    nome_copia = gerar_nome_copia(nome_orig)
    shutil.copy(nome_orig, nome_copia)

def rotacionar(nome_img):
    with open(nome_img) as entrada:
        im = Image.open(entrada)
        im_rot = im.rotate(-90)
    with open(nome_img, 'wb') as saida:
        im_rot.save(saida)

def cortar(nome_img):
    with open(nome_img) as entrada:
        im = Image.open(entrada)
        x0 = DIM_ORIG[0]-DIM_CROP[0]
        y0 = 0
        x1 = DIM_ORIG[0]
        y1 = DIM_CROP[1]
        im_crop = im.crop((x0, y0, x1, y1 ))
    with open(nome_img, 'wb') as saida:
        im_crop.save(saida, 'PNG')


def media_rgb(amostra):
    somas = (sum(a[0] for a in amostra),
             sum(a[1] for a in amostra),
             sum(a[2] for a in amostra))
    return (somas[0]/len(amostra), somas[1]/len(amostra), somas[2]/len(amostra))

def mediana(amostra):
    return sorted(amostra)[len(amostra)/2]

def reduzir(nome_img, nome_dim):
    with open(nome_img) as entrada:
        im = Image.open(entrada)
        im_thumb = im.copy()
    nome_arq = os.path.split(nome_img)[-1]
    with open(os.path.join(PATH_THUMBS, nome_dim, nome_arq), 'wb') as saida:
        im_thumb.thumbnail(DIM_THUMBS[nome_dim], Image.ANTIALIAS)
        im_thumb.save(saida)

def retocar_margens_internas(nome_img):
    with open(nome_img) as entrada:
        im = Image.open(entrada)
        pix = im.load()
        a_pintar = []
        im_retoque = None
        for area in AREAS_AMOSTRAS:
            amostra = []
            for x in range(area[0], area[2], 10):
                for y in range(area[1], area[3], 10):
                    amostra.append(pix[x, y])
            valores = media_rgb(amostra) + mediana(amostra)
            dif = 255*6 - sum(valores)
            if dif < 20:
                a_pintar.append(area)
                if im_retoque is None:
                    im_retoque = im.copy()
            else:
                a_pintar.append(None)

    if im_retoque:
        backup(nome_img)
        with open(nome_img, 'wb') as saida:
            for pintar, area in zip(a_pintar, MARGENS):
                if pintar:
                    im_retoque.paste((255, 255, 255), area)
            im_retoque.save(saida, 'PNG')


def main():
    for dir_path, dir_names, nomes_arqs in os.walk(PATH):
        for nome_img in nomes_arqs:
            if PADRAO_PAGINA.match(nome_img):
                path_img = os.path.join(dir_path, nome_img)
                t0 = time.time()
                #backup(path_img)
                #rotacionar(path_img)
                #cortar(path_img)
                #retocar_margens_internas(path_img)
                for dim in DIM_THUMBS:
                    reduzir(path_img, dim)
                print '%0.3fs %s' % (time.time()-t0, path_img)

if __name__=='__main__':
    main()

