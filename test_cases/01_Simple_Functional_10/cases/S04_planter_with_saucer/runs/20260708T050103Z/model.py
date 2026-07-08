from __future__ import annotations

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Material,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)


MM = 0.001


def _safe_fillet(model: cq.Workplane, selector: str, radius_mm: float) -> cq.Workplane:
    """Apply a cosmetic fillet when CadQuery can solve it; keep geometry if not."""
    try:
        return model.edges(selector).fillet(radius_mm)
    except Exception:
        return model


def _make_planter() -> cq.Workplane:
    """Tapered 120 mm OD planter, hollow with 3 mm wall and central drain."""
    height = 130.0
    top_radius = 60.0
    bottom_radius = 45.0
    wall = 3.0
    floor_thickness = 7.0
    drain_radius = 5.0

    outer = (
        cq.Workplane("XY")
        .circle(bottom_radius)
        .workplane(offset=height)
        .circle(top_radius)
        .loft(combine=True)
    )

    outer_radius_at_floor = bottom_radius + (top_radius - bottom_radius) * (floor_thickness / height)
    inner_floor_radius = outer_radius_at_floor - wall
    inner_top_radius = top_radius - wall
    inner_slope = (inner_top_radius - inner_floor_radius) / (height - floor_thickness)
    cutter_top_z = height + 3.0
    cutter_top_radius = inner_top_radius + inner_slope * (cutter_top_z - height)

    planting_cavity = (
        cq.Workplane("XY")
        .workplane(offset=floor_thickness)
        .circle(inner_floor_radius)
        .workplane(offset=cutter_top_z - floor_thickness)
        .circle(cutter_top_radius)
        .loft(combine=True)
    )

    drain_cutter = cq.Workplane("XY").workplane(offset=-1.0).circle(drain_radius).extrude(floor_thickness + 2.0)

    planter = outer.cut(planting_cavity).cut(drain_cutter)
    planter = _safe_fillet(planter, ">Z", 1.5)
    planter = _safe_fillet(planter, "<Z", 0.8)
    return planter


def _make_saucer() -> cq.Workplane:
    """Low matching 140 mm saucer with recessed nesting dish and flat base."""
    # Revolve the actual ceramic cross-section so the recessed center is a real
    # open dish, not a hidden solid proxy.
    profile = [
        (0.0, 0.0),
        (70.0, 0.0),
        (70.0, 13.0),
        (66.0, 18.0),
        (60.0, 18.0),
        (52.0, 5.0),
        (0.0, 5.0),
    ]
    saucer = (
        cq.Workplane("XY")
        .polyline(profile)
        .close()
        .revolve(360.0, (0, 0, 0), (0, 1, 0))
        .rotate((0, 0, 0), (1, 0, 0), 90.0)
    )
    saucer = _safe_fillet(saucer, ">Z", 1.0)
    saucer = _safe_fillet(saucer, "<Z", 0.8)
    return saucer


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="tapered_planter_with_saucer")

    ceramic = model.material("warm_matte_ceramic", rgba=(0.73, 0.63, 0.49, 1.0))

    saucer = model.part("saucer")
    saucer.visual(
        mesh_from_cadquery(_make_saucer(), "saucer_dish", tolerance=0.15, angular_tolerance=0.05, unit_scale=MM),
        material=ceramic,
        name="saucer_dish",
    )

    planter = model.part("planter")
    planter.visual(
        mesh_from_cadquery(_make_planter(), "planter_shell", tolerance=0.15, angular_tolerance=0.05, unit_scale=MM),
        material=ceramic,
        name="planter_shell",
    )

    # The two manufactured pieces are authored as separate semantic solids.  They
    # are shown side-by-side with a small manufacturing clearance rather than
    # fused together, making the removable saucer/planter relationship explicit.
    model.articulation(
        "saucer_to_planter",
        ArticulationType.FIXED,
        parent=saucer,
        child=planter,
        origin=Origin(xyz=(170.0 * MM, 0.0, 0.0)),
    )

    return model


def _aabb_size(aabb: object) -> tuple[float, float, float] | None:
    if aabb is None:
        return None
    lo, hi = aabb
    return (hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2])


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    planter = object_model.get_part("planter")
    saucer = object_model.get_part("saucer")

    ctx.allow_isolated_part(
        planter,
        reason="The planter and saucer are separate removable ceramic pieces; the fixed transform only lays out the two export solids side-by-side.",
    )

    planter_size = _aabb_size(ctx.part_world_aabb(planter))
    saucer_size = _aabb_size(ctx.part_world_aabb(saucer))

    ctx.check(
        "planter is about 120 mm diameter and 130 mm high",
        planter_size is not None
        and 0.118 <= max(planter_size[0], planter_size[1]) <= 0.122
        and 0.128 <= planter_size[2] <= 0.132,
        details=f"planter_size={planter_size}",
    )
    ctx.check(
        "saucer is about 140 mm diameter and 18 mm high",
        saucer_size is not None
        and 0.138 <= max(saucer_size[0], saucer_size[1]) <= 0.142
        and 0.017 <= saucer_size[2] <= 0.019,
        details=f"saucer_size={saucer_size}",
    )
    ctx.check(
        "saucer is wider than planter for nesting",
        planter_size is not None
        and saucer_size is not None
        and max(saucer_size[0], saucer_size[1]) > max(planter_size[0], planter_size[1]) + 0.015,
        details=f"planter_size={planter_size}, saucer_size={saucer_size}",
    )

    return ctx.report()


object_model = build_object_model()