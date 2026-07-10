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


BODY_W = 0.24
BODY_D = 0.255
BASE_H = 0.075
LID_H = 0.038
WALL = 0.003
PLATE_BASE_T = 0.006
BOSS_H = 0.0058
PLATE_GAP = 0.0012
HINGE_R = 0.008
HINGE_Z = BASE_H - 0.004
PLATE_W = BODY_W - 0.046
PLATE_D = BODY_D - 0.076
HANDLE_EXT = 0.050
FOOT_H = 0.010
LATCH_W = 0.036
LATCH_D = 0.012
LATCH_H = 0.010


def hollow_box(width: float, depth: float, height: float, wall: float) -> cq.Workplane:
    outer = cq.Workplane("XY").box(width, depth, height, centered=(True, True, False))
    inner = cq.Workplane("XY").box(width - 2 * wall, depth - 2 * wall, height - wall, centered=(True, True, False)).translate((0, 0, wall))
    return outer.cut(inner)


def make_waffle_plate(width: float, depth: float, base_t: float, boss_h: float) -> cq.Workplane:
    plate = cq.Workplane("XY").box(width, depth, base_t, centered=(True, True, False))
    pitch_x = width / 6.0
    pitch_y = depth / 6.0
    cell_w = pitch_x * 0.78
    cell_d = pitch_y * 0.78
    top_w = cell_w * 0.64
    top_d = cell_d * 0.64
    for ix in range(6):
        for iy in range(6):
            cx = -width / 2 + pitch_x * (ix + 0.5)
            cy = -depth / 2 + pitch_y * (iy + 0.5)
            boss = (
                cq.Workplane("XY")
                .center(cx, cy)
                .rect(cell_w, cell_d)
                .workplane(offset=base_t + boss_h)
                .rect(top_w, top_d)
                .loft(combine=True)
            )
            plate = plate.union(boss)
    rib = cq.Workplane("XY").box(0.012, depth * 0.94, base_t + boss_h, centered=(True, True, False))
    return plate.union(rib)


def make_base_shell() -> cq.Workplane:
    shell = hollow_box(BODY_W, BODY_D, BASE_H, WALL)
    cavity = cq.Workplane("XY").box(BODY_W - 0.026, BODY_D - 0.040, 0.024, centered=(True, True, False)).translate((0, -0.002, BASE_H - 0.024))
    shell = shell.cut(cavity)
    front_handle = cq.Workplane("XY").box(BODY_W * 0.74, HANDLE_EXT, 0.016, centered=(True, True, False)).translate((0, BODY_D / 2 + HANDLE_EXT / 2 - 0.010, 0))
    shell = shell.union(front_handle)
    grip = cq.Workplane("XY").box(BODY_W * 0.50, HANDLE_EXT * 0.50, 0.012, centered=(True, True, False)).translate((0, BODY_D / 2 + HANDLE_EXT / 2 - 0.010, 0.002))
    shell = shell.cut(grip)
    hinge_block = cq.Workplane("XY").box(0.156, 0.018, 0.020, centered=(True, True, False)).translate((0, BODY_D / 2 - 0.014, BASE_H - 0.020))
    shell = shell.union(hinge_block)
    keep = cq.Workplane("XY").box(0.030, 0.008, 0.006, centered=(True, True, False)).translate((0.0, BODY_D / 2 + HANDLE_EXT - 0.014, BASE_H - 0.006))
    shell = shell.union(keep)
    for sx in (-1, 1):
        for sy in (-1, 1):
            foot = (
                cq.Workplane("XY")
                .center(sx * (BODY_W / 2 - 0.030), sy * (BODY_D / 2 - 0.032))
                .circle(0.013)
                .extrude(FOOT_H)
                .translate((0, 0, -FOOT_H))
            )
            shell = shell.union(foot)
    return shell


def make_lid_shell() -> cq.Workplane:
    lid = hollow_box(BODY_W * 0.97, BODY_D * 0.92, LID_H, WALL).translate((0, -0.010, 0))
    recess = cq.Workplane("XY").box(BODY_W - 0.040, BODY_D - 0.064, 0.018, centered=(True, True, False)).translate((0, -0.010, WALL))
    lid = lid.cut(recess)
    handle = (
        cq.Workplane("XZ")
        .moveTo(-0.070, 0.004)
        .lineTo(-0.060, 0.038)
        .lineTo(-0.060, 0.078)
        .lineTo(0.060, 0.078)
        .lineTo(0.060, 0.038)
        .lineTo(0.070, 0.004)
        .close()
        .extrude(0.022)
        .translate((0, BODY_D / 2 - 0.020, 0.0))
    )
    window = (
        cq.Workplane("XZ")
        .moveTo(-0.044, 0.018)
        .lineTo(-0.034, 0.046)
        .lineTo(0.034, 0.046)
        .lineTo(0.044, 0.018)
        .close()
        .extrude(0.030)
        .translate((0, BODY_D / 2 - 0.024, 0.0))
    )
    hinge_tube = cq.Workplane("YZ").circle(HINGE_R + 0.0015).extrude(0.156).translate((-0.078, BODY_D / 2 - 0.014, -0.001))
    latch_mount = cq.Workplane("XY").box(0.044, 0.014, 0.008, centered=(True, True, False)).translate((0, BODY_D / 2 + HANDLE_EXT - 0.022, 0.002))
    return lid.union(handle).cut(window).union(hinge_tube).union(latch_mount)


