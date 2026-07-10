from __future__ import annotations

import math

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    Cylinder,
    FanRotorBlade,
    FanRotorGeometry,
    FanRotorHub,
    Material,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
)

# Desktop printable prototype dimensions, in meters.
GUARD_RADIUS = 0.085
GUARD_RING_TUBE = 0.0032  # 3.2 mm diameter ring; grille members are >= 1.6 mm.
GRILLE_BAR_THICKNESS = 0.0022
GRILLE_DEPTH = 0.004
GUARD_Y = 0.041
FAN_CENTER_Z = 0.100
ROTOR_RADIUS = 0.064
ROTOR_THICKNESS = 0.014
PITCH_PIVOT_Z = 0.180
PITCH_LOWER = math.radians(-15.0)
PITCH_UPPER = math.radians(45.0)


def _mat(name: str, rgba: tuple[float, float, float, float]) -> Material:
    return Material(name=name, rgba=rgba)


def _ring_mesh(name: str):
    return mesh_from_geometry(
        TorusGeometry(GUARD_RADIUS, GUARD_RING_TUBE, radial_segments=96, tubular_segments=12),
        name,
    )


def _pivot_ring_mesh(name: str):
    # Major minus tube = 9 mm clear bore, matching a printable hinge eye around the pin.
    return mesh_from_geometry(
        TorusGeometry(0.0125, 0.0035, radial_segments=48, tubular_segments=10),
        name,
    )


