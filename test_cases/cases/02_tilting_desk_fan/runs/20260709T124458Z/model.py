from __future__ import annotations

import math

import cadquery as cq
from sdk import (
    ArticulatedObject,
    ArticulationType,
    Cylinder,
    Material,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)


MINT = Material("mint", rgba=(0.63, 0.86, 0.73, 1.0))
MINT_DARK = Material("mint_dark", rgba=(0.49, 0.74, 0.60, 1.0))
AXLE = Material("axle", rgba=(0.76, 0.78, 0.80, 1.0))

HEAD_RADIUS = 0.090
HEAD_DEPTH = 0.050
GRILLE_RING = 0.008
GRILLE_WIRE = 0.0018
GRILLE_RADIAL_COUNT = 24
BLADE_TIP_RADIUS = 0.055
BLADE_HUB_RADIUS = 0.016
BLADE_THICKNESS = 0.003
AXLE_RADIUS = 0.004
PITCH_Y = 0.098
PITCH_Z = 0.168


def _cyl_x(radius: float, length: float) -> cq.Workplane:
    return cq.Workplane("YZ").circle(radius).extrude(length / 2, both=True)


def _front_grille() -> cq.Workplane:
    z = HEAD_DEPTH / 2 - GRILLE_WIRE
    face = cq.Workplane("XY").circle(HEAD_RADIUS).circle(HEAD_RADIUS - GRILLE_RING).extrude(GRILLE_WIRE).translate((0, 0, z))
    for i in range(GRILLE_RADIAL_COUNT):
        angle = i * 360.0 / GRILLE_RADIAL_COUNT
        spoke = (
            cq.Workplane("XY")
            .box((HEAD_RADIUS - 0.020), GRILLE_WIRE, GRILLE_WIRE)
            .translate(((HEAD_RADIUS - 0.020) / 2, 0, z + GRILLE_WIRE / 2))
            .rotate((0, 0, 0), (0, 0, 1), angle)
        )
        face = face.union(spoke)
    return face.union(cq.Workplane("XY").circle(0.020).extrude(GRILLE_WIRE).translate((0, 0, z)))


def _rear_grille() -> cq.Workplane:
    z = -HEAD_DEPTH / 2
    face = cq.Workplane("XY").circle(HEAD_RADIUS).circle(HEAD_RADIUS - GRILLE_RING).extrude(GRILLE_WIRE).translate((0, 0, z))
    for i in range(GRILLE_RADIAL_COUNT):
        angle = i * 360.0 / GRILLE_RADIAL_COUNT
        spoke = (
            cq.Workplane("XY")
            .box((HEAD_RADIUS - 0.022), GRILLE_WIRE, GRILLE_WIRE)
            .translate(((HEAD_RADIUS - 0.022) / 2, 0, z + GRILLE_WIRE / 2))
            .rotate((0, 0, 0), (0, 0, 1), angle)
        )
        face = face.union(spoke)
    return face.union(cq.Workplane("XY").circle(0.018).extrude(GRILLE_WIRE).translate((0, 0, z)))


def _side_rim() -> cq.Workplane:
    rim = cq.Workplane("XY").circle(HEAD_RADIUS).circle(HEAD_RADIUS - GRILLE_RING).extrude(HEAD_DEPTH)
    for angle in range(0, 360, 18):
        rib = cq.Workplane("XY").box(0.008, 0.002, HEAD_DEPTH - 0.010).translate((HEAD_RADIUS - GRILLE_RING / 2, 0, HEAD_DEPTH / 2)).rotate((0, 0, 0), (0, 0, 1), angle)
        rim = rim.union(rib)
    return rim


def _head_shell() -> cq.Workplane:
    return _side_rim().union(_front_grille()).union(_rear_grille())


def _blade() -> cq.Workplane:
    return (
        cq.Workplane("YZ")
        .moveTo(BLADE_HUB_RADIUS, -0.007)
        .lineTo(BLADE_TIP_RADIUS, -0.013)
        .lineTo(BLADE_TIP_RADIUS - 0.010, 0.011)
        .lineTo(BLADE_HUB_RADIUS + 0.007, 0.007)
        .close()
        .extrude(BLADE_THICKNESS / 2, both=True)
        .rotate((0, 0, 0), (0, 1, 0), 18)
        .translate((0.004, 0, 0))
    )


