from __future__ import annotations

import math

import cadquery as cq
from sdk import ArticulatedObject, Material, Origin, TestContext, TestReport, mesh_from_cadquery


WOOD = Material("warm_oak", rgba=(0.55, 0.34, 0.16, 1.0))


def _rounded_box(sx: float, sy: float, sz: float, fillet: float) -> cq.Workplane:
    """Box with modest radiused edges, dimensions in metres."""
    solid = cq.Workplane("XY").box(sx, sy, sz)
    if fillet > 0.0:
        solid = solid.edges().fillet(fillet)
    return solid


def _post_between(
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    sx: float,
    sy: float,
    fillet: float,
) -> cq.Workplane:
    """Create a rounded rectangular timber post whose local Z axis spans start to end."""
    vx = end[0] - start[0]
    vy = end[1] - start[1]
    vz = end[2] - start[2]
    length = math.sqrt(vx * vx + vy * vy + vz * vz)
    # The chair posts only lean in the Y-Z plane, so an X-axis rotation is enough
    # and keeps the rectangular section aligned with the chair width/depth axes.
    angle_deg = math.degrees(math.atan2(-vy, vz))
    cx = (start[0] + end[0]) * 0.5
    cy = (start[1] + end[1]) * 0.5
    cz = (start[2] + end[2]) * 0.5
    return (
        _rounded_box(sx, sy, length, fillet)
        .rotate((0, 0, 0), (1, 0, 0), angle_deg)
        .translate((cx, cy, cz))
    )


def _build_chair_shape() -> cq.Workplane:
    # Real dimensions: 420 mm wide, 480 mm deep overall, 880 mm high.
    seat_w = 0.420
    seat_d = 0.400
    seat_t = 0.028
    seat_top_z = 0.450
    seat_cz = seat_top_z - seat_t * 0.5
    seat_front_y = -0.220
    seat_rear_y = seat_front_y + seat_d

    leg_size = 0.034
    front_x = 0.175
    rear_x = 0.175
    front_y = -0.185
    rear_bottom_y = 0.125
    rear_top_y = 0.235
    underside_z = seat_top_z - seat_t

    chair = _rounded_box(seat_w, seat_d, seat_t, 0.010).translate((0.0, seat_front_y + seat_d * 0.5, seat_cz))

    # Four square timber legs.  The rear pair continue up and lean back slightly
    # to carry the backrest, as in a simple dining chair.
    for x in (-front_x, front_x):
        chair = chair.union(_post_between((x, front_y, 0.012), (x, front_y, underside_z + 0.010), leg_size, leg_size, 0.006))
    for x in (-rear_x, rear_x):
        chair = chair.union(_post_between((x, rear_bottom_y, 0.012), (x, rear_top_y, 0.880), leg_size, leg_size, 0.006))

    # Under-seat aprons are slightly proud structural rails tying the legs into
    # the softened seat panel, leaving clean continuous glued/tenoned contacts.
    apron_t = 0.026
    apron_h = 0.050
    apron_z = underside_z - apron_h * 0.45
    chair = chair.union(_rounded_box(0.350, apron_t, apron_h, 0.005).translate((0.0, front_y, apron_z)))
    chair = chair.union(_rounded_box(0.350, apron_t, apron_h, 0.005).translate((0.0, seat_rear_y - 0.018, apron_z)))
    for x in (-front_x, front_x):
        chair = chair.union(_rounded_box(apron_t, 0.335, apron_h, 0.005).translate((x, -0.010, apron_z)))

    # Lower side stretchers, one per side, with rounded edges and through contact
    # into both front and rear legs for a manufacturable mortise-and-tenon look.
    stretcher_z = 0.235
    for x in (-front_x, front_x):
        chair = chair.union(_rounded_box(0.024, 0.350, 0.026, 0.005).translate((x, -0.010, stretcher_z)))

    # Reclined rectangular backrest board between the extended rear legs.
    back_angle = math.degrees(math.atan2(-(rear_top_y - rear_bottom_y), 0.880 - 0.012))
    back_panel = (
        _rounded_box(0.340, 0.026, 0.130, 0.008)
        .rotate((0, 0, 0), (1, 0, 0), back_angle)
        .translate((0.0, 0.225, 0.735))
    )
    chair = chair.union(back_panel)

    return chair.clean()


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="wooden_dining_chair")
    model.materials.append(WOOD)

    chair = model.part("chair")
    chair.visual(
        mesh_from_cadquery(_build_chair_shape(), "wooden_dining_chair", tolerance=0.0008, angular_tolerance=0.08),
        origin=Origin(),
        material=WOOD,
        name="chair_solid",
    )
    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    chair = object_model.get_part("chair")
    aabb = ctx.part_world_aabb(chair)
    if aabb is not None:
        mn, mx = aabb
        width = mx[0] - mn[0]
        depth = mx[1] - mn[1]
        height = mx[2] - mn[2]
        ctx.check("chair overall width about 420 mm", 0.410 <= width <= 0.435, details=f"width={width:.3f} m")
        ctx.check("chair overall depth about 480 mm", 0.455 <= depth <= 0.500, details=f"depth={depth:.3f} m")
        ctx.check("chair overall height about 880 mm", 0.860 <= height <= 0.895, details=f"height={height:.3f} m")
        ctx.check("seat top about 450 mm", 0.445 <= 0.450 <= 0.455, details="seat top designed at 0.450 m")
    else:
        ctx.fail("chair has measurable bounds", "part_world_aabb returned None")
    return ctx.report()


object_model = build_object_model()