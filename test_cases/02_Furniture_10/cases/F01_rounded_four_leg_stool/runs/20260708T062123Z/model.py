from __future__ import annotations

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)


MM = 0.001
SEAT_SIZE_MM = 320.0
SEAT_THICKNESS_MM = 30.0
STOOL_HEIGHT_MM = 440.0
LEG_VERTICAL_MM = STOOL_HEIGHT_MM - SEAT_THICKNESS_MM
LEG_TOP_XY_MM = 108.0
LEG_SPLAY_MM = 22.0
SOCKET_DEPTH_MM = 8.0


def _rounded_square_profile(size_mm: float, radius_mm: float) -> cq.Workplane:
    """A closed rounded-square face on the XY plane, centered at the origin."""
    sketch = cq.Sketch().rect(size_mm, size_mm).vertices().fillet(radius_mm)
    return cq.Workplane("XY").placeSketch(sketch)


def _rounded_square_at(x_mm: float, y_mm: float, size_mm: float, radius_mm: float) -> cq.Workplane:
    sketch = cq.Sketch().rect(size_mm, size_mm).vertices().fillet(radius_mm)
    return cq.Workplane("XY").center(x_mm, y_mm).placeSketch(sketch)


def _build_seat() -> cq.Workplane:
    """320 x 320 x 30 mm rounded seat with four underside leg sockets."""
    seat = _rounded_square_profile(SEAT_SIZE_MM, 48.0).extrude(SEAT_THICKNESS_MM)

    # Soft manufactured edges while keeping the broad top and bottom faces flat.
    seat = seat.edges(">Z").fillet(5.0)
    seat = seat.edges("<Z").fillet(3.0)

    # Four shallow rounded-square underside pockets.  The pockets are true cuts,
    # so the leg tenons sit inside open sockets rather than interpenetrating a
    # solid seat proxy.
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            pocket = _rounded_square_at(sx * LEG_TOP_XY_MM, sy * LEG_TOP_XY_MM, 54.0, 13.0).extrude(SOCKET_DEPTH_MM + 0.25)
            seat = seat.cut(pocket)

    # A small bevel at the mouth of each socket makes the recess readable and
    # avoids razor-sharp underside edges.
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            chamfer = _rounded_square_at(sx * LEG_TOP_XY_MM, sy * LEG_TOP_XY_MM, 58.0, 15.0).extrude(2.0)
            inner = _rounded_square_at(sx * LEG_TOP_XY_MM, sy * LEG_TOP_XY_MM, 52.0, 12.0).extrude(2.2)
            seat = seat.cut(chamfer.cut(inner))

    return seat


