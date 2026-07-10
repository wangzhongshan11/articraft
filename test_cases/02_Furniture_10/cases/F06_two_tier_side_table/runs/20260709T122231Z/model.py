from __future__ import annotations

import cadquery as cq

from sdk import ArticulatedObject, Origin, TestContext, TestReport, mesh_from_cadquery


TABLE_SIZE = 0.450
TABLE_HEIGHT = 0.550
TOP_THICKNESS = 0.028
SHELF_THICKNESS = 0.020
APRON_HEIGHT = 0.050
APRON_THICKNESS = 0.018
LEG_SIZE = 0.048
CORNER_RADIUS = 0.035
TOP_EDGE_RADIUS = 0.010
SHELF_EDGE_RADIUS = 0.007
LEG_EDGE_RADIUS = 0.008
SHELF_TOP_Z = 0.120
TOP_UNDERSIDE_Z = TABLE_HEIGHT - TOP_THICKNESS
APRON_BOTTOM_Z = TOP_UNDERSIDE_Z - APRON_HEIGHT
LEG_TOP_Z = TOP_UNDERSIDE_Z
LEG_BOTTOM_Z = 0.0
LEG_XY_OFFSET = TABLE_SIZE * 0.5 - LEG_SIZE * 0.5 - 0.026
SHELF_CLEAR_TO_LEGS = -0.002
WOOD_COLOR = (0.73, 0.57, 0.37, 1.0)
WOOD_DARK = (0.66, 0.50, 0.31, 1.0)


def _rounded_panel(size_xy: float, thickness: float, corner_radius: float, edge_radius: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .rect(size_xy - 2.0 * corner_radius, size_xy - 2.0 * corner_radius)
        .extrude(thickness)
        .edges("|Z")
        .fillet(corner_radius)
        .faces(">Z or <Z")
        .edges()
        .fillet(edge_radius)
    )


def _leg() -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(LEG_SIZE, LEG_SIZE, LEG_TOP_Z, centered=(True, True, False))
        .edges("|Z")
        .fillet(LEG_EDGE_RADIUS)
        .faces(">Z or <Z")
        .edges()
        .fillet(LEG_EDGE_RADIUS * 0.5)
    )


def _table_base() -> cq.Workplane:
    top = _rounded_panel(TABLE_SIZE, TOP_THICKNESS, CORNER_RADIUS, TOP_EDGE_RADIUS).translate(
        (0.0, 0.0, TOP_UNDERSIDE_Z)
    )

    shelf_size = TABLE_SIZE - 2.0 * (LEG_SIZE + SHELF_CLEAR_TO_LEGS)
    shelf = _rounded_panel(shelf_size, SHELF_THICKNESS, CORNER_RADIUS * 0.55, SHELF_EDGE_RADIUS).translate(
        (0.0, 0.0, SHELF_TOP_Z - SHELF_THICKNESS)
    )

    aprons = None
    apron_span = 2.0 * LEG_XY_OFFSET
    apron_z = APRON_BOTTOM_Z
    apron_offset = LEG_XY_OFFSET
    apron_specs = (
        (apron_span, APRON_THICKNESS, 0.0, apron_offset),
        (apron_span, APRON_THICKNESS, 0.0, -apron_offset),
        (APRON_THICKNESS, apron_span, apron_offset, 0.0),
        (APRON_THICKNESS, apron_span, -apron_offset, 0.0),
    )
    for size_x, size_y, x, y in apron_specs:
        apron = (
            cq.Workplane("XY")
            .box(size_x, size_y, APRON_HEIGHT, centered=(True, True, False))
            .edges("|Z")
            .fillet(min(0.006, min(size_x, size_y) * 0.28))
            .translate((x, y, apron_z))
        )
        aprons = apron if aprons is None else aprons.union(apron)

    leg = _leg()
    legs = None
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            placed = leg.translate((sx * LEG_XY_OFFSET, sy * LEG_XY_OFFSET, 0.0))
            legs = placed if legs is None else legs.union(placed)

    return top.union(shelf).union(aprons).union(legs)



def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="two_tier_side_table")
    wood = model.material("wood_oak", rgba=WOOD_COLOR)
    model.material("wood_shadow", rgba=WOOD_DARK)

    table = model.part("table")
    table.visual(
        mesh_from_cadquery(_table_base(), "two_tier_side_table", unit_scale=1.0),
        origin=Origin(),
        material=wood,
        name="table_body",
    )
    return model



def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    return ctx.report()


object_model = build_object_model()