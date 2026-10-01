"""Build an artwork-only release. Python standard library; no game or ROM inputs."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

SYSTEMS = {'famicom', 'genesis', 'n64', 'gameboy', 'snes', 'psx'}

def safe_asset(name):
    p = PurePosixPath(name)
    return (isinstance(name, str) and name.startswith('assets/') and name == name.lower()
            and re.fullmatch(r'[a-z0-9_./-]+', name) and '..' not in p.parts
            and p.suffix in {'.obj', '.mtl', '.png'} and str(p) == name)

def build(root, out):
    root = Path(root).resolve(); out = Path(out)
    pack = json.loads((root / 'catalog.json').read_text())
    if pack.get('format') != 1 or pack.get('id') != 'bb-rentals':
        raise ValueError('Invalid catalog format')
    if not re.fullmatch(r'[a-z0-9][a-z0-9._-]{0,62}', pack['version']):
        raise ValueError('Invalid version')
    ids, hashes = set(), set()
    for game in pack['games']:
        if (not re.fullmatch(r'[a-z0-9][a-z0-9._-]{0,62}',game['id']) or '..' in game['id']
                or game['id'].endswith('.') or game['id'] in ids or game['system'] not in SYSTEMS):
            raise ValueError('Duplicate ID or unknown system')
        ids.add(game['id'])
        if not (1 <= len(game['name']) <= 16 and game['name'].isascii() and '|' not in game['name']):
            raise ValueError('Item name exceeds native label')
        if not isinstance(game['catalog'], bool) or not isinstance(game['rental'], bool):
            raise ValueError('Missing distribution policy')
        if type(game['price']) is not int or not 1<=game['price']<=60000:
            raise ValueError('Invalid price')
        if game.get('profile','') not in {'','generic','sm64','sonic3','mm2','battletoads','gameboy'}:
            raise ValueError('Unknown compiled profile')
        if game['system']=='gameboy' and (game['catalog'] or game['rental']):
            raise ValueError('Handheld physical adapter is not available')
        if not game['sha256']:
            raise ValueError('No recognition fingerprints')
        for h in game['sha256']:
            key = (game['system'], h)
            if not re.fullmatch('[0-9a-f]{64}', h) or key in hashes:
                raise ValueError('Invalid or ambiguous ROM hash')
            hashes.add(key)
    files = {}
    for path in sorted((root / 'assets').rglob('*')):
        if path.is_dir(): continue
        name = path.relative_to(root).as_posix()
        if not safe_asset(name) or path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError('Unexpected asset (ROMs/BIOS/executables are forbidden): ' + name)
        data = path.read_bytes()
        if not 0 < len(data) <= 16*1024*1024: raise ValueError('Invalid asset size')
        if path.suffix == '.png':
            if len(data)<33 or not data.startswith(b'\x89PNG\r\n\x1a\n') or data[12:16]!=b'IHDR':
                raise ValueError('Invalid PNG')
            dims=[int.from_bytes(data[i:i+4],'big') for i in (16,20)]
            if any(n<4 or n>512 or n%4 for n in dims):raise ValueError('Invalid PNG atlas dimensions')
        if path.suffix in {'.obj','.mtl'}: data.decode('ascii')
        files[name] = data
    for game in pack['games']:
        if (game['model'] not in files or game['material'] not in files
                or not game['model'].endswith('.obj') or not game['material'].endswith('.mtl')):
            raise ValueError('Missing model/material')
    for name, data in files.items():
        if name.endswith('.mtl'):
            for line in data.decode('ascii').splitlines():
                parts=line.split()
                if parts and parts[0].startswith('map_'):
                    if len(parts)!=2 or parts[0]!='map_Kd' or '/' in parts[1] or '\\' in parts[1]:
                        raise ValueError('Only adjacent diffuse textures are allowed')
                    if str(PurePosixPath(name).parent / parts[1]) not in files: raise ValueError('Missing texture')
    if len(files)>1024 or sum(map(len,files.values()))>128*1024*1024: raise ValueError('Pack too large')
    pack['files']=[{'path':k,'size':len(v),'sha256':hashlib.sha256(v).hexdigest()} for k,v in files.items()]
    out.mkdir(parents=True,exist_ok=True)
    archive=out/'BB-Rentals.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in {'pack.json':json.dumps(pack,indent=2).encode(),**files}.items():
            info=zipfile.ZipInfo(name,date_time=(2026,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16;z.writestr(info,data)
    data=archive.read_bytes()
    descriptor={'format':1,'repository':'DexOfTheWild/BB-Rentals','tag':'v'+pack['version'],
                'asset':archive.name,'size':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    (out/'BB-Rentals.json').write_text(json.dumps(descriptor,indent=2)+'\n')
    print(f"Built {len(pack['games'])} games, {len(files)} art files, {len(data)} bytes; no ROMs or BIOS.")
    return pack

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,default=Path('dist'))
    args=p.parse_args();build(Path(__file__).parent,args.out)
