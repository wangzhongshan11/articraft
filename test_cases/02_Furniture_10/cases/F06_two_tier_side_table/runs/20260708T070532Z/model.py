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


def _rounded_box_mm(width: float, depth: float, height: float, corner_radius: float, edge_radius: float = 0.0):
    """Centered CadQuery rounded rectangular slab authored in millimetres."""
    shape = cq.Workplane("XY").box(width, depth, height)
    shape = shape.edges("|Z").fillet(corner_radius)
    if edge_radius > 0.0:
        shape = shape.edges("#Z").fillet(edge_radius)
    return shape


def _leg_shape_mm():
    # Rounded-square wooden post, standing from floor z=0 to the tabletop underside.
    return (
        cq.Workplane("XY")
        .box(38.0, 38.0, 515.0)
        .edges("|Z")
        .fillet(6.0)
        .edges("#Z")
        .fillet(2.0)
        .translate((0.0, 0.0, 257.5))
    )


def _shelf_shape_mm():
    # A rounded shelf board with integral underside cleats that span between the four legs.
    shelf = _rounded_box_mm(330.0, 330.0, 24.0, corner_radius=18.0, edge_radius=3.0)

    front_cleat = cq.Workplane("XY").box(332.0, 18.0, 18.0).translate((0.0, 157.0, -20.5))
    rear_cleat = cq.Workplane("XY").box(332.0, 18.0, 18.0).translate((0.0, -157.0, -20.5))
    side_cleat = cq.Workplane("XY").box(18.0, 332.0, 18.0)
    right_cleat = side_cleat.translate((157.0, 0.0, -20.5))
    left_cleat = side_cleat.translate((-157.0, 0.0, -20.5))

    return shelf.union(front_cleat).union(rear_cleat).union(right_cleat).union(left_cleat)


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="two_tier_side_table")

    oak = Material("warm_oak", rgba=(0.72, 0.47, 0.24, 1.0))

    top_mesh = mesh_from_cadquery(
        _rounded_box_mm(450.0, 450.0, 35.0, corner_radius=28.0, edge_radius=5.0),
        "soft_rounded_tabletop",
        unit_scale=0.001,
        tolerance=0.35,
        angular_tolerance=0.08,
    )
    shelf_mesh = mesh_from_cadquery(
        _shelf_shape_mm(),
        "rounded_lower_shelf",
        unit_scale=0.001,
        tolerance=0.35,
        angular_tolerance=0.08,
    )
    leg_mesh = mesh_from_cadquery(
        _leg_shape_mm(),
        "rounded_square_leg",
        unit_scale=0.001,
        tolerance=0.35,
        angular_tolerance=0.08,
    )

    tabletop = model.part("tabletop")
    tabletop.visual(
        top_mesh,
        origin=Origin(xyz=(0.0, 0.0, 0.5325)),
        material=oak,
        name="upper_panel",
    )

    shelf = model.part("shelf")
    shelf.visual(shelf_mesh, material=oak, name="lower_panel")
    model.articulation(
        "tabletop_to_shelf",
        ArticulationType.FIXED,
        parent=tabletop,
        child=shelf,
        origin=Origin(xyz=(0.0, 0.0, 0.108)),
    )

    rail_block = _rounded_box_mm(38.0, 10.0, 18.0, corner_radius=3.0, edge_radius=1.0)
    rail_block_mesh = mesh_from_cadquery(
        rail_block,
        "shelf_leg_rail_block",
        unit_scale=0.001,
        tolerance=0.35,
        angular_tolerance=0.08,
    )

    leg_positions = ((0.185, 0.185), (-0.185, 0.185), (-0.185, -0.185), (0.185, -0.185))
    for index, (x_pos, y_pos) in enumerate(leg_positions):
        leg = model.part(f"leg_{index}")
        leg.visual(leg_mesh, material=oak, name="post")
        leg.visual(
            rail_block_mesh,
            origin=Origin(xyz=(0.0, -0.024 if y_pos > 0 else 0.024, 0.099)),
            material=oak,
            name="shelf_mount",
        )
        model.articulation(
            f"tabletop_to_leg_{index}",
            ArticulationType.FIXED,
            parent=tabletop,
            child=leg,
            origin=Origin(xyz=(x_pos, y_pos, 0.0)),
        )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    tabletop = object_model.get_part("tabletop")
    shelf = object_model.get_part("shelf")
    legs = [object_model.get_part(f"leg_{i}") for i in range(4)]

    all_parts = [tabletop, shelf, *legs]
    boxes = [ctx.part_world_aabb(part) for part in all_parts]
    if all(box is not None for box in boxes):
        mins = [min(box[0][axis] for box in boxes) for axis in range(3)]
        maxs = [max(box[1][axis] for box in boxes) for axis in range(3)]
        extents = [maxs[axis] - mins[axis] for axis in range(3)]
        ctx.check(
            "overall 450 x 450 x 550 mm envelope",
            abs(extents[0] - 0.450) < 0.003
            and abs(extents[1] - 0.450) < 0.003
            and abs(extents[2] - 0.550) < 0.003,
            details=f"extents={extents}",
        )
    else:
        ctx.fail("overall 450 x 450 x 550 mm envelope", "missing part AABB")

    shelf_box = ctx.part_world_aabb(shelf)
    if shelf_box is not None:
        shelf_top = shelf_box[1][2]
        ctx.check(
            "lower shelf top is about 120 mm high",
            abs(shelf_top - 0.120) < 0.003,
            details=f"shelf_top={shelf_top}",
        )

    for index, leg in enumerate(legs):
        ctx.expect_contact(
            leg,
            tabletop,
            elem_a="post",
            elem_b="upper_panel",
            contact_tol=0.0015,
            name=f"leg_{index} bears against tabletop underside",
        )
        ctx.expect_contact(
            leg,
            shelf,
            elem_a="shelf_mount",
            elem_b="lower_panel",
            contact_tol=0.0025,
            name=f"leg_{index} supports lower shelf cleats",
        )

    return ctx.report()


object_model = build_object_model()
