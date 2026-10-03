"""Pack original ImageGen panels into our established Genesis prop atlas.

Requires Pillow and NumPy. No ROMs or reference photographs are copied.
"""
from pathlib import Path
import base64, json, zipfile
import numpy as np
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
SIZE = 128
tiles = {'Front':(2,2,57,81), 'Back':(60,2,115,81), 'Spine':(118,2,125,81),
         'Opening':(2,86,81,93), 'Top':(2,98,57,105), 'Bottom':(2,110,57,117),
         'Corner':(86,98,93,105)}
source = Image.open(OUT/'generated_panels.png').convert('RGB')
w,h = source.size
front = source.crop((0,0,w//2,h))
back = source.crop((w//2,0,w,h))
# Printed spine/fold labels reuse the generated back's compact logo.
title = back.crop((int(w*.018),int(h*.073),int(w*.238),int(h*.258)))
panels = {
    'Front': front.resize((56,80),Image.Resampling.NEAREST),
    'Back': back.resize((56,80),Image.Resampling.NEAREST),
    'Spine': title.resize((80,8),Image.Resampling.NEAREST).transpose(Image.Transpose.ROTATE_270),
    'Top': title.resize((56,8),Image.Resampling.NEAREST),
    'Bottom': title.resize((56,8),Image.Resampling.NEAREST),
    'Opening': Image.new('RGB',(80,8),(12,14,16)),
    'Corner': Image.new('RGB',(8,8),(12,14,16)),
}
tex = Image.new('RGB',(SIZE,SIZE),(12,14,16))
for name,im in panels.items():
    if name in ('Front','Back'):
        ImageDraw.Draw(im).rectangle((0,0,55,79),outline=(12,14,16))
    x0,y0,x1,y1 = tiles[name]
    assert im.size == (x1-x0+1,y1-y0+1)
    tex.paste(im,(x0,y0))
    for x in range(x0,x1+1):
        tex.putpixel((x,y0-1),tex.getpixel((x,y0)))
        tex.putpixel((x,y1+1),tex.getpixel((x,y1)))
    for y in range(y0,y1+1):
        tex.putpixel((x0-1,y),tex.getpixel((x0,y)))
        tex.putpixel((x1+1,y),tex.getpixel((x1,y)))
tex = tex.quantize(colors=32,dither=Image.Dither.NONE).convert('RGB')
tex.save(OUT/'hyperstone_heist_box_atlas.png')
for name in ('Front','Back'):
    x0,y0,x1,y1 = tiles[name]
    tex.crop((x0,y0,x1+1,y1+1)).save(OUT/(name.lower()+'_cover.png'))
exec(compile((OUT/'geometry_export.py.inc').read_text(encoding='utf-8'), 'geometry_export.py.inc', 'exec'))
