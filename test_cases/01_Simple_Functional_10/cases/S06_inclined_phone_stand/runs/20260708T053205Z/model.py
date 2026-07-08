from __future__ import annotations

import math

import cadquery as cq
from sdk import (
    ArticulatedObject,
    Material,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)


MM = 0.001


def _safe_fillet(model: cq.Workplane, selector: str | None, radius: float) -> cq.Workplane:
    """Apply a cosmetic fillet but keep the solid valid if OCCT rejects an edge set."""
    try:
        edges = model.edges(selector) if selector is not None else model.edges()
        return edges.fillet(radius)
    except Exception:
        return model


def _stand_solid_mm() -> cq.Workplane:
    """One-piece smartphone stand authored in millimetres for CAD clarity."""

    width = 80.0
    depth = 75.0
    overall_height = 190.0

    base_thickness = 5.0
    lip_depth = 10.0
    lip_height = 12.0
    cable_slot_width = 18.0
    cable_slot_depth = 22.0

    panel_width = 68.0
    panel_length = 190.0
    panel_thickness = 6.0
    panel_angle_deg = 76.0
    panel_bottom_y = 18.0
    panel_bottom_z = 5.2

    # Low rectangular footplate, filleted before the larger union so the perimeter
    # remains a clean moulded/printed edge.
    base = cq.Workplane("XY").box(width, depth, base_thickness, centered=(True, False, False))
    base = _safe_fillet(base, None, 1.8)

    # Shallow raised front retainer.  A centered through-slot is removed later so
    # a charging cable can pass under the retained phone without fouling the lip.
    lip = (
        cq.Workplane("XY")
        .box(width, lip_depth, lip_height, centered=(True, False, False))
        .translate((0.0, 0.0, base_thickness - 0.4))
    )
    lip = _safe_fillet(lip, None, 2.2)

    # Inclined phone support: a broad rounded-rectangle plate, with one large
    # vertical rounded cutout through the back panel to remove material while
    # leaving full-width side rails and a strong top bridge.
    panel = cq.Workplane("XY").box(panel_width, panel_length, panel_thickness, centered=(True, False, True))
    panel = _safe_fillet(panel, "|Z", 6.0)

    cutout = (
        cq.Workplane("XY")
        .center(0.0, 96.0)
        .slot2D(86.0, 34.0, 90.0)
        .extrude(panel_thickness * 4.0, both=True)
    )
    panel = panel.cut(cutout)

    panel = _safe_fillet(panel, None, 1.4)
    panel = panel.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), panel_angle_deg).translate(
        (0.0, panel_bottom_y, panel_bottom_z)
    )

    stand = base.union(lip).union(panel)

    cable_cut = (
        cq.Workplane("XY")
        .box(cable_slot_width, cable_slot_depth, lip_height + base_thickness + 6.0, centered=(True, False, False))
        .translate((0.0, -1.0, -1.0))
    )
    stand = stand.cut(cable_cut)

    # A small rear underside relief keeps the part from looking like two blocks
    # simply overlapped, while preserving a continuous one-piece support spine.
    rear_relief = (
        cq.Workplane("YZ")
        .moveTo(depth - 7.0, base_thickness)
        .lineTo(depth - 1.5, base_thickness)
        .lineTo(depth - 1.5, 15.0)
        .close()
        .extrude(width + 4.0, both=True)
    )
    stand = stand.cut(rear_relief)

    # Final light pass for all newly exposed cable-slot and boolean edges.
    stand = _safe_fillet(stand, None, 1.2)

    # Keep the authored part within the exact requested envelope even after edge
    # radii and tilted-panel thickness are accounted for.
    bb = stand.val().BoundingBox()
    stand = stand.translate((-0.5 * (bb.xmin + bb.xmax), -bb.ymin, -bb.zmin))
    bb = stand.val().BoundingBox()
    z_trim = max(0.0, bb.zmax - overall_height)
    if z_trim > 0.001:
        trim = (
            cq.Workplane("XY")
            .box(width + 20.0, depth + 20.0, z_trim + 2.0, centered=(True, False, False))
            .translate((0.0, -10.0, overall_height))
        )
        stand = stand.cut(trim)
        stand = _safe_fillet(stand, None, 0.8)

    return stand


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="inclined_smartphone_stand")

    satin_gray = Material("satin_gray_polymer", rgba=(0.56, 0.56, 0.53, 1.0))

    stand = model.part("stand")
    stand.visual(
        mesh_from_cadquery(
            _stand_solid_mm(),
            "one_piece_inclined_stand",
            tolerance=0.35,
            angular_tolerance=0.08,
            unit_scale=MM,
        ),
        origin=Origin(),
        material=satin_gray,
        name="one_piece_body",
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    stand = object_model.get_part("stand")

    aabb = ctx.part_world_aabb(stand)
    if aabb is not None:
        lo, hi = aabb
        size = (hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2])
        ctx.check(
            "requested 80 by 75 mm footprint",
            abs(size[0] - 0.080) <= 0.002 and abs(size[1] - 0.075) <= 0.002,
            details=f"size={size}",
        )
        ctx.check(
            "requested 190 mm overall height",
            abs(size[2] - 0.190) <= 0.002,
            details=f"size={size}",
        )
    else:
        ctx.fail("stand has measurable bounds", "part_world_aabb returned None")

    ctx.check("single semantic part", len(object_model.parts) == 1, details=str(object_model.parts))

    return ctx.report()


object_model = build_object_model()