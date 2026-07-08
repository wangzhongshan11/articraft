from __future__ import annotations

import math

import cadquery as cq

from sdk import ArticulatedObject, Material, Origin, TestContext, TestReport, mesh_from_cadquery


MM = 0.001


def _rounded_rect_points(width: float, depth: float, radius: float, segments: int = 8) -> list[tuple[float, float]]:
    """Closed rounded-rectangle profile points in millimetres, without repeating the first point."""
    r = min(radius, width * 0.5 - 0.01, depth * 0.5 - 0.01)
    corners = (
        (width * 0.5 - r, depth * 0.5 - r, 0.0, 90.0),
        (-width * 0.5 + r, depth * 0.5 - r, 90.0, 180.0),
        (-width * 0.5 + r, -depth * 0.5 + r, 180.0, 270.0),
        (width * 0.5 - r, -depth * 0.5 + r, 270.0, 360.0),
    )
    pts: list[tuple[float, float]] = []
    for cx, cy, a0, a1 in corners:
        for i in range(segments + 1):
            if pts and i == 0:
                continue
            a = math.radians(a0 + (a1 - a0) * i / segments)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def _loft_rounded_rect(sections: list[tuple[float, float, float, float]]) -> cq.Workplane:
    """Loft rounded rectangles. Each section is (z_mm, width_mm, depth_mm, radius_mm)."""
    first_z, first_w, first_d, first_r = sections[0]
    wp = cq.Workplane("XY").workplane(offset=first_z).polyline(
        _rounded_rect_points(first_w, first_d, first_r)
    ).close()
    prev_z = first_z
    for z, w, d, r in sections[1:]:
        wp = wp.workplane(offset=z - prev_z).polyline(_rounded_rect_points(w, d, r)).close()
        prev_z = z
    return wp.loft(ruled=True, combine=True)


def _rounded_box(width: float, depth: float, height: float, radius: float, z_min: float) -> cq.Workplane:
    return _loft_rounded_rect(
        [
            (z_min, width, depth, radius),
            (z_min + height, width, depth, radius),
        ]
    )


def _make_parts_bin() -> cq.Workplane:
    # Overall dimensions are 160 x 120 x 90 mm. The lower shell is drafted inward;
    # the top rim reaches the nominal footprint and forms the stacking lip.
    outer = _loft_rounded_rect(
        [
            (0.0, 142.0, 102.0, 8.0),
            (8.0, 146.0, 106.0, 9.0),
            (78.0, 154.0, 114.0, 11.0),
            (90.0, 160.0, 120.0, 12.0),
        ]
    )

    # Open-top cavity: approximately 3 mm side walls through the body, with a
    # thicker reinforced top rim and a 4 mm base floor.
    cavity = _loft_rounded_rect(
        [
            (4.0, 130.0, 90.0, 5.0),
            (78.0, 148.0, 108.0, 8.0),
            (96.0, 148.0, 108.0, 8.0),
        ]
    )
    bin_body = outer.cut(cavity)

    # Recessed front label field on the front (-Y) face. The cutter is a rounded
    # rectangle extruded in Y so the bottom of the pocket stays blind in the wall.
    label_profile = _rounded_rect_points(72.0, 36.0, 3.0, segments=6)
    label_cutter = (
        cq.Workplane("XZ")
        .polyline(label_profile)
        .close()
        .extrude(12.0, both=True)
        .translate((0.0, -61.5, 43.0))
    )
    bin_body = bin_body.cut(label_cutter)

    # Shallow underside locating recesses: a continuous rounded rectangular groove
    # plus four small corner sockets, sized to engage the rim of an identical bin
    # without piercing the 4 mm floor.
    groove_outer = _rounded_box(132.0, 92.0, 3.0, 7.0, -0.8)
    groove_inner = _rounded_box(110.0, 70.0, 5.0, 5.0, -1.8)
    underside_groove = groove_outer.cut(groove_inner)
    bin_body = bin_body.cut(underside_groove)

    socket = _rounded_box(15.0, 15.0, 2.6, 2.0, -0.6)
    for x in (-56.0, 56.0):
        for y in (-38.0, 38.0):
            bin_body = bin_body.cut(socket.translate((x, y, 0.0)))

    return bin_body.clean()


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="stackable_parts_bin")

    plastic = Material("blue_grey_plastic", rgba=(0.33, 0.43, 0.50, 1.0))

    bin_part = model.part("bin")
    bin_part.visual(
        mesh_from_cadquery(
            _make_parts_bin(),
            "stackable_parts_bin_shell",
            tolerance=0.25,
            angular_tolerance=0.08,
            unit_scale=MM,
        ),
        origin=Origin(),
        material=plastic,
        name="bin_shell",
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    bin_part = object_model.get_part("bin")

    aabb = ctx.part_world_aabb(bin_part)
    if aabb is not None:
        mins, maxs = aabb
        dims = tuple(float(maxs[i] - mins[i]) for i in range(3))
        ctx.check(
            "nominal 160 x 120 x 90 mm envelope",
            abs(dims[0] - 0.160) < 0.004
            and abs(dims[1] - 0.120) < 0.004
            and abs(dims[2] - 0.090) < 0.003,
            details=f"measured envelope={dims}",
        )
    else:
        ctx.fail("nominal 160 x 120 x 90 mm envelope", "no part AABB available")

    return ctx.report()


object_model = build_object_model()
