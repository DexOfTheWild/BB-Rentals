Tony Hawk's Pro Skater 2 / reusable CD jewel case

Built-in ImageGen artwork, inspired by the user's front/back references.
The source and exact prompt are generated_panels.png and generation_prompt.txt.
Original reference photographs and game disc bytes are not included.

Unchanged approved Crash/generic CD geometry: 44 triangles, 24 unique positions,
142 x 125 x 10.4 mm, +Y up, +Z front, bottom-center origin.
Opaque plastic rim, bevel, ribbed hinge and clean fictional F badge retained.
128x128 atlas; front insert 54x54, back 62x54, spine 4x54; nearest filtering.
Rebuild: python build_model.py (Pillow + NumPy).
Runtime trio: assets/bb.thps2/model.obj, model.mtl, atlas0.png.

Stable ID: bb.thps2. Item: THPS2 CD case. 2500 Bells; catalog/rental eligible
when the player's matching disc is present. Generic PSX profile, no challenges.
Prepared in unpublished BB-Rentals v0.1.3.

The player's single MODE2/2352 track BIN/CUE was converted locally with official
MAME chdman 0.289, createcd -c cdlz,cdzl,cdfl -np 4, then passed chdman verify.
Original BIN/CUE retained. The generated CHD resides beside them in roms/psx.
Tool source: https://www.mamedev.org/release.php
Tool documentation: https://docs.mamedev.org/tools/chdman.html
BIN SHA-256: 7a69101183b76eadf02336963c6a89822b76aca2b3fa6537288d9f13bf6d16ed
CHD SHA-256: f840f560904ef145000aee4e63853394f51fba21e99a3f57be972a1e7f7c4900
Only the CHD fingerprint belongs in catalog.json; no ROM/disc/BIOS in the pack.
Other CHD encodings need their own fingerprints. Gameplay testing remains manual.
