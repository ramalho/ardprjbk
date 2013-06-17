#!/usr/bin/env python
# coding: utf-8

"""
Script descartável para publicar scans de um livro.
"""
import os
import io
import re
import pprint
import itertools

HTML5 = """
<!doctype html>
<html>
<head>
    <title>{title}</title>
</head>
<body>
{body}
</body>
</html>
"""

BODY_IDX = """
<h1>Arduino Projects Book</h1>

<p>Creative Commons Attribution-NonCommercial-ShareAlike 3.0 License by Arduino LLC
(<a href="pages/p002.html">license page</a>)</p>

{table}
"""

HTML_IDX = HTML5.format(title='Arduino Projects Book', body=BODY_IDX)

BODY_PG = ("""<a href="{link}">"""
           """<img src="{img}" title="pages {pg}-{pg1} (click for high resolution scan)" />"""
           """</a>""")

HTML_PG = HTML5.format(title='Arduino Projects Book: p.{pg}-{pg1}', body=BODY_PG)

PATH = 'scans/'
PATH_THUMBS = 'thumbs/'
PATH_PAGINAS = 'pages/'
PADRAO_PAGINA = re.compile(r'p(\d\d\d)\.png')
DIM_THUMBS = {'1000'  : (1006, 768),
              '300' : (314, 239)}

def indexar():
    indice = {}
    max_paginas = 0
    for dir_path, dir_names, nomes_arqs in os.walk(PATH):
        if dir_path.startswith(PATH_THUMBS):
            continue
        for nome in nomes_arqs:
            casou = PADRAO_PAGINA.match(nome)
            if casou:
                idx_dir = indice.setdefault(dir_path, [])
                idx_dir.append(int(casou.group(1)))
                if len(idx_dir) > max_paginas:
                    max_paginas = len(idx_dir)

    return indice, max_paginas

def gerar_tabela(indice, max_paginas):
    tab = []
    tab.append('<table>')
    for chave_cap, paginas in sorted(indice.items()):
        #print '\t<tr><th>{}</th></tr>'.format(chave_cap)
        tab.append('\t<tr>')
        for pg in paginas:
            link = PATH_PAGINAS + 'p{:03d}.html'.format(pg)
            img = PATH_THUMBS + '300/p{:03d}.png'.format(pg)
            larg = DIM_THUMBS['300'][0]
            alt = DIM_THUMBS['300'][1]
            pg1 = pg + 1
            tab.append('\t\t<td><a href="{link}">'
                   '<img src="{img}" width="{larg}" height="{alt}" title="pages {pg}-{pg1}" />'
                   '</a></td>'.format(**locals()))
        tab.append('\t</tr>')
    tab.append('</table>')
    return HTML_IDX.format(table='\n'.join(tab))

def gerar_paginas(indice):
    for chave_cap, paginas in sorted(indice.items()):
        for pg in paginas:
            with io.open(PATH_PAGINAS+'p{:03d}.html'.format(pg), 'w', encoding='utf-8') as saida:
                link = '../' + chave_cap + '/p{:03d}.png'.format(pg)
                img = '../' + PATH_THUMBS + '1000/p{:03d}.png'.format(pg)
                html = HTML_PG.format(pg=pg, pg1=pg+1, link=link, img=img)
                saida.write(html.decode('utf-8'))


def main():
    indice, max_paginas = indexar()
    print gerar_tabela(indice, max_paginas)
    gerar_paginas(indice)

if __name__=='__main__':
    main()
