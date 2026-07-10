from __future__ import annotations

import cadquery as cq

from sdk import ArticulatedObject, Material, TestContext, TestReport, mesh_from_cadquery


MM = 0.001


def _build_soap_dish_shape() -> cq.Workplane:
    outer_x = 130.0
    outer_y = 90.0
    outer_z = 80.0

    wall = 5.0
    floor = 6.0
    foot_h = 10.0
    foot_r = 8.0
    corner_r = 14.0
    slot_len = 44.0
    slot_w = 7.0
    slot_pitch = 13.0

    tray_top_z = outer_z - foot_h
    shell = (
        cq.Workplane("XY")
        .rect(outer_x, outer_y)
        .extrude(tray_top_z)
        .edges("|Z")
        .fillet(corner_r)
        .edges(">Z")
        .fillet(5.0)
    )

    inner = (
        cq.Workplane("XY")
        .workplane(offset=floor)
        .rect(outer_x - 2 * wall, outer_y - 2 * wall)
        .extrude(tray_top_z - floor)
        .edges("|Z")
        .fillet(max(corner_r - wall, 7.0))
    )

    dish = shell.cut(inner)

    basin = (
        cq.Workplane("XY")
        .workplane(offset=floor)
        .rect(78.0, 48.0)
        .extrude(5.0)
        .edges("|Z")
        .fillet(10.0)
        .faces(">Z")
        .edges()
        .fillet(3.0)
    )
    dish = dish.cut(basin)

    slot_cuts = cq.Workplane("XY")
    for y in (-2 * slot_pitch, -slot_pitch, 0.0, slot_pitch, 2 * slot_pitch):
        cutter = (
            cq.Workplane("XY")
            .workplane(offset=floor - 1.0)
            .center(0.0, y)
            .slot2D(slot_len, slot_w, 0)
            .extrude(floor + 3.0)
        )
        slot_cuts = slot_cuts.union(cutter)
    dish = dish.cut(slot_cuts)

    foot_x = outer_x / 2.0 - 22.0
    foot_y = outer_y / 2.0 - 20.0
    for px, py in [
        (-foot_x, -foot_y),
        (-foot_x, foot_y),
        (foot_x, -foot_y),
        (foot_x, foot_y),
    ]:
        foot = (
            cq.Workplane("XY")
            .center(px, py)
            .circle(foot_r)
            .extrude(foot_h)
            .edges(">Z")
            .fillet(3.0)
            .edges("<Z")
            .fillet(2.0)
        )
        dish = dish.union(foot)

    return dish


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="soap_dish")
    body = model.part("body")

    ceramic = Material(name="sage_ceramic", rgba=(0.82, 0.85, 0.79, 1.0))
    body.visual(
        mesh_from_cadquery(_build_soap_dish_shape(), "soap_dish", unit_scale=MM),
        material=ceramic,
        name="dish",
    )
    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    return ctx.report()


object_model = build_object_model()
