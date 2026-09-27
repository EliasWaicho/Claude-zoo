# Claude-zoo: 3D models for printing, written as code

Parametric 3D-printable models written in Python with
[build123d](https://build123d.readthedocs.io). Describe a part to Claude, it
writes a model file, builds it, checks it and exports files ready for your slicer.

## Layout

```
models/        one .py file per model (PARAMS defaults + build() function)
lib/printing.py  FDM design constants: clearances, hole compensation, helpers
tools/build.py   builds a model -> out/<name>.stl / .3mf / .step / .png
out/           generated files (committed so you can download them)
```

## Usage

```bash
pip install -r requirements.txt

python tools/build.py models/wall_hook.py
python tools/build.py models/wall_hook.py --set reach=45 --set width=25
```

Each build prints the size, volume/approx. weight and whether the mesh is
**watertight**, and renders a 3-view preview PNG.

## Which file to use

- **.3mf**: preferred for slicers (Bambu Studio, OrcaSlicer, PrusaSlicer, Cura)
- **.stl**: universal fallback
- **.step**: open or edit in real CAD (Fusion, Onshape, FreeCAD)
- **.png**: quick preview

## Adding a model

Create `models/<name>.py`:

```python
from build123d import *
from lib.printing import hole, CLEARANCE

PARAMS = dict(length=40.0, width=20.0)

def build(length, width) -> Part:
    return Box(length, width, 5)
```

Or just ask Claude: *"make a cable clip for a 6 mm cable that screws under a desk"*.
