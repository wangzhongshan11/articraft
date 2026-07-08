from __future__ import annotations

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Material,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)


MM = 0.001


def _rounded_box(length: float, width: float, height: float, radius: float) -> cq.Workplane:
    """Create a millimetre CadQuery box from z=0..height with rounded vertical corners."""
    return (
        cq.Workplane("XY")
        .box(length, width, height, centered=(True, True, False))
        .edges("|Z")
        .fillet(radius)
    )


def _rounded_rect_ring(
    outer_length: float,
    outer_width: float,
    inner_length: float,
    inner_width: float,
    height: float,
    outer_radius: float,
    inner_radius: float,
) -> cq.Workplane:
    outer = _rounded_box(outer_length, outer_width, height, outer_radius)
    inner = _rounded_box(inner_length, inner_width, height + 2.0, inner_radius).translate((0, 0, -1.0))
    return outer.cut(inner)


def _base_tub() -> cq.Workplane:
    # Overall base is a one-piece open tub: 260 x 140 mm footprint, 82 mm tall,
    # with 3 mm bottom/walls and a fully open interior.
    outer = _rounded_box(260.0, 140.0, 82.0, 15.0)
    cavity = _rounded_box(254.0, 134.0, 91.0, 12.0).translate((0, 0, 3.0))
    return outer.cut(cavity)


def _base_lip() -> cq.Workplane:
    # Internal lip/ledge protrudes inward just below the rim and supports the lid skirt.
    return _rounded_rect_ring(
        255.0,
        135.0,
        246.0,
        126.0,
        3.0,
        12.5,
        9.0,
    ).translate((0, 0, 73.0))


def _lid_top() -> cq.Workplane:
    # Lid local frame is at the visible assembly seam.  The upper cover rises
    # 18 mm above it and contains the rounded-rectangle dispensing opening.
    top = _rounded_box(260.0, 140.0, 18.0, 15.0)
    opening = _rounded_box(130.0, 35.0, 28.0, 17.0).translate((0, 0, -5.0))
    top = top.cut(opening)

    # Soften the outer lid perimeter and the dispensing hole rim without adding
    # decorative features.
    try:
        top = top.faces(">Z").edges().fillet(2.0)
    except Exception:
        pass
    try:
        top = top.faces("<Z").edges().fillet(1.0)
    except Exception:
        pass
    return top


def _lid_skirt() -> cq.Workplane:
    # Downward locating skirt seats on the base lip and keeps the removable lid aligned.
    return _rounded_rect_ring(
        250.0,
        130.0,
        238.0,
        118.0,
        6.5,
        10.0,
        7.0,
    ).translate((0, 0, -6.0))


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="tissue_box_with_removable_lid")

    base_material = Material("warm_matte_base", rgba=(0.78, 0.74, 0.66, 1.0))
    lid_material = Material("light_wood_lid", rgba=(0.82, 0.64, 0.39, 1.0))

    base = model.part("base")
    base.visual(
        mesh_from_cadquery(
            _base_tub(),
            "hollow_base_tub",
            tolerance=0.20,
            angular_tolerance=0.08,
            unit_scale=MM,
        ),
        material=base_material,
        name="base_tub",
    )
    base.visual(
        mesh_from_cadquery(
            _base_lip(),
            "internal_base_lip",
            tolerance=0.20,
            angular_tolerance=0.08,
            unit_scale=MM,
        ),
        material=base_material,
        name="base_lip",
    )

    lid = model.part("lid")
    lid.visual(
        mesh_from_cadquery(
            _lid_top(),
            "rounded_lid_top",
            tolerance=0.20,
            angular_tolerance=0.08,
            unit_scale=MM,
        ),
        material=lid_material,
        name="lid_top",
    )
    lid.visual(
        mesh_from_cadquery(
            _lid_skirt(),
            "lid_locating_skirt",
            tolerance=0.20,
            angular_tolerance=0.08,
            unit_scale=MM,
        ),
        material=lid_material,
        name="lid_skirt",
    )

    model.articulation(
        "base_to_lid",
        ArticulationType.PRISMATIC,
        parent=base,
        child=lid,
        origin=Origin(xyz=(0.0, 0.0, 82.0 * MM)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=20.0, velocity=0.25, lower=0.0, upper=90.0 * MM),
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    base = object_model.get_part("base")
    lid = object_model.get_part("lid")
    lift = object_model.get_articulation("base_to_lid")

    base_aabb = ctx.part_world_aabb(base)
    lid_aabb = ctx.part_world_aabb(lid)
    if base_aabb and lid_aabb:
        min_corner = tuple(min(base_aabb[0][i], lid_aabb[0][i]) for i in range(3))
        max_corner = tuple(max(base_aabb[1][i], lid_aabb[1][i]) for i in range(3))
        dims = tuple(max_corner[i] - min_corner[i] for i in range(3))
        ctx.check(
            "assembled footprint is 260 by 140 mm",
            abs(dims[0] - 0.260) < 0.002 and abs(dims[1] - 0.140) < 0.002,
            details=f"assembled dims={dims}",
        )
        ctx.check(
            "assembled height is 100 mm",
            abs(dims[2] - 0.100) < 0.002,
            details=f"assembled dims={dims}",
        )
    else:
        ctx.fail("assembled bounding box available", "missing part AABB")

    ctx.allow_overlap(
        base,
        lid,
        elem_a="base_lip",
        elem_b="lid_skirt",
        reason="The removable lid's locating skirt intentionally nests around the internal base lip for a tight seated fit.",
    )
    ctx.expect_overlap(
        lid,
        base,
        axes="xy",
        elem_a="lid_skirt",
        elem_b="base_lip",
        min_overlap=0.110,
        name="lid skirt captures the internal seating lip",
    )
    ctx.expect_gap(
        lid,
        base,
        axis="z",
        positive_elem="lid_top",
        negative_elem="base_tub",
        max_gap=0.001,
        max_penetration=0.0,
        name="visible lid seam is tight at the rim",
    )
    ctx.expect_overlap(
        lid,
        base,
        axes="xy",
        min_overlap=0.120,
        name="lid footprint aligns with base footprint",
    )

    rest_pos = ctx.part_world_position(lid)
    with ctx.pose({lift: 0.060}):
        raised_pos = ctx.part_world_position(lid)
        ctx.expect_gap(
            lid,
            base,
            axis="z",
            min_gap=0.050,
            name="removable lid lifts clear vertically",
        )
    ctx.check(
        "lid lift joint moves upward",
        rest_pos is not None and raised_pos is not None and raised_pos[2] > rest_pos[2] + 0.055,
        details=f"rest={rest_pos}, raised={raised_pos}",
    )

    return ctx.report()


object_model = build_object_model()
