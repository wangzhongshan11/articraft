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


BODY_SIZE = 0.120
BODY_HEIGHT = 0.024
HINGE_RADIUS = 0.074
ARM_LENGTH = 0.095
FOLD_ANGLE = math.pi / 2.0


DARK_GREY = Material("dark_grey_printed_nylon", rgba=(0.10, 0.105, 0.10, 1.0))
LIGHT_GREY = Material("matte_light_grey_printed_shell", rgba=(0.55, 0.57, 0.54, 1.0))
BLACK = Material("black_pin_and_latch_plastic", rgba=(0.015, 0.015, 0.014, 1.0))


def _rotated_box(length: float, width: float, height: float, center, angle_deg: float):
    return (
        cq.Workplane("XY")
        .box(length, width, height)
        .rotate((0, 0, 0), (0, 0, 1), angle_deg)
        .translate(center)
    )


def _vertical_cylinder(radius: float, height: float, center):
    return cq.Workplane("XY").cylinder(height, radius).translate(center)


def _body_shell_geometry():
    body = cq.Workplane("XY").box(BODY_SIZE, BODY_SIZE, BODY_HEIGHT)

    # A shallow open electronics-free tray makes the 120 mm square body read as a
    # printable lightweight shell rather than a solid block.
    body = body.faces(">Z").workplane().rect(0.070, 0.070).cutBlind(-0.014)
    body = body.faces(">Z").workplane().rect(0.034, 0.024).cutBlind(-0.030)

    # Side lightening windows on all four walls.
    for angle in (0.0, 90.0, 180.0, 270.0):
        rad = math.radians(angle)
        u = (math.cos(rad), math.sin(rad), 0.0)
        center = (u[0] * BODY_SIZE / 2.0, u[1] * BODY_SIZE / 2.0, 0.0)
        cutter = _rotated_box(0.028, 0.046, 0.012, center, angle)
        body = body.cut(cutter)

    # Corner screw relief holes.
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            body = body.cut(_vertical_cylinder(0.0017, 0.040, (sx * 0.048, sy * 0.048, 0.0)))

    # Four printable top/bottom hinge leaves with M3 pin holes, connected to the shell.
    for angle in (0.0, 90.0, 180.0, 270.0):
        rad = math.radians(angle)
        u = (math.cos(rad), math.sin(rad), 0.0)
        v = (-math.sin(rad), math.cos(rad), 0.0)
        pivot = (u[0] * HINGE_RADIUS, u[1] * HINGE_RADIUS, 0.0)
        for z in (-0.0085, 0.0085):
            leaf = _rotated_box(0.034, 0.036, 0.0030, (pivot[0], pivot[1], z), angle)
            body = body.union(leaf)
        # Small printed latch boss beside each hinge.
        latch_boss_xy = (pivot[0] - v[0] * 0.023, pivot[1] - v[1] * 0.023)
        boss = _vertical_cylinder(0.0055, 0.004, (latch_boss_xy[0], latch_boss_xy[1], 0.0105))
        body = body.union(boss)
        # Leave a visible solid M3-style pin in the fork so the separate arm lug
        # is physically captured in the assembled prototype model.
        pin = _vertical_cylinder(0.0020, 0.030, (pivot[0], pivot[1], 0.0))
        body = body.union(pin)
        body = body.cut(_vertical_cylinder(0.0012, 0.020, (latch_boss_xy[0], latch_boss_xy[1], 0.0105)))

    return body


def _arm_geometry():
    root_lug = cq.Workplane("XY").cylinder(0.010, 0.017)
    beam = cq.Workplane("XY").box(0.082, 0.016, 0.010).translate((0.046, 0.0, 0.0))
    motor_disk = cq.Workplane("XY").cylinder(0.008, 0.020).translate((ARM_LENGTH, 0.0, 0.0))
    nose = cq.Workplane("XY").box(0.018, 0.022, 0.008).translate((0.082, 0.0, 0.0))

    arm = root_lug.union(beam).union(nose).union(motor_disk)

    # Through features: M3 hinge-pin hole, circular mount center, two small screw holes,
    # and a long beam lightening slot that leaves side rails connected.
    arm = arm.cut(_vertical_cylinder(0.0017, 0.030, (0.0, 0.0, 0.0)))
    arm = arm.cut(_vertical_cylinder(0.0030, 0.020, (ARM_LENGTH, 0.0, 0.0)))
    for y in (-0.009, 0.009):
        arm = arm.cut(_vertical_cylinder(0.0014, 0.020, (ARM_LENGTH, y, 0.0)))
    slot = cq.Workplane("XY").box(0.040, 0.007, 0.020).translate((0.045, 0.0, 0.0))
    arm = arm.cut(slot)
    return arm


