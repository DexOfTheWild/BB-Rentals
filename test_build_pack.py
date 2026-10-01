import copy
import hashlib
import json
from pathlib import Path
import shutil
import unittest
import uuid
import zipfile
from build_pack import build

class PackTests(unittest.TestCase):
    def setUp(self):
        self.root=Path(__file__).parent/('fixture-'+uuid.uuid4().hex)
        self.root.mkdir();self.addCleanup(self.cleanup)
        assets=self.root/'assets/test';assets.mkdir(parents=True)
        (assets/'model.obj').write_text('v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n')
        (assets/'model.mtl').write_text('newmtl test\nKd 1 1 1\n')
        self.catalog={'format':1,'id':'bb-rentals','version':'0.1.0','games':[
            {'id':'test.racer','system':'n64','name':'Test Racer','price':2500,'catalog':True,'rental':True,
             'profile':'generic','sha256':['a'*64],'model':'assets/test/model.obj','material':'assets/test/model.mtl'}]}
    def cleanup(self):
        p=self.root.resolve();assert p.parent==Path(__file__).parent.resolve() and p.name.startswith('fixture-')
        shutil.rmtree(p)
    def run_build(self):
        (self.root/'catalog.json').write_text(json.dumps(self.catalog));return build(self.root,self.root/'dist')
    def test_deterministic_rom_free_archive(self):
        self.run_build();data=(self.root/'dist/BB-Rentals.zip').read_bytes();self.run_build()
        self.assertEqual(data,(self.root/'dist/BB-Rentals.zip').read_bytes())
        descriptor=json.loads((self.root/'dist/BB-Rentals.json').read_text())
        self.assertEqual(descriptor['sha256'],hashlib.sha256(data).hexdigest())
        with zipfile.ZipFile(self.root/'dist/BB-Rentals.zip') as z:
            self.assertEqual(set(z.namelist()),{'pack.json','assets/test/model.obj','assets/test/model.mtl'})
            pack=json.loads(z.read('pack.json'))
            for f in pack['files']:self.assertEqual(f['sha256'],hashlib.sha256(z.read(f['path'])).hexdigest())
    def test_rom_or_executable_in_assets_rejected(self):
        for extension in ['nes','gb','z64','sfc','chd','bin','exe','dll']:
            p=self.root/f'assets/test/forbidden.{extension}';p.write_bytes(b'synthetic')
            with self.subTest(extension=extension),self.assertRaises(ValueError):self.run_build()
            p.unlink()
    def test_ambiguous_recognition_rejected(self):
        second=copy.deepcopy(self.catalog['games'][0]);second['id']='test.other';self.catalog['games'].append(second)
        with self.assertRaisesRegex(ValueError,'ambiguous'):self.run_build()
    def test_missing_model_rejected(self):
        self.catalog['games'][0]['model']='assets/test/missing.obj'
        with self.assertRaisesRegex(ValueError,'Missing'):self.run_build()
    def test_nes_catalog_and_rental_supported_but_handheld_still_blocked(self):
        self.catalog['games'][0]['system']='famicom'
        result=self.run_build()
        self.assertTrue(result['games'][0]['catalog'])
        self.assertTrue(result['games'][0]['rental'])
        self.catalog['games'][0]['system']='gameboy'
        with self.assertRaisesRegex(ValueError,'Handheld'):self.run_build()
    def test_material_cannot_escape(self):
        (self.root/'assets/test/model.mtl').write_text('newmtl test\nmap_Kd ../outside.png\n')
        with self.assertRaisesRegex(ValueError,'adjacent'):self.run_build()
    def test_invalid_image_bytes_rejected(self):
        (self.root/'assets/test/fake.png').write_bytes(b'not an image')
        with self.assertRaisesRegex(ValueError,'PNG'):self.run_build()

if __name__=='__main__':unittest.main()
