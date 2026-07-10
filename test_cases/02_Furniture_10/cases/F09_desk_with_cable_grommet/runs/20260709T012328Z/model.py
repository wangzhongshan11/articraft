from __future__ import annotations

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    Material,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)


# All dimensions are authored in metres (1.200 m = 1200 mm) for the SDK.
TABLE_LENGTH = 1.200
TABLE_DEPTH = 0.600
OVERALL_HEIGHT = 0.750
TOP_THICKNESS = 0.030
LEG_HEIGHT = OVERALL_HEIGHT - TOP_THICKNESS
LEG_SIZE = 0.060
LEG_X = TABLE_LENGTH / 2.0 - 0.080
LEG_Y = TABLE_DEPTH / 2.0 - 0.080
RAIL_LENGTH = 1.000
RAIL_THICKNESS = 0.018
RAIL_HEIGHT = 0.120
RAIL_Y = -TABLE_DEPTH / 2.0 + 0.030
GROMMET_X = TABLE_LENGTH / 2.0 - 0.170
GROMMET_Y = TABLE_DEPTH / 2.0 - 0.105


def _tabletop_shape() -> cq.Workplane:
    """Rounded 1200 x 600 x 30 mm desktop with a rear-right cable hole."""
    top = cq.Workplane("XY").box(TABLE_LENGTH, TABLE_DEPTH, TOP_THICKNESS)
    # Large vertical-edge fillets make the plan-view corners genuinely rounded;
    # the smaller perimeter fillets soften top/bottom edge transitions.
    top = top.edges("|Z").fillet(0.035)
    top = top.edges("#Z").fillet(0.006)
    top = (
        top.faces(">Z")
        .workplane(centerOption="CenterOfBoundBox")
        .pushPoints([(GROMMET_X, GROMMET_Y)])
        .hole(0.078)
    )
    return top


def _leg_shape() -> cq.Workplane:
    return cq.Workplane("XY").box(LEG_SIZE, LEG_SIZE, LEG_HEIGHT).edges("|Z").fillet(0.004)


def _rail_shape() -> cq.Workplane:
    return cq.Workplane("XY").box(RAIL_LENGTH, RAIL_THICKNESS, RAIL_HEIGHT).edges("|Z").fillet(0.003)


def _grommet_shape() -> cq.Workplane:
    # A thin black plastic annular trim ring around the through-hole.  It sits
    # proud by only 3 mm, leaving the central cable opening unobstructed.
    return cq.Workplane("XY").circle(0.045).circle(0.026).extrude(0.003)


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="compact_writing_desk")

    wood = model.material("warm_oak_wood", rgba=(0.70, 0.46, 0.24, 1.0))
    dark_plastic = model.material("black_plastic", rgba=(0.015, 0.014, 0.012, 1.0))

    tabletop = model.part("tabletop")
    tabletop.visual(
        mesh_from_cadquery(_tabletop_shape(), "rounded_tabletop", tolerance=0.0008, angular_tolerance=0.08),
        origin=Origin(xyz=(0.0, 0.0, OVERALL_HEIGHT - TOP_THICKNESS / 2.0)),
        material=wood,
        name="rounded_tabletop",
    )

    leg_mesh = mesh_from_cadquery(_leg_shape(), "square_leg", tolerance=0.0008, angular_tolerance=0.08)
    for index, (x, y) in enumerate(
        [(-LEG_X, -LEG_Y), (LEG_X, -LEG_Y), (-LEG_X, LEG_Y), (LEG_X, LEG_Y)]
    ):
        leg = model.part(f"leg_{index}")
        leg.visual(
            leg_mesh,
            origin=Origin(xyz=(0.0, 0.0, LEG_HEIGHT / 2.0)),
            material=wood,
            name="leg_post",
        )
        model.articulation(
            f"tabletop_to_leg_{index}",
            ArticulationType.FIXED,
            parent=tabletop,
            child=leg,
            origin=Origin(xyz=(x, y, 0.0)),
        )

    front_rail = model.part("front_rail")
    front_rail.visual(
        mesh_from_cadquery(_rail_shape(), "front_support_rail", tolerance=0.0008, angular_tolerance=0.08),
        origin=Origin(),
        material=wood,
        name="front_support_rail",
    )
    model.articulation(
        "tabletop_to_front_rail",
        ArticulationType.FIXED,
        parent=tabletop,
        child=front_rail,
        origin=Origin(xyz=(0.0, RAIL_Y, LEG_HEIGHT - RAIL_HEIGHT / 2.0)),
    )

    grommet = model.part("cable_grommet")
    grommet.visual(
        mesh_from_cadquery(_grommet_shape(), "cable_grommet_insert", tolerance=0.0005, angular_tolerance=0.06),
        origin=Origin(),
        material=dark_plastic,
        name="cable_grommet_insert",
    )
    model.articulation(
        "tabletop_to_cable_grommet",
        ArticulationType.FIXED,
        parent=tabletop,
        child=grommet,
        origin=Origin(xyz=(GROMMET_X, GROMMET_Y, OVERALL_HEIGHT)),
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    tabletop = object_model.get_part("tabletop")
    front_rail = object_model.get_part("front_rail")
    grommet = object_model.get_part("cable_grommet")

    aabb = ctx.part_world_aabb(tabletop)
    if aabb is not None:
        lo, hi = aabb
        ctx.check(
            "tabletop is 1200 by 600 mm",
            abs((hi[0] - lo[0]) - TABLE_LENGTH) < 0.003 and abs((hi[1] - lo[1]) - TABLE_DEPTH) < 0.003,
            details=f"tabletop_aabb={aabb}",
        )
        ctx.check(
            "desktop top is 750 mm high",
            abs(hi[2] - OVERALL_HEIGHT) < 0.002,
            details=f"tabletop_aabb={aabb}",
        )

    for index in range(4):
        leg = object_model.get_part(f"leg_{index}")
        ctx.expect_gap(
            tabletop,
            leg,
            axis="z",
            max_gap=0.0015,
            max_penetration=0.0,
            name=f"leg_{index} bears on tabletop underside",
        )
        ctx.expect_overlap(
            tabletop,
            leg,
            axes="xy",
            min_overlap=0.045,
            name=f"leg_{index} footprint is under desktop",
        )

    ctx.expect_gap(
        tabletop,
        front_rail,
        axis="z",
        max_gap=0.0015,
        max_penetration=0.0,
        name="front support rail touches underside",
    )
    ctx.expect_overlap(
        tabletop,
        front_rail,
        axes="x",
        min_overlap=0.90,
        name="front rail spans the desk width",
    )

    grommet_pos = ctx.part_world_position(grommet)
    ctx.check(
        "cable grommet is near rear right corner",
        grommet_pos is not None and grommet_pos[0] > 0.35 and grommet_pos[1] > 0.15,
        details=f"grommet_pos={grommet_pos}",
    )

    return ctx.report()


object_model = build_object_model()