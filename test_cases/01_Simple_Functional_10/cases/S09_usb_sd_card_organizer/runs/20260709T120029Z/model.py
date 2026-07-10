from __future__ import annotations

import cadquery as cq

from sdk import ArticulatedObject, Material, TestContext, TestReport, mesh_from_cadquery


MM = 0.001


def _build_organizer_shape() -> cq.Workplane:
    width = 120.0
    depth = 70.0
    height = 36.0
    corner_r = 7.0
    edge_r = 2.2

    usb_len = 10.0
    usb_w = 5.2
    usb_depth = 24.0

    sd_len = 18.0
    sd_w = 2.8
    sd_depth = 18.0

    wall_front = 9.0
    row_gap = 10.0

    shape = (
        cq.Workplane("XY")
        .rect(width - 2.0 * corner_r, depth - 2.0 * corner_r)
        .extrude(height)
        .edges("|Z")
        .fillet(corner_r)
        .edges(">Z and (|X or |Y)")
        .fillet(edge_r)
    )

    x_pitch_usb = 16.0
    x_pitch_sd = 21.0
    usb_xs = [(-2.5 + i) * x_pitch_usb for i in range(6)]
    sd_xs = [(-1.5 + i) * x_pitch_sd for i in range(4)]

    y_usb = depth / 2.0 - wall_front - usb_len / 2.0
    y_sd = y_usb - usb_len / 2.0 - row_gap - sd_len / 2.0

    for x in usb_xs:
        shape = shape.faces(">Z").workplane(centerOption="CenterOfBoundBox").center(x, y_usb).slot2D(usb_len, usb_w, 0).cutBlind(-usb_depth)
    for x in sd_xs:
        shape = shape.faces(">Z").workplane(centerOption="CenterOfBoundBox").center(x, y_sd).slot2D(sd_len, sd_w, 0).cutBlind(-sd_depth)

    return shape


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="usb_sd_organizer")
    base = model.part("base")

    base_shape = _build_organizer_shape()
    base.visual(
        mesh_from_cadquery(base_shape, "usb_sd_organizer_base", unit_scale=MM),
        material=Material("body", color=(0.78, 0.78, 0.80, 1.0)),
        name="base_shell",
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    base = object_model.get_part("base")

    ctx.expect_gap(base, base, axis="z", max_penetration=0.036, max_gap=0.0, name="organizer height is 36 mm")
    ctx.expect_overlap(base, base, axes="xy", min_overlap=0.055, name="organizer footprint exceeds 55 mm in both plan axes")

    return ctx.report()


object_model = build_object_model()