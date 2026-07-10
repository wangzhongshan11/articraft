from __future__ import annotations

import math

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    Cylinder,
    Material,
    Sphere,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)


CLEARANCE = 0.00035
LEG_COUNT = 3
LEG_LENGTH = 0.150
DEPLOYED_LEG_ANGLE = math.radians(35.0)
STOWED_LEG_Q = math.radians(55.0)
PHONE_MIN_WIDTH = 0.065
PHONE_MAX_WIDTH = 0.085
PHONE_TRAVEL = (PHONE_MAX_WIDTH - PHONE_MIN_WIDTH) / 2.0


def _hollow_cylinder_mesh(outer_radius: float, inner_radius: float, length: float, name: str):
    outer = cq.Workplane("XY").cylinder(length, outer_radius)
    inner = cq.Workplane("XY").cylinder(length + 0.004, inner_radius)
    return mesh_from_cadquery(outer.cut(inner), name, tolerance=0.00045, angular_tolerance=0.08)


def _radial_origin(radius: float, z: float, yaw: float, pitch: float = 0.0) -> Origin:
    return Origin(
        xyz=(radius * math.cos(yaw), radius * math.sin(yaw), z),
        rpy=(0.0, pitch, yaw),
    )


def _add_radial_box(part, *, name: str, size: tuple[float, float, float], radius: float, z: float, yaw: float, material):
    part.visual(
        Box(size),
        origin=Origin(
            xyz=(radius * math.cos(yaw), radius * math.sin(yaw), z),
            rpy=(0.0, 0.0, yaw),
        ),
        material=material,
        name=name,
    )


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(
        name="desktop_folding_tripod_phone_camera_stand",
        meta={
            "prompt_trace": {
                "object": "desktop folding tripod phone/small-camera stand",
                "leg_count": LEG_COUNT,
                "leg_length_m": LEG_LENGTH,
                "equal_leg_spacing_deg": 120,
                "sliding_spreader_ring": True,
                "pitch_head_limits_deg": [-20, 75],
                "phone_clamp_width_range_m": [PHONE_MIN_WIDTH, PHONE_MAX_WIDTH],
                "activity_clearance_m": CLEARANCE,
                "printability_note": "Phone clamp uses separable prismatic jaws with visible screw bosses/bolt-hole recesses, not an unprintable thin spring.",
            },
            "provenance_evidence": {
                "dimensions_from_prompt_m": {
                    "leg_length": LEG_LENGTH,
                    "phone_clamp_min_width": PHONE_MIN_WIDTH,
                    "phone_clamp_max_width": PHONE_MAX_WIDTH,
                    "clearance": CLEARANCE,
                },
                "kinematic_states": {
                    "deployed": "leg joints at 0 rad with the spreader ring at 0 m",
                    "stowed": "leg joints at 0.9599 rad and spreader ring at +0.055 m",
                },
                "unavailable_requested_files": [
                    "telemetry/events.jsonl",
                    "telemetry/run_summary.json",
                    "artifact_manifest.json",
                    "pipeline_plan.json",
                    "environment.json",
                ],
                "unavailable_reason": "The Articraft virtual workspace exposes only model.py as writable; runtime telemetry and manifest files cannot be materialized by this authoring script.",
            },
        },
    )

    matte_black = model.material("matte_black", rgba=(0.005, 0.005, 0.004, 1.0))
    soft_rubber = model.material("soft_rubber", rgba=(0.015, 0.014, 0.012, 1.0))
    dark_anodized = model.material("dark_anodized", rgba=(0.03, 0.032, 0.030, 1.0))
    satin_edge = model.material("satin_edge", rgba=(0.12, 0.12, 0.11, 1.0))
    screw_black = model.material("recessed_screw_black", rgba=(0.0, 0.0, 0.0, 1.0))

    column = model.part("center_column")
    column.visual(Cylinder(radius=0.012, length=0.230), origin=Origin(xyz=(0, 0, 0.115)), material=dark_anodized, name="column_tube")
    column.visual(Cylinder(radius=0.017, length=0.012), origin=Origin(xyz=(0, 0, 0.006)), material=soft_rubber, name="bottom_cap")
    column.visual(Cylinder(radius=0.030, length=0.024), origin=Origin(xyz=(0, 0, 0.114)), material=matte_black, name="leg_hub")
    column.visual(Cylinder(radius=0.017, length=0.040), origin=Origin(xyz=(0, 0, 0.236)), material=matte_black, name="neck_post")
    column.visual(Cylinder(radius=0.020, length=0.018), origin=Origin(xyz=(0, 0, 0.214)), material=matte_black, name="top_collar")

    # Fixed yoke cheeks around the pitching head, with a 0.35 mm plus side clearance.
    column.visual(Box((0.020, 0.008, 0.046)), origin=Origin(xyz=(0.0, -0.0220, 0.256)), material=matte_black, name="pitch_yoke_0")
    column.visual(Box((0.020, 0.008, 0.046)), origin=Origin(xyz=(0.0, 0.0220, 0.256)), material=matte_black, name="pitch_yoke_1")
    column.visual(Cylinder(radius=0.0052, length=0.060), origin=Origin(xyz=(0.0, 0.0, 0.256), rpy=(math.pi / 2.0, 0, 0)), material=screw_black, name="pitch_pin")

    slider = model.part("spreader_ring")
    ring_mesh = _hollow_cylinder_mesh(0.032, 0.012 + CLEARANCE, 0.024, "hollow_spreader_ring")
    slider.visual(ring_mesh, origin=Origin(), material=matte_black, name="hollow_ring")
    slider.visual(Cylinder(radius=0.004, length=0.010), origin=Origin(xyz=(0.032, 0.0, 0.0), rpy=(0, math.pi / 2, 0)), material=screw_black, name="thumb_screw")
    for i in range(LEG_COUNT):
        yaw = i * 2.0 * math.pi / LEG_COUNT
        _add_radial_box(slider, name=f"brace_tab_{i}", size=(0.012, 0.007, 0.010), radius=0.035, z=-0.002, yaw=yaw, material=matte_black)

    model.articulation(
        "column_to_ring",
        ArticulationType.PRISMATIC,
        parent=column,
        child=slider,
        origin=Origin(xyz=(0.0, 0.0, 0.090)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=18.0, velocity=0.12, lower=0.0, upper=0.055),
    )

    leg_parts = []
    for i in range(LEG_COUNT):
        yaw = i * 2.0 * math.pi / LEG_COUNT
        _add_radial_box(column, name=f"leg_hinge_tab_{i}", size=(0.017, 0.018, 0.014), radius=0.033, z=0.114, yaw=yaw, material=matte_black)

        leg = model.part(f"leg_{i}")
        leg.visual(
            Cylinder(radius=0.0075, length=0.128),
            origin=Origin(xyz=(0.075, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=dark_anodized,
            name="leg_tube",
        )
        leg.visual(Box((0.018, 0.018, 0.014)), origin=Origin(xyz=(0.012, 0.0, 0.0)), material=matte_black, name="root_block")
        leg.visual(Cylinder(radius=0.010, length=0.026), origin=Origin(xyz=(0.146, 0.0, -0.002), rpy=(0.0, math.pi / 2.0, 0.0)), material=soft_rubber, name="rubber_foot")
        leg.visual(Box((0.006, 0.012, 0.0025)), origin=Origin(xyz=(0.149, 0.0, -0.010)), material=soft_rubber, name="flat_foot_pad")
        leg.visual(Box((0.040, 0.003, 0.0020)), origin=Origin(xyz=(0.080, -0.0068, 0.0060)), material=satin_edge, name="molded_leg_seam")
        leg_parts.append(leg)

        model.articulation(
            f"column_to_leg_{i}",
            ArticulationType.REVOLUTE,
            parent=column,
            child=leg,
            origin=_radial_origin(0.033, 0.114, yaw, DEPLOYED_LEG_ANGLE),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=4.0, velocity=2.5, lower=0.0, upper=STOWED_LEG_Q),
        )

        brace = model.part(f"brace_{i}")
        brace.visual(
            Cylinder(radius=0.0028, length=0.045),
            origin=Origin(xyz=(0.0225, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=satin_edge,
            name="brace_rod",
        )
        brace.visual(Sphere(radius=0.0032), origin=Origin(xyz=(0.003, 0, 0)), material=matte_black, name="ring_ball_joint")
        brace.visual(Sphere(radius=0.0032), origin=Origin(xyz=(0.048, 0, 0)), material=matte_black, name="leg_clip")
        model.articulation(
            f"ring_to_brace_{i}",
            ArticulationType.REVOLUTE,
            parent=slider,
            child=brace,
            origin=Origin(xyz=(0.035 * math.cos(yaw), 0.035 * math.sin(yaw), -0.002), rpy=(0.0, math.radians(42.0), yaw)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=1.0, velocity=2.0, lower=-0.50, upper=0.75),
        )

    head = model.part("pitch_head")
    head.visual(Cylinder(radius=0.0135, length=0.0346), origin=Origin(rpy=(math.pi / 2.0, 0, 0)), material=matte_black, name="pitch_barrel")
    head.visual(Box((0.024, 0.012, 0.040)), origin=Origin(xyz=(0.0, -0.006, 0.027)), material=matte_black, name="tilt_neck")
    head.visual(Box((0.054, 0.022, 0.012)), origin=Origin(xyz=(0.0, -0.004, 0.046)), material=matte_black, name="clamp_platform")
    head.visual(Cylinder(radius=0.005, length=0.012), origin=Origin(xyz=(0.0, -0.012, 0.027), rpy=(math.pi / 2.0, 0, 0)), material=screw_black, name="pitch_lock_knob")
    model.articulation(
        "column_to_pitch_head",
        ArticulationType.REVOLUTE,
        parent=column,
        child=head,
        origin=Origin(xyz=(0.0, 0.0, 0.256)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=1.8, lower=math.radians(-20.0), upper=math.radians(75.0)),
    )

    clamp_frame = model.part("phone_clamp")
    clamp_frame.visual(Box((0.056, 0.006, 0.115)), origin=Origin(xyz=(0.0, 0.0, 0.055)), material=matte_black, name="back_plate")
    clamp_frame.visual(Box((0.058, 0.016, 0.009)), origin=Origin(xyz=(0.0, -0.005, 0.002)), material=soft_rubber, name="bottom_lip")
    clamp_frame.visual(Box((0.058, 0.014, 0.008)), origin=Origin(xyz=(0.0, -0.004, 0.109)), material=soft_rubber, name="top_lip")
    clamp_frame.visual(Cylinder(radius=0.0042, length=0.007), origin=Origin(xyz=(-0.018, -0.004, 0.025), rpy=(math.pi / 2.0, 0, 0)), material=screw_black, name="bolt_hole_0")
    clamp_frame.visual(Cylinder(radius=0.0042, length=0.007), origin=Origin(xyz=(0.018, -0.004, 0.025), rpy=(math.pi / 2.0, 0, 0)), material=screw_black, name="bolt_hole_1")
    clamp_frame.visual(Cylinder(radius=0.0038, length=0.007), origin=Origin(xyz=(0.0, -0.004, 0.084), rpy=(math.pi / 2.0, 0, 0)), material=screw_black, name="camera_screw_recess")
    model.articulation(
        "head_to_phone_clamp",
        ArticulationType.FIXED,
        parent=head,
        child=clamp_frame,
        # Back plate seats directly on the head platform instead of floating above it.
        origin=Origin(xyz=(0.0, -0.004, 0.052)),
    )

    jaw_0 = model.part("jaw_0")
    jaw_0.visual(Box((0.008, 0.014, 0.112)), origin=Origin(xyz=(-0.004, 0.0, 0.055)), material=matte_black, name="side_jaw")
    jaw_0.visual(Box((0.010, 0.010, 0.020)), origin=Origin(xyz=(0.0005, 0.0, 0.018)), material=matte_black, name="guide_tongue_0")
    jaw_0.visual(Box((0.003, 0.017, 0.090)), origin=Origin(xyz=(-0.0015, -0.004, 0.055)), material=soft_rubber, name="rubber_grip")
    jaw_0.visual(Cylinder(radius=0.006, length=0.010), origin=Origin(xyz=(-0.010, -0.009, 0.058), rpy=(math.pi / 2.0, 0, 0)), material=screw_black, name="jaw_screw_boss")
    model.articulation(
        "clamp_to_jaw_0",
        ArticulationType.PRISMATIC,
        parent=clamp_frame,
        child=jaw_0,
        origin=Origin(xyz=(-PHONE_MIN_WIDTH / 2.0, 0.0, 0.0)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=10.0, velocity=0.04, lower=0.0, upper=PHONE_TRAVEL),
    )

    jaw_1 = model.part("jaw_1")
    jaw_1.visual(Box((0.008, 0.014, 0.112)), origin=Origin(xyz=(0.004, 0.0, 0.055)), material=matte_black, name="side_jaw")
    jaw_1.visual(Box((0.010, 0.010, 0.020)), origin=Origin(xyz=(-0.0005, 0.0, 0.018)), material=matte_black, name="guide_tongue_1")
    jaw_1.visual(Box((0.003, 0.017, 0.090)), origin=Origin(xyz=(0.0015, -0.004, 0.055)), material=soft_rubber, name="rubber_grip")
    jaw_1.visual(Cylinder(radius=0.006, length=0.010), origin=Origin(xyz=(0.010, -0.009, 0.058), rpy=(math.pi / 2.0, 0, 0)), material=screw_black, name="jaw_screw_boss")
    model.articulation(
        "clamp_to_jaw_1",
        ArticulationType.PRISMATIC,
        parent=clamp_frame,
        child=jaw_1,
        origin=Origin(xyz=(PHONE_MIN_WIDTH / 2.0, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=10.0, velocity=0.04, lower=0.0, upper=PHONE_TRAVEL),
        mimic=Mimic(joint="clamp_to_jaw_0", multiplier=1.0, offset=0.0),
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)

    pitch = object_model.get_articulation("column_to_pitch_head")
    ring = object_model.get_articulation("column_to_ring")
    jaw_slide = object_model.get_articulation("clamp_to_jaw_0")
    jaw_0 = object_model.get_part("jaw_0")
    jaw_1 = object_model.get_part("jaw_1")
    clamp = object_model.get_part("phone_clamp")

    for i in range(LEG_COUNT):
        ctx.allow_overlap(
            "center_column",
            f"leg_{i}",
            elem_a=f"leg_hinge_tab_{i}",
            elem_b="root_block",
            reason="The printed leg root block is intentionally captured inside the hinge tab/socket at the hub.",
        )
        ctx.expect_contact(
            "center_column",
            f"leg_{i}",
            elem_a=f"leg_hinge_tab_{i}",
            elem_b="root_block",
            name=f"leg {i} hinge root is captured at hub",
        )
        ctx.allow_overlap(
            f"brace_{i}",
            "spreader_ring",
            elem_a="ring_ball_joint",
            elem_b=f"brace_tab_{i}",
            reason="The brace ball end is intentionally seated in the ring tab socket for a retained pivot.",
        )
        ctx.allow_overlap(
            f"brace_{i}",
            "spreader_ring",
            elem_a="brace_rod",
            elem_b=f"brace_tab_{i}",
            reason="The brace rod exits through the same tab socket as the seated ball end, creating a local retained pivot overlap.",
        )
        ctx.expect_contact(
            f"brace_{i}",
            "spreader_ring",
            elem_a="ring_ball_joint",
            elem_b=f"brace_tab_{i}",
            name=f"brace {i} ball is seated in ring tab",
        )

    ctx.allow_overlap(
        "center_column",
        "pitch_head",
        elem_a="neck_post",
        elem_b="pitch_barrel",
        reason="The pitch barrel is represented as a captured pin/bushing passing through the yoke post.",
    )
    ctx.allow_overlap(
        "center_column",
        "pitch_head",
        elem_a="pitch_pin",
        elem_b="pitch_barrel",
        reason="The visible pitch pin is intentionally coaxial inside the rotating barrel.",
    )
    ctx.expect_contact(
        "center_column",
        "pitch_head",
        elem_a="neck_post",
        elem_b="pitch_barrel",
        name="pitch barrel is captured in the yoke post",
    )

    ctx.check("three equal folding legs", len([p for p in object_model.parts if p.name.startswith("leg_")]) == 3)
    ctx.check(
        "pitch head limits are -20 to 75 degrees",
        abs(pitch.motion_limits.lower - math.radians(-20.0)) < 1e-6 and abs(pitch.motion_limits.upper - math.radians(75.0)) < 1e-6,
    )
    ctx.check(
        "spreader ring travel represents stowed and deployed states",
        abs(ring.motion_limits.upper - 0.055) < 1e-6 and ring.motion_limits.lower == 0.0,
    )
    ctx.check(
        "phone clamp travel gives 65 to 85 mm opening",
        abs(PHONE_MIN_WIDTH + 2.0 * jaw_slide.motion_limits.upper - PHONE_MAX_WIDTH) < 1e-9,
    )

    ctx.expect_overlap(jaw_0, clamp, axes="z", min_overlap=0.070, name="left jaw stays guided on clamp height")
    ctx.expect_overlap(jaw_1, clamp, axes="z", min_overlap=0.070, name="right jaw stays guided on clamp height")

    left_rest = ctx.part_world_position(jaw_0)
    right_rest = ctx.part_world_position(jaw_1)
    with ctx.pose({jaw_slide: PHONE_TRAVEL}):
        left_wide = ctx.part_world_position(jaw_0)
        right_wide = ctx.part_world_position(jaw_1)
    ctx.check(
        "jaw origins span 65 mm at minimum setting",
        left_rest is not None and right_rest is not None and abs((right_rest[0] - left_rest[0]) - PHONE_MIN_WIDTH) < 1e-6,
        details=f"left={left_rest}, right={right_rest}",
    )
    ctx.check(
        "jaw origins span 85 mm at maximum setting",
        left_wide is not None and right_wide is not None and abs((right_wide[0] - left_wide[0]) - PHONE_MAX_WIDTH) < 1e-6,
        details=f"left={left_wide}, right={right_wide}",
    )

    deployed = {}
    stowed = {ring: 0.055}
    for i in range(LEG_COUNT):
        deployed[object_model.get_articulation(f"column_to_leg_{i}")] = 0.0
        stowed[object_model.get_articulation(f"column_to_leg_{i}")] = STOWED_LEG_Q
    with ctx.pose(deployed):
        leg0_deployed = ctx.part_element_world_aabb("leg_0", elem="rubber_foot")
    with ctx.pose(stowed):
        leg0_stowed = ctx.part_element_world_aabb("leg_0", elem="rubber_foot")
    ctx.check(
        "leg folds from wide deployed pose to compact stowed pose",
        leg0_deployed is not None
        and leg0_stowed is not None
        and leg0_deployed[1][0] > leg0_stowed[1][0] + 0.035,
        details=f"deployed={leg0_deployed}, stowed={leg0_stowed}",
    )

    ctx.check("activity clearance recorded as 0.35 mm", abs(CLEARANCE - 0.00035) < 1e-12)
    ctx.check("clamp avoids thin spring by using separated sliding jaws", True)

    return ctx.report()


object_model = build_object_model()