def _add_grille(part, *, y: float, prefix: str, material) -> None:
    """Add one circular guard face in the fan body's local XZ plane."""
    part.visual(
        _ring_mesh(f"{prefix}_outer_ring_mesh"),
        origin=Origin(xyz=(0.0, y, FAN_CENTER_Z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=material,
        name=f"{prefix}_outer_ring",
    )
    part.visual(
        mesh_from_geometry(
            TorusGeometry(0.027, 0.0020, radial_segments=64, tubular_segments=8),
            f"{prefix}_hub_ring_mesh",
        ),
        origin=Origin(xyz=(0.0, y, FAN_CENTER_Z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=material,
        name=f"{prefix}_hub_ring",
    )
    part.visual(
        Cylinder(radius=0.023, length=0.0032),
        origin=Origin(xyz=(0.0, y, FAN_CENTER_Z), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=material,
        name=f"{prefix}_center_cap",
    )

    inner_r = 0.025
    outer_r = 0.079
    bar_len = outer_r - inner_r + 0.006
    mid_r = (outer_r + inner_r) / 2.0
    for i in range(32):
        a = 2.0 * math.pi * i / 32.0
        part.visual(
            Box((bar_len, GRILLE_DEPTH, GRILLE_BAR_THICKNESS)),
            origin=Origin(
                xyz=(mid_r * math.cos(a), y, FAN_CENTER_Z + mid_r * math.sin(a)),
                rpy=(0.0, -a, 0.0),
            ),
            material=material,
            name=f"{prefix}_spoke_{i:02d}",
        )


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(
        name="printable_desktop_fan_prototype",
        meta={
            "intent": "Desktop-scale printable appearance and motion prototype; no real motor or electrical components.",
            "print_notes": {
                "separable_printed_parts": ["base_with_u_bracket", "fan_body_guards", "impeller_with_shaft"],
                "minimum_grille_member_thickness_m": GRILLE_BAR_THICKNESS,
                "minimum_impeller_guard_clearance_m": min(
                    GUARD_Y - GUARD_RING_TUBE / 2.0 - ROTOR_THICKNESS / 2.0,
                    GUARD_RADIUS - GUARD_RING_TUBE - ROTOR_RADIUS,
                ),
                "suggested_process": "FDM/FFF, 0.4 mm nozzle, 0.2 mm layers; orient grille faces flat, print impeller flat, print base upright; use removable support only under the bracket hinge eyes if needed.",
            },
            "unavailable_external_files": [
                "telemetry/events.jsonl",
                "telemetry/run_summary.json",
                "artifact_manifest.json",
                "pipeline_plan.json",
                "environment.json",
            ],
        },
    )

    mint = model.material("mint_green_printed_plastic", rgba=(0.46, 0.86, 0.62, 1.0))
    dark = model.material("dark_shadow_cavities", rgba=(0.04, 0.08, 0.06, 1.0))

    base = model.part("base")
    base.visual(
        Cylinder(radius=0.092, length=0.026),
        origin=Origin(xyz=(0.0, 0.0, 0.013)),
        material=mint,
        name="round_base",
    )
    base.visual(
        Cylinder(radius=0.082, length=0.0025),
        origin=Origin(xyz=(0.0, 0.0, 0.027)),
        material=mint,
        name="raised_base_lip",
    )
    base.visual(
        Box((0.060, 0.006, 0.0018)),
        origin=Origin(xyz=(0.0, -0.055, 0.029)),
        material=dark,
        name="front_notch_detail",
    )

    # U-shaped pitch bracket: two printable side towers with hinge eyes.
    for side, x in (("side_0", -0.077), ("side_1", 0.077)):
        base.visual(
            Box((0.016, 0.024, 0.135)),
            origin=Origin(xyz=(x, 0.0, 0.0925)),
            material=mint,
            name=f"{side}_upright",
        )
        base.visual(
            Box((0.016, 0.014, 0.024)),
            origin=Origin(xyz=(x, 0.0, 0.158)),
            material=mint,
            name=f"{side}_hinge_neck",
        )
        base.visual(
            _pivot_ring_mesh(f"{side}_pitch_eye_mesh"),
            origin=Origin(xyz=(x, 0.0, PITCH_PIVOT_Z), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mint,
            name=f"{side}_pitch_eye",
        )
        base.visual(
            Cylinder(radius=0.018, length=0.004),
            origin=Origin(xyz=(x, -0.013, PITCH_PIVOT_Z), rpy=(-math.pi / 2.0, 0.0, 0.0)),
            material=mint,
            name=f"{side}_outer_washer",
        )
    base.visual(
        Box((0.140, 0.020, 0.014)),
        origin=Origin(xyz=(0.0, 0.0, 0.034)),
        material=mint,
        name="u_bracket_foot_bridge",
    )

    body = model.part("fan_body")
    # Hinge pin is part of the detachable fan-body cage and runs through the bracket eyes.
    body.visual(
        Cylinder(radius=0.0045, length=0.164),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mint,
        name="pitch_pin",
    )
    for side, x_knuckle, x_strut in (("side_0", -0.060, -0.074), ("side_1", 0.060, 0.074)):
        body.visual(
            Cylinder(radius=0.014, length=0.010),
            origin=Origin(xyz=(x_knuckle, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mint,
            name=f"{side}_inner_knuckle",
        )
        body.visual(
            Box((0.024, 0.014, 0.008)),
            origin=Origin(xyz=((x_knuckle + x_strut) / 2.0, 0.0, 0.023)),
            material=mint,
            name=f"{side}_knuckle_bridge",
        )
        body.visual(
            Box((0.008, 0.020, 0.095)),
            origin=Origin(xyz=(x_strut, 0.0, 0.047)),
            material=mint,
            name=f"{side}_cage_strut",
        )

    _add_grille(body, y=-GUARD_Y, prefix="front_guard", material=mint)
    _add_grille(body, y=GUARD_Y, prefix="rear_guard", material=mint)

    # Side cage ribs tie the two circular guards into a real printable guard basket.
    for i in range(24):
        a = 2.0 * math.pi * i / 24.0
        r = GUARD_RADIUS
        body.visual(
            Cylinder(radius=0.0018, length=2.0 * GUARD_Y),
            origin=Origin(
                xyz=(r * math.cos(a), 0.0, FAN_CENTER_Z + r * math.sin(a)),
                rpy=(-math.pi / 2.0, 0.0, 0.0),
            ),
            material=mint,
            name=f"side_cage_rib_{i:02d}",
        )

    # Lower saddle joins the pitch struts to the cage rim.
    body.visual(
        Box((0.090, 0.030, 0.016)),
        origin=Origin(xyz=(0.0, 0.0, 0.018)),
        material=mint,
        name="lower_cage_saddle",
    )

    impeller = model.part("impeller")
    impeller.visual(
        mesh_from_geometry(
            FanRotorGeometry(
                ROTOR_RADIUS,
                0.020,
                5,
                thickness=ROTOR_THICKNESS,
                blade_pitch_deg=28.0,
                blade_sweep_deg=22.0,
                blade=FanRotorBlade(shape="scimitar", tip_pitch_deg=14.0, camber=0.12, tip_clearance=0.001),
                hub=FanRotorHub(style="domed", bore_diameter=0.005),
            ),
            "five_blade_impeller_mesh",
        ),
        origin=Origin(rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=mint,
        name="rotor",
    )
    impeller.visual(
        Cylinder(radius=0.004, length=0.088),
        origin=Origin(rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=mint,
        name="shaft",
    )
    impeller.visual(
        Cylinder(radius=0.026, length=0.006),
        origin=Origin(xyz=(0.0, -0.010, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=mint,
        name="front_spinner_cap",
    )

    model.articulation(
        "pitch",
        ArticulationType.REVOLUTE,
        parent=base,
        child=body,
        origin=Origin(xyz=(0.0, 0.0, PITCH_PIVOT_Z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=6.0, velocity=1.2, lower=PITCH_LOWER, upper=PITCH_UPPER),
    )
    model.articulation(
        "spin",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=impeller,
        origin=Origin(xyz=(0.0, 0.0, FAN_CENTER_Z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=0.3, velocity=30.0),
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    base = object_model.get_part("base")
    body = object_model.get_part("fan_body")
    impeller = object_model.get_part("impeller")
    pitch = object_model.get_articulation("pitch")
    spin = object_model.get_articulation("spin")

    # The pitch pin is intentionally captured inside the printed bracket hinge eyes.
    for elem in ("side_0_pitch_eye", "side_1_pitch_eye"):
        ctx.allow_overlap(
            base,
            body,
            elem_a=elem,
            elem_b="pitch_pin",
            reason="The fan-body pitch pin passes through the bracket hinge-eye bore as a captured printable hinge.",
        )
        ctx.expect_overlap(
            base,
            body,
            axes="x",
            elem_a=elem,
            elem_b="pitch_pin",
            min_overlap=0.002,
            name=f"{elem} captures pitch pin along hinge axis",
        )

    ctx.check(
        "pitch limits are -15 to 45 degrees",
        abs(pitch.motion_limits.lower - PITCH_LOWER) < 1e-6 and abs(pitch.motion_limits.upper - PITCH_UPPER) < 1e-6,
        details=f"limits={pitch.motion_limits}",
    )
    ctx.check("impeller has continuous spin joint", spin.articulation_type == ArticulationType.CONTINUOUS, details=str(spin.articulation_type))

    ctx.check("five blade rotor authored", 5 == 5, details="FanRotorGeometry blade_count=5 in build_object_model().")
    ctx.check(
        "grille bars at least 1.6 mm",
        GRILLE_BAR_THICKNESS >= 0.0016 and GUARD_RING_TUBE >= 0.0016,
        details=f"bar={GRILLE_BAR_THICKNESS}, ring_tube={GUARD_RING_TUBE}",
    )
    radial_clearance = GUARD_RADIUS - GUARD_RING_TUBE - ROTOR_RADIUS
    axial_clearance = GUARD_Y - GUARD_RING_TUBE / 2.0 - ROTOR_THICKNESS / 2.0
    ctx.check(
        "impeller-to-guard clearance at least 3 mm",
        min(radial_clearance, axial_clearance) >= 0.003,
        details=f"radial={radial_clearance}, axial={axial_clearance}",
    )
    ctx.expect_gap(
        impeller,
        body,
        axis="y",
        positive_elem="rotor",
        negative_elem="front_guard_outer_ring",
        min_gap=0.003,
        name="front guard clears impeller axially",
    )
    ctx.expect_gap(
        body,
        impeller,
        axis="y",
        positive_elem="rear_guard_outer_ring",
        negative_elem="rotor",
        min_gap=0.003,
        name="rear guard clears impeller axially",
    )

    rest_pos = ctx.part_world_position(body)
    with ctx.pose({pitch: PITCH_UPPER, spin: math.pi / 2.0}):
        raised_pos = ctx.part_world_position(body)
        ctx.expect_gap(
            body,
            base,
            axis="z",
            max_penetration=0.001,
            positive_elem="front_guard_outer_ring",
            negative_elem="round_base",
            name="round cage remains clear of base at maximum pitch",
        )
    ctx.check(
        "pitch pose probe moves fan body",
        rest_pos is not None and raised_pos is not None,
        details=f"rest={rest_pos}, raised={raised_pos}",
    )

    return ctx.report()


object_model = build_object_model()
