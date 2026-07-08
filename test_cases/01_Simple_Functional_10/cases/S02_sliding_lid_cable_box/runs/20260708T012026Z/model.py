from __future__ import annotations

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Material,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)


MM = 0.001


def _box_body_cadquery() -> cq.Workplane:
    """Open-topped 300 x 120 x 130 mm cable-organizer body with 3 mm walls."""
    length = 300.0
    depth = 120.0
    height = 130.0
    wall = 3.0

    outer = (
        cq.Workplane("XY")
        .box(length, depth, height, centered=(True, True, False))
        .edges("|Z")
        .fillet(6.0)
        .edges(">Z")
        .fillet(3.0)
        .edges("<Z")
        .fillet(2.0)
    )

    inner_void = (
        cq.Workplane("XY")
        .box(length - 2.0 * wall, depth - 2.0 * wall, height + 12.0, centered=(True, True, False))
        .translate((0.0, 0.0, wall))
    )
    body = outer.cut(inner_void)

    # Low longitudinal guide ledges just below the top rim, integral with the long walls.
    for y in (-53.5, 53.5):
        rail = (
            cq.Workplane("XY")
            .box(length - 24.0, 9.0, 6.0)
            .translate((0.0, y, 118.0))
            .edges("|X")
            .fillet(1.2)
        )
        body = body.union(rail)

    # A tiny hidden rear stop touches the lid runner at the closed position so the
    # assembly is physically grounded while the main rail/lip fit keeps clearance.
    rear_stop = (
        cq.Workplane("XY")
        .box(4.0, 6.0, 7.0)
        .translate((-136.0, 47.0, 117.5))
        .edges("|Z")
        .fillet(0.8)
    )
    body = body.union(rear_stop)

    # One circular cable port in each short side.
    port_r = 17.0
    side_port_z = 57.0
    for x0 in (-160.0, 140.0):
        cutter = (
            cq.Workplane("YZ")
            .center(0.0, side_port_z)
            .circle(port_r)
            .extrude(20.0)
            .translate((x0, 0.0, 0.0))
        )
        body = body.cut(cutter)

    # Two circular cable ports through the front face only.
    front_port_r = 16.0
    front_port_z = 50.0
    for x in (-70.0, 70.0):
        cutter = (
            cq.Workplane("XZ")
            .center(x, front_port_z)
            .circle(front_port_r)
            .extrude(20.0)
            .translate((0.0, -70.0, 0.0))
        )
        body = body.cut(cutter)

    return body


def _sliding_lid_cadquery() -> cq.Workplane:
    """Wood-toned sliding lid with underside runner lips captured by the body rails."""
    lid = (
        cq.Workplane("XY")
        .box(284.0, 108.0, 8.0)
        .translate((0.0, 0.0, 128.5))
        .edges("|Z")
        .fillet(5.0)
        .edges(">Z")
        .fillet(2.0)
        .edges("<Z")
        .fillet(1.2)
    )

    # Continuous underside webs connect the visible lid to lower lips, making a T-slot style capture.
    for y_sign in (-1.0, 1.0):
        web = (
            cq.Workplane("XY")
            .box(270.0, 3.0, 10.7)
            .translate((0.0, y_sign * 47.0, 119.15))
        )
        lip = (
            cq.Workplane("XY")
            .box(270.0, 7.0, 4.0)
            .translate((0.0, y_sign * 50.0, 111.8))
            .edges("|X")
            .fillet(0.8)
        )
        lid = lid.union(web).union(lip)

    return lid


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="desktop_cable_organizer")

    warm_plastic = Material("warm_white_molded_plastic", rgba=(0.78, 0.76, 0.68, 1.0))
    bamboo = Material("light_bamboo_lid", rgba=(0.72, 0.49, 0.25, 1.0))
    model.materials.extend([warm_plastic, bamboo])

    box = model.part("box")
    box.visual(
        mesh_from_cadquery(_box_body_cadquery(), "hollow_box", tolerance=0.6, angular_tolerance=0.08, unit_scale=MM),
        origin=Origin(),
        material=warm_plastic,
        name="hollow_box",
    )

    lid = model.part("lid")
    lid.visual(
        mesh_from_cadquery(_sliding_lid_cadquery(), "sliding_lid", tolerance=0.6, angular_tolerance=0.08, unit_scale=MM),
        origin=Origin(),
        material=bamboo,
        name="sliding_lid",
    )

    model.articulation(
        "box_to_lid",
        ArticulationType.PRISMATIC,
        parent=box,
        child=lid,
        origin=Origin(),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=35.0, velocity=0.25, lower=0.0, upper=0.09),
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    box = object_model.get_part("box")
    lid = object_model.get_part("lid")
    slide = object_model.get_articulation("box_to_lid")

    ctx.allow_overlap(
        box,
        lid,
        elem_a="hollow_box",
        elem_b="sliding_lid",
        reason=(
            "The shallow captured lid runners are seated inside the one-piece hollow box guide-rail slot; "
            "the mesh element represents the full open shell and its integral rails as one manufactured part."
        ),
    )

    box_aabb = ctx.part_world_aabb(box)
    if box_aabb is not None:
        mn, mx = box_aabb
        dims = (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])
        ctx.check(
            "box matches requested 300x120x130 mm envelope",
            abs(dims[0] - 0.300) < 0.004 and abs(dims[1] - 0.120) < 0.004 and abs(dims[2] - 0.130) < 0.004,
            details=f"box dims={dims}",
        )

    ctx.expect_within(
        lid,
        box,
        axes="xy",
        margin=0.006,
        name="closed lid is contained by box footprint",
    )

    closed_pos = ctx.part_world_position(lid)
    with ctx.pose({slide: 0.09}):
        open_pos = ctx.part_world_position(lid)
        ctx.expect_overlap(
            lid,
            box,
            axes="x",
            min_overlap=0.18,
            name="slid lid remains substantially engaged with guide rails",
        )
        ctx.expect_within(
            lid,
            box,
            axes="y",
            margin=0.006,
            name="slid lid remains laterally captured",
        )

    ctx.check(
        "lid slides along the 300 mm length",
        closed_pos is not None and open_pos is not None and open_pos[0] > closed_pos[0] + 0.085,
        details=f"closed={closed_pos}, open={open_pos}",
    )

    return ctx.report()


object_model = build_object_model()
