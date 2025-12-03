from PIL import Image
import os

src = 'assets/shushu/run/0_Archer_Running_007-1.png'
dst = 'icon.ico'

if os.path.exists(src):
    img = Image.open(src)
    img.save(dst, format='ICO', sizes=[(256, 256)])
    print(f"Converted {src} to {dst}")
else:
    print(f"Source file not found: {src}")
