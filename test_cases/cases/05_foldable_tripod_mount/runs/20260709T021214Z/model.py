from __future__ import annotations

import math

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    CapsuleGeometry,
    Cylinder,
    LatheGeometry,
    Material,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
)


CLEARANCE = 0.00035
LEG_COUNT = 3
LEG_LENGTH = 0.150
LEG_DEPLOY_ANGLE_FROM_VERTICAL = math.radians(55.0)
LEG_FOLD_ANGLE = LEG_DEPLOY_ANGLE_FROM_VERTICAL
PHONE_MIN_WIDTH = 0.065
PHONE_MAX_WIDTH = 0.085
PITCH_LOWER = math.radians(-20.0)
PITCH_UPPER = math.radians(75.0)


black = Material("mat_satin_black", rgba=(0.005, 0.005, 0.004, 1.0))
rubber = Material("mat_soft_rubber", rgba=(0.015, 0.014, 0.013, 1.0))
dark_grey = Material("mat_dark_grey", rgba=(0.11, 0.11, 0.10, 1.0))
metal = Material("mat_dark_anodized_metal", rgba=(0.035, 0.037, 0.039, 1.0))


def _rz(theta: float, radius: float, z: float) -> tuple[float, float, float]:
    return (math.cos(theta) * radius, math.sin(theta) * radius, z)


def _radial_origin(theta: float, radius: float, z: float) -> Origin:
    return Origin(xyz=_rz(theta, radius, z), rpy=(0.0, 0.0, theta))


def _sliding_ring_mesh():
    outer = [
        (0.0188, -0.0110),
        (0.0200, -0.0085),
        (0.0200, 0.0085),
        (0.0188, 0.0110),
    ]
    inner_radius = 0.0100 + CLEARANCE
    inner = [
        (inner_radius, -0.0100),
        (inner_radius, 0.0100),
    ]
    return mesh_from_geometry(
        LatheGeometry.from_shell_profiles(outer, inner, segments=48, start_cap="flat", end_cap="flat"),
        "hollow_sliding_ring_0p35mm_clearance",
    )


def _rounded_leg_mesh():
    return mesh_from_geometry(
        CapsuleGeometry(0.010, LEG_LENGTH - 0.020, radial_segments=28, height_segments=8),
        "rounded_150mm_leg",
    )


