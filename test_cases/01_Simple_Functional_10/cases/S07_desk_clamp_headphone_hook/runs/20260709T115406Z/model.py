from __future__ import annotations

import cadquery as cq

from sdk import ArticulatedObject, Material, TestContext, TestReport, mesh_from_cadquery


MM = 0.001


def build_hook_shape() -> cq.Workplane:
    width = 90.0
    depth = 60.0
    height = 110.0
    body_thickness = 10.0
    top_thickness = 12.0
    desk_clear = 35.0
    retaining_drop = 8.0
    front_lip = 18.0

    outer_profile = (
        cq.Workplane("YZ")
        .polyline(
            [
                (0.0, 0.0),
                (depth, 0.0),
                (depth, top_thickness),
                (body_thickness, top_thickness),
                (body_thickness, height - 28.0),
                (depth - 18.0, height - 28.0),
                (depth - 18.0, height - 18.0),
                (depth - front_lip, height),
                (0.0, height),
            ]
        )
        .close()
        .extrude(width, both=True)
    )

    slot_cut = (
        cq.Workplane("YZ")
        .moveTo(body_thickness, top_thickness)
        .rect(desk_clear, height - top_thickness - 22.0, centered=False)
        .extrude(width + 4.0, both=True)
    )

    front_relief = (
        cq.Workplane("YZ")
        .moveTo(depth - 22.0, height - 32.0)
        .lineTo(depth - 8.0, height - 18.0)
        .lineTo(depth - front_lip, height - 8.0)
        .lineTo(depth - front_lip, height - 18.0)
        .close()
        .extrude(width + 4.0, both=True)
    )

    retaining_ledge = (
        cq.Workplane("YZ")
        .moveTo(body_thickness, top_thickness)
        .lineTo(body_thickness + desk_clear, top_thickness)
        .lineTo(body_thickness + desk_clear, top_thickness + retaining_drop)
        .lineTo(body_thickness + desk_clear - 12.0, top_thickness + retaining_drop)
        .lineTo(body_thickness + desk_clear - 18.0, top_thickness + 3.0)
        .lineTo(body_thickness, top_thickness + 3.0)
        .close()
        .extrude(width - 24.0, both=True)
    )

    hook = outer_profile.cut(slot_cut).cut(front_relief).union(retaining_ledge)
    return hook


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="headphone_desk_hook")
    body = model.part("hook")
    body.visual(
        mesh_from_cadquery(build_hook_shape(), "headphone_desk_hook", unit_scale=MM),
        name="body",
        material=Material("matte_abs", color=(0.24, 0.24, 0.26, 1.0)),
    )
    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    hook = object_model.get_part("hook")

    ctx.expect_origin_distance(hook, hook, axes="xy", min_dist=0.0, max_dist=0.0, name="single_part_exists")
    return ctx.report()


object_model = build_object_model()