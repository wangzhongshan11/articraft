from __future__ import annotations

import math

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)


CLEARANCE = 0.00035
LEG_LENGTH = 0.150
PHONE_MIN = 0.065
PHONE_MAX = 0.085
CLAMP_TRAVEL = PHONE_MAX - PHONE_MIN


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="desktop_folding_tripod_phone_stand")

    black = model.material("black", rgba=(0.10, 0.10, 0.11, 1.0))
    dark_gray = model.material("dark_gray", rgba=(0.20, 0.21, 0.22, 1.0))
    rubber = model.material("rubber", rgba=(0.07, 0.07, 0.07, 1.0))
    steel = model.material("steel", rgba=(0.45, 0.47, 0.50, 1.0))

    base = model.part("base")
    base.visual(Cylinder(radius=0.016, length=0.160), origin=Origin(xyz=(0.0, 0.0, 0.080)), material=black, name="center_post")
    base.visual(Cylinder(radius=0.026, length=0.016), origin=Origin(xyz=(0.0, 0.0, 0.125)), material=dark_gray, name="leg_hub")
    base.visual(Cylinder(radius=0.018, length=0.012), origin=Origin(xyz=(0.0, 0.0, 0.006)), material=rubber, name="bottom_cap")
    base.visual(Cylinder(radius=0.010, length=0.034), origin=Origin(xyz=(0.0, 0.0, 0.177)), material=black, name="head_stem")

    slide_ring = model.part("slide_ring")
    slide_ring.visual(Cylinder(radius=0.024, length=0.012), origin=Origin(xyz=(0.0, 0.0, 0.006)), material=dark_gray, name="ring_shell")
    slide_ring.visual(Box((0.014, 0.012, 0.012)), origin=Origin(xyz=(0.025, 0.0, 0.006)), material=dark_gray, name="ring_lug")
    model.articulation(
        "base_to_slide_ring",
        ArticulationType.PRISMATIC,
        parent=base,
        child=slide_ring,
        origin=Origin(xyz=(0.0, 0.0, 0.070)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=18.0, velocity=0.08, lower=0.0, upper=0.055),
    )

    leg_angles = (0.0, 2.0 * math.pi / 3.0, 4.0 * math.pi / 3.0)
    for index, angle in enumerate(leg_angles):
        leg = model.part(f"leg_{index}")
        leg.visual(Box((LEG_LENGTH, 0.020, 0.014)), origin=Origin(xyz=(LEG_LENGTH / 2.0, 0.0, -0.007)), material=black, name="leg_body")
        leg.visual(Box((0.020, 0.022, 0.014)), origin=Origin(xyz=(0.010, 0.0, -0.007)), material=dark_gray, name="hinge_block")
        leg.visual(Cylinder(radius=0.0085, length=0.016), origin=Origin(xyz=(LEG_LENGTH - 0.010, 0.0, -0.009), rpy=(math.pi / 2.0, 0.0, 0.0)), material=rubber, name="foot")
        model.articulation(
            f"base_to_leg_{index}",
            ArticulationType.REVOLUTE,
            parent=base,
            child=leg,
            origin=Origin(xyz=(0.026, 0.0, 0.125), rpy=(0.0, 0.0, angle)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=8.0, velocity=2.0, lower=0.0, upper=1.05),
        )

    head = model.part("head")
    head.visual(Box((0.024, 0.032, 0.020)), origin=Origin(xyz=(0.0, 0.0, 0.010)), material=black, name="tilt_block")
    head.visual(Cylinder(radius=0.014, length=0.010), origin=Origin(xyz=(0.0, 0.0, 0.005)), material=dark_gray, name="mount_collar")
    head.visual(Cylinder(radius=0.006, length=0.040), origin=Origin(xyz=(0.0, 0.0, 0.010), rpy=(0.0, math.pi / 2.0, 0.0)), material=steel, name="tilt_axle")
    model.articulation("base_to_head", ArticulationType.FIXED, parent=base, child=head, origin=Origin(xyz=(0.0, 0.0, 0.194)))

    cradle = model.part("cradle")
    cradle.visual(Box((0.010, 0.030, 0.120)), origin=Origin(xyz=(0.0, 0.0, 0.060)), material=black, name="back_plate")
    cradle.visual(Box((0.018, 0.020, 0.020)), origin=Origin(xyz=(0.0, 0.0, 0.010)), material=dark_gray, name="tilt_hub")
    cradle.visual(Cylinder(radius=0.003, length=0.022), origin=Origin(xyz=(0.006, 0.0, 0.060), rpy=(0.0, math.pi / 2.0, 0.0)), material=steel, name="mount_bolt")
    cradle.visual(Box((0.034, 0.008, 0.010)), origin=Origin(xyz=(0.018, 0.0, 0.060)), material=dark_gray, name="slider_rail")
    model.articulation(
        "head_to_cradle",
        ArticulationType.REVOLUTE,
        parent=head,
        child=cradle,
        origin=Origin(xyz=(0.0, 0.0, 0.010)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=1.5, lower=math.radians(-20.0), upper=math.radians(75.0)),
    )

    jaw_fixed = model.part("jaw_fixed")
    jaw_fixed.visual(Box((0.018, 0.018, 0.092)), origin=Origin(xyz=(0.009, 0.0, 0.046)), material=black, name="jaw_body")
    jaw_fixed.visual(Box((0.006, 0.018, 0.014)), origin=Origin(xyz=(0.003, 0.0, 0.007)), material=black, name="lip")
    jaw_fixed.visual(Box((0.014, 0.020, 0.050)), origin=Origin(xyz=(0.017, 0.0, 0.046)), material=dark_gray, name="mount_block")
    jaw_fixed.visual(Box((0.012, 0.008, 0.010)), origin=Origin(xyz=(0.006, 0.0, 0.046)), material=dark_gray, name="rail_block")
    model.articulation("cradle_to_jaw_fixed", ArticulationType.FIXED, parent=cradle, child=jaw_fixed, origin=Origin(xyz=(0.020, -0.026, 0.014)))

    jaw_moving = model.part("jaw_moving")
    jaw_moving.visual(Box((0.018, 0.018, 0.092)), origin=Origin(xyz=(-0.009, 0.0, 0.046)), material=black, name="jaw_body")
    jaw_moving.visual(Box((0.006, 0.018, 0.014)), origin=Origin(xyz=(-0.003, 0.0, 0.007)), material=black, name="lip")
    jaw_moving.visual(Box((0.034, 0.008, 0.010)), origin=Origin(xyz=(-0.017, 0.0, 0.046)), material=dark_gray, name="slider_block")
    jaw_moving.visual(Cylinder(radius=0.004, length=0.020), origin=Origin(xyz=(-0.028, 0.0, 0.046), rpy=(0.0, math.pi / 2.0, 0.0)), material=steel, name="clamp_bolt")
    model.articulation(
        "cradle_to_jaw_moving",
        ArticulationType.PRISMATIC,
        parent=cradle,
        child=jaw_moving,
        origin=Origin(xyz=(0.020, 0.03935, 0.014)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=10.0, velocity=0.03, lower=0.0, upper=CLAMP_TRAVEL),
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    base = object_model.get_part("base")
    slide_ring = object_model.get_part("slide_ring")
    cradle = object_model.get_part("cradle")
    jaw_fixed = object_model.get_part("jaw_fixed")
    jaw_moving = object_model.get_part("jaw_moving")
    pitch = object_model.get_articulation("head_to_cradle")
    slider = object_model.get_articulation("cradle_to_jaw_moving")
    ring_joint = object_model.get_articulation("base_to_slide_ring")

    ctx.allow_overlap(slide_ring, base, elem_a="ring_shell", elem_b="center_post", reason="The sliding ring is intentionally represented as a sleeve around the center post.")
    ctx.expect_overlap(slide_ring, base, axes="z", elem_a="ring_shell", elem_b="center_post", min_overlap=0.010, name="slide ring remains captured on post")
    ctx.expect_contact(jaw_fixed, cradle, elem_a="rail_block", elem_b="slider_rail", name="fixed jaw mounts to cradle rail")
    ctx.expect_gap(jaw_moving, jaw_fixed, axis="y", positive_elem="jaw_body", negative_elem="jaw_body", min_gap=PHONE_MIN - 0.0005, max_gap=PHONE_MIN + 0.0005, name="default clamp width matches minimum phone width")
    with ctx.pose({slider: CLAMP_TRAVEL}):
        ctx.expect_gap(jaw_moving, jaw_fixed, axis="y", positive_elem="jaw_body", negative_elem="jaw_body", min_gap=PHONE_MAX - 0.0005, max_gap=PHONE_MAX + 0.0005, name="extended clamp width matches maximum phone width")
    with ctx.pose({pitch: math.radians(75.0)}):
        ctx.expect_origin_gap(cradle, base, axis="z", min_gap=0.05, name="pitched head lifts cradle above base")
    with ctx.pose({ring_joint: 0.055}):
        ctx.expect_origin_gap(slide_ring, base, axis="z", min_gap=0.11, name="ring moves upward in folded state")

    return ctx.report()


object_model = build_object_model()