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


def mm(value: float) -> float:
    return value * MM


def rounded_rect_wire(length_mm: float, width_mm: float, radius_mm: float) -> cq.Workplane:
    return cq.Workplane("XY").rect(length_mm - 2 * radius_mm, width_mm - 2 * radius_mm).vertices().circle(radius_mm)


def build_base_shape() -> cq.Workplane:
    outer_l = 260.0
    outer_w = 140.0
    base_h = 76.0
    wall = 3.0
    corner_r = 14.0
    floor_t = 3.0
    lip_drop = 8.0
    seat_step = 1.0

    outer = (
        cq.Workplane("XY")
        .rect(outer_l - 2 * corner_r, outer_w - 2 * corner_r)
        .vertices()
        .circle(corner_r)
        .extrude(base_h)
        .edges("|Z")
        .fillet(2.0)
    )

    inner = (
        cq.Workplane("XY")
        .workplane(offset=floor_t)
        .rect(outer_l - 2 * (wall + corner_r - 2.0), outer_w - 2 * (wall + corner_r - 2.0))
        .vertices()
        .circle(corner_r - wall)
        .extrude(base_h - floor_t - lip_drop)
    )

    seat_cut = (
        cq.Workplane("XY")
        .workplane(offset=base_h - lip_drop)
        .rect(
            outer_l - 2 * (wall + seat_step + corner_r - 2.0),
            outer_w - 2 * (wall + seat_step + corner_r - 2.0),
        )
        .vertices()
        .circle(corner_r - wall - seat_step)
        .extrude(lip_drop + 2.0)
    )

    return outer.cut(inner).cut(seat_cut)


def build_lid_shape() -> cq.Workplane:
    outer_l = 260.0
    outer_w = 140.0
    lid_t = 8.0
    top_t = 3.0
    wall = 3.0
    corner_r = 14.0
    lip_depth = 7.0
    fit_clearance = 0.4
    seat_step = 1.0
    opening_l = 130.0
    opening_w = 35.0
    opening_r = 17.5

    top = (
        cq.Workplane("XY")
        .rect(outer_l - 2 * corner_r, outer_w - 2 * corner_r)
        .vertices()
        .circle(corner_r)
        .extrude(lid_t)
        .edges("|Z")
        .fillet(2.0)
        .edges(">Z")
        .fillet(1.2)
    )

    opening = (
        cq.Workplane("XY")
        .workplane(offset=-1.0)
        .rect(opening_l - 2 * opening_r, opening_w - 2 * opening_r)
        .vertices()
        .circle(opening_r)
        .extrude(lid_t + 2.0)
    )

    inner_l = outer_l - 2 * (wall + seat_step + fit_clearance)
    inner_w = outer_w - 2 * (wall + seat_step + fit_clearance)
    inner_r = corner_r - wall - seat_step - fit_clearance

    skirt_outer = (
        cq.Workplane("XY")
        .rect(inner_l - 2 * inner_r, inner_w - 2 * inner_r)
        .vertices()
        .circle(inner_r)
        .extrude(lip_depth)
    )
    skirt_inner = (
        cq.Workplane("XY")
        .workplane(offset=top_t)
        .rect((inner_l - 2 * wall) - 2 * (inner_r - wall), (inner_w - 2 * wall) - 2 * (inner_r - wall))
        .vertices()
        .circle(inner_r - wall)
        .extrude(lip_depth + 1.0)
    )
    skirt = skirt_outer.cut(skirt_inner)

    return top.cut(opening).union(skirt.translate((0, 0, -lip_depth)))


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="tissue_box")

    ceramic = model.material("ceramic", color=(0.90, 0.89, 0.85, 1.0))
    bamboo = model.material("bamboo", color=(0.87, 0.77, 0.60, 1.0))

    base = model.part("base")
    base.visual(
        mesh_from_cadquery(build_base_shape(), "base_shell", unit_scale=MM),
        material=ceramic,
        name="base_shell",
    )

    lid = model.part("lid")
    lid.visual(
        mesh_from_cadquery(build_lid_shape(), "lid_panel", unit_scale=MM),
        origin=Origin(xyz=(0.0, 0.0, mm(83.0))),
        material=bamboo,
        name="lid_panel",
    )

    model.articulation(
        "base_to_lid",
        ArticulationType.FIXED,
        parent=base,
        child=lid,
        origin=Origin(),
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    base = object_model.get_part("base")
    lid = object_model.get_part("lid")

    ctx.expect_overlap(lid, base, axes="xy", min_overlap=0.12, name="lid aligns with base footprint")
    ctx.expect_gap(lid, base, axis="z", min_gap=0.0, max_gap=0.0015, positive_elem="lid_panel", negative_elem="base_shell", name="lid sits tightly on base")

    return ctx.report()


object_model = build_object_model()