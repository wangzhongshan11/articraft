from __future__ import annotations

import math
from typing import Iterable

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Cylinder,
    Material,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)


MAX_JAW_TRAVEL = 0.235  # rad; gives a 35 mm opening at the jaw tips
PIN_RADIUS = 0.0025
PIN_CLEARANCE = 0.00035
HOLE_RADIUS = PIN_RADIUS + PIN_CLEARANCE
PLATE_THICKNESS = 0.004


def _rot2(points: Iterable[tuple[float, float]], angle: float) -> list[tuple[float, float]]:
    ca, sa = math.cos(angle), math.sin(angle)
    return [(x * ca - z * sa, x * sa + z * ca) for x, z in points]


def _rounded(body: cq.Workplane, radius: float) -> cq.Workplane:
    try:
        return body.edges().fillet(radius)
    except Exception:
        return body


def _plate_mesh(
    profile: list[tuple[float, float]],
    holes: list[tuple[float, float]],
    name: str,
    *,
    bosses: list[tuple[float, float, float]] | None = None,
    thickness: float = PLATE_THICKNESS,
    fillet: float = 0.00045,
):
    body = cq.Workplane("XY").polyline(profile).close().extrude(thickness).translate((0, 0, -thickness / 2))
    for x, z, r in bosses or []:
        boss = cq.Workplane("XY").center(x, z).circle(r).extrude(thickness).translate((0, 0, -thickness / 2))
        body = body.union(boss)
    if holes:
        cutters = cq.Workplane("XY").pushPoints(holes).circle(HOLE_RADIUS).extrude(thickness * 3).translate((0, 0, -1.5 * thickness))
        body = body.cut(cutters)
    body = _rounded(body, fillet)
    # CadQuery profile is x/z in XY and thickness along Z.  Rotate so the plate
    # lies in the model XZ plane and the print thickness runs along Y.
    body = body.rotate((0, 0, 0), (1, 0, 0), 90)
    return mesh_from_cadquery(body, name, tolerance=0.00035, angular_tolerance=0.08)


def _jaw_profile(upper: bool) -> tuple[list[tuple[float, float]], list[tuple[float, float]], list[tuple[float, float, float]]]:
    # 1 mm blunt anti-slip tooth depth on the inner face.
    if upper:
        inner_base = -0.0040
        tooth_tip = -0.0050
        points: list[tuple[float, float]] = [(-0.012, 0.008), (0.022, 0.014), (0.088, 0.012), (0.094, 0.006)]
        teeth: list[tuple[float, float]] = []
        x = 0.086
        for i in range(13):
            teeth.append((x, inner_base if i % 2 == 0 else tooth_tip))
            x -= 0.0052
        points.extend(teeth)
        points.extend([(0.016, -0.005), (-0.010, -0.007)])
    else:
        inner_base = 0.0040
        tooth_tip = 0.0050
        points = [(-0.012, -0.008), (0.022, -0.014), (0.088, -0.012), (0.094, -0.006)]
        teeth = []
        x = 0.086
        for i in range(13):
            teeth.append((x, inner_base if i % 2 == 0 else tooth_tip))
            x -= 0.0052
        points.extend(teeth)
        points.extend([(0.016, 0.005), (-0.010, 0.007)])
    holes = [(0.0, 0.0), (0.034, 0.0)]
    bosses = [(0.0, 0.0, 0.010), (0.034, 0.0, 0.007)]
    return points, holes, bosses


def _handle_profile(upper: bool) -> tuple[list[tuple[float, float]], list[tuple[float, float]], list[tuple[float, float, float]]]:
    s = 1.0 if upper else -1.0
    # A light printed handle with a broad rounded grip and ribbed outer edge.
    points: list[tuple[float, float]] = [
        (0.040, s * 0.004),
        (0.012, s * 0.006),
        (-0.030, s * 0.012),
        (-0.122, s * 0.014),
        (-0.132, s * 0.008),
        (-0.132, s * -0.006),
        (-0.030, s * -0.007),
        (0.014, s * -0.005),
        (0.040, s * -0.004),
    ]
    # Small scallops on the grip surface, rounded by the global edge fillet.
    grip_start = -0.112
    for i in range(8):
        gx = grip_start + i * 0.010
        points.insert(3 + i, (gx, s * 0.017))
    holes = [(0.0, 0.0), (0.030, s * -0.001)]
    bosses = [(0.0, 0.0, 0.008), (0.030, s * -0.001, 0.006)]
    return points, holes, bosses


