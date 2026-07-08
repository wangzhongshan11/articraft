from __future__ import annotations

import cadquery as cq

from sdk import ArticulatedObject, Material, Origin, TestContext, TestReport, mesh_from_cadquery


MM = 0.001


def _soft_box(length: float, width: float, height: float, radius: float, edge_radius: float, z_center: float) -> cq.Workplane:
    """Create a rounded rectangular solid in millimetres, centered on XY."""
    shape = cq.Workplane("XY").box(length, width, height).translate((0, 0, z_center))
    if radius > 0:
        shape = shape.edges("|Z").fillet(radius)
    if edge_radius > 0:
        shape = shape.edges("#Z").fillet(edge_radius)
    return shape


def _rail(length: float, width: float, height: float, x: float, y: float, z: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(length, width, height)
        .translate((x, y, z))
        .edges("|Z").fillet(4.0)
        .edges("#Z").fillet(2.0)
    )


def _splayed_leg(top_x: float, top_y: float) -> cq.Workplane:
    """Tapered coffee-table leg, slightly splayed outward from the centre."""
    outward_x = 18.0 if top_x > 0 else -18.0
    outward_y = 14.0 if top_y > 0 else -14.0
    bottom_x = top_x + outward_x
    bottom_y = top_y + outward_y

    leg = (
        cq.Workplane("XY")
        .center(bottom_x, bottom_y)
        .circle(15.0)
        .workplane(offset=374.0)
        .center(top_x - bottom_x, top_y - bottom_y)
        .circle(23.0)
        .loft(combine=False)
    )
    return leg.edges().fillet(1.5)


def _build_table_geometry() -> cq.Workplane:
    # All dimensions are authored in millimetres and scaled to metres on export.
    tabletop = _soft_box(
        length=900.0,
        width=500.0,
        height=30.0,
        radius=80.0,
        edge_radius=5.0,
        z_center=385.0,
    )

    # A clean shallow apron frame directly under the top, inset from the rounded edge.
    # The rails tuck into the underside so the exported body is one manufacturable solid.
    parts = [tabletop]
    parts.extend(
        [
            _rail(740.0, 28.0, 48.0, 0.0, 185.0, 346.0),
            _rail(740.0, 28.0, 48.0, 0.0, -185.0, 346.0),
            _rail(28.0, 340.0, 48.0, 375.0, 0.0, 346.0),
            _rail(28.0, 340.0, 48.0, -375.0, 0.0, 346.0),
        ]
    )

    for top_x in (-350.0, 350.0):
        for top_y in (-170.0, 170.0):
            parts.append(_splayed_leg(top_x, top_y))

    table = parts[0]
    for body in parts[1:]:
        table = table.union(body)
    return table.clean()


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="rounded_rectangular_coffee_table")

    warm_oak = Material("warm_oak", rgba=(0.72, 0.48, 0.25, 1.0))

    table = model.part("table")
    table.visual(
        mesh_from_cadquery(
            _build_table_geometry(),
            "rounded_rectangular_coffee_table_body",
            tolerance=0.45,
            angular_tolerance=0.08,
            unit_scale=MM,
        ),
        origin=Origin(),
        material=warm_oak,
        name="one_piece_table_body",
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    table = object_model.get_part("table")

    aabb = ctx.part_world_aabb(table)
    if aabb is None:
        ctx.fail("table has measurable bounds", "no world AABB was available")
    else:
        mn, mx = aabb
        dims = (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])
        ctx.check(
            "overall dimensions are 900 x 500 x 400 mm",
            abs(dims[0] - 0.900) <= 0.003
            and abs(dims[1] - 0.500) <= 0.003
            and abs(dims[2] - 0.400) <= 0.003,
            details=f"measured dimensions={dims}",
        )
        ctx.check(
            "table stands on the floor plane",
            abs(mn[2]) <= 0.001 and abs(mx[2] - 0.400) <= 0.003,
            details=f"min={mn}, max={mx}",
        )

    ctx.check(
        "static coffee table is a single semantic part",
        len(object_model.parts) == 1 and len(object_model.articulations) == 0,
        details=f"parts={len(object_model.parts)}, articulations={len(object_model.articulations)}",
    )

    return ctx.report()


object_model = build_object_model()
