"""Compress the Blender frames for the site and create mobile versions."""
from argparse import ArgumentParser
from pathlib import Path
from PIL import Image
parser=ArgumentParser()
parser.add_argument('shots',type=Path)
args=parser.parse_args()
dest=Path(__file__).resolve().parents[1]/'dist/media'
dest.mkdir(exist_ok=True,parents=True)
for file in sorted(args.shots.glob('*.png')):
    is_spin=file.stem.startswith('spin-')
    target=dest/'spin' if is_spin else dest
    target.mkdir(exist_ok=True)
    with Image.open(file) as raw:
        im=raw.convert('RGBA')
        im.save(target/(file.stem+'.webp'),quality=84 if is_spin else 91,method=5)
        if not is_spin:
            im.thumbnail((570,570),Image.Resampling.LANCZOS)
            im.save(target/(file.stem+'-sm.webp'),quality=86,method=5)