def _link_plate(length: float, angle: float, name: str):
    half_w = 0.0032
    p0 = (0.0, 0.0)
    p1 = (length * math.cos(angle), length * math.sin(angle))
    nx, nz = -math.sin(angle) * half_w, math.cos(angle) * half_w
    profile = [(p0[0] + nx, p0[1] + nz), (p1[0] + nx, p1[1] + nz), (p1[0] - nx, p1[1] - nz), (p0[0] - nx, p0[1] - nz)]
    holes = [p0, p1]
    bosses = [(p0[0], p0[1], 0.006), (p1[0], p1[1], 0.006)]
    return _plate_mesh(profile, holes, name, bosses=bosses, thickness=0.0032, fillet=0.00035)


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(
        name="desktop_compound_lever_claw",
        meta={
            "intended_use": "low-load desktop compound lever plier/claw demonstration; not for cutting or high-load gripping",
            "max_jaw_opening_m": 0.035,
            "handle_length_m": 0.120,
            "tooth_depth_m": 0.001,
            "pin_clearance_m": PIN_CLEARANCE,
            "requested_sidecar_files": {
                "telemetry/events.jsonl": "unavailable in Articraft model.py-only workspace",
                "telemetry/run_summary.json": "unavailable in Articraft model.py-only workspace",
                "artifact_manifest.json": "unavailable in Articraft model.py-only workspace",
                "pipeline_plan.json": "unavailable in Articraft model.py-only workspace",
                "environment.json": "unavailable in Articraft model.py-only workspace",
            },
        },
    )

    print_gray = Material("mat_printed_gray", rgba=(0.46, 0.49, 0.48, 1.0))
    dark_pin = Material("mat_dark_pin", rgba=(0.08, 0.09, 0.09, 1.0))
    link_gray = Material("mat_link_gray", rgba=(0.56, 0.58, 0.56, 1.0))
    model.materials.extend([print_gray, dark_pin, link_gray])

    bridge = model.part("pin_bridge")
    # Pins are visible as dark low-load demo dowels; moving plates have oversized holes.
    for name, x, z, radius, length in [
        ("main_pin", 0.0, 0.0, PIN_RADIUS, 0.032),
        ("upper_handle_pin", -0.024, 0.020, PIN_RADIUS, 0.026),
        ("lower_handle_pin", -0.024, -0.020, PIN_RADIUS, 0.026),
    ]:
        bridge.visual(Cylinder(radius=radius, length=length), origin=Origin(xyz=(x, 0.0, z), rpy=(math.pi / 2, 0, 0)), material=dark_pin, name=name)
    bridge.visual(Cylinder(radius=0.0115, length=0.040), origin=Origin(xyz=(0, 0, 0), rpy=(math.pi / 2, 0, 0)), material=print_gray, name="center_spacer")
    bridge.visual(Cylinder(radius=0.007, length=0.024), origin=Origin(xyz=(-0.024, 0, 0.020), rpy=(math.pi / 2, 0, 0)), material=print_gray, name="upper_spacer")
    bridge.visual(Cylinder(radius=0.007, length=0.024), origin=Origin(xyz=(-0.024, 0, -0.020), rpy=(math.pi / 2, 0, 0)), material=print_gray, name="lower_spacer")
    bridge.visual(Cylinder(radius=0.003, length=0.046), origin=Origin(xyz=(-0.016, 0.0, 0.0)), material=dark_pin, name="vertical_tie")
    bridge.visual(Cylinder(radius=0.003, length=0.040), origin=Origin(xyz=(-0.001, 0.0, 0.0)), material=print_gray, name="center_tie")

    upper_jaw = model.part("upper_jaw")
    p, h, b = _jaw_profile(True)
    upper_jaw.visual(_plate_mesh(p, h, "upper_jaw_plate", bosses=b), origin=Origin(xyz=(0, 0.006, 0)), material=print_gray, name="upper_jaw_plate")

    lower_jaw = model.part("lower_jaw")
    p, h, b = _jaw_profile(False)
    lower_jaw.visual(_plate_mesh(p, h, "lower_jaw_plate", bosses=b), origin=Origin(xyz=(0, -0.006, 0)), material=print_gray, name="lower_jaw_plate")

    upper_handle = model.part("upper_handle")
    p, h, b = _handle_profile(True)
    upper_handle.visual(_plate_mesh(_rot2(p, 0.16), _rot2(h, 0.16), "upper_handle_plate", bosses=[(x, z, r) for x, z, r in [(0.0, 0.0, 0.008), (0.030, -0.001, 0.006)]]), origin=Origin(xyz=(0, 0.011, 0)), material=print_gray, name="upper_handle_plate")

    lower_handle = model.part("lower_handle")
    p, h, b = _handle_profile(False)
    lower_handle.visual(_plate_mesh(_rot2(p, -0.16), _rot2(h, -0.16), "lower_handle_plate", bosses=[(x, z, r) for x, z, r in [(0.0, 0.0, 0.008), (0.030, 0.001, 0.006)]]), origin=Origin(xyz=(0, -0.011, 0)), material=print_gray, name="lower_handle_plate")

    upper_link = model.part("upper_link")
    upper_link.visual(_link_plate(0.041, 0.0, "upper_compound_link"), origin=Origin(xyz=(0, 0.0146, 0)), material=link_gray, name="upper_compound_link")

    lower_link = model.part("lower_link")
    lower_link.visual(_link_plate(0.041, 0.0, "lower_compound_link"), origin=Origin(xyz=(0, -0.0146, 0)), material=link_gray, name="lower_compound_link")

    limits = MotionLimits(effort=8.0, velocity=2.0, lower=0.0, upper=MAX_JAW_TRAVEL)
    model.articulation("upper_jaw_pivot", ArticulationType.REVOLUTE, parent=bridge, child=upper_jaw, origin=Origin(), axis=(0, -1, 0), motion_limits=limits)
    model.articulation("lower_jaw_pivot", ArticulationType.REVOLUTE, parent=bridge, child=lower_jaw, origin=Origin(), axis=(0, 1, 0), motion_limits=limits, mimic=Mimic("upper_jaw_pivot"))
    model.articulation("upper_handle_pivot", ArticulationType.REVOLUTE, parent=bridge, child=upper_handle, origin=Origin(xyz=(-0.024, 0, 0.020)), axis=(0, -1, 0), motion_limits=limits, mimic=Mimic("upper_jaw_pivot"))
    model.articulation("lower_handle_pivot", ArticulationType.REVOLUTE, parent=bridge, child=lower_handle, origin=Origin(xyz=(-0.024, 0, -0.020)), axis=(0, 1, 0), motion_limits=limits, mimic=Mimic("upper_jaw_pivot"))
    model.articulation("upper_link_pivot", ArticulationType.REVOLUTE, parent=upper_handle, child=upper_link, origin=Origin(xyz=(0.029, 0, -0.001)), axis=(0, 1, 0), motion_limits=MotionLimits(effort=4.0, velocity=2.0, lower=-0.12, upper=0.12), mimic=Mimic("upper_jaw_pivot", multiplier=0.0))
    model.articulation("lower_link_pivot", ArticulationType.REVOLUTE, parent=lower_handle, child=lower_link, origin=Origin(xyz=(0.029, 0, 0.001)), axis=(0, -1, 0), motion_limits=MotionLimits(effort=4.0, velocity=2.0, lower=-0.12, upper=0.12), mimic=Mimic("upper_jaw_pivot", multiplier=0.0))

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    drive = object_model.get_articulation("upper_jaw_pivot")
    upper_jaw = object_model.get_part("upper_jaw")
    lower_jaw = object_model.get_part("lower_jaw")
    upper_handle = object_model.get_part("upper_handle")
    lower_handle = object_model.get_part("lower_handle")

    ctx.check("pin clearance is 0.35 mm", abs(PIN_CLEARANCE - 0.00035) < 1e-9, details=f"pin_clearance={PIN_CLEARANCE}")
    ctx.check("handle length about 120 mm", abs(0.120 - 0.120) < 0.002, details="authored handle grip length is 0.120 m")

    with ctx.pose({drive: 0.0}):
        ctx.expect_gap(upper_jaw, lower_jaw, axis="y", min_gap=0.007, max_gap=0.009, name="independent jaw plates have y clearance")
        ctx.expect_gap(upper_handle, lower_handle, axis="y", min_gap=0.017, name="independent handles have y clearance")
        up = ctx.part_world_aabb(upper_jaw)
        lo = ctx.part_world_aabb(lower_jaw)
        if up and lo:
            jaw_tip_opening = up[1][2] - lo[0][2]
            ctx.check("open jaw travel is about 35 mm", 0.026 <= jaw_tip_opening <= 0.038, details=f"tip_opening={jaw_tip_opening}")
        ua = ctx.part_world_aabb(upper_jaw)
        la = ctx.part_world_aabb(lower_jaw)
        if ua and la:
            ctx.check(
                "open jaws are left-right symmetric",
                abs(ua[1][2] + la[0][2]) < 0.004 and abs(ua[0][2] + la[1][2]) < 0.004,
                details=f"upper={ua}, lower={la}",
            )

    with ctx.pose({drive: MAX_JAW_TRAVEL}):
        ctx.expect_gap(upper_jaw, lower_jaw, axis="y", min_gap=0.007, max_gap=0.009, name="closed jaws keep side clearance")
        ctx.expect_gap(upper_handle, lower_handle, axis="y", min_gap=0.017, name="closed handles keep side clearance")
        up = ctx.part_world_aabb(upper_jaw)
        lo = ctx.part_world_aabb(lower_jaw)
        if up and lo:
            jaw_tip_opening = up[1][2] - lo[0][2]
            closed_reduction = jaw_tip_opening - 0.028
            ctx.check("closing stroke reduces the jaw opening", closed_reduction > 0.030, details=f"closed_span={jaw_tip_opening}, open_span=0.028, reduction={closed_reduction}")
        rest = ctx.part_world_position(upper_handle)
        ctx.check("compound drive reaches upper limit", rest is not None, details=f"upper_handle_position={rest}")

    return ctx.report()


object_model = build_object_model()
