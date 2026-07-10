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


def rounded_rect_sketch(length: float, width: float, radius: float) -> cq.Sketch:
    return cq.Sketch().rect(length, width).vertices().fillet(radius)


def make_lower_tray() -> cq.Workplane:
    length = 160.0
    width = 120.0
    height = 18.0
    wall = 2.8
    corner_r = 12.0
    floor = 3.0
    split_z = 15.0
    boss_offset = 18.0
    boss_od = 9.0
    hole_d = 3.2

    outer = (
        cq.Workplane("XY")
        .placeSketch(rounded_rect_sketch(length, width, corner_r))
        .extrude(height)
    )
    inner = (
        cq.Workplane("XY")
        .workplane(offset=floor)
        .placeSketch(rounded_rect_sketch(length - 2 * wall, width - 2 * wall, corner_r - wall))
        .extrude(height - floor + 0.2)
    )
    tray = outer.cut(inner)

    boss_positions = [
        (length / 2 - boss_offset, width / 2 - boss_offset),
        (-length / 2 + boss_offset, width / 2 - boss_offset),
        (-length / 2 + boss_offset, -width / 2 + boss_offset),
        (length / 2 - boss_offset, -width / 2 + boss_offset),
    ]
    bosses = (
        cq.Workplane("XY")
        .workplane(offset=floor)
        .pushPoints(boss_positions)
        .circle(boss_od / 2)
        .circle(hole_d / 2)
        .extrude(split_z - floor, combine=False)
    )
    return tray.union(bosses)


def make_upper_cover() -> cq.Workplane:
    length = 160.0
    width = 120.0
    cover_h = 15.0
    wall = 2.8
    top = 3.0
    corner_r = 12.0
    lip_depth = 8.0
    lip_clearance = 0.35
    vent_l = 88.0
    vent_w = 58.0
    vent_pitch = 8.0
    vent_hole = 4.8
    cutout_w = 18.0
    cutout_h = 8.0
    cutout_r = 2.0

    outer = (
        cq.Workplane("XY")
        .placeSketch(rounded_rect_sketch(length, width, corner_r))
        .extrude(cover_h)
    )
    inner = (
        cq.Workplane("XY")
        .workplane(offset=wall)
        .placeSketch(rounded_rect_sketch(length - 2 * wall, width - 2 * wall, corner_r - wall))
        .extrude(cover_h - top + 0.2)
    )
    shell = outer.cut(inner)

    shell = (
        shell.faces("<Z")
        .workplane(centerOption="CenterOfMass")
        .placeSketch(
            rounded_rect_sketch(
                length - 2 * wall - 2 * lip_clearance,
                width - 2 * wall - 2 * lip_clearance,
                corner_r - wall - lip_clearance,
            )
        )
        .placeSketch(
            rounded_rect_sketch(
                length - 4 * wall - 2 * lip_clearance,
                width - 4 * wall - 2 * lip_clearance,
                corner_r - 2 * wall - lip_clearance,
            )
        )
        .extrude(-lip_depth)
    )

    x_count = int(vent_l // vent_pitch)
    y_count = int(vent_w // vent_pitch)
    x_start = -((x_count - 1) * vent_pitch) / 2
    y_start = -((y_count - 1) * vent_pitch) / 2
    vent_points = [
        (x_start + i * vent_pitch, y_start + j * vent_pitch)
        for i in range(x_count)
        for j in range(y_count)
    ]
    shell = (
        shell.faces(">Z")
        .workplane(centerOption="CenterOfMass")
        .pushPoints(vent_points)
        .hole(vent_hole)
    )

    side_cut = (
        cq.Workplane("YZ")
        .workplane(offset=length / 2)
        .center(0, 8.0)
        .rect(cutout_w, cutout_h)
        .extrude(-6.0)
        .edges("|X").fillet(cutout_r)
    )
    return shell.cut(side_cut)


GRAY = Material("case_gray", color=(0.78, 0.78, 0.82, 1.0))


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="electronic_enclosure")

    base = model.part("lower_tray")
    base.visual(
        mesh_from_cadquery(make_lower_tray(), "lower_tray", unit_scale=MM),
        material=GRAY,
        name="tray_shell",
    )

    cover = model.part("upper_cover")
    cover.visual(
        mesh_from_cadquery(make_upper_cover(), "upper_cover", unit_scale=MM),
        origin=Origin(xyz=(0.0, 0.0, 0.015)),
        material=GRAY,
        name="cover_shell",
    )

    model.articulation(
        "tray_to_cover",
        ArticulationType.PRISMATIC,
        parent=base,
        child=cover,
        origin=Origin(xyz=(0.0, 0.0, 0.015)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=0.03, effort=20.0, velocity=0.2),
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    ctx.expect_gap(
        "upper_cover",
        "lower_tray",
        axis="z",
        min_gap=0.0,
        max_gap=0.013,
        name="cover seats on tray split line",
    )
    ctx.expect_overlap(
        "upper_cover",
        "lower_tray",
        axes="xy",
        min_overlap=0.10,
        name="cover footprint matches tray footprint",
    )
    ctx.allow_isolated_part(
        "upper_cover",
        reason="The upper cover is a detachable enclosure half shown in assembled position with a narrow seam clearance.",
    )
    return ctx.report()


object_model = build_object_model()