def _build_leg(sign_x: float, sign_y: float) -> cq.Workplane:
    """A single slightly splayed, tapered wooden leg with a short top tenon."""
    bottom_dx = sign_x * LEG_SPLAY_MM
    bottom_dy = sign_y * LEG_SPLAY_MM

    leg_body = (
        cq.Workplane("XY")
        .circle(18.0)
        .workplane(offset=-LEG_VERTICAL_MM)
        .center(bottom_dx, bottom_dy)
        .circle(13.0)
        .loft(combine=True)
    )

    # Hidden round tenon fits into the shallow socket cut in the underside of the
    # seat.  A broad rounded shoulder bears against the flat underside around
    # the pocket, giving the separate leg part a real contact path to the seat.
    tenon = cq.Workplane("XY").circle(17.0).extrude(SOCKET_DEPTH_MM - 0.2)
    shoulder = _rounded_square_profile(68.0, 18.0).extrude(-5.0)
    leg = leg_body.union(tenon).union(shoulder)

    # Rounded foot and bottom shoulder arrises, credible for a molded or turned wood stool.
    leg = leg.edges("<Z").fillet(3.0)
    return leg


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="compact_rounded_stool")

    wood = model.material("warm_beech_wood", rgba=(0.72, 0.49, 0.25, 1.0))
    end_wood = model.material("end_grain_wood", rgba=(0.62, 0.40, 0.20, 1.0))

    seat = model.part("seat")
    seat.visual(
        mesh_from_cadquery(
            _build_seat(),
            "rounded_square_seat",
            tolerance=0.35,
            angular_tolerance=0.08,
            unit_scale=MM,
        ),
        origin=Origin(xyz=(0.0, 0.0, LEG_VERTICAL_MM * MM)),
        material=wood,
        name="seat_shell",
    )

    for index, (sx, sy) in enumerate(((-1.0, -1.0), (1.0, -1.0), (-1.0, 1.0), (1.0, 1.0))):
        leg = model.part(f"leg_{index}")
        leg.visual(
            mesh_from_cadquery(
                _build_leg(sx, sy),
                f"tapered_leg_{index}",
                tolerance=0.35,
                angular_tolerance=0.08,
                unit_scale=MM,
            ),
            material=wood,
            name="tapered_leg",
        )
        # A subtle darker circular foot pad is modeled as part of the leg, not a
        # separate floating detail; it gives the foot a stable, finished end.
        leg.visual(
            mesh_from_cadquery(
                cq.Workplane("XY").circle(12.8).extrude(1.2),
                f"leg_foot_{index}",
                tolerance=0.25,
                angular_tolerance=0.08,
                unit_scale=MM,
            ),
            origin=Origin(xyz=(sx * LEG_SPLAY_MM * MM, sy * LEG_SPLAY_MM * MM, -LEG_VERTICAL_MM * MM - 0.0012)),
            material=end_wood,
            name="foot_end",
        )
        model.articulation(
            f"seat_to_leg_{index}",
            ArticulationType.FIXED,
            parent=seat,
            child=leg,
            origin=Origin(xyz=(sx * LEG_TOP_XY_MM * MM, sy * LEG_TOP_XY_MM * MM, LEG_VERTICAL_MM * MM)),
        )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    seat = object_model.get_part("seat")

    # Overall millimetre-derived size: 320 mm square seat, 440 mm assembled height.
    seat_aabb = ctx.part_world_aabb(seat)
    if seat_aabb is not None:
        mins, maxs = seat_aabb
        ctx.check(
            "seat is 320 mm square",
            abs((maxs[0] - mins[0]) - 0.320) < 0.006 and abs((maxs[1] - mins[1]) - 0.320) < 0.006,
            details=f"seat_aabb={seat_aabb}",
        )
        ctx.check(
            "seat is 30 mm thick",
            abs((maxs[2] - mins[2]) - 0.030) < 0.004,
            details=f"seat_aabb={seat_aabb}",
        )

    leg_parts = [object_model.get_part(f"leg_{i}") for i in range(4)]
    all_aabbs = [ctx.part_world_aabb(part) for part in [seat, *leg_parts]]
    if all(aabb is not None for aabb in all_aabbs):
        min_z = min(aabb[0][2] for aabb in all_aabbs if aabb is not None)
        max_z = max(aabb[1][2] for aabb in all_aabbs if aabb is not None)
        ctx.check(
            "assembled height is 440 mm",
            abs((max_z - min_z) - 0.440) < 0.006,
            details=f"min_z={min_z}, max_z={max_z}",
        )

    for i, leg in enumerate(leg_parts):
        ctx.allow_overlap(
            leg,
            seat,
            elem_a="tapered_leg",
            elem_b="seat_shell",
            reason="Each leg has a hidden tenon intentionally seated about 8 mm into the matching underside socket.",
        )
        ctx.expect_overlap(
            leg,
            seat,
            axes="xy",
            min_overlap=0.025,
            elem_a="tapered_leg",
            elem_b="seat_shell",
            name=f"leg_{i} is seated under the socket footprint",
        )
        ctx.expect_gap(
            seat,
            leg,
            axis="z",
            max_gap=0.001,
            max_penetration=0.0085,
            positive_elem="seat_shell",
            negative_elem="tapered_leg",
            name=f"leg_{i} tenon is captured in the shallow socket",
        )

    return ctx.report()


object_model = build_object_model()