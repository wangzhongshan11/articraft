from __future__ import annotations

from math import pi

import cadquery as cq
from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    Cylinder,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

BASE_RADIUS = 0.055
BASE_THICKNESS = 0.020
WEIGHT_RADIUS = 0.024
WEIGHT_HEIGHT = 0.008
SHOULDER_Z = BASE_THICKNESS + 0.032
FORK_GAP = 0.0147
CHEEK_THICKNESS = 0.006
CHEEK_HEIGHT = 0.026
CHEEK_LENGTH = 0.020
HOLE_RADIUS = 0.002175
PIN_RADIUS = 0.002
CLEARANCE = 0.00035
LOWER_ARM_LENGTH = 0.120
UPPER_ARM_LENGTH = 0.100
ARM_THICKNESS = 0.006
ARM_WIDTH = 0.010
ARM_SPACING = 0.026
END_RADIUS = 0.010
HEAD_YOKE_WIDTH = ARM_SPACING
HEAD_YOKE_PLATE = 0.005
HEAD_NECK_LENGTH = 0.030
SHADE_LENGTH = 0.048
SHADE_FRONT_RADIUS = 0.035
SHADE_REAR_RADIUS = 0.019
SHADE_WALL = 0.0024
LOWER_LIMITS = (-0.55, 1.15)
ELBOW_LIMITS = (-1.20, 1.05)
HEAD_LIMITS = (-1.05, 0.65)


def _arm_rail(length: float, y_center: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .center(length / 2.0, y_center)
        .rect(length - END_RADIUS * 1.2, ARM_WIDTH)
        .extrude(ARM_THICKNESS)
        .union(cq.Workplane("XY").center(END_RADIUS, y_center).circle(END_RADIUS).extrude(ARM_THICKNESS))
        .union(cq.Workplane("XY").center(length - END_RADIUS, y_center).circle(END_RADIUS).extrude(ARM_THICKNESS))
    )


def _arm_shape(length: float) -> cq.Workplane:
    y_offset = ARM_SPACING / 2.0
    arm = _arm_rail(length, y_offset).union(_arm_rail(length, -y_offset))
    bridge_width = ARM_SPACING - ARM_WIDTH
    for x_pos in (END_RADIUS * 0.85, length - END_RADIUS * 0.85):
        arm = arm.union(
            cq.Workplane("XY")
            .center(x_pos, 0.0)
            .rect(ARM_THICKNESS, bridge_width)
            .extrude(ARM_THICKNESS)
        )
    for x_pos in (END_RADIUS, length - END_RADIUS):
        arm = arm.cut(
            cq.Workplane("YZ")
            .workplane(offset=x_pos)
            .pushPoints([(y_offset, ARM_THICKNESS / 2.0), (-y_offset, ARM_THICKNESS / 2.0)])
            .circle(HOLE_RADIUS)
            .extrude(ARM_THICKNESS * 2.5, both=True)
        )
    return arm


def _base_shape() -> cq.Workplane:
    plate = cq.Workplane("XY").circle(BASE_RADIUS).extrude(BASE_THICKNESS)
    boss = cq.Workplane("XY").circle(0.020).extrude(0.006).translate((0.0, 0.0, BASE_THICKNESS))

    cheek = (
        cq.Workplane("XZ")
        .moveTo(-CHEEK_LENGTH / 2.0, 0.0)
        .lineTo(CHEEK_LENGTH / 2.0, 0.0)
        .lineTo(CHEEK_LENGTH / 2.0, CHEEK_HEIGHT - 0.006)
        .lineTo(-0.003, CHEEK_HEIGHT)
        .lineTo(-CHEEK_LENGTH / 2.0, CHEEK_HEIGHT - 0.010)
        .close()
        .extrude(CHEEK_THICKNESS)
    )
    y_offset = FORK_GAP / 2.0 + CHEEK_THICKNESS / 2.0
    left_cheek = cheek.translate((0.0, y_offset - CHEEK_THICKNESS / 2.0, BASE_THICKNESS + 0.006))
    right_cheek = cheek.translate((0.0, -y_offset - CHEEK_THICKNESS / 2.0, BASE_THICKNESS + 0.006))
    axle = (
        cq.Workplane("YZ")
        .workplane(offset=0.0)
        .center(0.0, CHEEK_HEIGHT - 0.006 + BASE_THICKNESS + 0.006)
        .circle(PIN_RADIUS)
        .extrude(FORK_GAP / 2.0, both=True)
    )
    stop = (
        cq.Workplane("XZ")
        .moveTo(-0.012, 0.0)
        .lineTo(0.010, 0.0)
        .lineTo(0.006, 0.010)
        .lineTo(-0.008, 0.012)
        .close()
        .extrude(0.020)
        .translate((0.0, -0.010, BASE_THICKNESS))
    )
    return plate.union(boss).union(left_cheek).union(right_cheek).union(axle).union(stop)


