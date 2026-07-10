from __future__ import annotations

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    Cylinder,
    Material,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)


HANDLE_LENGTH = 0.120
HANDLE_SECTION = (0.090, 0.012, 0.008)
GRIP_SECTION = (0.040, 0.016, 0.011)
JAW_LENGTH = 0.048
JAW_THICK = 0.008
JAW_WIDTH = 0.012
JAW_REST_GAP = 0.035
JAW_CLOSE_GAP = 0.002
JAW_OPEN_ANGLE = 0.30
HANDLE_CLOSE_ANGLE = 0.52
PIN_RADIUS = 0.003
PIN_LENGTH = 0.018
PIN_CLEARANCE = 0.00035
PIVOT_RADIUS = 0.005
PI_HALF = 1.57079632679


def add_box(part, size, xyz, material, name):
    part.visual(Box(size), origin=Origin(xyz=xyz), material=material, name=name)


def build_handle(part, sign: float, frame: Material, grip: Material) -> None:
    add_box(part, (0.030, 0.016, 0.010), (0.000, sign * 0.012, -0.002), frame, "pivot_block")
    add_box(part, (0.038, 0.012, 0.008), (0.024, sign * 0.020, -0.018), frame, "neck")
    add_box(part, HANDLE_SECTION, (0.070, sign * 0.030, -0.050), frame, "spine")
    add_box(part, GRIP_SECTION, (0.102, sign * 0.032, -0.076), grip, "grip")
    part.visual(
        Cylinder(radius=PIVOT_RADIUS + PIN_CLEARANCE, length=0.012),
        origin=Origin(xyz=(0.0, sign * 0.012, 0.0), rpy=(PI_HALF, 0.0, 0.0)),
        material=frame,
        name="pivot_boss",
    )


def build_jaw(part, sign: float, metal: Material, tooth: Material) -> None:
    add_box(part, (0.022, 0.014, 0.008), (0.002, sign * 0.012, 0.004), metal, "heel")
    add_box(part, (0.030, 0.010, JAW_THICK), (0.018, sign * 0.018, 0.010), metal, "arm")
    add_box(part, (JAW_LENGTH, 0.010, JAW_THICK), (0.050, sign * 0.0225, 0.014), metal, "tip")
    add_box(part, (0.018, 0.008, 0.006), (0.026, sign * 0.021, 0.007), metal, "link_tab")
    part.visual(
        Cylinder(radius=PIVOT_RADIUS + PIN_CLEARANCE, length=JAW_WIDTH),
        origin=Origin(xyz=(0.0, sign * 0.012, 0.0), rpy=(PI_HALF, 0.0, 0.0)),
        material=metal,
        name="pivot_boss",
    )
    for idx in range(8):
        add_box(
            part,
            (0.0026, 0.0018, 0.0010),
            (0.032 + idx * 0.005, sign * (JAW_REST_GAP / 2.0), 0.012 + idx * 0.0004),
            tooth,
            f"tooth_{idx}",
        )


