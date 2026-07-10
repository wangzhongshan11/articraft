from __future__ import annotations

import cadquery as cq

from sdk import ArticulatedObject, Origin, TestContext, TestReport, mesh_from_cadquery


MM = 0.001


def mm(value: float) -> float:
    return value * MM


TABLE_LENGTH = mm(900)
TABLE_WIDTH = mm(500)
TABLE_HEIGHT = mm(400)
TOP_THICKNESS = mm(30)
TOP_CORNER_RADIUS = mm(70)
LEG_HEIGHT = TABLE_HEIGHT - TOP_THICKNESS
LEG_TOP_X = mm(42)
LEG_TOP_Y = mm(30)
LEG_BOTTOM_X = mm(34)
LEG_BOTTOM_Y = mm(26)
LEG_INSET_X = mm(92)
LEG_INSET_Y = mm(74)
APRON_TOP_DROP = mm(18)
APRON_HEIGHT = mm(58)
APRON_THICKNESS = mm(20)


def rounded_rect_prism(length: float, width: float, height: float, radius: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .moveTo(-length / 2 + radius, -width / 2)
        .lineTo(length / 2 - radius, -width / 2)
        .radiusArc((length / 2, -width / 2 + radius), radius)
        .lineTo(length / 2, width / 2 - radius)
        .radiusArc((length / 2 - radius, width / 2), radius)
        .lineTo(-length / 2 + radius, width / 2)
        .radiusArc((-length / 2, width / 2 - radius), radius)
        .lineTo(-length / 2, -width / 2 + radius)
        .radiusArc((-length / 2 + radius, -width / 2), radius)
        .close()
        .extrude(height)
    )


def rounded_tabletop() -> cq.Workplane:
    return rounded_rect_prism(TABLE_LENGTH, TABLE_WIDTH, TOP_THICKNESS, TOP_CORNER_RADIUS)



def leg_shape() -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .rect(LEG_TOP_X, LEG_TOP_Y)
        .workplane(offset=LEG_HEIGHT)
        .rect(LEG_BOTTOM_X, LEG_BOTTOM_Y)
        .loft(combine=True)
    )



def apron_shape() -> cq.Workplane:
    outer_x = TABLE_LENGTH - 2 * LEG_INSET_X + LEG_TOP_X + APRON_THICKNESS
    outer_y = TABLE_WIDTH - 2 * LEG_INSET_Y + LEG_TOP_Y + APRON_THICKNESS
    inner_x = outer_x - 2 * APRON_THICKNESS
    inner_y = outer_y - 2 * APRON_THICKNESS
    outer = cq.Workplane("XY").rect(outer_x, outer_y).extrude(APRON_HEIGHT)
    inner = cq.Workplane("XY").rect(inner_x, inner_y).extrude(APRON_HEIGHT + mm(2)).translate((0, 0, -mm(1)))
    return outer.cut(inner)



def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="rounded_rectangular_coffee_table")

    wood = model.material("oak", rgba=(0.75, 0.61, 0.43, 1.0))

    table = model.part("table")
    table.visual(
        mesh_from_cadquery(rounded_tabletop(), "top"),
        origin=Origin(xyz=(0.0, 0.0, LEG_HEIGHT)),
        material=wood,
        name="top",
    )

    leg = leg_shape()
    for ix, x_sign in enumerate((-1, 1)):
        for iy, y_sign in enumerate((-1, 1)):
            x = x_sign * (TABLE_LENGTH / 2 - LEG_INSET_X)
            y = y_sign * (TABLE_WIDTH / 2 - LEG_INSET_Y)
            table.visual(
                mesh_from_cadquery(leg, f"leg_{ix}_{iy}"),
                origin=Origin(xyz=(x, y, 0.0)),
                material=wood,
                name=f"leg_{ix}_{iy}",
            )

    table.visual(
        mesh_from_cadquery(apron_shape(), "apron"),
        origin=Origin(xyz=(0.0, 0.0, LEG_HEIGHT - APRON_TOP_DROP - APRON_HEIGHT)),
        material=wood,
        name="apron",
    )

    return model



def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    table = object_model.get_part("table")

    ctx.expect_overlap(
        table,
        table,
        axes="xy",
        min_overlap=0.1,
        elem_a="top",
        elem_b="apron",
        name="apron stays within tabletop footprint",
    )
    ctx.expect_gap(
        table,
        table,
        axis="z",
        positive_elem="top",
        negative_elem="apron",
        min_gap=mm(15),
        max_gap=mm(25),
        name="apron sits slightly below top",
    )

    return ctx.report()


object_model = build_object_model()