from __future__ import annotations

import math

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


BODY_SIZE = 0.12
BODY_HEIGHT = 0.034
BODY_WALL = 0.0024
ARM_LENGTH = 0.095
ARM_WIDTH = 0.014
ARM_HEIGHT = 0.008
ARM_TIP_RADIUS = 0.016
HINGE_RADIUS = 0.007
HINGE_WIDTH = 0.018
PIN_RADIUS = 0.0018
LOCK_TAB_WIDTH = 0.010
LOCK_TAB_HEIGHT = 0.004
LOCK_TAB_LENGTH = 0.012
MOTOR_PLATE_RADIUS = 0.018
MOTOR_PLATE_THICKNESS = 0.003
HINGE_OFFSET = 0.050


ANGLE_BY_NAME = {
    "front_arm": 0.0,
    "arm_1": 90.0,
    "arm_2": 180.0,
    "arm_3": 270.0,
}

FOLD_LIMITS = {
    "front_arm": (-math.radians(120.0), 0.0),
    "arm_1": (0.0, math.radians(120.0)),
    "arm_2": (-math.radians(120.0), 0.0),
    "arm_3": (0.0, math.radians(120.0)),
}


def shell_shape() -> cq.Workplane:
    outer = cq.Workplane("XY").box(BODY_SIZE, BODY_SIZE, BODY_HEIGHT)
    inner = (
        cq.Workplane("XY")
        .box(BODY_SIZE - 2 * BODY_WALL, BODY_SIZE - 2 * BODY_WALL, BODY_HEIGHT - 2 * BODY_WALL)
        .translate((0.0, 0.0, BODY_WALL))
    )
    shell = outer.cut(inner)

    top_window = cq.Workplane("XY").box(0.050, 0.050, BODY_HEIGHT).translate((0.0, 0.0, 0.006))
    side_relief_x = cq.Workplane("XY").box(0.050, 0.110, 0.020)
    side_relief_y = cq.Workplane("XY").box(0.110, 0.050, 0.020)
    corner_hole = cq.Workplane("XY").circle(0.004).extrude(BODY_HEIGHT)

    shell = shell.cut(top_window).cut(side_relief_x).cut(side_relief_y)
    for sx in (-0.040, 0.040):
        for sy in (-0.040, 0.040):
            shell = shell.cut(corner_hole.translate((sx, sy, -BODY_HEIGHT / 2)))

    return shell


def hinge_block(angle_deg: float) -> cq.Workplane:
    r = HINGE_OFFSET
    x = r * math.cos(math.radians(angle_deg))
    y = r * math.sin(math.radians(angle_deg))
    block = cq.Workplane("XY").box(0.020, 0.016, 0.018).translate((x, y, 0.0))
    cylinder = (
        cq.Workplane("YZ")
        .circle(HINGE_RADIUS)
        .extrude(HINGE_WIDTH / 2, both=True)
        .rotate((0, 0, 0), (0, 0, 1), angle_deg)
        .translate((x, y, 0.0))
    )
    return block.union(cylinder)


def latch_body(angle_deg: float) -> cq.Workplane:
    r = HINGE_OFFSET - 0.010
    x = r * math.cos(math.radians(angle_deg))
    y = r * math.sin(math.radians(angle_deg))
    latch = cq.Workplane("XY").box(0.012, 0.008, 0.010).translate((x, y, -0.006))
    tab = cq.Workplane("XY").box(0.010, 0.005, 0.003).translate((x, y, 0.001))
    return latch.union(tab)


