from __future__ import annotations

import cadquery as cq

from sdk import ArticulatedObject, Material, Origin, TestContext, TestReport, mesh_from_cadquery


def _wood_mesh(model: cq.Workplane, name: str):
    return mesh_from_cadquery(model, name, unit_scale=0.001)


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="writing_desk")

    wood = Material("oak_veneer", rgba=(0.73, 0.60, 0.42, 1.0))
    dark_insert = Material("grommet_black", rgba=(0.12, 0.12, 0.12, 1.0))

    desk = model.part("desk")

    top_length = 1200.0
    top_depth = 600.0
    top_thickness = 28.0
    corner_radius = 45.0
    edge_radius = 6.0
    leg_thickness = 36.0
    leg_depth = 70.0
    leg_height = 722.0
    leg_inset_x = 90.0
    leg_inset_y = 40.0
    rail_height = 90.0
    rail_depth = 24.0
    rail_setback = 70.0
    rail_drop = 95.0
    grommet_radius = 30.0
    grommet_x = top_length / 2.0 - 95.0
    grommet_y = top_depth / 2.0 - 80.0

    top = (
        cq.Workplane("XY")
        .rect(top_length, top_depth)
        .extrude(top_thickness)
        .edges("|Z").fillet(corner_radius)
        .edges("not |Z").fillet(edge_radius)
        .faces(">Z")
        .workplane()
        .center(grommet_x, grommet_y)
        .circle(grommet_radius)
        .cutBlind(-top_thickness)
    )

    leg_x = top_length / 2.0 - leg_inset_x - leg_thickness / 2.0
    front_y = top_depth / 2.0 - leg_inset_y - leg_depth / 2.0
    rear_y = -top_depth / 2.0 + leg_inset_y + leg_depth / 2.0

    leg_positions = [
        (leg_x, front_y),
        (-leg_x, front_y),
        (leg_x, rear_y),
        (-leg_x, rear_y),
    ]
    leg_blank = cq.Workplane("XY").box(leg_thickness, leg_depth, leg_height)
    legs = cq.Workplane("XY")
    for x, y in leg_positions:
        legs = legs.add(leg_blank.translate((x, y, leg_height / 2.0)))

    front_rail = cq.Workplane("XY").box(
        top_length - 2.0 * (leg_inset_x + leg_thickness),
        rail_depth,
        rail_height,
    ).translate((0.0, front_y - leg_depth / 2.0 + rail_setback, leg_height - 135.0))

    top_mesh = _wood_mesh(top.translate((0.0, 0.0, leg_height)), "tabletop")
    legs_mesh = _wood_mesh(legs, "legs")
    rail_mesh = _wood_mesh(front_rail, "front_rail")
    desk.visual(top_mesh, origin=Origin(), material=wood, name="tabletop")
    desk.visual(legs_mesh, origin=Origin(), material=wood, name="legs")
    desk.visual(rail_mesh, origin=Origin(), material=wood, name="front_rail")

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    desk = object_model.get_part("desk")

    ctx.expect_gap(desk, desk, axis="z", positive_elem="tabletop", negative_elem="legs", min_gap=0.0, max_gap=0.0, name="legs meet underside of tabletop")
    ctx.expect_gap(desk, desk, axis="z", positive_elem="tabletop", negative_elem="front_rail", min_gap=0.089, max_gap=0.111, name="support rail sits below top")

    return ctx.report()


object_model = build_object_model()