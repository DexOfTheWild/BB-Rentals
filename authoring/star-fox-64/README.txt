Star Fox 64 / original pixel-art interpretation

Front and back artwork: built-in image_gen, inspired by the supplied box photos.
Exact generation prompt: generation_prompt.txt
Generated source: generated_panels.png (two stacked landscape panels).

Runtime model: ../../assets/bb.star-fox-64/model.obj + model.mtl + atlas0.png
12 triangles, 8 unique positions, 128x128 32-color texture, 64x48 cover panels.
Existing N64 carton dimensions: .180 x .135 x .028 metres.
+Y up, +Z front, floor-centered pivot. Use nearest-neighbor texture sampling.
The spines and folds reuse the generated title, with one-pixel atlas gutters.

Rebuild authoring exports with Python build_model.py (Pillow and NumPy).
Copy the rebuilt atlas into ../../assets/bb.star-fox-64/atlas0.png afterward.
The OBJ/MTL in assets use model.mtl/atlas0.png names; preserve these references.
viewer.html is self-contained; viewer_fragment.html is the inline preview.

The catalog recognizes the local player ROM in all three N64 dump byte orders.
ROM bytes are never copied here. No release was pushed or published.
