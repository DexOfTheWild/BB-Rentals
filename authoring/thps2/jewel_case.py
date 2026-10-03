"""Reusable opaque PS1 jewel-case, no game art. Requires Pillow and NumPy.

Edit inputs/front.png, back.png and spine.png, then run this script again.
The shell, mesh, UVs and orientation remain identical for each game.
"""
from pathlib import Path
import argparse
import base64
import json
import zipfile
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
SIZE = 128
W, H, D = .142, .125, .0104
BEVEL = .0007
SPLIT = -.059
INK = (24, 29, 35)
PAPER = (202, 203, 192)
SILVER = (162, 176, 179)
LIGHT = (220, 229, 220)
TILES = {
    'Front': (2, 2, 57, 57), 'Back': (61, 2, 124, 57),
    'Hinge': (2, 62, 7, 117), 'Spine': (11, 62, 16, 117),
    'Opening': (20, 62, 25, 117), 'Top': (30, 62, 93, 67),
    'Bottom': (30, 71, 93, 76), 'Bevel': (98, 62, 101, 65),
}
FONT = dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', [
 '010101111101101','110101110101110','011100100100011','110101101101110',
 '111100110100111','111100110100100','011100101101011','101101111101101',
 '111010010010111','001001001101010','101101110101101','100100100100111',
 '101111111101101','101111111111101','010101101101010','110101110100100',
 '010101101111011','110101110101101','011100010001110','111010010010010',
 '101101101101111','101101101101010','101101111111101','101101010101101',
 '101101010010010','111001010100111','111101101101111','010110010010111',
 '110001010100111','110001010001110','101101111001001','111100110001110',
 '011100111101111','111001010010010','111101111101111','111101111001110']))