def _impeller() -> cq.Workplane:
    hub = _cyl_x(BLADE_HUB_RADIUS, 0.014)
    shape = hub
    for i in range(5):
        shape = shape.union(_blade().rotate((0, 0, 0), (1, 0, 0), i * 72.0))
    return shape.translate((0.0, 0.0, PITCH_Z))


def _base_shape() -> cq.Workplane:
    disk = cq.Workplane("XY").circle(0.075).extrude(0.020)
    pedestal = cq.Workplane("XY").box(0.022, 0.060, 0.088).translate((0.0, 0.0, 0.064))
    return disk.union(pedestal)


def _yoke_shape() -> cq.Workplane:
    left_arm = cq.Workplane("XY").box(0.020, 0.012, 0.112).translate((0.0, PITCH_Y / 2, 0.112))
    right_arm = cq.Workplane("XY").box(0.020, 0.012, 0.112).translate((0.0, -PITCH_Y / 2, 0.112))
    bridge = cq.Workplane("XY").box(0.018, 0.088, 0.020).translate((0.0, 0.0, 0.064))
    fork_tabs = cq.Workplane("XY").box(0.018, 0.020, 0.018).translate((0.0, PITCH_Y / 2, PITCH_Z)).union(
        cq.Workplane("XY").box(0.018, 0.020, 0.018).translate((0.0, -PITCH_Y / 2, PITCH_Z))
    )
    return left_arm.union(right_arm).union(bridge).union(fork_tabs)


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="desktop_printable_fan")
    model.material(MINT.name, rgba=MINT.rgba)
    model.material(MINT_DARK.name, rgba=MINT_DARK.rgba)
    model.material(AXLE.name, rgba=AXLE.rgba)

    base = model.part("base")
    yoke = model.part("yoke")
    head = model.part("head")
    impeller = model.part("impeller")
    shaft = model.part("shaft")

    base.visual(mesh_from_cadquery(_base_shape(), "base_mesh"), material=MINT, name="base_body")
    yoke.visual(mesh_from_cadquery(_yoke_shape(), "yoke_mesh"), material=MINT_DARK, name="yoke_body")
    head.visual(mesh_from_cadquery(_head_shell(), "head_shell_mesh"), material=MINT, name="head_shell")
    head.visual(Cylinder(radius=0.011, length=0.018), origin=Origin(xyz=(0.0, PITCH_Y / 2, PITCH_Z), rpy=(math.pi / 2, 0.0, 0.0)), material=MINT_DARK, name="pivot_0")
    head.visual(Cylinder(radius=0.011, length=0.018), origin=Origin(xyz=(0.0, -PITCH_Y / 2, PITCH_Z), rpy=(math.pi / 2, 0.0, 0.0)), material=MINT_DARK, name="pivot_1")
    impeller.visual(mesh_from_cadquery(_impeller(), "impeller_mesh"), material=MINT_DARK, name="fan_blades")
    shaft.visual(Cylinder(radius=AXLE_RADIUS, length=0.024), origin=Origin(xyz=(0.0, 0.0, PITCH_Z), rpy=(math.pi / 2, 0.0, 0.0)), material=AXLE, name="shaft_body")

    model.articulation("base_yoke", ArticulationType.FIXED, parent=base, child=yoke, origin=Origin())
    model.articulation(
        "head_tilt",
        ArticulationType.REVOLUTE,
        parent=yoke,
        child=head,
        origin=Origin(xyz=(0.0, 0.0, PITCH_Z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(lower=math.radians(-15.0), upper=math.radians(45.0), effort=5.0, velocity=2.0),
    )
    model.articulation(
        "impeller_spin",
        ArticulationType.CONTINUOUS,
        parent=head,
        child=impeller,
        origin=Origin(xyz=(0.0, 0.0, PITCH_Z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=20.0),
    )
    model.articulation("shaft_mount", ArticulationType.FIXED, parent=head, child=shaft, origin=Origin())

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    head = object_model.get_part("head")
    impeller = object_model.get_part("impeller")
    tilt = object_model.get_articulation("head_tilt")

    ctx.expect_contact("yoke", "base", name="yoke joins base")
    ctx.expect_contact("head", "yoke", elem_a="pivot_0", name="upper pivot sits in one fork tab")
    ctx.expect_within(impeller, head, axes="yz", margin=0.003, inner_elem="fan_blades", outer_elem="head_shell", name="impeller fits within grille aperture")

    with ctx.pose({tilt: math.radians(45.0)}):
        ctx.expect_contact("head", "yoke", elem_a="pivot_0", name="tilted head remains carried by fork")

    return ctx.report()


object_model = build_object_model()