def _head_shape() -> cq.Workplane:
    yoke_side = (
        cq.Workplane("XZ")
        .moveTo(-0.004, -0.008)
        .lineTo(0.018, -0.008)
        .lineTo(0.018, 0.010)
        .lineTo(0.004, 0.014)
        .lineTo(-0.004, 0.009)
        .close()
        .extrude(HEAD_YOKE_PLATE)
    )
    y_offset = HEAD_YOKE_WIDTH / 2.0
    yoke = yoke_side.translate((0.0, y_offset - HEAD_YOKE_PLATE / 2.0, 0.0)).union(
        yoke_side.translate((0.0, -y_offset - HEAD_YOKE_PLATE / 2.0, 0.0))
    )
    yoke = yoke.union(
        cq.Workplane("YZ")
        .workplane(offset=0.001)
        .center(0.0, -0.001)
        .circle(PIN_RADIUS)
        .extrude(HEAD_YOKE_WIDTH / 2.0, both=True)
    )
    neck = (
        cq.Workplane("YZ")
        .circle(SHADE_REAR_RADIUS)
        .extrude(HEAD_NECK_LENGTH)
        .rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 90.0)
        .translate((0.018, 0.0, 0.0))
    )
    outer = (
        cq.Workplane("XZ")
        .moveTo(0.0, SHADE_REAR_RADIUS)
        .lineTo(SHADE_LENGTH, SHADE_FRONT_RADIUS)
        .lineTo(SHADE_LENGTH, 0.0)
        .lineTo(0.0, 0.0)
        .close()
        .revolve(360.0, (0.0, 0.0), (SHADE_LENGTH, 0.0))
    )
    inner = (
        cq.Workplane("XZ")
        .moveTo(SHADE_WALL, SHADE_REAR_RADIUS - SHADE_WALL)
        .lineTo(SHADE_LENGTH - SHADE_WALL, SHADE_FRONT_RADIUS - SHADE_WALL)
        .lineTo(SHADE_LENGTH - SHADE_WALL, 0.0)
        .lineTo(SHADE_WALL, 0.0)
        .close()
        .revolve(360.0, (0.0, 0.0), (SHADE_LENGTH, 0.0))
    )
    shade = outer.cut(inner).translate((HEAD_NECK_LENGTH + 0.014, 0.0, 0.0))
    stop_tab = cq.Workplane("XY").center(0.010, 0.0).rect(0.008, 0.012).extrude(0.004).translate((0.0, -0.006, -0.010))
    return yoke.union(neck).union(shade).union(stop_tab)


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="adjustable_desk_lamp")
    model.material("sand", rgba=(0.82, 0.73, 0.56, 1.0))
    model.material("steel", rgba=(0.68, 0.70, 0.73, 1.0))
    model.material("white", rgba=(0.95, 0.95, 0.93, 1.0))

    base = model.part("base")
    base.visual(mesh_from_cadquery(_base_shape(), "base"), material="sand", name="base_body")
    base.visual(Cylinder(radius=WEIGHT_RADIUS, length=WEIGHT_HEIGHT), origin=Origin(xyz=(0.0, 0.0, WEIGHT_HEIGHT / 2.0)), material="steel", name="weight_core")
    base.inertial = Inertial.from_geometry(Cylinder(radius=BASE_RADIUS, length=BASE_THICKNESS), mass=1.5, origin=Origin(xyz=(0.0, 0.0, BASE_THICKNESS / 2.0)))

    lower_arm = model.part("lower_arm")
    lower_arm.visual(mesh_from_cadquery(_arm_shape(LOWER_ARM_LENGTH), "lower_arm"), material="sand", name="arm_frame")
    lower_arm.inertial = Inertial.from_geometry(Box((LOWER_ARM_LENGTH, ARM_SPACING, ARM_THICKNESS)), mass=0.20, origin=Origin(xyz=(LOWER_ARM_LENGTH / 2.0, 0.0, ARM_THICKNESS / 2.0)))

    upper_arm = model.part("upper_arm")
    upper_arm.visual(mesh_from_cadquery(_arm_shape(UPPER_ARM_LENGTH), "upper_arm"), material="sand", name="arm_frame")
    upper_arm.inertial = Inertial.from_geometry(Box((UPPER_ARM_LENGTH, ARM_SPACING, ARM_THICKNESS)), mass=0.17, origin=Origin(xyz=(UPPER_ARM_LENGTH / 2.0, 0.0, ARM_THICKNESS / 2.0)))

    head = model.part("head")
    head.visual(mesh_from_cadquery(_head_shape(), "head"), material="sand", name="shade_shell")
    head.visual(Cylinder(radius=0.011, length=0.024), origin=Origin(xyz=(HEAD_NECK_LENGTH + 0.020, 0.0, 0.0), rpy=(0.0, pi / 2.0, 0.0)), material="white", name="bulb")
    head.inertial = Inertial.from_geometry(Box((0.085, HEAD_YOKE_WIDTH, 0.070)), mass=0.18, origin=Origin(xyz=(0.040, 0.0, 0.0)))

    model.articulation(
        "shoulder",
        ArticulationType.REVOLUTE,
        parent=base,
        child=lower_arm,
        origin=Origin(xyz=(0.0, 0.0, SHOULDER_Z - ARM_THICKNESS / 2.0)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(lower=LOWER_LIMITS[0], upper=LOWER_LIMITS[1], effort=8.0, velocity=1.6),
        meta={"hardware": "M4_or_printed_pin", "hole_diameter_m": 0.00435, "clearance_m": CLEARANCE},
    )
    model.articulation(
        "elbow",
        ArticulationType.REVOLUTE,
        parent=lower_arm,
        child=upper_arm,
        origin=Origin(xyz=(LOWER_ARM_LENGTH - END_RADIUS, 0.0, ARM_THICKNESS / 2.0)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(lower=ELBOW_LIMITS[0], upper=ELBOW_LIMITS[1], effort=6.0, velocity=1.8),
        meta={"hardware": "M4_or_printed_pin", "hole_diameter_m": 0.00435, "clearance_m": CLEARANCE},
    )
    model.articulation(
        "head_pitch",
        ArticulationType.REVOLUTE,
        parent=upper_arm,
        child=head,
        origin=Origin(xyz=(UPPER_ARM_LENGTH - END_RADIUS, 0.0, -0.004)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(lower=HEAD_LIMITS[0], upper=HEAD_LIMITS[1], effort=3.0, velocity=2.2),
        meta={"hardware": "M4_or_printed_pin", "hole_diameter_m": 0.00435, "clearance_m": CLEARANCE},
    )
    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    base = object_model.get_part("base")
    lower_arm = object_model.get_part("lower_arm")
    upper_arm = object_model.get_part("upper_arm")
    head = object_model.get_part("head")
    ctx.allow_overlap("head", "upper_arm", reason="The lamp head uses a simplified captured pivot/yoke proxy, so the rear shade shoulder intentionally nests slightly into the upper arm near the M4 pin line.")
    ctx.expect_overlap(head, upper_arm, axes="x", min_overlap=0.010, name="head remains captured at the upper arm pivot")
    shoulder = object_model.get_articulation("shoulder")
    elbow = object_model.get_articulation("elbow")
    head_pitch = object_model.get_articulation("head_pitch")

    ctx.expect_gap(lower_arm, base, axis="z", max_penetration=0.0035, name="lower arm sits just on base pivot line without deep embed")
    ctx.expect_overlap(lower_arm, base, axes="xy", min_overlap=0.010, name="shoulder remains above support footprint")

    with ctx.pose({shoulder: 0.65, elbow: -0.55, head_pitch: -0.30}):
        ctx.expect_gap(head, base, axis="z", min_gap=0.018, name="head clears base in task pose")

    rest_pos = ctx.part_world_position(head)
    with ctx.pose({shoulder: 0.85, elbow: -0.75, head_pitch: -0.65}):
        posed_pos = ctx.part_world_position(head)
    ctx.check(
        "head raises in articulated pose",
        rest_pos is not None and posed_pos is not None and posed_pos[2] > rest_pos[2] + 0.06,
        details=f"rest={rest_pos}, posed={posed_pos}",
    )
    return ctx.report()


object_model = build_object_model()