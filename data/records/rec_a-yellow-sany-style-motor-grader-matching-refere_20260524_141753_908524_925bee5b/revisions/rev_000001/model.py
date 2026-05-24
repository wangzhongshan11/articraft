from __future__ import annotations

from math import pi

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
)

# Part-local layout: rear_chassis origin is the frame articulation pin.
# +X points toward the rear of the machine, -X toward the front blade/nose.


def _wheel_visuals(part, *, tire_radius: float, tire_width: float, rubber, wheel_steel) -> None:
    part.visual(
        Cylinder(radius=tire_radius, length=tire_width),
        origin=Origin(rpy=(0.0, pi / 2.0, 0.0)),
        material=rubber,
    )
    part.visual(
        Cylinder(radius=tire_radius * 0.55, length=tire_width * 0.55),
        origin=Origin(rpy=(0.0, pi / 2.0, 0.0)),
        material=wheel_steel,
    )


def build_object_model() -> ArticulatedObject:
    """Yellow articulated motor grader matching assembly-agent-v2 preview.png."""
    model = ArticulatedObject(name="sany_style_motor_grader")

    yellow = model.material("industrial_yellow", rgba=(0.95, 0.72, 0.12, 1.0))
    black = model.material("machinery_black", rgba=(0.10, 0.10, 0.10, 1.0))
    dark_grey = model.material("dark_grey", rgba=(0.28, 0.28, 0.30, 1.0))
    rubber = model.material("rubber", rgba=(0.07, 0.07, 0.07, 1.0))
    glass = model.material("cab_glass", rgba=(0.45, 0.52, 0.60, 0.45))

    rear_chassis = model.part("rear_chassis")
    rear_chassis.inertial = Inertial.from_geometry(
        Box((3.2, 2.3, 1.5)),
        mass=12000.0,
        origin=Origin(xyz=(1.6, 0.0, 0.75)),
    )
    rear_chassis.visual(Box((2.3, 2.18, 1.2)), origin=Origin(xyz=(2.05, 0.0, 0.55)), material=yellow)
    rear_chassis.visual(Box((0.8, 1.58, 0.14)), origin=Origin(xyz=(2.0, 0.0, -0.12)), material=yellow)
    rear_chassis.visual(Box((3.0, 0.18, 0.14)), origin=Origin(xyz=(1.55, -0.7, -0.12)), material=yellow)
    rear_chassis.visual(Box((3.0, 0.18, 0.14)), origin=Origin(xyz=(1.55, 0.7, -0.12)), material=yellow)
    rear_chassis.visual(Box((0.55, 0.35, 0.25)), origin=Origin(xyz=(0.0, 0.0, 0.0)), material=yellow)
    rear_chassis.visual(Box((2.7, 0.26, 0.18)), origin=Origin(xyz=(-0.6, 0.0, -0.38)), material=yellow)
    rear_chassis.visual(Box((0.28, 1.96, 0.24)), origin=Origin(xyz=(1.45, 0.0, -0.7)), material=dark_grey)
    rear_chassis.visual(Box((0.28, 1.96, 0.24)), origin=Origin(xyz=(3.05, 0.0, -0.7)), material=dark_grey)
    rear_chassis.visual(Cylinder(radius=0.055, length=0.92), origin=Origin(xyz=(1.75, -0.55, 1.1)), material=black)
    rear_chassis.visual(Cylinder(radius=0.055, length=0.92), origin=Origin(xyz=(1.75, 0.55, 1.1)), material=black)

    front_frame = model.part("front_frame")
    front_frame.inertial = Inertial.from_geometry(
        Box((4.5, 2.0, 0.9)),
        mass=4500.0,
        origin=Origin(xyz=(-2.0, 0.0, 0.2)),
    )
    front_frame.visual(Box((3.8, 0.22, 0.14)), origin=Origin(xyz=(-2.1, 0.0, 0.0)), material=yellow)
    front_frame.visual(Box((0.9, 1.55, 1.18)), origin=Origin(xyz=(-4.2, 0.0, 0.66)), material=yellow)
    front_frame.visual(Box((3.1, 0.42, 0.11)), origin=Origin(xyz=(-2.15, 0.0, 0.32)), material=black)
    front_frame.visual(Box((0.26, 2.14, 0.24)), origin=Origin(xyz=(-3.6, 0.0, -0.67)), material=dark_grey)

    cab = model.part("cab")
    cab.inertial = Inertial.from_geometry(
        Box((1.2, 1.2, 1.6)),
        mass=900.0,
        origin=Origin(xyz=(0.0, 0.0, 0.8)),
    )
    cab.visual(Box((1.05, 1.18, 0.52)), origin=Origin(xyz=(0.0, 0.0, 0.0)), material=yellow)
    cab.visual(Box((0.92, 1.04, 1.38)), origin=Origin(xyz=(0.0, 0.0, 0.95)), material=glass)
    cab.visual(Box((1.32, 1.52, 0.12)), origin=Origin(xyz=(0.0, 0.0, 1.7)), material=black)

    blade_circle = model.part("blade_circle")
    blade_circle.inertial = Inertial.from_geometry(
        Box((2.8, 0.6, 0.4)),
        mass=1800.0,
        origin=Origin(xyz=(0.0, 0.0, 0.1)),
    )
    blade_circle.visual(Box((2.7, 0.26, 0.18)), origin=Origin(xyz=(0.0, 0.0, 0.0)), material=yellow)

    blade_carriage = model.part("blade_carriage")
    blade_carriage.inertial = Inertial.from_geometry(
        Box((0.6, 0.6, 0.3)),
        mass=400.0,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    blade_carriage.visual(Box((0.5, 0.5, 0.12)), origin=Origin(xyz=(0.0, 0.0, -0.08)), material=dark_grey)

    blade = model.part("blade")
    blade.inertial = Inertial.from_geometry(
        Box((2.6, 0.3, 0.6)),
        mass=650.0,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    blade.visual(Box((2.55, 0.12, 0.46)), origin=Origin(xyz=(0.0, 0.0, -0.31)), material=yellow)

    front_wheel_left = model.part("front_wheel_left")
    front_wheel_left.inertial = Inertial.from_geometry(
        Cylinder(radius=0.79, length=0.42),
        mass=320.0,
        origin=Origin(rpy=(0.0, pi / 2.0, 0.0)),
    )
    _wheel_visuals(front_wheel_left, tire_radius=0.79, tire_width=0.42, rubber=rubber, wheel_steel=dark_grey)

    front_wheel_right = model.part("front_wheel_right")
    front_wheel_right.inertial = Inertial.from_geometry(
        Cylinder(radius=0.79, length=0.42),
        mass=320.0,
        origin=Origin(rpy=(0.0, pi / 2.0, 0.0)),
    )
    _wheel_visuals(front_wheel_right, tire_radius=0.79, tire_width=0.42, rubber=rubber, wheel_steel=dark_grey)

    rear_wheel_fl = model.part("rear_wheel_fl")
    rear_wheel_fl.inertial = Inertial.from_geometry(
        Cylinder(radius=0.64, length=0.36),
        mass=260.0,
        origin=Origin(rpy=(0.0, pi / 2.0, 0.0)),
    )
    _wheel_visuals(rear_wheel_fl, tire_radius=0.64, tire_width=0.36, rubber=rubber, wheel_steel=dark_grey)

    rear_wheel_fr = model.part("rear_wheel_fr")
    rear_wheel_fr.inertial = Inertial.from_geometry(
        Cylinder(radius=0.64, length=0.36),
        mass=260.0,
        origin=Origin(rpy=(0.0, pi / 2.0, 0.0)),
    )
    _wheel_visuals(rear_wheel_fr, tire_radius=0.64, tire_width=0.36, rubber=rubber, wheel_steel=dark_grey)

    rear_wheel_rl = model.part("rear_wheel_rl")
    rear_wheel_rl.inertial = Inertial.from_geometry(
        Cylinder(radius=0.64, length=0.36),
        mass=260.0,
        origin=Origin(rpy=(0.0, pi / 2.0, 0.0)),
    )
    _wheel_visuals(rear_wheel_rl, tire_radius=0.64, tire_width=0.36, rubber=rubber, wheel_steel=dark_grey)

    rear_wheel_rr = model.part("rear_wheel_rr")
    rear_wheel_rr.inertial = Inertial.from_geometry(
        Cylinder(radius=0.64, length=0.36),
        mass=260.0,
        origin=Origin(rpy=(0.0, pi / 2.0, 0.0)),
    )
    _wheel_visuals(rear_wheel_rr, tire_radius=0.64, tire_width=0.36, rubber=rubber, wheel_steel=dark_grey)

    model.articulation(
        "frame_articulation",
        ArticulationType.REVOLUTE,
        parent=rear_chassis,
        child=front_frame,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=-0.35, upper=0.35, effort=50000.0, velocity=0.25),
    )
    model.articulation(
        "cab_mount",
        ArticulationType.FIXED,
        parent=rear_chassis,
        child=cab,
        origin=Origin(xyz=(0.27, 0.0, 0.33)),
    )
    model.articulation(
        "blade_circle_mount",
        ArticulationType.FIXED,
        parent=rear_chassis,
        child=blade_circle,
        origin=Origin(xyz=(-0.6, 0.0, -0.38)),
    )
    model.articulation(
        "blade_circle_yaw",
        ArticulationType.CONTINUOUS,
        parent=blade_circle,
        child=blade_carriage,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=20000.0, velocity=0.4),
    )
    model.articulation(
        "blade_pitch",
        ArticulationType.REVOLUTE,
        parent=blade_carriage,
        child=blade,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(lower=-0.45, upper=0.35, effort=15000.0, velocity=0.3),
    )

    wheel_spin = MotionLimits(effort=8000.0, velocity=8.0)
    model.articulation(
        "front_wheel_left_spin",
        ArticulationType.CONTINUOUS,
        parent=front_frame,
        child=front_wheel_left,
        origin=Origin(xyz=(-3.6, -1.01, -0.67)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=wheel_spin,
    )
    model.articulation(
        "front_wheel_right_spin",
        ArticulationType.CONTINUOUS,
        parent=front_frame,
        child=front_wheel_right,
        origin=Origin(xyz=(-3.6, 1.01, -0.67)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=wheel_spin,
    )
    model.articulation(
        "rear_wheel_fl_spin",
        ArticulationType.CONTINUOUS,
        parent=rear_chassis,
        child=rear_wheel_fl,
        origin=Origin(xyz=(1.45, -1.08, -0.82)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=wheel_spin,
    )
    model.articulation(
        "rear_wheel_fr_spin",
        ArticulationType.CONTINUOUS,
        parent=rear_chassis,
        child=rear_wheel_fr,
        origin=Origin(xyz=(1.45, 1.08, -0.82)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=wheel_spin,
    )
    model.articulation(
        "rear_wheel_rl_spin",
        ArticulationType.CONTINUOUS,
        parent=rear_chassis,
        child=rear_wheel_rl,
        origin=Origin(xyz=(3.05, -1.08, -0.82)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=wheel_spin,
    )
    model.articulation(
        "rear_wheel_rr_spin",
        ArticulationType.CONTINUOUS,
        parent=rear_chassis,
        child=rear_wheel_rr,
        origin=Origin(xyz=(3.05, 1.08, -0.82)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=wheel_spin,
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)

    rear = object_model.get_part("rear_chassis")
    front = object_model.get_part("front_frame")
    cab = object_model.get_part("cab")
    blade = object_model.get_part("blade")
    blade_circle = object_model.get_part("blade_circle")
    blade_carriage = object_model.get_part("blade_carriage")

    ctx.allow_overlap(rear, front, reason="frame articulation block overlaps at the hinge pin")
    ctx.allow_overlap(rear, cab, reason="cab base seats on rear deck")
    ctx.allow_overlap(rear, blade_circle, reason="blade circle carrier is bolted to the main frame")
    ctx.allow_overlap(blade_circle, blade_carriage, reason="blade carriage sits on the circle")
    ctx.allow_overlap(blade_carriage, blade, reason="moldboard mounts to the carriage")
    ctx.allow_overlap(blade, blade_circle, reason="moldboard overlaps the circle carrier at the mount")
    ctx.allow_overlap(blade, rear, reason="moldboard sits under the main frame")
    ctx.allow_overlap(blade_carriage, rear, reason="carriage bolts through the frame blade support")
    for wheel_name in (
        "front_wheel_left",
        "front_wheel_right",
        "rear_wheel_fl",
        "rear_wheel_fr",
        "rear_wheel_rl",
        "rear_wheel_rr",
    ):
        wheel = object_model.get_part(wheel_name)
        parent = front if wheel_name.startswith("front") else rear
        ctx.allow_overlap(parent, wheel, reason="tire encloses axle beam")

    ctx.expect_overlap(rear, cab, axes="xy", min_overlap=0.06)
    ctx.expect_overlap(rear, blade_circle, axes="xy", min_overlap=0.04)
    ctx.expect_overlap(rear, front, axes="xy", min_overlap=0.02)
    ctx.expect_overlap(rear, blade, axes="xy", min_overlap=0.03)

    ctx.pose({"frame_articulation": 0.18, "blade_circle_yaw": 0.4, "blade_pitch": -0.12})
    ctx.expect_overlap(rear, front, axes="xy", min_overlap=0.01)

    return ctx.report()


object_model = build_object_model()