def build_link(part, sign: float, metal: Material) -> None:
    add_box(part, (0.044, 0.005, 0.004), (0.042, sign * 0.022, 0.006), metal, "bar")
    add_box(part, (0.010, 0.008, 0.006), (0.020, sign * 0.022, 0.006), metal, "rear_pad")
    add_box(part, (0.010, 0.008, 0.006), (0.064, sign * 0.022, 0.006), metal, "front_pad")
    part.visual(
        Cylinder(radius=PIN_RADIUS + PIN_CLEARANCE, length=0.010),
        origin=Origin(xyz=(0.020, sign * 0.022, 0.006), rpy=(PI_HALF, 0.0, 0.0)),
        material=metal,
        name="rear_eye",
    )
    part.visual(
        Cylinder(radius=PIN_RADIUS + PIN_CLEARANCE, length=0.010),
        origin=Origin(xyz=(0.064, sign * 0.022, 0.006), rpy=(PI_HALF, 0.0, 0.0)),
        material=metal,
        name="front_eye",
    )


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="desktop_compound_plier_demo")

    steel = model.material("steel", rgba=(0.70, 0.72, 0.75, 1.0))
    dark = model.material("dark", rgba=(0.55, 0.57, 0.60, 1.0))
    rubber = model.material("rubber", rgba=(0.16, 0.17, 0.20, 1.0))
    tooth = model.material("tooth", rgba=(0.63, 0.65, 0.68, 1.0))
    pin = model.material("pin", rgba=(0.42, 0.44, 0.47, 1.0))

    lower_handle = model.part("lower_handle")
    build_handle(lower_handle, -1.0, steel, rubber)
    add_box(lower_handle, (0.014, 0.030, 0.012), (-0.006, 0.0, 0.0), dark, "pivot_bridge")
    lower_handle.visual(
        Cylinder(radius=PIVOT_RADIUS, length=PIN_LENGTH),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(PI_HALF, 0.0, 0.0)),
        material=pin,
        name="main_pivot_pin",
    )

    upper_handle = model.part("upper_handle")
    build_handle(upper_handle, 1.0, steel, rubber)

    lower_jaw = model.part("lower_jaw")
    build_jaw(lower_jaw, -1.0, dark, tooth)

    upper_jaw = model.part("upper_jaw")
    build_jaw(upper_jaw, 1.0, dark, tooth)

    lower_link = model.part("lower_link")
    build_link(lower_link, -1.0, steel)

    upper_link = model.part("upper_link")
    build_link(upper_link, 1.0, steel)

    model.articulation(
        "upper_handle_joint",
        ArticulationType.REVOLUTE,
        parent=lower_handle,
        child=upper_handle,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=HANDLE_CLOSE_ANGLE, effort=5.0, velocity=1.5),
    )
    model.articulation(
        "lower_jaw_joint",
        ArticulationType.REVOLUTE,
        parent=lower_handle,
        child=lower_jaw,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=JAW_OPEN_ANGLE, effort=5.0, velocity=1.5),
    )
    model.articulation(
        "upper_jaw_joint",
        ArticulationType.REVOLUTE,
        parent=lower_handle,
        child=upper_jaw,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=JAW_OPEN_ANGLE, effort=5.0, velocity=1.5),
        mimic=Mimic(joint="lower_jaw_joint", multiplier=1.0, offset=0.0),
    )
    model.articulation(
        "lower_link_joint",
        ArticulationType.FIXED,
        parent=lower_handle,
        child=lower_link,
        origin=Origin(xyz=(0.006, 0.0, 0.0)),
    )
    model.articulation(
        "upper_link_joint",
        ArticulationType.FIXED,
        parent=lower_handle,
        child=upper_link,
        origin=Origin(xyz=(0.006, 0.0, 0.0)),
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    lower_jaw = object_model.get_part("lower_jaw")
    upper_jaw = object_model.get_part("upper_jaw")
    lower_handle = object_model.get_part("lower_handle")
    upper_handle = object_model.get_part("upper_handle")
    lower_link = object_model.get_part("lower_link")
    upper_link = object_model.get_part("upper_link")
    lower_jaw_joint = object_model.get_articulation("lower_jaw_joint")
    upper_handle_joint = object_model.get_articulation("upper_handle_joint")

    ctx.expect_gap(
        upper_jaw,
        lower_jaw,
        axis="y",
        min_gap=0.034,
        max_gap=0.036,
        positive_elem="tip",
        negative_elem="tip",
        name="jaw opening stroke is 35 mm at rest",
    )
    ctx.expect_origin_distance(
        upper_jaw,
        lower_jaw,
        axes="y",
        min_dist=0.0,
        max_dist=0.0005,
        name="jaw halves remain left-right symmetric about the pivot plane",
    )
    ctx.expect_gap(
        upper_handle,
        lower_handle,
        axis="y",
        min_gap=0.020,
        positive_elem="spine",
        negative_elem="spine",
        name="handles stay separated in display pose",
    )
    ctx.expect_gap(
        upper_link,
        lower_link,
        axis="y",
        min_gap=0.036,
        positive_elem="bar",
        negative_elem="bar",
        name="compound links do not interfere at rest",
    )

    with ctx.pose({lower_jaw_joint: JAW_OPEN_ANGLE, upper_handle_joint: HANDLE_CLOSE_ANGLE}):
        ctx.expect_gap(
            upper_jaw,
            lower_jaw,
            axis="y",
            min_gap=0.0015,
            max_gap=0.004,
            positive_elem="tip",
            negative_elem="tip",
            name="jaws close near 2 mm without collision",
        )
        ctx.expect_gap(
            upper_handle,
            lower_handle,
            axis="y",
            min_gap=0.006,
            positive_elem="neck",
            negative_elem="neck",
            name="closed handles keep printable clearance",
        )
        ctx.expect_gap(
            upper_jaw,
            lower_jaw,
            axis="z",
            max_penetration=0.0,
            positive_elem="tip",
            negative_elem="tip",
            name="jaw plates avoid vertical interference",
        )

    return ctx.report()


object_model = build_object_model()