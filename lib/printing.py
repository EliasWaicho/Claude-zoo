"""Shared design-for-FDM-printing constants and helpers (all units mm)."""
from build123d import Axis, Part, chamfer

NOZZLE = 0.4
MIN_WALL = 2 * NOZZLE          # thinnest wall worth printing
LAYER = 0.2
CLEARANCE = 0.25               # per-side gap for parts that must fit together
HOLE_COMP = 0.2                # holes print small; add this to diameters
MAX_OVERHANG_DEG = 45          # steeper than this needs support


def hole(d: float) -> float:
    """Return a compensated hole diameter so a d-mm pin/screw actually fits."""
    return d + HOLE_COMP


def elephant_foot_chamfer(part: Part, size: float = 0.5) -> Part:
    """Chamfer the bottom (z-min) edges to hide first-layer squish."""
    bottom = part.faces().sort_by(Axis.Z)[0]
    return chamfer(bottom.edges(), size)
