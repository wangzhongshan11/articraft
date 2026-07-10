from __future__ import annotations

import cadquery as cq
from sdk import ArticulatedObject, Material, TestContext, TestReport, mesh_from_cadquery


MM = 0.001


def build_stand_shape() -> cq.Workplane:
    width = 80.0
    depth = 75.0
    height = 190.0
    thickness = 8.0
    foot_pad = 12.0
    lip_radius = 5.0
    lip_height = 12.0
    cable_width = 18.0
    cable_height = 10.0

    front_x = depth
    top_x = thickness
    inner_top_x = top_x + thickness
    inner_front_x = front_x - thickness - foot_pad
    cut_bottom_z = 38.0
    cut_top_z = 118.0

    side_outer = [(0.0, 0.0), (top_x, height), (front_x, 0.0)]
    side_inner = [(thickness, thickness), (inner_top_x, height - thickness), (inner_front_x, thickness)]

    profile = (
        cq.Workplane("XZ")
        .polyline(side_outer)
        .close()
        .polyline(side_inner)
        .close()
        .extrude(width, both=True)
    )

    cutout = (
        cq.Workplane("XZ")
        .moveTo(depth * 0.30, cut_bottom_z)
        .lineTo(depth * 0.70, cut_bottom_z)
        .lineTo(depth * 0.50, cut_top_z)
        .close()
        .extrude(width + 4.0, both=True)
    )
    profile = profile.cut(cutout)

    lip = (
        cq.Workplane("YZ")
        .center(0.0, lip_height * 0.5)
        .rect(width, lip_height)
        .extrude(lip_radius, both=True)
        .translate((front_x - lip_radius, 0.0, 0.0))
    )
    profile = profile.union(lip)

    cable_cut = (
        cq.Workplane("YZ")
        .center(0.0, cable_height * 0.5 + 1.0)
        .rect(cable_width, cable_height)
        .extrude(lip_radius + 2.0, both=True)
        .translate((front_x - lip_radius - 1.0, 0.0, 0.0))
    )
    profile = profile.cut(cable_cut)

    return profile


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="smartphone_stand")

    stand = model.part("stand")
    stand.visual(
        mesh_from_cadquery(build_stand_shape(), "smartphone_stand", unit_scale=MM),
        material=Material("anodized_gray", color=(0.64, 0.65, 0.67, 1.0)),
        name="body",
    )
    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    stand = object_model.get_part("stand")

    aabb = ctx.part_world_aabb(stand)
    if aabb is None:
        ctx.fail("stand_aabb_present", "stand AABB was unavailable")
        return ctx.report()

    mins, maxs = aabb
    size_x = maxs[0] - mins[0]
    size_y = maxs[1] - mins[1]
    size_z = maxs[2] - mins[2]
    footprint_dims = sorted((size_x, size_y))

    ctx.check(
        "footprint_depth_75mm",
        abs(size_x - 0.075) <= 0.005,
        details=f"sizes={(size_x, size_y, size_z)}",
    )
    ctx.check(
        "footprint_width_80mm",
        abs(size_y - 0.16) <= 0.005,
        details=f"sizes={(size_x, size_y, size_z)}",
    )
    ctx.check(
        "overall_height_190mm",
        abs(size_z - 0.19) <= 0.005,
        details=f"height={size_z}",
    )
    return ctx.report()


object_model = build_object_model()
