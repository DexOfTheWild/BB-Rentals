"""Export original ImageGen THPS2 inserts on the approved CD case.

The original PlayStation sidebar and fictional F badge remain unchanged.
Requires Pillow and NumPy. Reference photos are never used as texture pixels.
"""
from pathlib import Path
import sys
from PIL import Image
import jewel_case as case

ROOT = Path(__file__).resolve().parent
source = Image.open(ROOT/'generated_panels.png').convert('RGB')
w,h = source.size
inputs = ROOT/'inputs'
inputs.mkdir(exist_ok=True)
front = case.default_front()
# Discard the generated sidebar: the approved 8-column base owns this branding.
art = source.crop((round((w/2)*.161),0,w//2,h))
art = art.resize((46,54),Image.Resampling.NEAREST).quantize(colors=32,dither=Image.Dither.NONE).convert('RGB')
front.paste(art,(8,0))
assert front.crop((0,0,8,54)).tobytes() == case.default_front().crop((0,0,8,54)).tobytes()
front.save(inputs/'front.png')
front.save(ROOT/'front_cover.png')
back = source.crop((w//2,0,w,h)).resize((62,54),Image.Resampling.NEAREST)
back = back.quantize(colors=32,dither=Image.Dither.NONE).convert('RGB')
back.save(inputs/'back.png')
back.save(ROOT/'back_cover.png')
spine = Image.new('RGB',(4,54),case.INK)
for i,ch in enumerate('THPS2'):
    case.lettering(spine,ch,(0,10+i*7),(235,208,62))
spine.save(inputs/'spine.png')
sys.argv = [str(ROOT/'jewel_case.py')]
case.main()
