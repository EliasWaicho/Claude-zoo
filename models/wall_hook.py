"""Parametric wall hook with two countersunk screw holes.

Printed lying on its side (as modeled) so layer lines run along the hook
arm, which makes it much stronger than printing it standing up.
"""
from build123d import *

from lib.printing import hole

PARAMS = dict(
    width=20.0,        # hook width (the printed height on the bed)
    plate_h=60.0,      # height of the wall plate
    thickness=5.0,     # plate/arm thickness
    reach=30.0,        # how far the hook sticks out from the wall
    lip=12.0,          # height of the upturned tip
    screw_d=4.0,       # screw shank diameter
    head_d=8.0,        # countersink head diameter
)


def build(width, plate_h, thickness, reach, lip, screw_d, head_d) -> Part:
    # 2D side profile: wall plate (x 0..t) with the arm along the bottom
    # and an upturned lip at the tip, like a "J".
    t = thickness
    with BuildPart() as p:
        with BuildSketch(Plane.XY):
            Polygon(
                (0, 0), (reach + t, 0), (reach + t, lip), (reach, lip),
                (reach, t), (t, t), (t, plate_h), (0, plate_h),
                align=None,
            )
        extrude(amount=width)
        # Round the inside corner where arm meets plate so the load doesn't crack it.
        inner = p.edges().filter_by(Axis.Z).filter_by_position(Axis.X, t - 0.01, t + 0.01)
        inner = inner.filter_by_position(Axis.Y, t - 0.01, t + 0.01)
        fillet(inner, radius=t * 0.8)
        # Countersunk screw holes through the wall plate; heads sit on the
        # hook side (x = thickness), local -Z of each location points into the plate.
        for y in (plate_h * 0.5, plate_h * 0.85):
            with Locations(Pos(thickness, y, width / 2) * Rot(0, 90, 0)):
                CounterSinkHole(radius=hole(screw_d) / 2,
                                counter_sink_radius=head_d / 2,
                                depth=thickness)
    return p.part