def arm_shape() -> cq.Workplane:
    beam = cq.Workplane("XY").box(ARM_LENGTH, ARM_WIDTH, ARM_HEIGHT).translate((ARM_LENGTH / 2, 0.0, 0.0))
    tip = cq.Workplane("XY").circle(ARM_TIP_RADIUS).extrude(ARM_HEIGHT).translate((ARM_LENGTH, 0.0, -ARM_HEIGHT / 2))
    shoulder = cq.Workplane("XY").box(0.018, 0.016, 0.012).translate((0.009, 0.0, 0.0))
    foot = cq.Workplane("XY").box(0.014, 0.016, 0.002).translate((0.009, 0.0, -0.005))
    hinge_barrel = (
        cq.Workplane("YZ")
        .circle(HINGE_RADIUS - 0.0006)
        .extrude(HINGE_WIDTH / 2, both=True)
        .translate((0.0, 0.0, 0.0))
    )
    pin_hole = (
        cq.Workplane("YZ")
        .circle(PIN_RADIUS)
        .extrude(HINGE_WIDTH, both=True)
        .translate((0.0, 0.0, 0.0))
    )
    latch = cq.Workplane("XY").box(LOCK_TAB_LENGTH, LOCK_TAB_WIDTH, LOCK_TAB_HEIGHT).translate((0.022, 0.0, 0.007))
    motor_plate = cq.Workplane("XY").circle(MOTOR_PLATE_RADIUS).extrude(MOTOR_PLATE_THICKNESS).translate((ARM_LENGTH, 0.0, ARM_HEIGHT / 2))
    center_hole = cq.Workplane("XY").circle(0.0045).extrude(MOTOR_PLATE_THICKNESS).translate((ARM_LENGTH, 0.0, ARM_HEIGHT / 2))

    arm = beam.union(tip).union(shoulder).union(foot).union(hinge_barrel).union(latch).union(motor_plate)
    arm = arm.cut(pin_hole).cut(center_hole)
    return arm


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="folding_quadcopter_frame")

    carbon = model.material("carbon", color=(0.18, 0.18, 0.20, 1.0))
    polymer = model.material("polymer", color=(0.46, 0.48, 0.50, 1.0))
    latch_mat = model.material("latch", color=(0.12, 0.12, 0.12, 1.0))

    body = model.part("body")
    shell = shell_shape()
    for arm_name, angle in ANGLE_BY_NAME.items():
        shell = shell.union(hinge_block(angle)).union(latch_body(angle))
    body.visual(mesh_from_cadquery(shell, "body_shell"), material=polymer, name="body_shell")

    for arm_name, angle in ANGLE_BY_NAME.items():
        arm = model.part(arm_name)
        arm.visual(mesh_from_cadquery(arm_shape(), f"{arm_name}_mesh"), material=carbon, name="arm")
        arm.visual(
            mesh_from_cadquery(
                cq.Workplane("XY").box(LOCK_TAB_LENGTH, LOCK_TAB_WIDTH, LOCK_TAB_HEIGHT).translate((0.022, 0.0, 0.007)),
                f"{arm_name}_latch",
            ),
            material=latch_mat,
            name="lock_tab",
        )

        radius = HINGE_OFFSET
        x = radius * math.cos(math.radians(angle))
        y = radius * math.sin(math.radians(angle))
        joint = model.articulation(
            f"body_to_{arm_name}",
            ArticulationType.REVOLUTE,
            parent=body,
            child=arm,
            origin=Origin(xyz=(x, y, BODY_HEIGHT / 2 + ARM_HEIGHT / 2), rpy=(0.0, 0.0, math.radians(angle))),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                lower=FOLD_LIMITS[arm_name][0],
                upper=FOLD_LIMITS[arm_name][1],
                effort=2.0,
                velocity=3.0,
            ),
        )
        joint.meta = {
            "expanded": 0.0,
            "folded": FOLD_LIMITS[arm_name][0] if FOLD_LIMITS[arm_name][0] != 0.0 else FOLD_LIMITS[arm_name][1],
        }

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    body = object_model.get_part("body")
    joint_names = [f"body_to_{name}" for name in ANGLE_BY_NAME]

    for name in ANGLE_BY_NAME:
        arm = object_model.get_part(name)
        ctx.expect_contact(arm, body, name=f"{name} mounts to body")

    expanded_pose = {object_model.get_articulation(j): 0.0 for j in joint_names}
    with ctx.pose(expanded_pose):
        for name in ANGLE_BY_NAME:
            arm = object_model.get_part(name)
            ctx.expect_gap(arm, body, axis="z", min_gap=-0.003, max_gap=0.006, name=f"{name} sits near body top plane when deployed")

    folded_pose = {}
    for name in ANGLE_BY_NAME:
        articulation = object_model.get_articulation(f"body_to_{name}")
        limits = FOLD_LIMITS[name]
        folded_pose[articulation] = limits[0] if limits[0] != 0.0 else limits[1]
    with ctx.pose(folded_pose):
        front = object_model.get_part("front_arm")
        arm_1 = object_model.get_part("arm_1")
        arm_2 = object_model.get_part("arm_2")
        arm_3 = object_model.get_part("arm_3")
        ctx.expect_origin_distance(front, arm_2, axes="xy", min_dist=0.030, name="folded opposing arms stay laterally separated")
        ctx.expect_origin_distance(arm_1, arm_3, axes="xy", min_dist=0.030, name="folded secondary arms stay laterally separated")

    return ctx.report()


object_model = build_object_model()
