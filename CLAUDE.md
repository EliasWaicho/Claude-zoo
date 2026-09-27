# Claude-zoo

Parametric 3D-printable models in build123d. See README.md for layout.

## Workflow for a new model
1. Create `models/<snake_name>.py` with a module docstring (what it is, how
   to orient it on the bed), a `PARAMS` dict of defaults in mm with a short
   comment per param, and `build(**PARAMS) -> Part`.
2. Model it already in print orientation (flat face on z=0).
3. Run `python tools/build.py models/<name>.py`; the mesh must be watertight.
4. Look at `out/<name>.png` to sanity-check geometry before reporting done.
5. Commit the model and its `out/` files.

## FDM design rules (use lib/printing.py constants)
- Units are mm. Walls >= MIN_WALL (0.8), prefer 1.2+.
- Holes: `hole(d)` adds compensation; mating parts get CLEARANCE per side.
- Overhangs <= 45 deg; prefer chamfers over fillets on downward-facing edges.
- Put load along layer lines (layers are weak in Z); say so in the docstring.
- Prefer heat-set inserts or nut traps over printed threads.
- Consider `elephant_foot_chamfer` for parts with tight bottom-edge fits.
