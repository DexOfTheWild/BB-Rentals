verts=[];uvs=[];normals=[];faces=[];groups=[]
W=.135;H=.190;D=.024;R=.0025
# Counterclockwise perimeter when viewed from the printed front.
outline=[(-W/2+R,0),(W/2-R,0),(W/2,R),(W/2,H-R),
         (W/2-R,H),(-W/2+R,H),(-W/2,H-R),(-W/2,R)]

def polygon(name,points,localuv):
    p=np.array(points,dtype=float);n=np.cross(p[1]-p[0],p[2]-p[0]);n/=np.linalg.norm(n)
    x0,y0,x1,y1=tiles[name]
    uv=[((x0+.5+u*(x1-x0))/SIZE,1-(y1+.5-v*(y1-y0))/SIZE) for u,v in localuv]
    for j in range(1,len(points)-1):
        k=len(verts)
        for i in (0,j,j+1): verts.append(tuple(p[i]));uvs.append(uv[i]);normals.append(tuple(n))
        faces.append((k,k+1,k+2));groups.append(name)

polygon('Front',[(x,y,D/2) for x,y in outline],[(x/W+.5,y/H) for x,y in outline])
back=list(reversed(outline))
polygon('Back',[(x,y,-D/2) for x,y in back],[(.5-x/W,y/H) for x,y in back])
for i in range(8):
    a=outline[i];b=outline[(i+1)%8]
    points=[(*a,-D/2),(*b,-D/2),(*b,D/2),(*a,D/2)]
    name={0:'Bottom',2:'Opening',4:'Top',6:'Spine'}.get(i,'Corner')
    uv=[(0,0),(1,0),(1,1),(0,1)]
    if name=='Spine': uv=[(0,1),(0,0),(1,0),(1,1)]
    polygon(name,points,uv)
V=np.array(verts);UV=np.array(uvs);N=np.array(normals);F=np.array(faces)
lines=['# Genesis clamshell template / Hyperstone Heist. Metres, +Y up, +Z front.','mtllib hyperstone_heist_box.mtl','s off','usemtl Genesis_print']
for prefix,data in [('v',V),('vt',UV),('vn',N)]:
    lines += [prefix+' '+' '.join(f'{v:.7f}' for v in p) for p in data]
for tri,g in zip(F,groups):
    lines+=['g '+g,'f '+' '.join(f'{i+1}/{i+1}/{i+1}' for i in tri)]
(OUT/'hyperstone_heist_box.obj').write_text('\n'.join(lines)+'\n')
(OUT/'hyperstone_heist_box.mtl').write_text('newmtl Genesis_print\nKa 1 1 1\nKd 1 1 1\nKs 0 0 0\nNs 0\nd 1\nillum 1\nmap_Kd hyperstone_heist_box_atlas.png\n')
assert len(F)==28 and len(np.unique(V,axis=0))==16
assert np.isfinite(V).all() and 0<=UV.min()<=UV.max()<=1
cross=np.cross(V[F[:,1]]-V[F[:,0]],V[F[:,2]]-V[F[:,0]])
assert (np.sum(cross*(V[F].mean(axis=1)-[0,H/2,0]),axis=1)>0).all()
assert np.allclose(np.linalg.norm(N,axis=1),1)
# Welded edge count establishes a closed case even across UV seams.
edges={}
for tri in F:
    for i,j in ((0,1),(1,2),(2,0)):
        edge=tuple(sorted((tuple(V[tri[i]]),tuple(V[tri[j]]))))
        edges[edge]=edges.get(edge,0)+1
assert set(edges.values())=={2}
stats=dict(triangles=28,unique_positions=16,materials=1,texture=[128,128],
           front_cover_pixels=[56,80],dimensions_metres=[W,H,D],corner_clip_metres=R,
           up_axis='+Y',front_axis='+Z',origin='bottom center',filter='nearest',closed_manifold=True)
(OUT/'model_stats.json').write_text(json.dumps(stats,indent=2)+'\n')
(OUT/'uv_layout.json').write_text(json.dumps(tiles,indent=2)+'\n')

def render(eye,width=800,height=800):
    eye=np.array(eye,dtype=float);eye/=np.linalg.norm(eye)
    right=np.cross([0,1,0],eye);right/=np.linalg.norm(right);up=np.cross(eye,right)
    p=V-[0,H/2,0];scale=min(width/.23,height/.25)
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

render([-.70,.35,1.9]).save(OUT/'preview.png')
render([.65,.35,-1.9]).save(OUT/'preview_rear.png')
packed=[]
for i in range(len(V)): packed.extend([*V[i],*N[i],*UV[i]])
data=json.dumps(dict(vertices=packed,texture=base64.b64encode((OUT/'hyperstone_heist_box_atlas.png').read_bytes()).decode()),separators=(',',':'))
template=(OUT/'viewer_template.html').read_text(encoding='utf-8')
fragment=template.replace('__MODEL__',data)
(OUT/'viewer_fragment.html').write_text(fragment,encoding='utf-8')
shell=(OUT/'viewer_shell.html').read_text(encoding='utf-8')
(OUT/'viewer.html').write_text(shell.replace('__VIEWER__',fragment),encoding='utf-8')
with zipfile.ZipFile(OUT/'hyperstone_heist_box_bundle.zip','w',zipfile.ZIP_DEFLATED) as bundle:
    for path in sorted(OUT.iterdir()):
        if path.is_file() and path.suffix!='.zip': bundle.write(path,'hyperstone_heist_box/'+path.name)
print(json.dumps(stats,indent=2))