def lettering(im, text, xy, color=INK):
    x, y = xy
    for ch in text:
        for i, bit in enumerate(FONT.get(ch, '0' * 15)):
            if bit == '1': im.putpixel((x + i % 3, y + i // 3), color)
        x += 4


def emblem(im, x, y, scale=1):
    """Blocky hand-constructed placeholder PS mark, not a photo crop."""
    d = ImageDraw.Draw(im)
    def shape(points, color):
        d.polygon([(x + a*scale, y + b*scale) for a, b in points], fill=color)
    shape([(0,9),(5,7),(11,8),(9,10),(4,12),(0,11)], (43,123,171))
    shape([(4,9),(10,7),(14,9),(14,11),(8,13),(5,12),(11,10),(8,10)], (53,148,115))
    shape([(0,9),(4,8),(6,9),(3,10),(7,11),(4,12),(0,11)], (227,177,59))
    shape([(5,0),(10,1),(12,3),(12,7),(10,8),(8,7),(8,4),(7,3),(7,12),(5,11)], (196,54,53))


def default_front():
    front = Image.new('RGB', (54,54), PAPER)
    d = ImageDraw.Draw(front)
    d.rectangle((0,0,7,53), fill=INK)
    strip = Image.new('RGB',(43,5),INK)
    lettering(strip,'PLAYSTATION',(0,0),LIGHT)
    front.paste(strip.transpose(Image.Transpose.ROTATE_90),(1,1))
    # Fictional F rating: tiny black-on-white badge beneath the wordmark.
    d.rectangle((1,45,6,52), fill=LIGHT)
    # Leave the first row blank so the F's top bar has a clean white margin.
    lettering(front,'F',(2,47))
    emblem(front,17,13,2)
    lettering(front,'PS1',(27,44))
    return front


def create_inputs():
    folder = ROOT / 'inputs'
    folder.mkdir(exist_ok=True)
    front = default_front()
    back = Image.new('RGB',(62,54),PAPER)
    emblem(back,24,5)
    lettering(back,'PLAYSTATION',(9,23))
    bd = ImageDraw.Draw(back)
    for y,length in [(33,44),(36,48),(39,37)]: bd.line((7,y,7+length,y),fill=(145,150,147))
    for x in [43,45,48,49,52,55,57]: bd.line((x,44,x,50),fill=INK)
    lettering(back,'PS1',(7,46))
    spine = Image.new('RGB',(4,54),PAPER)
    # Narrow title strip is a disposable placeholder as well.
    lettering(spine,'P',(0,4))
    lettering(spine,'S',(0,12))
    lettering(spine,'1',(0,20))
    for name,im in [('front',front),('back',back),('spine',spine)]:
        path = folder / (name+'.png')
        if not path.exists(): im.save(path)


def atlas(inputs):
    panels = {}
    for name,size in [('front',(54,54)),('back',(62,54)),('spine',(4,54))]:
        with Image.open(inputs/(name+'.png')) as src:
            if src.size != size:
                raise ValueError(f'{name}.png must be {size}, received {src.size}; export deliberately at native resolution')
            im = src.convert('RGB')
        frame = Image.new('RGB',(size[0]+2,size[1]+2),SILVER)
        frame.paste(im,(1,1))
        ImageDraw.Draw(frame).line((0,0,frame.width-1,0),fill=LIGHT)
        ImageDraw.Draw(frame).line((frame.width-1,1,frame.width-1,frame.height-1),fill=(90,107,114))
        panels[name.capitalize()] = frame
    hinge = Image.new('RGB',(6,56),INK)
    hd = ImageDraw.Draw(hinge)
    for x in (0,2,4): hd.line((x,0,x,55),fill=(49,62,69))
    for y in (2,3,51,52): hd.line((0,y,5,y),fill=(89,105,111))
    panels['Hinge'] = hinge
    opening = Image.new('RGB',(6,56),(110,128,137))
    od = ImageDraw.Draw(opening)
    for x,c in [(0,LIGHT),(1,SILVER),(2,INK),(3,(64,82,92)),(5,LIGHT)]: od.line((x,0,x,55),fill=c)
    for y in (5,6,48,49): od.line((0,y,1,y),fill=INK)
    panels['Opening'] = opening
    for name in ('Top','Bottom'):
        im = Image.new('RGB',(64,6),(91,112,121));d = ImageDraw.Draw(im)
        for y,c in [(0,LIGHT),(1,SILVER),(2,INK),(3,(47,64,72)),(5,SILVER)]: d.line((0,y,63,y),fill=c)
        d.rectangle((0,1,5,4),fill=INK)
        for x in (10,11,54,55): d.line((x,0,x,1),fill=LIGHT)
        panels[name] = im
    panels['Bevel'] = Image.new('RGB',(4,4),SILVER)
    tex = Image.new('RGB',(SIZE,SIZE),INK)
    for name,im in panels.items():
        x0,y0,x1,y1 = TILES[name]
        assert im.size == (x1-x0+1,y1-y0+1)
        tex.paste(im,(x0,y0))
        # Extrude all four borders and corners for sampler safety.
        for y in range(y0-1,y1+2):
            for x in range(x0-1,x1+2):
                if x<x0 or x>x1 or y<y0 or y>y1:
                    tex.putpixel((x,y),im.getpixel((max(0,min(im.width-1,x-x0)),max(0,min(im.height-1,y-y0)))))
    return tex


def mesh():
    vertices=[];uvs=[];normals=[];faces=[];groups=[]
    def polygon(group,tile,points,localuv):
        p=np.array(points,dtype=float)
        n=np.cross(p[1]-p[0],p[2]-p[0]);n/=np.linalg.norm(n)
        x0,y0,x1,y1=TILES[tile]
        uv=[((x0+.5+u*(x1-x0))/SIZE,1-(y1+.5-v*(y1-y0))/SIZE) for u,v in localuv]
        for j in range(1,len(points)-1):
            k=len(vertices)
            for i in (0,j,j+1): vertices.append(p[i]);uvs.append(uv[i]);normals.append(n)
            faces.append((k,k+1,k+2));groups.append(group)
    def ring(inset,z):
        return [(-W/2+inset,inset,z),(SPLIT,inset,z),(W/2-inset,inset,z),
                (W/2-inset,H-inset,z),(SPLIT,H-inset,z),(-W/2+inset,H-inset,z)]
    front=ring(BEVEL,D/2);outerfront=ring(0,D/2-BEVEL)
    rear=ring(BEVEL,-D/2);outerrear=ring(0,-D/2+BEVEL)
    unit=[(0,0),(1,0),(1,1),(0,1)]
    polygon('Ribbed_hinge','Hinge',[front[i] for i in [0,1,4,5]],unit)
    polygon('Front_insert','Front',[front[i] for i in [1,2,3,4]],unit)
    # Split the rear into the same two rectangles to keep shared edges manifold;
    # one continuous full-width back print spans both.
    for ids in ([5,4,1,0],[4,3,2,1]):
        points=[rear[i] for i in ids]
        polygon('Back_insert','Back',points,[(.5-x/(W-2*BEVEL),(y-BEVEL)/(H-2*BEVEL)) for x,y,z in points])
    for i in range(6):
        j=(i+1)%6
        polygon('Front_plastic_bevel','Bevel',[outerfront[i],outerfront[j],front[j],front[i]],unit)
        polygon('Rear_plastic_bevel','Bevel',[rear[i],rear[j],outerrear[j],outerrear[i]],unit)
        tile={0:'Bottom',1:'Bottom',2:'Opening',3:'Top',4:'Top',5:'Spine'}[i]
        uv=unit
        if tile in ('Spine','Opening'):
            points=[outerrear[i],outerrear[j],outerfront[j],outerfront[i]]
            uv=[((z+D/2-BEVEL)/(D-2*BEVEL),y/H) for x,y,z in points]
        else:
            points=[outerrear[i],outerrear[j],outerfront[j],outerfront[i]]
            uv=[(x/W+.5,(z+D/2-BEVEL)/(D-2*BEVEL)) for x,y,z in points]
        polygon(tile,tile,points,uv)
    return tuple(map(np.array,(vertices,uvs,normals,faces))),groups


def validate(V,UV,N,F):
    assert len(F)==44 and len(np.unique(V,axis=0))==24
    assert np.isfinite(V).all() and 0<=UV.min()<=UV.max()<=1
    cross=np.cross(V[F[:,1]]-V[F[:,0]],V[F[:,2]]-V[F[:,0]])
    assert (np.sum(cross*(V[F].mean(axis=1)-[0,H/2,0]),axis=1)>0).all()
    assert np.allclose(np.linalg.norm(N,axis=1),1)
    edges={}
    for tri in F:
        for i,j in ((0,1),(1,2),(2,0)):
            e=tuple(sorted((tuple(V[tri[i]]),tuple(V[tri[j]]))))
            edges[e]=edges.get(e,0)+1
    assert set(edges.values())=={2}, 'Mesh must remain closed across the UV splits'


def render(V,UV,N,F,tex,eye):
    width=800;height=740
    eye=np.array(eye,dtype=float);eye/=np.linalg.norm(eye)
    right=np.cross([0,1,0],eye);right/=np.linalg.norm(right);up=np.cross(eye,right)
    p=V-[0,H/2,0];scale=4400
    q=np.stack([p@right*scale+width/2,-p@up*scale+height/2,p@eye],axis=1)
    bg=np.zeros((height,width,3))+[36,41,46];zb=np.full((height,width),-1e9)
    texture=np.array(tex);light=np.array([-.5,1,1]);light/=np.linalg.norm(light)
    for tri in F:
        if N[tri[0]]@eye<=0:continue
        a,b,c=q[tri];uv=UV[tri]
        lo=np.maximum(np.floor(q[tri,:2].min(0)).astype(int),0)
        hi=np.minimum(np.ceil(q[tri,:2].max(0)).astype(int),[width-1,height-1])
        xs,ys=np.meshgrid(np.arange(lo[0],hi[0]+1)+.5,np.arange(lo[1],hi[1]+1)+.5)
        den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-9:continue
        wa=((b[1]-c[1])*(xs-c[0])+(c[0]-b[0])*(ys-c[1]))/den
        wb=((c[1]-a[1])*(xs-c[0])+(a[0]-c[0])*(ys-c[1]))/den;wc=1-wa-wb
        dep=wa*a[2]+wb*b[2]+wc*c[2];zv=zb[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
        mask=(wa>=0)&(wb>=0)&(wc>=0)&(dep>zv)
        u=wa*uv[0,0]+wb*uv[1,0]+wc*uv[2,0];v=wa*uv[0,1]+wb*uv[1,1]+wc*uv[2,1]
        pixels=texture[np.clip(((1-v)*SIZE).astype(int),0,SIZE-1),np.clip((u*SIZE).astype(int),0,SIZE-1)]
        shade=.80+.20*max(0,N[tri[0]]@light)
        bg[lo[1]:hi[1]+1,lo[0]:hi[0]+1][mask]=(pixels*shade)[mask];zv[mask]=dep[mask]
    return Image.fromarray(np.uint8(bg))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs',type=Path,default=ROOT/'inputs')
    parser.add_argument('--output',type=Path,default=ROOT)
    args=parser.parse_args()
    create_inputs()
    out=args.output;out.mkdir(parents=True,exist_ok=True)
    tex=atlas(args.inputs);(V,UV,N,F),groups=mesh();validate(V,UV,N,F)
    tex.save(out/'thps2_case_atlas.png')
    lines=['# THPS2 / reusable CD jewel case. Metres, +Y up, +Z front.','mtllib thps2_case.mtl','s off','usemtl PS1_case']
    for prefix,data in [('v',V),('vt',UV),('vn',N)]:
        lines += [prefix+' '+' '.join(f'{v:.7f}' for v in p) for p in data]
    for tri,g in zip(F,groups): lines += ['g '+g,'f '+' '.join(f'{i+1}/{i+1}/{i+1}' for i in tri)]
    (out/'thps2_case.obj').write_text('\n'.join(lines)+'\n')
    (out/'thps2_case.mtl').write_text('newmtl PS1_case\nKa 1 1 1\nKd 1 1 1\nKs 0 0 0\nNs 0\nd 1\nillum 1\nmap_Kd thps2_case_atlas.png\n')
    stats=dict(triangles=len(F),unique_positions=24,materials=1,texture=[128,128],
        front_insert_pixels=[54,54],back_insert_pixels=[62,54],spine_insert_pixels=[4,54],
        dimensions_metres=[W,H,D],bevel_metres=BEVEL,up_axis='+Y',front_axis='+Z',
        origin='bottom center',filter='nearest',closed_manifold=True,alpha=False)
    (out/'model_stats.json').write_text(json.dumps(stats,indent=2)+'\n')
    (out/'uv_layout.json').write_text(json.dumps(dict(pixel_rectangles_inclusive=TILES,
        replaceable_insert_rectangles=dict(front=[3,3,56,56],back=[62,3,123,56],spine=[12,63,15,116])),indent=2)+'\n')
    for name,eye in [('preview',[-.85,.40,1.8]),('preview_rear',[.80,.40,-1.8]),('preview_edge',[-1.8,.7,.65])]:
        render(V,UV,N,F,tex,eye).save(out/(name+'.png'))
    packed=np.concatenate([V,N,UV],axis=1).round(8).flatten().tolist()
    data=json.dumps(dict(vertices=packed,texture=base64.b64encode((out/'thps2_case_atlas.png').read_bytes()).decode()),separators=(',',':'))
    fragment=(ROOT/'viewer_template.html').read_text(encoding='utf-8').replace('__MODEL__',data)
    (out/'viewer_fragment.html').write_text(fragment,encoding='utf-8')
    (out/'viewer.html').write_text((ROOT/'viewer_shell.html').read_text(encoding='utf-8').replace('__VIEWER__',fragment),encoding='utf-8')
    with zipfile.ZipFile(out/'thps2_case_bundle.zip','w',zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(out.rglob('*')):
            if path.is_file() and path.suffix!='.zip' and '__pycache__' not in path.parts:
                bundle.write(path,'thps2_case/'+path.relative_to(out).as_posix())
    print(json.dumps(stats,indent=2))


if __name__=='__main__': main()
