from __future__ import annotations

import math

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    Cylinder,
    Material,
    MeshGeometry,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_geometry,
)


CLEARANCE = 0.00035
M4_CLEARANCE_DIAMETER = 0.004 + 2.0 * CLEARANCE
BASE_DIAMETER = 0.110
LOWER_ARM_LENGTH = 0.120
UPPER_ARM_LENGTH = 0.100


def _mat(name: str, rgba: tuple[float, float, float, float]) -> Material:
    return Material(name=name, rgba=rgba)


def _bar_origin(p0: tuple[float, float, float], p1: tuple[float, float, float], y: float) -> Origin:
    dx = p1[0] - p0[0]
    dz = p1[2] - p0[2]
    angle_y = math.atan2(-dz, dx)
    return Origin(
        xyz=((p0[0] + p1[0]) * 0.5, y, (p0[2] + p1[2]) * 0.5),
        rpy=(0.0, angle_y, 0.0),
    )


def _bar_length(p0: tuple[float, float, float], p1: tuple[float, float, float]) -> float:
    return math.sqrt((p1[0] - p0[0]) ** 2 + (p1[2] - p0[2]) ** 2)


def _add_parallel_arm(
    part,
    prefix: str,
    end: tuple[float, float, float],
    material: Material,
    *,
    rail_y: float = 0.014,
    include_start_disks: bool = True,
) -> None:
    """Two printable side rails with cylindrical bosses at both pivots."""
    start = (0.0, 0.0, 0.0)
    rail_len = _bar_length(start, end)
    rail_size = (rail_len, 0.006, 0.008)
    for y, side in ((-rail_y, "rail_0"), (rail_y, "rail_1")):
        part.visual(
            Box(rail_size),
            origin=_bar_origin(start, end, y),
            material=material,
            name=f"{prefix}_{side}",
        )
    # End bosses are printed as part of the arm.  Side bosses straddle a center lug from the next link.
    for point, tag in ((start, "pivot_0"), (end, "pivot_1")):
        if tag != "pivot_0" or include_start_disks:
            for y, side in ((-0.014, "disk_0"), (0.014, "disk_1")):
                part.visual(
                    Cylinder(radius=0.012, length=0.006),
                    origin=Origin(xyz=(point[0], y, point[2]), rpy=(math.pi / 2.0, 0.0, 0.0)),
                    material=material,
                    name=f"{prefix}_{tag}_{side}",
                )
        # Dark bore surfaces denote a printable M4 clearance hole (4.70 mm diameter).
        bore_name = {
            ("lower", "pivot_0"): "lower_pivot_0_m4_bore",
            ("lower", "pivot_1"): "lower_pivot_1_m4_bore",
            ("upper", "pivot_0"): "upper_pivot_0_m4_bore",
            ("upper", "pivot_1"): "upper_pivot_1_m4_bore",
        }[(prefix, tag)]
        part.visual(
            Cylinder(radius=M4_CLEARANCE_DIAMETER * 0.5, length=0.038),
            origin=Origin(xyz=(point[0], 0.0, point[2]), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=_mat("dark_hole", (0.03, 0.027, 0.022, 1.0)),
            name=bore_name,
        )
    # Small center web keeps the twin rails a single printable part without blocking the forks.
    mid = (end[0] * 0.5, 0.0, end[2] * 0.5)
    part.visual(
        Box((0.016, 0.034, 0.006)),
        origin=Origin(xyz=mid, rpy=(0.0, math.atan2(-end[2], end[0]), 0.0)),
        material=material,
        name=f"{prefix}_center_web",
    )


def _frustum_shade_mesh(name: str) -> MeshGeometry:
    """Open thin-wall conical lamp shade along local -X, suitable for FDM printing."""
    seg = 64
    length = 0.056
    rear_r = 0.019
    front_r = 0.045
    wall = 0.0018
    geom = MeshGeometry()
    rings: list[list[int]] = []
    # outer rear, outer front, inner rear, inner front
    for x, radius in ((0.0, rear_r), (-length, front_r), (0.0, rear_r - wall), (-length, front_r - wall)):
        ring = []
        for i in range(seg):
            a = 2.0 * math.pi * i / seg
            ring.append(geom.add_vertex(x, radius * math.cos(a), radius * math.sin(a)))
        rings.append(ring)
    outer_rear, outer_front, inner_rear, inner_front = rings
    for i in range(seg):
        j = (i + 1) % seg
        # outer wall
        geom.add_face(outer_rear[i], outer_front[i], outer_front[j])
        geom.add_face(outer_rear[i], outer_front[j], outer_rear[j])
        # inner wall, reversed normals
        geom.add_face(inner_rear[i], inner_front[j], inner_front[i])
        geom.add_face(inner_rear[i], inner_rear[j], inner_front[j])
        # rolled front lip and rear throat lip connect inner/outer shells
        geom.add_face(outer_front[i], inner_front[i], inner_front[j])
        geom.add_face(outer_front[i], inner_front[j], outer_front[j])
        geom.add_face(outer_rear[i], outer_rear[j], inner_rear[j])
        geom.add_face(outer_rear[i], inner_rear[j], inner_rear[i])
    return geom


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(
        name="printable_dual_arm_desk_lamp",
        meta={
            "scale": "desktop printable; dimensions in meters",
            "design_clearance_m": CLEARANCE,
            "m4_clearance_hole_diameter_m": M4_CLEARANCE_DIAMETER,
            "nominal_exports": ["URDF", "model.py", "STEP", "STL", "3MF"],
            "parts_list": [
                "base with weighted disk and lower yoke",
                "lower_arm detachable twin-rail link, 120 mm pivot spacing",
                "upper_arm detachable twin-rail link, 100 mm pivot spacing",
                "lamp_head with hollow shade, bulb, neck, and pitch lug",
            ],
            "print_orientations": {
                "base": "flat on circular underside; yoke upright with support only under pivot bridge if desired",
                "lower_arm": "on side rail outer face, pivot axes horizontal; holes printed along Y for cleanup with 4.7 mm drill",
                "upper_arm": "on side rail outer face, pivot axes horizontal; holes printed along Y for cleanup with 4.7 mm drill",
                "lamp_head": "shade mouth on bed for clean rim, or tilted 30 deg with tree supports for neck lug",
            },
            "trace": {
                "requirements_modeled": [
                    "110 mm diameter weighted base",
                    "120 mm lower arm",
                    "100 mm upper arm",
                    "three horizontal revolute pitch axes",
                    "M4 clearance bores with 0.35 mm radial print clearance",
                    "mechanical joint limits to prevent self-intersection",
                    "detachable printable parts",
                ],
                "unavailable": [
                    "real telemetry/events.jsonl",
                    "real telemetry/run_summary.json",
                    "artifact_manifest.json outside model metadata",
                    "pipeline_plan.json outside model metadata",
                    "environment.json outside model metadata",
                ],
            },
        },
    )

    sand = _mat("matte_sand_pla", (0.74, 0.58, 0.30, 1.0))
    edge = _mat("slightly_darker_edges", (0.58, 0.44, 0.22, 1.0))
    dark = _mat("dark_bore_shadow", (0.02, 0.018, 0.014, 1.0))
    warm_white = _mat("warm_white_diffuser", (1.0, 0.92, 0.72, 1.0))

    lower_end = (0.045, 0.0, math.sqrt(LOWER_ARM_LENGTH**2 - 0.045**2))
    upper_end = (-0.046, 0.0, math.sqrt(UPPER_ARM_LENGTH**2 - 0.046**2))

    base = model.part("base")
    base.visual(Cylinder(radius=BASE_DIAMETER / 2.0, length=0.016), origin=Origin(xyz=(0.0, 0.0, 0.008)), material=sand, name="weighted_disk")
    base.visual(Cylinder(radius=0.046, length=0.004), origin=Origin(xyz=(0.0, 0.0, 0.018)), material=edge, name="top_inset")
    base.visual(Box((0.042, 0.040, 0.006)), origin=Origin(xyz=(0.0, 0.0, 0.023)), material=sand, name="yoke_foot")
    for y, side in ((-0.020, "cheek_0"), (0.020, "cheek_1")):
        base.visual(Box((0.020, 0.006, 0.036)), origin=Origin(xyz=(0.0, y, 0.039)), material=sand, name=f"lower_yoke_{side}")
        base.visual(Cylinder(radius=0.010, length=0.002), origin=Origin(xyz=(0.0, y + (0.0035 if y > 0 else -0.0035), 0.050), rpy=(math.pi / 2.0, 0.0, 0.0)), material=edge, name=f"lower_yoke_washer_{side}")
    base.visual(Cylinder(radius=M4_CLEARANCE_DIAMETER * 0.5, length=0.050), origin=Origin(xyz=(0.0, 0.0, 0.050), rpy=(math.pi / 2.0, 0.0, 0.0)), material=dark, name="base_m4_bore")
    base.visual(Box((0.012, 0.032, 0.010)), origin=Origin(xyz=(0.018, 0.0, 0.031)), material=edge, name="lower_stop_block")

    lower_arm = model.part("lower_arm")
    _add_parallel_arm(lower_arm, "lower", lower_end, sand)
    lower_arm.visual(Cylinder(radius=0.009, length=0.020), origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)), material=edge, name="base_center_lug")
    lower_arm.visual(Box((0.014, 0.026, 0.006)), origin=Origin(xyz=(0.032, 0.0, 0.079), rpy=(0.0, math.atan2(-lower_end[2], lower_end[0]), 0.0)), material=edge, name="lower_printed_stop")

    upper_arm = model.part("upper_arm")
    _add_parallel_arm(upper_arm, "upper", upper_end, sand, rail_y=0.007, include_start_disks=False)
    upper_arm.visual(Cylinder(radius=0.009, length=0.020), origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)), material=edge, name="elbow_center_lug")
    upper_arm.visual(Cylinder(radius=0.009, length=0.020), origin=Origin(xyz=upper_end, rpy=(math.pi / 2.0, 0.0, 0.0)), material=edge, name="head_center_lug")
    upper_arm.visual(Box((0.012, 0.026, 0.006)), origin=Origin(xyz=(-0.025, 0.0, 0.049), rpy=(0.0, math.atan2(-upper_end[2], upper_end[0]), 0.0)), material=edge, name="upper_printed_stop")

    lamp_head = model.part("lamp_head")
    lamp_head.visual(Cylinder(radius=0.012, length=0.010), origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)), material=sand, name="pitch_lug")
    lamp_head.visual(Cylinder(radius=M4_CLEARANCE_DIAMETER * 0.5, length=0.014), origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)), material=dark, name="pitch_m4_bore")
    lamp_head.visual(Cylinder(radius=0.016, length=0.034), origin=Origin(xyz=(-0.026, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)), material=sand, name="vented_socket")
    for i, z in enumerate((-0.007, -0.0035, 0.0, 0.0035, 0.007)):
        lamp_head.visual(Box((0.015, 0.0018, 0.003)), origin=Origin(xyz=(-0.026, -0.015, z)), material=dark, name=f"rear_vent_{i}")
    lamp_head.visual(
        mesh_from_geometry(_frustum_shade_mesh("shade_shell"), "hollow_shade_shell"),
        origin=Origin(xyz=(-0.036, 0.0, -0.004)),
        material=sand,
        name="hollow_shade_shell",
    )
    lamp_head.visual(Sphere(radius=0.014), origin=Origin(xyz=(-0.056, 0.0, -0.004)), material=warm_white, name="bulb_diffuser")
    lamp_head.visual(Cylinder(radius=0.007, length=0.022), origin=Origin(xyz=(-0.046, 0.0, -0.004), rpy=(0.0, math.pi / 2.0, 0.0)), material=edge, name="bulb_retainer")

    model.articulation(
        "base_pitch",
        ArticulationType.REVOLUTE,
        parent=base,
        child=lower_arm,
        origin=Origin(xyz=(0.0, 0.0, 0.050)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=2.5, velocity=1.5, lower=-0.35, upper=0.75),
        meta={"joint_hardware": "M4 bolt or printable pin; 4.70 mm bore; 0.35 mm radial clearance"},
    )
    model.articulation(
        "elbow_pitch",
        ArticulationType.REVOLUTE,
        parent=lower_arm,
        child=upper_arm,
        origin=Origin(xyz=lower_end),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=1.5, lower=-1.15, upper=0.55),
        meta={"joint_hardware": "M4 bolt or printable pin; 4.70 mm bore; 0.35 mm radial clearance"},
    )
    model.articulation(
        "head_pitch",
        ArticulationType.REVOLUTE,
        parent=upper_arm,
        child=lamp_head,
        origin=Origin(xyz=upper_end),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=1.2, velocity=1.5, lower=-0.95, upper=0.75),
        meta={"joint_hardware": "M4 bolt or printable pin; 4.70 mm bore; 0.35 mm radial clearance"},
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    base = object_model.get_part("base")
    lower = object_model.get_part("lower_arm")
    upper = object_model.get_part("upper_arm")
    head = object_model.get_part("lamp_head")
    base_pitch = object_model.get_articulation("base_pitch")
    elbow_pitch = object_model.get_articulation("elbow_pitch")
    head_pitch = object_model.get_articulation("head_pitch")

    ctx.check("base diameter is about 110 mm", abs(BASE_DIAMETER - 0.110) < 0.001)
    ctx.check("lower arm pivot spacing is about 120 mm", abs(LOWER_ARM_LENGTH - 0.120) < 0.001)
    ctx.check("upper arm pivot spacing is about 100 mm", abs(UPPER_ARM_LENGTH - 0.100) < 0.001)
    ctx.check("m4 clearance bore uses 0.35 mm radial clearance", abs(M4_CLEARANCE_DIAMETER - 0.0047) < 1e-6)
    ctx.check("three horizontal pitch joints", all(j.axis == (0.0, 1.0, 0.0) for j in (base_pitch, elbow_pitch, head_pitch)))

    # At rest each forked joint is coaxial and has projected overlap, while the lugs are separated in Y.
    ctx.allow_overlap(
        upper,
        head,
        elem_a="head_center_lug",
        elem_b="pitch_lug",
        reason="The head pitch lug is intentionally captured inside the upper-arm end boss; the real assembly uses an M4 bolt through coaxial bores.",
    )
    ctx.expect_contact(upper, head, elem_a="head_center_lug", elem_b="pitch_lug", contact_tol=0.013, name="head lug captured by upper boss")
    ctx.expect_overlap(base, lower, axes="xz", min_overlap=0.004, elem_a="base_m4_bore", elem_b="base_center_lug", name="base pivot coaxial")
    ctx.expect_overlap(lower, upper, axes="xz", min_overlap=0.004, elem_a="lower_pivot_1_m4_bore", elem_b="elbow_center_lug", name="elbow pivot coaxial")
    ctx.expect_overlap(upper, head, axes="xz", min_overlap=0.004, elem_a="upper_pivot_1_m4_bore", elem_b="pitch_lug", name="head pivot coaxial")

    with ctx.pose({base_pitch: 0.75, elbow_pitch: -1.15, head_pitch: 0.75}):
        ctx.expect_gap(head, base, axis="z", min_gap=0.010, name="mechanical limits keep shade above base")

    return ctx.report()


object_model = build_object_model()