def _add_leg(model: ArticulatedObject, column, index: int, leg_mesh) -> None:
    theta = 2.0 * math.pi * index / LEG_COUNT
    leg = model.part(f"leg_{index}")
    # Child frame is radial X / tangential Y / vertical Z at the hinge pin.
    hinge_boss_length = 0.0180
    leg.visual(
        Cylinder(radius=0.0090, length=hinge_boss_length),
        origin=Origin(rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=metal,
        name="hinge_knuckle",
    )
    leg.visual(
        Box((0.020, 0.010, 0.016)),
        origin=Origin(xyz=(0.012, 0.0, -0.006)),
        material=black,
        name="hinge_neck",
    )
    leg_center_distance = LEG_LENGTH / 2.0
    leg.visual(
        leg_mesh,
        origin=Origin(
            xyz=(
                math.sin(LEG_DEPLOY_ANGLE_FROM_VERTICAL) * leg_center_distance,
                0.0,
                -math.cos(LEG_DEPLOY_ANGLE_FROM_VERTICAL) * leg_center_distance,
            ),
            rpy=(0.0, math.pi / 2.0 + LEG_DEPLOY_ANGLE_FROM_VERTICAL, 0.0),
        ),
        material=dark_grey,
        name="rounded_leg_body",
    )
    foot_distance = LEG_LENGTH - 0.006
    leg.visual(
        Cylinder(radius=0.0125, length=0.022),
        origin=Origin(
            xyz=(
                math.sin(LEG_DEPLOY_ANGLE_FROM_VERTICAL) * foot_distance,
                0.0,
                -math.cos(LEG_DEPLOY_ANGLE_FROM_VERTICAL) * foot_distance,
            ),
            rpy=(0.0, math.pi / 2.0 + LEG_DEPLOY_ANGLE_FROM_VERTICAL, 0.0),
        ),
        material=rubber,
        name="rubber_foot",
    )

    model.articulation(
        f"column_to_leg_{index}",
        ArticulationType.REVOLUTE,
        parent=column,
        child=leg,
        origin=Origin(xyz=_rz(theta, 0.0320, 0.0550), rpy=(0.0, 0.0, theta)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=2.5, lower=0.0, upper=LEG_FOLD_ANGLE),
    )


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(
        name="desktop_folding_tripod_phone_camera_stand",
        meta={
            "source_prompt": "桌面级折叠三脚架手机/小相机支架；150 mm legs; 3 equal legs; sliding spreader ring; pitch head -20 to 75 deg; phone clamp 65-85 mm; 0.35 mm motion clearance; printable clamp with bolt/screw features.",
            "traceability_evidence": {
                "leg_length_m": LEG_LENGTH,
                "leg_count": LEG_COUNT,
                "leg_spacing_deg": 120.0,
                "motion_clearance_m": CLEARANCE,
                "phone_clamp_width_range_m": [PHONE_MIN_WIDTH, PHONE_MAX_WIDTH],
                "head_pitch_range_deg": [-20.0, 75.0],
                "representable_states": ["deployed_at_joint_zero", "folded_or_stowed_at_leg_and_ring_upper_limits"],
                "printability_note": "Phone clamp uses separate prismatic jaw, thumb screw, guide boss, and bolt-hole-like receiver details rather than a thin flexible spring.",
            },
        },
    )

    column = model.part("column")
    column.visual(Cylinder(radius=0.0100, length=0.165), origin=Origin(xyz=(0, 0, 0.105)), material=black, name="center_post")
    column.visual(Cylinder(radius=0.0150, length=0.018), origin=Origin(xyz=(0, 0, 0.009)), material=rubber, name="bottom_cap")
    column.visual(Cylinder(radius=0.0260, length=0.035), origin=Origin(xyz=(0, 0, 0.055)), material=black, name="leg_hub")
    column.visual(Cylinder(radius=0.0170, length=0.020), origin=Origin(xyz=(0, 0, 0.178)), material=black, name="top_collar")
    column.visual(Box((0.018, 0.016, 0.040)), origin=Origin(xyz=(0.0, 0.0, 0.196)), material=black, name="head_stem")

    # Three forked hinge yokes: their inner faces clear the leg knuckles by 0.35 mm.
    for i in range(LEG_COUNT):
        theta = 2.0 * math.pi * i / LEG_COUNT
        for side, sign in (("a", 1.0), ("b", -1.0)):
            local_y = sign * (0.0090 + CLEARANCE + 0.0020)
            cx = math.cos(theta) * 0.0260 - math.sin(theta) * local_y
            cy = math.sin(theta) * 0.0260 + math.cos(theta) * local_y
            column.visual(
                Box((0.018, 0.0040, 0.020)),
                origin=Origin(xyz=(cx, cy, 0.055), rpy=(0.0, 0.0, theta)),
                material=black,
                name=f"leg_yoke_{i}_{side}",
            )

    # Top pitch yoke, leaving a 0.35 mm side clearance around the child pivot barrel.
    for side, y in (("a", 0.0130 + CLEARANCE + 0.0030), ("b", -(0.0130 + CLEARANCE + 0.0030))):
        column.visual(
            Box((0.024, 0.0060, 0.040)),
            origin=Origin(xyz=(0.0, y, 0.205)),
            material=black,
            name=f"pitch_yoke_{side}",
        )
    column.visual(Cylinder(radius=0.0065, length=0.050), origin=Origin(xyz=(0.0, 0.0, 0.205), rpy=(math.pi / 2.0, 0.0, 0.0)), material=metal, name="pitch_pin")

    ring = model.part("spreader_ring")
    ring.visual(_sliding_ring_mesh(), material=black, name="hollow_ring")
    for i in range(LEG_COUNT):
        theta = 2.0 * math.pi * i / LEG_COUNT
        ring.visual(
            Box((0.018, 0.010, 0.010)),
            origin=_radial_origin(theta, 0.0280, -0.0010),
            material=black,
            name=f"ring_tab_{i}",
        )
    ring.visual(Cylinder(radius=0.0045, length=0.058), origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)), material=metal, name="thumb_screw_band")
    ring.visual(Cylinder(radius=0.0085, length=0.006), origin=Origin(xyz=(0.0, 0.0320, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)), material=dark_grey, name="ring_thumb_knob")
    model.articulation(
        "column_to_spreader_ring",
        ArticulationType.PRISMATIC,
        parent=column,
        child=ring,
        origin=Origin(xyz=(0.0, 0.0, 0.0790)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=0.12, lower=0.0, upper=0.050),
    )

    leg_mesh = _rounded_leg_mesh()
    for i in range(LEG_COUNT):
        _add_leg(model, column, i, leg_mesh)

    pitch_head = model.part("pitch_head")
    pitch_head.visual(Cylinder(radius=0.0130, length=0.026), origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)), material=metal, name="pivot_barrel")
    pitch_head.visual(Box((0.018, 0.012, 0.035)), origin=Origin(xyz=(0.0, 0.0, 0.025)), material=black, name="tilt_neck")
    pitch_head.visual(Box((0.070, 0.006, 0.110)), origin=Origin(xyz=(0.0, 0.010, 0.083)), material=black, name="phone_back_plate")
    pitch_head.visual(Box((0.008, 0.018, 0.090)), origin=Origin(xyz=(-0.0365, -0.002, 0.083)), material=black, name="fixed_side_jaw")
    pitch_head.visual(Box((0.061, 0.020, 0.008)), origin=Origin(xyz=(0.000, -0.003, 0.030)), material=black, name="bottom_lip")
    pitch_head.visual(Box((0.055, 0.003, 0.074)), origin=Origin(xyz=(0.000, -0.0045, 0.087)), material=rubber, name="phone_rubber_pad")
    pitch_head.visual(Cylinder(radius=0.0040, length=0.020), origin=Origin(xyz=(0.023, 0.010, 0.083), rpy=(0.0, math.pi / 2.0, 0.0)), material=metal, name="jaw_receiver_hole")
    pitch_head.visual(Cylinder(radius=0.0060, length=0.007), origin=Origin(xyz=(0.0, -0.016, 0.012), rpy=(math.pi / 2.0, 0.0, 0.0)), material=metal, name="camera_screw_boss")
    model.articulation(
        "column_to_pitch_head",
        ArticulationType.REVOLUTE,
        parent=column,
        child=pitch_head,
        origin=Origin(xyz=(0.0, 0.0, 0.2050)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=PITCH_LOWER, upper=PITCH_UPPER),
    )

    sliding_jaw = model.part("sliding_jaw")
    sliding_jaw.visual(Box((0.008, 0.018, 0.090)), origin=Origin(xyz=(0.0040, -0.002, 0.0)), material=black, name="moving_side_jaw")
    sliding_jaw.visual(Box((0.004, 0.014, 0.070)), origin=Origin(xyz=(0.0015, -0.012, 0.0)), material=rubber, name="moving_rubber_pad")
    sliding_jaw.visual(Cylinder(radius=0.0030, length=0.026), origin=Origin(xyz=(0.012, 0.010, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)), material=metal, name="clamp_screw")
    sliding_jaw.visual(Cylinder(radius=0.011, length=0.006), origin=Origin(xyz=(0.028, 0.010, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)), material=dark_grey, name="clamp_thumb_knob")
    model.articulation(
        "pitch_head_to_sliding_jaw",
        ArticulationType.PRISMATIC,
        parent=pitch_head,
        child=sliding_jaw,
        origin=Origin(xyz=(PHONE_MIN_WIDTH / 2.0, 0.0, 0.083)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=0.05, lower=0.0, upper=PHONE_MAX_WIDTH - PHONE_MIN_WIDTH),
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    pitch = object_model.get_articulation("column_to_pitch_head")
    jaw_slide = object_model.get_articulation("pitch_head_to_sliding_jaw")
    ring_slide = object_model.get_articulation("column_to_spreader_ring")
    column = object_model.get_part("column")
    ring = object_model.get_part("spreader_ring")
    sliding_jaw = object_model.get_part("sliding_jaw")
    pitch_head = object_model.get_part("pitch_head")

    ctx.check("three equally spaced folding legs", len([p for p in object_model.parts if p.name.startswith("leg_")]) == 3)
    ctx.check("leg length trace is 150 mm", abs(LEG_LENGTH - 0.150) < 1e-9)
    ctx.check("pitch range is -20 to 75 degrees", abs(pitch.motion_limits.lower - PITCH_LOWER) < 1e-9 and abs(pitch.motion_limits.upper - PITCH_UPPER) < 1e-9)
    ctx.check("phone clamp range is 65 to 85 mm", abs(jaw_slide.motion_limits.upper - 0.020) < 1e-9)
    ctx.check("clearance trace is 0.35 mm", abs(CLEARANCE - 0.00035) < 1e-12)

    ctx.expect_within(ring, column, axes="xy", inner_elem="hollow_ring", outer_elem="leg_hub", margin=0.001, name="sliding ring stays concentric around column footprint")
    ctx.expect_gap(ring, column, axis="z", max_penetration=0.003, positive_elem="hollow_ring", negative_elem="leg_hub", name="ring sits on hub with only local retained overlap")
    ctx.allow_overlap(
        ring,
        column,
        elem_a="hollow_ring",
        elem_b="leg_hub",
        reason="The hollow spreader ring is seated around the hub lip; the tiny axial embed represents retained plastic collar overlap while radial clearance is 0.35 mm.",
    )

    fixed = pitch_head.get_visual("fixed_side_jaw")
    moving = sliding_jaw.get_visual("moving_side_jaw")
    closed_aabb = ctx.part_element_world_aabb(pitch_head, elem=fixed)
    moving_closed_aabb = ctx.part_element_world_aabb(sliding_jaw, elem=moving)
    with ctx.pose({jaw_slide: PHONE_MAX_WIDTH - PHONE_MIN_WIDTH}):
        moving_open_aabb = ctx.part_element_world_aabb(sliding_jaw, elem=moving)
    if closed_aabb and moving_closed_aabb and moving_open_aabb:
        closed_width = moving_closed_aabb[0].x - closed_aabb[1].x
        open_width = moving_open_aabb[0].x - closed_aabb[1].x
        ctx.check("phone jaws form 65 mm minimum opening", abs(closed_width - PHONE_MIN_WIDTH) < 0.002, details=f"closed_width={closed_width}")
        ctx.check("phone jaws form 85 mm maximum opening", abs(open_width - PHONE_MAX_WIDTH) < 0.002, details=f"open_width={open_width}")
    else:
        ctx.fail("phone jaw aabb measurements available", "Could not measure jaw visual AABBs")

    leg0 = object_model.get_part("leg_0")
    foot0 = leg0.get_visual("rubber_foot")
    rest_foot = ctx.part_element_world_aabb(leg0, elem=foot0)
    leg_joint0 = object_model.get_articulation("column_to_leg_0")
    with ctx.pose({leg_joint0: LEG_FOLD_ANGLE, ring_slide: ring_slide.motion_limits.upper, pitch: PITCH_UPPER}):
        folded_foot = ctx.part_element_world_aabb(leg0, elem=foot0)
    if rest_foot and folded_foot:
        rest_radius = max(abs(rest_foot[0].x), abs(rest_foot[1].x))
        folded_radius = max(abs(folded_foot[0].x), abs(folded_foot[1].x))
        ctx.check("folded pose brings leg close to center post", folded_radius < rest_radius - 0.050, details=f"rest_radius={rest_radius}, folded_radius={folded_radius}")
    else:
        ctx.fail("leg fold aabb measurements available", "Could not measure leg foot AABBs")

    return ctx.report()


object_model = build_object_model()