def make_latch() -> cq.Workplane:
    body = cq.Workplane("XY").box(LATCH_W, LATCH_D, LATCH_H, centered=(True, True, False))
    tab = cq.Workplane("XY").box(0.020, 0.007, 0.006, centered=(True, True, False)).translate((0, 0.008, LATCH_H - 0.002))
    pin = cq.Workplane("YZ").circle(0.0035).extrude(0.040).translate((-0.020, 0, 0.001))
    return body.union(tab).union(pin)


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="desktop_waffle_maker")

    plastic = model.material("plastic", rgba=(0.40, 0.40, 0.42, 1.0))
    dark = model.material("dark", rgba=(0.09, 0.09, 0.10, 1.0))
    steel = model.material("steel", rgba=(0.58, 0.59, 0.61, 1.0))

    base = model.part("base")
    base.visual(mesh_from_cadquery(make_base_shell(), "base_shell"), material=plastic, name="shell")

    lower_plate = model.part("lower_plate")
    lower_plate.visual(mesh_from_cadquery(make_waffle_plate(PLATE_W, PLATE_D, PLATE_BASE_T, BOSS_H), "lower_plate"), material=dark, name="plate")

    lid = model.part("lid")
    lid.visual(mesh_from_cadquery(make_lid_shell(), "lid_shell"), material=plastic, name="shell")

    upper_plate = model.part("upper_plate")
    upper_plate.visual(
        mesh_from_cadquery(make_waffle_plate(PLATE_W, PLATE_D, PLATE_BASE_T, BOSS_H), "upper_plate"),
        origin=Origin(rpy=(math.pi, 0.0, 0.0)),
        material=dark,
        name="plate",
    )

    latch = model.part("latch")
    latch.visual(mesh_from_cadquery(make_latch(), "front_latch"), material=steel, name="hook")

    model.articulation(
        "base_to_lower_plate",
        ArticulationType.FIXED,
        parent=base,
        child=lower_plate,
        origin=Origin(xyz=(0.0, -0.002, BASE_H - (PLATE_BASE_T + BOSS_H) - 0.001)),
    )
    model.articulation(
        "base_to_lid",
        ArticulationType.REVOLUTE,
        parent=base,
        child=lid,
        origin=Origin(xyz=(0.0, BODY_D / 2 - 0.014, HINGE_Z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=10.0, velocity=1.8, lower=0.0, upper=math.radians(105.0)),
    )
    model.articulation(
        "lid_to_upper_plate",
        ArticulationType.FIXED,
        parent=lid,
        child=upper_plate,
        origin=Origin(xyz=(0.0, -0.010, LID_H - 0.010 - PLATE_GAP)),
    )
    model.articulation(
        "lid_to_latch",
        ArticulationType.REVOLUTE,
        parent=lid,
        child=latch,
        origin=Origin(xyz=(0.0, BODY_D / 2 + HANDLE_EXT - 0.022, 0.006)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=4.0, lower=0.0, upper=math.radians(38.0)),
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    base = object_model.get_part("base")
    lid = object_model.get_part("lid")
    lower_plate = object_model.get_part("lower_plate")
    upper_plate = object_model.get_part("upper_plate")
    latch = object_model.get_part("latch")
    lid_hinge = object_model.get_articulation("base_to_lid")
    latch_joint = object_model.get_articulation("lid_to_latch")

    ctx.expect_gap(
        upper_plate,
        lower_plate,
        axis="z",
        min_gap=0.001,
        elem_a="plate",
        elem_b="plate",
        name="plates keep at least one millimeter clearance when closed",
    )
    ctx.expect_overlap(
        upper_plate,
        lower_plate,
        axes="xy",
        min_overlap=0.15,
        elem_a="plate",
        elem_b="plate",
        name="upper and lower 6x6 grids align in plan",
    )
    ctx.expect_contact(
        latch,
        lid,
        elem_a="hook",
        elem_b="shell",
        name="latch is mounted to the lid by its pivot block",
    )
    ctx.expect_contact(
        latch,
        base,
        elem_a="hook",
        elem_b="shell",
        name="front latch reaches the front base handle in the closed pose",
    )

    closed_lid_pos = ctx.part_world_position(lid)
    with ctx.pose({lid_hinge: math.radians(105.0)}):
        open_lid_pos = ctx.part_world_position(lid)
        ctx.check(
            "open lid raises forward edge",
            open_lid_pos is not None and closed_lid_pos is not None and open_lid_pos[2] > closed_lid_pos[2] + 0.05,
            details=f"closed={closed_lid_pos}, open={open_lid_pos}",
        )
    with ctx.pose({latch_joint: math.radians(30.0)}):
        ctx.expect_gap(
            latch,
            base,
            axis="y",
            min_gap=0.002,
            elem_a="hook",
            elem_b="shell",
            name="released latch swings clear of the base front",
        )

    return ctx.report()


object_model = build_object_model()
