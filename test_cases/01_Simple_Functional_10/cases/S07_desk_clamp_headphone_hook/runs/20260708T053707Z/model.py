from __future__ import annotations

import cadquery as cq

from sdk import ArticulatedObject, Material, Origin, TestContext, TestReport, mesh_from_cadquery


WIDTH_MM = 90.0
DEPTH_MM = 62.1
HEIGHT_MM = 118.8
SLOT_CLEARANCE_MM = 35.0


def _headphone_hook_shape() -> cq.Workplane:
    """One-piece desk-edge headphone hook authored in millimetres.

    X is width across the desk edge, Y is projection out from the desk edge,
    and Z is vertical height.  The side profile is a continuous C-shaped clamp
    with a short internal ledge and an upturned lower hook for a headband.
    """
    side_profile_yz = [
        (0.0, 0.0),
        (0.0, HEIGHT_MM),
        (DEPTH_MM, HEIGHT_MM),
        (DEPTH_MM, 92.0),
        (16.0, 92.0),
        (16.0, 57.0),
        (38.0, 57.0),
        (38.0, 45.0),
        (16.0, 45.0),
        (16.0, 20.0),
        (48.0, 20.0),
        (48.0, 32.0),
        (DEPTH_MM, 32.0),
        (DEPTH_MM, 0.0),
    ]

    hook = (
        cq.Workplane("YZ")
        .moveTo(*side_profile_yz[0])
        .polyline(side_profile_yz[1:])
        .close()
        .extrude(WIDTH_MM)
        # Rounded molded/printed edges in the functional side profile, including
        # the hook-to-spine transition and the front nose of the clamp.
        .edges("|X")
        .fillet(3.0)
    )

    return hook


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="desk_edge_headphone_hook")

    matte_graphite = Material("matte_graphite", rgba=(0.18, 0.18, 0.17, 1.0))

    hook_part = model.part("hook")
    hook_part.visual(
        mesh_from_cadquery(
            _headphone_hook_shape(),
            "desk_edge_headphone_hook_body",
            tolerance=0.15,
            angular_tolerance=0.08,
            unit_scale=0.001,
        ),
        origin=Origin(),
        material=matte_graphite,
        name="one_piece_body",
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    hook = object_model.get_part("hook")

    aabb = ctx.part_world_aabb(hook)
    if aabb is None:
        ctx.fail("hook has measurable body", "No world AABB was available for the hook part.")
    else:
        lower, upper = aabb
        dims = tuple(upper[i] - lower[i] for i in range(3))
        ctx.check(
            "overall size matches requested envelope",
            0.088 <= dims[0] <= 0.092
            and 0.058 <= dims[1] <= 0.062
            and 0.108 <= dims[2] <= 0.112,
            details=f"measured dimensions in metres: {dims}",
        )

    ctx.check(
        "desk slot clearance fits 25 to 35 mm desktop",
        25.0 <= SLOT_CLEARANCE_MM <= 35.0,
        details=f"slot clearance is {SLOT_CLEARANCE_MM} mm",
    )

    return ctx.report()


object_model = build_object_model()