"""Export imagegen artwork at the existing N64 prop texel budget.

Only texture packing/downsampling is procedural; the cover art is generated.
Run from any directory. Requires Pillow and NumPy, never reads a ROM.
"""
from pathlib import Path
import base64, json, zipfile
import numpy as np
from PIL import Image

OUT = Path(__file__).resolve().parent
SIZE = 128
tiles = {'Front': (2,2,65,49), 'Back': (2,54,65,101),
         'Opening': (70,2,77,49), 'Spine': (80,2,87,49),
         'Top': (2,108,65,115), 'Bottom': (2,118,65,125),
         'Corner': (92,2,99,9)}
source = Image.open(OUT/'generated_panels.png').convert('RGB')
w,h = source.size
split = round(h * 733 / 1448) # Generated panel boundary; source remains untouched.
front = source.crop((0,0,w,split))
back = source.crop((0,split,w,h))
# Reuse the generated title band for the narrow carton folds.
title = front.crop((int(w*.005),int(split*.008),int(w*.69),int(split*.425)))
panels = {'Front':front.resize((64,48),Image.Resampling.NEAREST),
          'Back':back.resize((64,48),Image.Resampling.NEAREST),
          'Top':title.resize((64,8),Image.Resampling.NEAREST),
          'Bottom':title.resize((64,8),Image.Resampling.NEAREST),
          'Spine':title.resize((48,8),Image.Resampling.NEAREST).transpose(Image.Transpose.ROTATE_270),
          'Opening':title.resize((48,8),Image.Resampling.NEAREST).transpose(Image.Transpose.ROTATE_270),
          'Corner':Image.new('RGB',(8,8),(16,22,32))}
tex = Image.new('RGB',(SIZE,SIZE),(16,22,32))
for name, im in panels.items():
    x0,y0,x1,y1=tiles[name]
    tex.paste(im,(x0,y0))
    for x in range(x0,x1+1):
        tex.putpixel((x,y0-1),tex.getpixel((x,y0)))
        tex.putpixel((x,y1+1),tex.getpixel((x,y1)))
    for y in range(y0,y1+1):
        tex.putpixel((x0-1,y),tex.getpixel((x0,y)))
        tex.putpixel((x1+1,y),tex.getpixel((x1,y)))
tex=tex.quantize(colors=32,dither=Image.Dither.NONE).convert('RGB')
tex.save(OUT/'bomberman_64_box_atlas.png')
for name in ('Front','Back'):
    x0,y0,x1,y1=tiles[name]
    tex.crop((x0,y0,x1+1,y1+1)).save(OUT/(name.lower()+'_cover.png'))
exec(compile((OUT/'geometry_export.py.inc').read_text(), 'geometry_export.py.inc', 'exec'))
