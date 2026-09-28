"""Twisted, rippled flower vase, designed for the slicer's spiral "vase mode".

The model is SOLID on purpose: in vase mode (Bambu Studio / OrcaSlicer:
Others -> Spiral vase) the slicer prints only the outer skin plus a solid
bottom, in one continuous spiral with no seam. Print upright as modeled.

Design notes for printability:
- the radius changes smoothly and the wall never leans out more than ~35 deg,
  so it needs no supports;
- the ripples twist slowly with height, which looks great in silk/dual-color PLA;
- flat base on z=0 with a wide footprint so it won't tip over.

For water-tightness use a 0.6-1.0 mm line width in vase mode (e.g. with a
0.4 mm nozzle set outer wall line width to 0.8 mm), or coat the inside.
"""
import math

from build123d import *

PARAMS = dict(
    height=180.0,        # total height
    base_r=38.0,         # radius at the bottom
    belly_r=50.0,        # widest radius (the "belly")
    belly_at=0.35,       # belly position as a fraction of height
    neck_r=24.0,         # narrowest radius (the neck)
    neck_at=0.82,        # neck position as a fraction of height
    lip_r=32.0,          # radius at the flared rim
    lobes=8,             # number of ripples around the vase
    ripple=4.0,          # ripple depth in mm (0 = smooth)
    twist=90.0,          # total twist of the ripples, degrees, bottom to top
    sections=16,         # loft cross-sections (more = smoother, slower)
)


def _radius(f, base_r, belly_r, belly_at, neck_r, neck_at, lip_r):
    """Smooth vase silhouette radius at height fraction f (0..1)."""
    pts = [(0.0, base_r), (belly_at, belly_r), (neck_at, neck_r), (1.0, lip_r)]
    for (f0, r0), (f1, r1) in zip(pts, pts[1:]):
        if f <= f1:
            t = (f - f0) / (f1 - f0)
            t = t * t * (3 - 2 * t)          # smoothstep: no kinks between zones
            return r0 + (r1 - r0) * t
    return lip_r


def build(height, base_r, belly_r, belly_at, neck_r, neck_at, lip_r,
          lobes, ripple, twist, sections) -> Part:
    profiles = []
    for i in range(sections + 1):
        f = i / sections
        z = f * height
        r = _radius(f, base_r, belly_r, belly_at, neck_r, neck_at, lip_r)
        rot = math.radians(twist * f)
        pts = []
        n = lobes * 8
        for k in range(n):
            a = 2 * math.pi * k / n
            rr = r + ripple * math.cos(lobes * (a - rot))
            pts.append((rr * math.cos(a), rr * math.sin(a), z))
        profiles.append(Face(Wire(Spline(*pts, periodic=True))))
    return Part(Solid.make_loft([f.outer_wire() for f in profiles], ruled=False).wrapped)