def _latch_geometry():
    pivot = cq.Workplane("XY").cylinder(0.005, 0.005).translate((0.0, 0.0, 0.0025))
    tab = cq.Workplane("XY").box(0.012, 0.046, 0.004).translate((0.006, 0.023, 0.0065))
    toe = cq.Workplane("XY").box(0.008, 0.010, 0.006).translate((0.008, 0.043, 0.0055))
    latch = pivot.union(tab).union(toe)
    latch = latch.cut(_vertical_cylinder(0.0012, 0.012, (0.0, 0.0, 0.003)))
    return latch


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(
        name="desktop_foldable_quadcopter_frame",
        meta={
            "requested_scale": "desktop structural prototype, no electronics, no flyable propellers",
            "body_size_m": BODY_SIZE,
            "arm_hinge_to_mount_center_m": ARM_LENGTH,
            "traceability_note": "telemetry and manifest sidecar files are unavailable in this sandbox; see final response.",
        },
    )

    for mat in (DARK_GREY, LIGHT_GREY, BLACK):
        model.material(mat)

    body = model.part("body_shell")
    body.visual(
        mesh_from_cadquery(_body_shell_geometry(), "lightweight_body_shell"),
        origin=Origin(),
        material=LIGHT_GREY,
        name="body_shell_mesh",
    )

    arm_mesh = mesh_from_cadquery(_arm_geometry(), "printable_fold_arm")
    latch_mesh = mesh_from_cadquery(_latch_geometry(), "hinge_lock_latch")

    for i, angle in enumerate((0.0, 90.0, 180.0, 270.0)):
        rad = math.radians(angle)
        u = (math.cos(rad), math.sin(rad), 0.0)
        v = (-math.sin(rad), math.cos(rad), 0.0)
        pivot = (u[0] * HINGE_RADIUS, u[1] * HINGE_RADIUS, 0.0)

        arm = model.part(f"arm_{i}", meta={"printable_as_separate_part": True})
        arm.visual(arm_mesh, origin=Origin(), material=DARK_GREY, name="arm_with_mount_disk")
        model.articulation(
            f"body_to_arm_{i}",
            ArticulationType.REVOLUTE,
            parent=body,
            child=arm,
            origin=Origin(xyz=pivot, rpy=(0.0, 0.0, rad)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=FOLD_ANGLE),
            meta={"deployed_angle_rad": 0.0, "folded_storage_angle_rad": FOLD_ANGLE, "hinge_pin_hole": "M3 clearance"},
        )

        latch_xy = (pivot[0] - v[0] * 0.023, pivot[1] - v[1] * 0.023, 0.0125)
        latch = model.part(f"lock_latch_{i}")
        latch.visual(latch_mesh, origin=Origin(), material=BLACK, name="swing_lock_tab")
        model.articulation(
            f"body_to_lock_{i}",
            ArticulationType.REVOLUTE,
            parent=body,
            child=latch,
            origin=Origin(xyz=latch_xy, rpy=(0.0, 0.0, rad)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=0.5, velocity=3.0, lower=0.0, upper=1.1),
            meta={"function": "independent swing latch for the adjacent folding arm"},
        )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)

    body = object_model.get_part("body_shell")
    arm_joints = [object_model.get_articulation(f"body_to_arm_{i}") for i in range(4)]
    lock_joints = [object_model.get_articulation(f"body_to_lock_{i}") for i in range(4)]
    arms = [object_model.get_part(f"arm_{i}") for i in range(4)]

    ctx.check("four independently printable arms", len(arms) == 4, "expected four separate arm links")
    ctx.check("four independent lock latches", len(lock_joints) == 4, "expected four separate latch joints")

    for i in range(4):
        ctx.allow_overlap(
            "body_shell",
            f"arm_{i}",
            elem_a="body_shell_mesh",
            elem_b="arm_with_mount_disk",
            reason="The arm root lug is intentionally captured on the visible M3-style hinge pin between the printed body fork leaves.",
        )
        ctx.expect_overlap(
            f"arm_{i}",
            "body_shell",
            axes="xy",
            min_overlap=0.010,
            elem_a="arm_with_mount_disk",
            elem_b="body_shell_mesh",
            name=f"arm {i} hinge lug remains captured on body pin",
        )

    with ctx.pose({joint: 0.0 for joint in arm_joints}):
        deployed = [ctx.part_world_aabb(arm) for arm in arms]
        ctx.check(
            "deployed arms form broad cross envelope",
            deployed[0][1][0] > 0.165
            and deployed[1][1][1] > 0.165
            and deployed[2][0][0] < -0.165
            and deployed[3][0][1] < -0.165,
            details=f"deployed_aabbs={deployed}",
        )

    folded_pose = {joint: FOLD_ANGLE for joint in arm_joints}
    folded_pose.update({joint: 1.0 for joint in lock_joints})
    with ctx.pose(folded_pose):
        folded = [ctx.part_world_aabb(arm) for arm in arms]
        max_abs_xy = max(max(abs(aabb[0][0]), abs(aabb[1][0]), abs(aabb[0][1]), abs(aabb[1][1])) for aabb in folded)
        ctx.check(
            "folded arms stay in compact desktop storage envelope",
            max_abs_xy < 0.125,
            details=f"max_abs_xy={max_abs_xy}, folded_aabbs={folded}",
        )
        ctx.check(
            "folded arms lie on four different body sides",
            folded[0][1][1] > 0.105
            and folded[1][0][0] < -0.105
            and folded[2][0][1] < -0.105
            and folded[3][1][0] > 0.105,
            details=f"folded_aabbs={folded}",
        )

    ctx.expect_origin_distance("arm_0", body, axes="xy", min_dist=0.070, max_dist=0.078, name="arm 0 hinge origin at body perimeter")
    ctx.expect_origin_distance("arm_1", body, axes="xy", min_dist=0.070, max_dist=0.078, name="arm 1 hinge origin at body perimeter")
    ctx.expect_origin_distance("arm_2", body, axes="xy", min_dist=0.070, max_dist=0.078, name="arm 2 hinge origin at body perimeter")
    ctx.expect_origin_distance("arm_3", body, axes="xy", min_dist=0.070, max_dist=0.078, name="arm 3 hinge origin at body perimeter")

    return ctx.report()


object_model = build_object_model()
