# coding: utf-8

"""
Crop (dimensões)
p094    2910    3783

"""

import shutil
import time
import os
import glob
import re
from PIL import Image

PATH = 'testes/'
PATH = 'scans/'
PADRAO_PAGINA = re.compile(r'p\d\d\d\.png')
SUFIXO_VERSAO = re.compile(r'.*-(\d+)')
DIM_ORIG = (4091, 2962)
DIM_CROP = (3800, 2900)

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

def main():
    for dir_path, dir_names, nomes_arqs in os.walk(PATH):
        for nome_img in nomes_arqs:
            if PADRAO_PAGINA.match(nome_img):
                path_img = os.path.join(dir_path, nome_img)
                t0 = time.time()
                backup(path_img)
                rotacionar(path_img)
                cortar(path_img)
                print '%0.3fs %s' % (time.time()-t0, path_img)

if __name__=='__main__':
    main()

