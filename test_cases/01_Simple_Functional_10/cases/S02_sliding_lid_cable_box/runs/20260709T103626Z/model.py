from __future__ import annotations

import math

import cadquery as cq
from sdk import (
    ArticulatedObject,
    ArticulationType,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)


MM = 0.001


def mm(value: float) -> float:
    return value * MM


def _rounded_box_shell() -> cq.Workplane:
    outer_l = 300.0
    outer_d = 120.0
    outer_h = 130.0
    wall = 3.0
    floor = 3.0
    corner_r = 14.0
    inner_corner_r = max(corner_r - wall, 4.0)

    body = cq.Workplane("XY").box(outer_l, outer_d, outer_h, centered=(True, True, False))

    cavity = (
        cq.Workplane("XY")
        .workplane(offset=floor)
        .rect(outer_l - 2.0 * wall - 2.0 * inner_corner_r, outer_d - 2.0 * wall - 2.0 * inner_corner_r)
        .extrude(outer_h - floor)
        .edges("|Z")
        .fillet(inner_corner_r)
    )

    shell = body.cut(cavity)

    rail_height = 5.0
    rail_width = 3.0
    rail_drop = 5.0
    rail_inset = wall + 6.0
    rail_bottom_z = outer_h - rail_drop - rail_height

    for rail_y in (outer_d / 2.0 - rail_inset - rail_width / 2.0, -(outer_d / 2.0 - rail_inset - rail_width / 2.0)):
        rail = (
            cq.Workplane("XZ")
            .workplane(offset=rail_y)
            .center(0.0, rail_bottom_z + rail_height / 2.0)
            .rect(outer_l - 2.0 * (wall + 10.0), rail_height)
            .extrude(rail_width)
        )
        shell = shell.union(rail)

    port_r = 12.0
    front_z = 48.0
    side_z = 55.0
    front_x_positions = (-70.0, 70.0)

    for x in front_x_positions:
        shell = (
            shell.faces("<Y")
            .workplane()
            .pushPoints([(x, side_z)])
            .hole(2.0 * port_r)
        )

    for face in (">X", "<X"):
        shell = (
            shell.faces(face)
            .workplane()
            .pushPoints([(0.0, front_z)])
            .hole(2.0 * port_r)
        )

    shell = shell.edges("|Z").fillet(2.0)
    return shell


def _sliding_lid() -> cq.Workplane:
    lid_l = 292.0
    lid_d = 108.0
    top_t = 6.0
    lip_drop = 4.0
    lip_t = 2.6
    corner_r = 12.0

    top = cq.Workplane("XY").box(lid_l, lid_d, top_t, centered=(True, True, False))

    lip_span = lid_l - 18.0
    lip_y = lid_d / 2.0 - 8.0
    lips = []
    for y in (lip_y, -lip_y):
        lip = (
            cq.Workplane("XZ")
            .workplane(offset=y)
            .center(0.0, -lip_drop / 2.0)
            .rect(lip_span, lip_drop)
            .extrude(lip_t)
        )
        lips.append(lip)

    finger = (
        cq.Workplane("XY")
        .center(90.0, 0.0)
        .circle(8.0)
        .extrude(top_t + 0.2)
    )

    lid = top.union(lips[0]).union(lips[1]).cut(finger)
    return lid


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="desktop_cable_organizer")

    shell_mat = model.material("shell", color=(0.93, 0.93, 0.90, 1.0))
    lid_mat = model.material("lid", color=(0.74, 0.62, 0.45, 1.0))
    liner_mat = model.material("lid_liner", color=(0.12, 0.12, 0.12, 1.0))

    box = model.part("box")
    box.visual(
        mesh_from_cadquery(_rounded_box_shell(), "box_shell", unit_scale=MM),
        material=shell_mat,
        name="shell",
    )

    lid = model.part("lid")
    lid.visual(
        mesh_from_cadquery(_sliding_lid(), "top_lid", unit_scale=MM),
        origin=Origin(xyz=(mm(140.0), 0.0, mm(130.5))),
        material=lid_mat,
        name="panel",
    )
    lid.visual(
        mesh_from_cadquery(
            cq.Workplane("XY").box(0.274, 0.09, 0.0016),
            "lid_liner",
            unit_scale=1.0,
        ),
        origin=Origin(xyz=(mm(140.0), 0.0, mm(128.7))),
        material=liner_mat,
        name="liner",
    )

    model.articulation(
        "box_to_lid",
        ArticulationType.PRISMATIC,
        parent=box,
        child=lid,
        origin=Origin(xyz=(mm(-140.0), 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=mm(128.0), effort=20.0, velocity=0.15),
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    box = object_model.get_part("box")
    lid = object_model.get_part("lid")
    slide = object_model.get_articulation("box_to_lid")

    ctx.expect_within(lid, box, axes="y", margin=mm(2.5), elem_a="panel", elem_b="shell", name="lid stays captured laterally")
    ctx.expect_overlap(lid, box, axes="x", min_overlap=mm(120.0), elem_a="panel", elem_b="shell", name="lid remains inserted at rest")
    ctx.expect_gap(lid, box, axis="z", min_gap=mm(-4.0), max_gap=mm(8.0), positive_elem="panel", negative_elem="shell", name="lid sits near top opening")

    with ctx.pose({slide: mm(128.0)}):
        ctx.expect_overlap(lid, box, axes="x", min_overlap=mm(12.0), elem_a="panel", elem_b="shell", name="lid remains retained when open")
        rest_pos = ctx.part_world_position(box)
        open_pos = ctx.part_world_position(lid)
        ctx.check(
            "lid slides forward",
            rest_pos is not None and open_pos is not None and open_pos[0] > rest_pos[0] - mm(40.0),
            details=f"box={rest_pos}, lid={open_pos}",
        )

    return ctx.report()


object_model = build_object_model()