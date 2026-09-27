"""Build a model: export STL/3MF/STEP, check printability, render a preview.

Usage:
    python tools/build.py models/wall_hook.py [--set name=value ...]

Each model file defines PARAMS (dict of defaults) and build(**PARAMS) -> Part.
Outputs land in out/<model>.{stl,3mf,step,png}.
"""
import argparse
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from build123d import Mesher, export_step, export_stl


def load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def parse_value(v: str):
    for cast in (int, float):
        try:
            return cast(v)
        except ValueError:
            pass
    return {"true": True, "false": False}.get(v.lower(), v)


def _view_matrix(elev: float, azim: float) -> np.ndarray:
    """Rotation mapping world coords to camera coords (x right, y up, z toward viewer)."""
    e, a = np.radians(elev), np.radians(azim)
    fwd = -np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    up = np.array([0.0, 0.0, 1.0]) if abs(np.sin(e)) < 0.99 else np.array([0.0, 1.0, 0.0])
    right = np.cross(fwd, up)
    right /= np.linalg.norm(right)
    true_up = np.cross(right, fwd)
    return np.stack([right, true_up, -fwd])


def _rasterize(mesh: trimesh.Trimesh, elev: float, azim: float, res: int = 360) -> np.ndarray:
    """Tiny z-buffered flat-shaded software renderer (no GPU/display needed)."""
    R = _view_matrix(elev, azim)
    v = (mesh.vertices - mesh.bounds.mean(axis=0)) @ R.T
    scale = (res * 0.9) / (2 * np.abs(v[:, :2]).max())
    px = v[:, :2] * scale + res / 2
    px[:, 1] = res - px[:, 1]
    depth = v[:, 2]
    normals = mesh.face_normals @ R.T
    light = np.array([0.3, 0.5, 0.8])
    light /= np.linalg.norm(light)
    shade = 0.3 + 0.7 * np.abs(normals @ light)

    zbuf = np.full((res, res), -np.inf)
    img = np.ones((res, res, 3))
    base = np.array([0.23, 0.52, 0.88])
    for f, s in zip(mesh.faces, shade):
        (x0, y0), (x1, y1), (x2, y2) = px[f]
        xmin, xmax = int(max(min(x0, x1, x2), 0)), int(min(max(x0, x1, x2) + 1, res))
        ymin, ymax = int(max(min(y0, y1, y2), 0)), int(min(max(y0, y1, y2) + 1, res))
        if xmin >= xmax or ymin >= ymax:
            continue
        det = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(det) < 1e-12:
            continue
        xs, ys = np.meshgrid(np.arange(xmin, xmax) + 0.5, np.arange(ymin, ymax) + 0.5)
        w0 = ((y1 - y2) * (xs - x2) + (x2 - x1) * (ys - y2)) / det
        w1 = ((y2 - y0) * (xs - x2) + (x0 - x2) * (ys - y2)) / det
        w2 = 1 - w0 - w1
        inside = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
        z = w0 * depth[f[0]] + w1 * depth[f[1]] + w2 * depth[f[2]]
        region = zbuf[ymin:ymax, xmin:xmax]
        closer = inside & (z > region)
        region[closer] = z[closer]
        img[ymin:ymax, xmin:xmax][closer] = base * s
    return img


def render(mesh: trimesh.Trimesh, png: Path, title: str):
    views = [(30, -55, "iso"), (90, -90, "top (as printed)"), (0, -90, "front")]
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.4))
    for ax, (elev, azim, name) in zip(axes, views):
        ax.imshow(_rasterize(mesh, elev, azim))
        ax.set_title(name)
        ax.axis("off")
    fig.suptitle(title, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(png, dpi=100)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model", type=Path)
    ap.add_argument("--set", action="append", default=[], metavar="NAME=VALUE",
                    help="override a parameter, e.g. --set width=25")
    ap.add_argument("--no-preview", action="store_true")
    args = ap.parse_args()

    mod = load(args.model)
    params = dict(getattr(mod, "PARAMS", {}))
    for kv in args.set:
        k, v = kv.split("=", 1)
        if k not in params:
            sys.exit(f"unknown parameter {k!r}; known: {', '.join(params)}")
        params[k] = parse_value(v)

    part = mod.build(**params)
    out = ROOT / "out"
    out.mkdir(exist_ok=True)
    stem = out / args.model.stem

    export_stl(part, f"{stem}.stl", tolerance=0.01, angular_tolerance=0.1)
    export_step(part, f"{stem}.step")
    mesher = Mesher()
    mesher.add_shape(part, linear_deflection=0.01, angular_deflection=0.1)
    mesher.write(f"{stem}.3mf")

    mesh = trimesh.load(f"{stem}.stl")
    size = mesh.bounds[1] - mesh.bounds[0]
    print(f"model      : {args.model.stem}")
    print(f"params     : {params}")
    print(f"size (mm)  : {size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f}")
    print(f"volume     : {mesh.volume / 1000:.2f} cm^3  (~{mesh.volume / 1000 * 1.24:.1f} g PLA solid)")
    print(f"watertight : {mesh.is_watertight}")
    print(f"triangles  : {len(mesh.faces)}")
    if not mesh.is_watertight:
        print("WARNING: mesh is not watertight; slicers may misprint it")

    if not args.no_preview:
        render(mesh, Path(f"{stem}.png"), args.model.stem)
    print(f"wrote      : {stem}.stl/.3mf/.step" + ("" if args.no_preview else "/.png"))


if __name__ == "__main__":
    main()
