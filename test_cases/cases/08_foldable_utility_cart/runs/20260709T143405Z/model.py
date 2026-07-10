from __future__ import annotations

from math import pi

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


FRAME_L = 0.22
FRAME_W = 0.14
BASE_Z = 0.028
TOP_Z = 0.110
WHEEL_R = 0.022
WHEEL_W = 0.012
BAR_T = 0.008
LINK_L = 0.118
LINK_W = 0.012
LINK_T = 0.005


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="folding_cart_frame")

    black = model.material("black", rgba=(0.08, 0.08, 0.09, 1.0))
    dark = model.material("dark", rgba=(0.18, 0.18, 0.19, 1.0))
    gray = model.material("gray", rgba=(0.42, 0.42, 0.44, 1.0))
    rubber = model.material("rubber", rgba=(0.12, 0.12, 0.12, 1.0))

    chassis = model.part("chassis")
    chassis.visual(Box((FRAME_L, BAR_T, BAR_T)), origin=Origin(xyz=(FRAME_L / 2.0, BAR_T / 2.0, BASE_Z)), material=black, name="front_rail")
    chassis.visual(Box((FRAME_L, BAR_T, BAR_T)), origin=Origin(xyz=(FRAME_L / 2.0, FRAME_W - BAR_T / 2.0, BASE_Z)), material=black, name="rear_rail")
    chassis.visual(Box((BAR_T, FRAME_W - 2 * BAR_T, BAR_T)), origin=Origin(xyz=(BAR_T / 2.0, FRAME_W / 2.0, BASE_Z)), material=black, name="left_rail")
    chassis.visual(Box((BAR_T, FRAME_W - 2 * BAR_T, BAR_T)), origin=Origin(xyz=(FRAME_L - BAR_T / 2.0, FRAME_W / 2.0, BASE_Z)), material=black, name="right_rail")
    chassis.visual(Cylinder(radius=0.004, length=FRAME_W + 0.008), origin=Origin(xyz=(0.016, FRAME_W / 2.0, WHEEL_R), rpy=(pi / 2.0, 0.0, 0.0)), material=dark, name="front_axle")
    chassis.visual(Cylinder(radius=0.004, length=FRAME_W + 0.008), origin=Origin(xyz=(FRAME_L - 0.016, FRAME_W / 2.0, WHEEL_R), rpy=(pi / 2.0, 0.0, 0.0)), material=dark, name="rear_axle")
    chassis.visual(Box((0.010, 0.010, 0.060)), origin=Origin(xyz=(0.032, 0.022, BASE_Z + 0.030)), material=black)
    chassis.visual(Box((0.010, 0.096, 0.010)), origin=Origin(xyz=(0.032, FRAME_W / 2.0, BASE_Z + 0.055)), material=black)
    chassis.visual(Box((0.010, 0.010, 0.060)), origin=Origin(xyz=(0.032, FRAME_W - 0.022, BASE_Z + 0.030)), material=black)
    chassis.visual(Box((0.010, 0.010, 0.060)), origin=Origin(xyz=(FRAME_L - 0.032, 0.022, BASE_Z + 0.030)), material=black)
    chassis.visual(Box((0.010, 0.096, 0.010)), origin=Origin(xyz=(FRAME_L - 0.032, FRAME_W / 2.0, BASE_Z + 0.055)), material=black)
    chassis.visual(Box((0.010, 0.010, 0.060)), origin=Origin(xyz=(FRAME_L - 0.032, FRAME_W - 0.022, BASE_Z + 0.030)), material=black)

    basket = model.part("basket")
    basket.visual(Box((0.182, BAR_T, BAR_T)), origin=Origin(xyz=(0.091, BAR_T / 2.0, 0.0)), material=black, name="front_rail")
    basket.visual(Box((0.182, BAR_T, BAR_T)), origin=Origin(xyz=(0.091, 0.106 - BAR_T / 2.0, 0.0)), material=black, name="rear_rail")
    basket.visual(Box((BAR_T, 0.106 - 2 * BAR_T, BAR_T)), origin=Origin(xyz=(BAR_T / 2.0, 0.053, 0.0)), material=black, name="left_rail")
    basket.visual(Box((BAR_T, 0.106 - 2 * BAR_T, BAR_T)), origin=Origin(xyz=(0.182 - BAR_T / 2.0, 0.053, 0.0)), material=black, name="right_rail")
    basket.visual(Box((0.010, 0.010, 0.054)), origin=Origin(xyz=(0.014, 0.014, -0.031)), material=black)
    basket.visual(Box((0.010, 0.078, 0.010)), origin=Origin(xyz=(0.014, 0.053, -0.053)), material=black)
    basket.visual(Box((0.010, 0.010, 0.054)), origin=Origin(xyz=(0.014, 0.092, -0.031)), material=black)
    basket.visual(Box((0.010, 0.010, 0.054)), origin=Origin(xyz=(0.168, 0.014, -0.031)), material=black)
    basket.visual(Box((0.010, 0.078, 0.010)), origin=Origin(xyz=(0.168, 0.053, -0.053)), material=black)
    basket.visual(Box((0.010, 0.010, 0.048)), origin=Origin(xyz=(0.168, 0.092, -0.034)), material=black)

    handle = model.part("handle")
    handle.visual(Box((0.010, 0.010, 0.098)), origin=Origin(xyz=(0.000, 0.000, 0.049)), material=gray, name="left_leg")
    handle.visual(Box((0.010, 0.120, 0.010)), origin=Origin(xyz=(0.000, 0.060, 0.098)), material=gray, name="top_bar")
    handle.visual(Box((0.010, 0.010, 0.098)), origin=Origin(xyz=(0.000, 0.120, 0.049)), material=gray, name="right_leg")
    handle.visual(Cylinder(radius=0.007, length=0.060), origin=Origin(xyz=(0.000, 0.060, 0.105), rpy=(pi / 2.0, 0.0, 0.0)), material=rubber, name="grip")

    front_link_0 = model.part("front_link_0")
    front_link_0.visual(Box((LINK_L, LINK_W, LINK_T)), origin=Origin(xyz=(LINK_L / 2.0 - 0.002, 0.0, 0.0), rpy=(0.0, 0.0, 0.95)), material=dark, name="bar")
    front_link_1 = model.part("front_link_1")
    front_link_1.visual(Box((LINK_L, LINK_W, LINK_T)), origin=Origin(xyz=(LINK_L / 2.0, 0.0, 0.0), rpy=(0.0, 0.0, -0.95)), material=dark, name="bar")
    rear_link_0 = model.part("rear_link_0")
    rear_link_0.visual(Box((LINK_L, LINK_W, LINK_T)), origin=Origin(xyz=(LINK_L / 2.0 - 0.002, 0.0, 0.0), rpy=(0.0, 0.0, 0.95)), material=dark, name="bar")
    rear_link_1 = model.part("rear_link_1")
    rear_link_1.visual(Box((LINK_L, LINK_W, LINK_T)), origin=Origin(xyz=(LINK_L / 2.0, 0.0, 0.0), rpy=(0.0, 0.0, -0.95)), material=dark, name="bar")

    lock_0 = model.part("lock_0")
    lock_0.visual(Box((0.018, 0.008, 0.004)), origin=Origin(xyz=(0.009, 0.0, 0.0)), material=gray, name="lock")
    lock_0.visual(Box((0.008, 0.008, 0.012)), origin=Origin(xyz=(0.018, 0.0, 0.004)), material=gray)
    lock_1 = model.part("lock_1")
    lock_1.visual(Box((0.018, 0.008, 0.004)), origin=Origin(xyz=(0.009, 0.0, 0.0)), material=gray, name="lock")
    lock_1.visual(Box((0.008, 0.008, 0.012)), origin=Origin(xyz=(0.018, 0.0, 0.004)), material=gray)

    for i in range(4):
        wheel = model.part(f"wheel_{i}")
        wheel.visual(Cylinder(radius=WHEEL_R, length=WHEEL_W), origin=Origin(rpy=(pi / 2.0, 0.0, 0.0)), material=rubber, name="tire")
        wheel.visual(Cylinder(radius=0.010, length=WHEEL_W + 0.002), origin=Origin(rpy=(pi / 2.0, 0.0, 0.0)), material=dark, name="hub")

    model.articulation("chassis_to_basket", ArticulationType.PRISMATIC, parent=chassis, child=basket, origin=Origin(xyz=(0.019, 0.017, TOP_Z)), axis=(0.0, 0.0, -1.0), motion_limits=MotionLimits(effort=25.0, velocity=0.08, lower=0.0, upper=0.050))
    model.articulation("basket_to_handle", ArticulationType.REVOLUTE, parent=basket, child=handle, origin=Origin(xyz=(0.172, 0.010, -0.004)), axis=(0.0, -1.0, 0.0), motion_limits=MotionLimits(effort=10.0, velocity=1.5, lower=-0.20, upper=1.10))

    model.articulation("chassis_to_front_link_0", ArticulationType.REVOLUTE, parent=chassis, child=front_link_0, origin=Origin(xyz=(0.030, 0.024, BASE_Z + 0.008)), axis=(0.0, 1.0, 0.0), motion_limits=MotionLimits(effort=6.0, velocity=1.5, lower=-0.50, upper=0.55))
    model.articulation("basket_to_front_link_1", ArticulationType.REVOLUTE, parent=basket, child=front_link_1, origin=Origin(xyz=(0.030, 0.024, -0.002)), axis=(0.0, 1.0, 0.0), motion_limits=MotionLimits(effort=6.0, velocity=1.5, lower=-0.55, upper=0.50))
    model.articulation("chassis_to_rear_link_0", ArticulationType.REVOLUTE, parent=chassis, child=rear_link_0, origin=Origin(xyz=(FRAME_L - 0.148, FRAME_W - 0.024, BASE_Z + 0.008)), axis=(0.0, 1.0, 0.0), motion_limits=MotionLimits(effort=6.0, velocity=1.5, lower=-0.50, upper=0.55))
    model.articulation("basket_to_rear_link_1", ArticulationType.REVOLUTE, parent=basket, child=rear_link_1, origin=Origin(xyz=(0.022, 0.082, -0.002)), axis=(0.0, 1.0, 0.0), motion_limits=MotionLimits(effort=6.0, velocity=1.5, lower=-0.55, upper=0.50))

    model.articulation("basket_to_lock_0", ArticulationType.REVOLUTE, parent=basket, child=lock_0, origin=Origin(xyz=(0.124, 0.008, 0.004)), axis=(0.0, 1.0, 0.0), motion_limits=MotionLimits(effort=1.0, velocity=1.0, lower=-0.85, upper=0.10))
    model.articulation("basket_to_lock_1", ArticulationType.REVOLUTE, parent=basket, child=lock_1, origin=Origin(xyz=(0.124, 0.098, 0.004)), axis=(0.0, 1.0, 0.0), motion_limits=MotionLimits(effort=1.0, velocity=1.0, lower=-0.85, upper=0.10))

    wheel_positions = [
        (0.016, -0.004, WHEEL_R),
        (0.016, FRAME_W + 0.004, WHEEL_R),
        (FRAME_L - 0.016, -0.004, WHEEL_R),
        (FRAME_L - 0.016, FRAME_W + 0.004, WHEEL_R),
    ]
    for index, pos in enumerate(wheel_positions):
        model.articulation(
            f"chassis_to_wheel_{index}",
            ArticulationType.CONTINUOUS,
            parent=chassis,
            child=model.get_part(f"wheel_{index}"),
            origin=Origin(xyz=pos),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=10.0),
        )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    chassis = object_model.get_part("chassis")
    basket = object_model.get_part("basket")
    handle = object_model.get_part("handle")
    lock_0 = object_model.get_part("lock_0")
    wheel_0 = object_model.get_part("wheel_0")

    basket_slide = object_model.get_articulation("chassis_to_basket")
    handle_hinge = object_model.get_articulation("basket_to_handle")
    lock_hinge = object_model.get_articulation("basket_to_lock_0")

    ctx.expect_origin_gap(basket, chassis, axis="z", min_gap=0.070, max_gap=0.120, name="basket stays above chassis")
    ctx.expect_origin_gap(handle, basket, axis="x", min_gap=0.160, max_gap=0.180, name="handle hinge stays near rear basket edge")
    ctx.expect_contact(wheel_0, chassis, elem_a="hub", elem_b="front_axle", name="wheel mounts on axle")

    with ctx.pose({basket_slide: 0.045, handle_hinge: 0.95, lock_hinge: 0.0}):
        ctx.expect_origin_gap(basket, chassis, axis="z", min_gap=0.060, name="basket lifts in open pose")
        ctx.expect_origin_gap(handle, basket, axis="x", min_gap=0.160, name="handle remains behind basket when open")

    with ctx.pose({basket_slide: 0.0, handle_hinge: -0.15, lock_hinge: -0.75}):
        ctx.expect_origin_gap(handle, basket, axis="x", max_gap=0.180, name="handle folds close to basket")

    ctx.expect_origin_gap(lock_0, basket, axis="z", min_gap=-0.005, max_gap=0.020, name="lock sits on basket rail")

    return ctx.report()


object_model = build_object_model()