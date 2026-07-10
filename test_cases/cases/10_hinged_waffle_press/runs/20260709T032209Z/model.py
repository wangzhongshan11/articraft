from __future__ import annotations

import math

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    Cylinder,
    Material,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)


OPEN_ANGLE_RAD = math.radians(105.0)


def _mat(model: ArticulatedObject, name: str, rgba: tuple[float, float, float, float]) -> Material:
    return model.material(name, rgba=rgba)


def _add_plate_grid(part, *, plate_name: str, z_top: float, center_x: float, downward: bool, material: Material) -> None:
    """Add a 6 x 6 shallow square waffle grid as connected pads on a plate slab."""
    pitch = 0.034
    square = 0.022
    pad_h = 0.006
    for ix in range(6):
        for iy in range(6):
            x = center_x + (ix - 2.5) * pitch
            y = (iy - 2.5) * pitch
            if downward:
                z = z_top - pad_h / 2.0
            else:
                z = z_top + pad_h / 2.0
            part.visual(
                Box((square, square, pad_h)),
                origin=Origin(xyz=(x, y, z)),
                material=material,
                name=f"{plate_name}_cell_{ix}_{iy}",
            )


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(
        name="desktop_hinged_waffle_press",
        meta={
            "design_notes": (
                "Desktop non-heated articulated press appearance model; visible housing walls are 12 mm, "
                "well above the requested 2 mm minimum. Plates are separate fixed links for removable/printable representation."
            ),
            "requested_exports": {
                "STEP": "unavailable in authoring sandbox",
                "STL": "unavailable in authoring sandbox",
                "3MF": "unavailable in authoring sandbox",
                "agent_trace": "unavailable in authoring sandbox",
                "telemetry": "unavailable in authoring sandbox",
            },
        },
    )

    shell_gray = _mat(model, "warm_gray_plastic", (0.36, 0.36, 0.33, 1.0))
    dark_gray = _mat(model, "dark_textured_plastic", (0.045, 0.045, 0.04, 1.0))
    black_plate = _mat(model, "matte_black_plate", (0.005, 0.005, 0.004, 1.0))
    screw_black = _mat(model, "black_screw_heads", (0.0, 0.0, 0.0, 1.0))

    base = model.part("base", meta={"role": "root lower housing tray with rear hinge supports"})
    # Open tray: 12 mm walls and an 18 mm bottom slab, intentionally hollow rather than a solid block.
    base.visual(Box((0.340, 0.270, 0.018)), origin=Origin(xyz=(0.020, 0.0, 0.009)), material=shell_gray, name="bottom_slab")
    base.visual(Box((0.340, 0.012, 0.045)), origin=Origin(xyz=(0.020, 0.135, 0.035)), material=shell_gray, name="side_wall_0")
    base.visual(Box((0.340, 0.012, 0.045)), origin=Origin(xyz=(0.020, -0.135, 0.035)), material=shell_gray, name="side_wall_1")
    base.visual(Box((0.012, 0.270, 0.045)), origin=Origin(xyz=(0.190, 0.0, 0.035)), material=shell_gray, name="front_wall")
    base.visual(Box((0.012, 0.270, 0.045)), origin=Origin(xyz=(-0.150, 0.0, 0.035)), material=shell_gray, name="rear_wall")
    base.visual(Box((0.292, 0.246, 0.006)), origin=Origin(xyz=(0.040, 0.0, 0.050)), material=dark_gray, name="inner_ledge")
    # Rails make the lower removable plate visibly seated and supported.
    base.visual(Box((0.260, 0.012, 0.009)), origin=Origin(xyz=(0.040, 0.106, 0.0485)), material=dark_gray, name="plate_rail_0")
    base.visual(Box((0.260, 0.012, 0.009)), origin=Origin(xyz=(0.040, -0.106, 0.0485)), material=dark_gray, name="plate_rail_1")
    base.visual(Box((0.012, 0.215, 0.009)), origin=Origin(xyz=(0.170, 0.0, 0.0485)), material=dark_gray, name="plate_rail_2")
    base.visual(Box((0.012, 0.215, 0.009)), origin=Origin(xyz=(-0.090, 0.0, 0.0485)), material=dark_gray, name="plate_rail_3")
    # Front molded handle/lip with a dark recessed grip cue.
    base.visual(Box((0.060, 0.180, 0.020)), origin=Origin(xyz=(0.220, 0.0, 0.022)), material=shell_gray, name="front_handle")
    base.visual(Box((0.038, 0.120, 0.008)), origin=Origin(xyz=(0.226, 0.0, 0.035)), material=dark_gray, name="grip_recess")
    # Rubber feet overlap the bottom slab so the base part is one supported assembly.
    for i, x in enumerate((-0.095, 0.135)):
        for j, y in enumerate((-0.095, 0.095)):
            base.visual(
                Cylinder(radius=0.018, length=0.018),
                origin=Origin(xyz=(x, y, -0.003)),
                material=dark_gray,
                name=f"foot_{i}_{j}",
            )
    # Rear double hinge: two visible hinge groups, each with paired base ears.
    hinge_group_centers = (-0.066, 0.066)
    for gi, gy in enumerate(hinge_group_centers):
        for ei, ey in enumerate((gy - 0.020, gy + 0.020)):
            base.visual(
                Box((0.030, 0.018, 0.020)),
                origin=Origin(xyz=(-0.130, ey, 0.057)),
                material=shell_gray,
                name=f"hinge_ear_{gi}_{ei}",
            )
            base.visual(
                Cylinder(radius=0.012, length=0.016),
                origin=Origin(xyz=(-0.130, ey, 0.071), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=dark_gray,
                name=f"base_barrel_{gi}_{ei}",
            )
    # Latch pivot ears capture the latch pin; overlap is intentionally allowed in tests.
    for i, y in enumerate((-0.032, 0.032)):
        base.visual(Box((0.018, 0.016, 0.018)), origin=Origin(xyz=(0.205, y, 0.058)), material=shell_gray, name=f"latch_ear_{i}")
    base.visual(Box((0.020, 0.080, 0.010)), origin=Origin(xyz=(0.182, 0.0, 0.059)), material=shell_gray, name="front_catch")

    lower_plate = model.part("lower_plate", meta={"removable_printable_plate": True, "grid": "6 x 6 shallow square array"})
    lower_plate.visual(Box((0.250, 0.210, 0.008)), origin=Origin(xyz=(0.040, 0.0, 0.057)), material=black_plate, name="lower_plate_slab")
    lower_plate.visual(Box((0.268, 0.228, 0.007)), origin=Origin(xyz=(0.040, 0.0, 0.0535)), material=black_plate, name="lower_plate_outer_rim")
    lower_plate.visual(Box((0.012, 0.225, 0.012)), origin=Origin(xyz=(0.040, 0.0, 0.063)), material=black_plate, name="center_stiffener")
    _add_plate_grid(lower_plate, plate_name="lower", z_top=0.061, center_x=0.040, downward=False, material=black_plate)

    lid = model.part("lid", meta={"role": "upper housing with handle, hinge leaves, and latch catch"})
    # Child frame is the hinge line. At q=0 the lid extends along +X over the base.
    lid.visual(Box((0.310, 0.260, 0.020)), origin=Origin(xyz=(0.160, 0.0, 0.049)), material=shell_gray, name="top_skin")
    lid.visual(Box((0.310, 0.012, 0.050)), origin=Origin(xyz=(0.160, 0.130, 0.035)), material=shell_gray, name="lid_side_wall_0")
    lid.visual(Box((0.310, 0.012, 0.050)), origin=Origin(xyz=(0.160, -0.130, 0.035)), material=shell_gray, name="lid_side_wall_1")
    lid.visual(Box((0.012, 0.260, 0.050)), origin=Origin(xyz=(0.315, 0.0, 0.035)), material=shell_gray, name="lid_front_wall")
    lid.visual(Box((0.012, 0.260, 0.050)), origin=Origin(xyz=(0.005, 0.0, 0.035)), material=shell_gray, name="lid_rear_wall")
    lid.visual(Box((0.298, 0.248, 0.006)), origin=Origin(xyz=(0.160, 0.0, 0.018)), material=dark_gray, name="upper_recess_frame")
    # Four screw/boss pads touch the replaceable upper plate at its top face.
    for i, x in enumerate((0.055, 0.265)):
        for j, y in enumerate((-0.090, 0.090)):
            lid.visual(Box((0.020, 0.020, 0.016)), origin=Origin(xyz=(x, y, 0.023)), material=dark_gray, name=f"plate_boss_{i}_{j}")
            lid.visual(Cylinder(radius=0.006, length=0.002), origin=Origin(xyz=(x, y, 0.014)), material=screw_black, name=f"screw_head_{i}_{j}")
    # Molded carry handle on the top, connected by two posts.
    lid.visual(Box((0.030, 0.200, 0.020)), origin=Origin(xyz=(0.160, 0.0, 0.085)), material=shell_gray, name="handle_bar")
    lid.visual(Box((0.045, 0.036, 0.052)), origin=Origin(xyz=(0.070, 0.082, 0.069)), material=shell_gray, name="handle_post_0")
    lid.visual(Box((0.045, 0.036, 0.052)), origin=Origin(xyz=(0.250, -0.082, 0.069)), material=shell_gray, name="handle_post_1")
    # Centered latch catch on the lid front.
    lid.visual(Box((0.008, 0.070, 0.014)), origin=Origin(xyz=(0.319, 0.0, 0.026)), material=dark_gray, name="lid_latch_catch")
    # Lid hinge leaves and center barrels, interleaved between base hinge ears.
    for gi, gy in enumerate(hinge_group_centers):
        lid.visual(Box((0.040, 0.024, 0.010)), origin=Origin(xyz=(-0.020, gy, 0.010)), material=shell_gray, name=f"lid_hinge_leaf_{gi}")
        lid.visual(
            Cylinder(radius=0.010, length=0.020),
            origin=Origin(xyz=(0.0, gy, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=dark_gray,
            name=f"lid_barrel_{gi}",
        )

    upper_plate = model.part("upper_plate", meta={"removable_printable_plate": True, "grid": "6 x 6 shallow square array mirrored downward"})
    upper_plate.visual(Box((0.250, 0.210, 0.008)), origin=Origin(xyz=(0.160, 0.0, 0.012)), material=black_plate, name="upper_plate_slab")
    upper_plate.visual(Box((0.268, 0.228, 0.006)), origin=Origin(xyz=(0.160, 0.0, 0.015)), material=black_plate, name="upper_plate_outer_rim")
    upper_plate.visual(Box((0.012, 0.225, 0.012)), origin=Origin(xyz=(0.160, 0.0, 0.006)), material=black_plate, name="upper_center_stiffener")
    _add_plate_grid(upper_plate, plate_name="upper", z_top=0.008, center_x=0.160, downward=True, material=black_plate)

    front_latch = model.part("front_latch", meta={"role": "front rotating lock clasp"})
    front_latch.visual(
        Cylinder(radius=0.006, length=0.078),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=dark_gray,
        name="latch_pin",
    )
    front_latch.visual(Box((0.010, 0.052, 0.036)), origin=Origin(xyz=(0.0, 0.0, 0.020)), material=shell_gray, name="latch_arm")
    front_latch.visual(Box((0.020, 0.052, 0.008)), origin=Origin(xyz=(-0.006, 0.0, 0.040)), material=shell_gray, name="latch_thumb_tab")

    model.articulation(
        "base_to_lower_plate",
        ArticulationType.FIXED,
        parent=base,
        child=lower_plate,
        origin=Origin(),
    )
    model.articulation(
        "base_to_lid",
        ArticulationType.REVOLUTE,
        parent=base,
        child=lid,
        origin=Origin(xyz=(-0.130, 0.0, 0.071)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=12.0, velocity=1.6, lower=0.0, upper=OPEN_ANGLE_RAD),
    )
    model.articulation(
        "lid_to_upper_plate",
        ArticulationType.FIXED,
        parent=lid,
        child=upper_plate,
        origin=Origin(),
    )
    model.articulation(
        "base_to_front_latch",
        ArticulationType.REVOLUTE,
        parent=base,
        child=front_latch,
        origin=Origin(xyz=(0.205, 0.0, 0.058)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=0.70),
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    base = object_model.get_part("base")
    lid = object_model.get_part("lid")
    lower_plate = object_model.get_part("lower_plate")
    upper_plate = object_model.get_part("upper_plate")
    front_latch = object_model.get_part("front_latch")
    lid_joint = object_model.get_articulation("base_to_lid")
    latch_joint = object_model.get_articulation("base_to_front_latch")

    # The latch pin is intentionally captured through the two base ears.
    for i in range(2):
        ctx.allow_overlap(
            base,
            front_latch,
            elem_a=f"latch_ear_{i}",
            elem_b="latch_pin",
            reason="The latch pin is intentionally seated through the molded latch ear bore.",
        )
        ctx.expect_overlap(
            base,
            front_latch,
            axes="yz",
            elem_a=f"latch_ear_{i}",
            elem_b="latch_pin",
            min_overlap=0.006,
            name=f"latch pin retained by ear {i}",
        )

    ctx.check(
        "lid hinge limit is 105 degrees",
        lid_joint.motion_limits is not None
        and abs(lid_joint.motion_limits.lower - 0.0) < 1e-9
        and abs(lid_joint.motion_limits.upper - OPEN_ANGLE_RAD) < 1e-9,
        details=f"limits={lid_joint.motion_limits}",
    )
    ctx.check(
        "front latch has a positive release swing",
        latch_joint.motion_limits is not None
        and latch_joint.motion_limits.lower == 0.0
        and latch_joint.motion_limits.upper >= 0.60,
        details=f"limits={latch_joint.motion_limits}",
    )

    with ctx.pose({lid_joint: 0.0}):
        ctx.expect_gap(
            upper_plate,
            lower_plate,
            axis="z",
            min_gap=0.001,
            name="closed press plates keep at least 1 mm vertical clearance",
        )
        ctx.expect_overlap(
            upper_plate,
            lower_plate,
            axes="xy",
            min_overlap=0.190,
            name="upper and lower press plates align over the waffle grid",
        )
        closed_aabb = ctx.part_world_aabb(upper_plate)

    with ctx.pose({lid_joint: OPEN_ANGLE_RAD}):
        open_aabb = ctx.part_world_aabb(upper_plate)
        ctx.expect_gap(
            upper_plate,
            lower_plate,
            axis="z",
            min_gap=0.020,
            name="open pose separates the replaceable plates visibly",
        )

    ctx.check(
        "lid opens upward from the rear double hinge",
        closed_aabb is not None and open_aabb is not None and open_aabb[1][2] > closed_aabb[1][2] + 0.18,
        details=f"closed_aabb={closed_aabb}, open_aabb={open_aabb}",
    )

    return ctx.report()


object_model = build_object_model()
