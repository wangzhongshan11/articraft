from __future__ import annotations

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Material,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

MM = 0.001


def _rounded_box_mm(x: float, y: float, z: float, radius: float) -> cq.Workplane:
    """Centered rounded rectangular solid in millimetres."""
    shape = cq.Workplane("XY").box(x, y, z)
    if radius > 0:
        shape = shape.edges().fillet(radius)
    return shape


def _top_rail_mm() -> cq.Workplane:
    """A gently arched rear top rail, extruded in depth from an X/Z profile."""
    width = 430.0
    depth = 34.0
    # Local Z profile: flat lower edge, rounded arched upper edge with a 10 mm crown.
    profile = (
        cq.Workplane("XZ")
        .moveTo(-width / 2.0, -25.0)
        .lineTo(width / 2.0, -25.0)
        .lineTo(width / 2.0, 15.0)
        .threePointArc((0.0, 25.0), (-width / 2.0, 15.0))
        .close()
        .extrude(depth)
    )
    # Center the extrusion about Y=0 before placement by the SDK visual origin.
    return profile.translate((0.0, -depth / 2.0, 0.0)).edges().fillet(4.0)


def _add_fixed(model: ArticulatedObject, parent, child, xyz_mm: tuple[float, float, float]) -> None:
    model.articulation(
        f"seat_to_{child.name}",
        ArticulationType.FIXED,
        parent=parent,
        child=child,
        origin=Origin(xyz=tuple(v * MM for v in xyz_mm)),
    )


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="slat_back_dining_chair")
    wood = Material("warm_beech_wood", rgba=(0.62, 0.38, 0.17, 1.0))

    # Overall target envelope, in millimetres: W 430 x D 460 x H 860.
    seat_width = 430.0
    seat_depth = 428.0
    seat_thick = 38.0
    seat_center_y = -11.0
    seat_top_z = 440.0
    seat_center_z = seat_top_z - seat_thick / 2.0

    seat = model.part("seat")
    seat.visual(
        mesh_from_cadquery(_rounded_box_mm(seat_width, seat_depth, seat_thick, 10.0), "seat_solid", unit_scale=MM),
        origin=Origin(xyz=(0.0, seat_center_y * MM, seat_center_z * MM)),
        material=wood,
        name="seat_solid",
    )

    # Two front legs; the rear legs are the taller rear uprights.
    front_leg_h = seat_center_z - seat_thick / 2.0
    for i, x in enumerate((-185.0, 185.0)):
        leg = model.part(f"front_leg_{i}")
        leg.visual(
            mesh_from_cadquery(_rounded_box_mm(32.0, 32.0, front_leg_h, 4.0), f"front_leg_{i}_post", unit_scale=MM),
            origin=Origin(),
            material=wood,
            name="leg_post",
        )
        _add_fixed(model, seat, leg, (x, -190.0, front_leg_h / 2.0))

    # Rear uprights are full-height rear legs positioned just behind the seat back edge.
    rear_y = 219.0
    upright_h = 806.0
    for i, x in enumerate((-199.0, 199.0)):
        upright = model.part(f"rear_upright_{i}")
        upright.visual(
            mesh_from_cadquery(_rounded_box_mm(32.0, 32.0, upright_h, 4.0), f"rear_upright_{i}_post", unit_scale=MM),
            origin=Origin(),
            material=wood,
            name="upright_post",
        )
        _add_fixed(model, seat, upright, (x, rear_y, upright_h / 2.0))

    # Five identical, equally spaced vertical back slats above the seat.
    slat_bottom_z = seat_top_z
    slat_top_z = 806.0
    slat_h = slat_top_z - slat_bottom_z
    slat_xs = [-120.0, -60.0, 0.0, 60.0, 120.0]
    for i, x in enumerate(slat_xs):
        slat = model.part(f"slat_{i}")
        slat.visual(
            mesh_from_cadquery(_rounded_box_mm(20.0, 18.0, slat_h, 5.0), f"slat_{i}_bar", unit_scale=MM),
            origin=Origin(),
            material=wood,
            name="slat_bar",
        )
        _add_fixed(model, seat, slat, (x, 188.0, (slat_bottom_z + slat_top_z) / 2.0))

    top_rail = model.part("top_rail")
    top_rail.visual(
        mesh_from_cadquery(_top_rail_mm(), "arched_top_rail", unit_scale=MM),
        origin=Origin(xyz=(0.0, 219.0 * MM, 831.0 * MM)),
        material=wood,
        name="arched_rail",
    )
    _add_fixed(model, seat, top_rail, (0.0, 0.0, 0.0))

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)

    seat = object_model.get_part("seat")
    top_rail = object_model.get_part("top_rail")
    slats = [object_model.get_part(f"slat_{i}") for i in range(5)]
    front_legs = [object_model.get_part(f"front_leg_{i}") for i in range(2)]
    rear_uprights = [object_model.get_part(f"rear_upright_{i}") for i in range(2)]

    # Overall proportions and seat height match the millimetre brief after SDK metre conversion.
    boxes = [ctx.part_world_aabb(p) for p in [seat, top_rail, *slats, *front_legs, *rear_uprights]]
    mins = [min(b[0][axis] for b in boxes if b is not None) for axis in range(3)]
    maxs = [max(b[1][axis] for b in boxes if b is not None) for axis in range(3)]
    dims = [maxs[i] - mins[i] for i in range(3)]
    ctx.check(
        "chair envelope is approximately 430 x 460 x 860 mm",
        0.425 <= dims[0] <= 0.435 and 0.455 <= dims[1] <= 0.465 and 0.850 <= dims[2] <= 0.865,
        details=f"dims={dims}",
    )
    seat_box = ctx.part_world_aabb(seat)
    seat_top = seat_box[1][2] if seat_box is not None else None
    ctx.check(
        "seat height is 440 mm",
        seat_top is not None and abs(seat_top - 0.440) <= 0.002,
        details=f"seat_top={seat_top}",
    )

    # The five back slats are vertical, equally spaced, and retained between seat and rail.
    slat_x = [ctx.part_world_position(s)[0] for s in slats]
    gaps = [slat_x[i + 1] - slat_x[i] for i in range(4)]
    ctx.check(
        "five slats are evenly spaced",
        len(slats) == 5 and max(gaps) - min(gaps) <= 0.001,
        details=f"slat_x={slat_x}, gaps={gaps}",
    )
    for i, slat in enumerate(slats):
        ctx.expect_contact(slat, seat, elem_a="slat_bar", elem_b="seat_solid", contact_tol=0.001, name=f"slat_{i} seats on solid seat")
        ctx.expect_contact(slat, top_rail, elem_a="slat_bar", elem_b="arched_rail", contact_tol=0.001, name=f"slat_{i} meets top rail")

    for i, leg in enumerate(front_legs):
        ctx.expect_contact(leg, seat, elem_a="leg_post", elem_b="seat_solid", contact_tol=0.001, name=f"front_leg_{i} supports seat")
    for i, upright in enumerate(rear_uprights):
        ctx.expect_contact(upright, seat, elem_a="upright_post", elem_b="seat_solid", contact_tol=0.0015, name=f"rear_upright_{i} bears against seat back")
        ctx.expect_contact(upright, top_rail, elem_a="upright_post", elem_b="arched_rail", contact_tol=0.005, name=f"rear_upright_{i} supports top rail")

    return ctx.report()


object_model = build_object_model()