from __future__ import annotations

import cadquery as cq

from sdk import (
    ArticulatedObject,
    Material,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)


# All CadQuery dimensions below are authored in millimetres, then exported to the
# SDK in metres with unit_scale=0.001.
BASE_LENGTH_MM = 120.0
BASE_WIDTH_MM = 70.0
BASE_HEIGHT_MM = 36.0


def _rounded_prism_cutter(
    *,
    x_mm: float,
    y_mm: float,
    width_mm: float,
    depth_mm: float,
    z_bottom_mm: float,
    height_mm: float,
    radius_mm: float,
) -> cq.Workplane:
    """A vertical rounded-rectangle prism used to cut a blind pocket."""
    cutter = cq.Workplane("XY").box(width_mm, depth_mm, height_mm)
    cutter = cutter.edges("|Z").fillet(radius_mm)
    return cutter.translate((x_mm, y_mm, z_bottom_mm + height_mm / 2.0))


def _make_organizer_body() -> cq.Workplane:
    body = cq.Workplane("XY").box(BASE_LENGTH_MM, BASE_WIDTH_MM, BASE_HEIGHT_MM)
    body = body.translate((0.0, 0.0, BASE_HEIGHT_MM / 2.0))

    # Small manufacturable radii on the outside: rounded enough to remove sharp
    # edges while leaving broad flat side, top, and base faces.
    body = body.edges("|Z").fillet(4.0)
    body = body.edges("#Z").fillet(1.6)

    top_z = BASE_HEIGHT_MM
    cutter_extra = 1.5

    # Six narrow USB plug pockets in the rear/top row.  The pitch leaves a
    # continuous solid field between slots and a strong perimeter wall.
    usb_slot_w = 8.8
    slot_d = 22.0
    usb_pitch = 14.5
    usb_y = 15.0
    usb_floor_z = 9.0
    first_usb_x = -usb_pitch * (6 - 1) / 2.0
    for i in range(6):
        cutter = _rounded_prism_cutter(
            x_mm=first_usb_x + i * usb_pitch,
            y_mm=usb_y,
            width_mm=usb_slot_w,
            depth_mm=slot_d,
            z_bottom_mm=usb_floor_z,
            height_mm=top_z - usb_floor_z + cutter_extra,
            radius_mm=1.7,
        )
        body = body.cut(cutter)

    # Four wider SD-card pockets in the second row.  Wider x-widths distinguish
    # them clearly from the USB row while keeping the same front-to-back depth.
    sd_slot_w = 18.5
    sd_pitch = 25.0
    sd_y = -15.0
    sd_floor_z = 8.0
    first_sd_x = -sd_pitch * (4 - 1) / 2.0
    for i in range(4):
        cutter = _rounded_prism_cutter(
            x_mm=first_sd_x + i * sd_pitch,
            y_mm=sd_y,
            width_mm=sd_slot_w,
            depth_mm=slot_d,
            z_bottom_mm=sd_floor_z,
            height_mm=top_z - sd_floor_z + cutter_extra,
            radius_mm=2.4,
        )
        body = body.cut(cutter)

    # Lightly break the upper pocket rims and external top edge after cutting.
    # The radius is intentionally small so the pockets remain rectangular and
    # sized for cards/connectors.
    body = body.edges(">Z").fillet(0.6)
    return body.clean()


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="usb_sd_card_organizer")

    grey_plastic = Material("warm_grey_plastic", rgba=(0.62, 0.62, 0.58, 1.0))

    base = model.part("base")
    base.visual(
        mesh_from_cadquery(
            _make_organizer_body(),
            "usb_sd_organizer_base",
            tolerance=0.08,
            angular_tolerance=0.08,
            unit_scale=0.001,
        ),
        origin=Origin(),
        material=grey_plastic,
        name="pocketed_base",
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    base = object_model.get_part("base")

    aabb = ctx.part_world_aabb(base)
    if aabb is not None:
        mn, mx = aabb
        dims = (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])
        ctx.check(
            "overall size is 120 x 70 x 36 mm",
            abs(dims[0] - 0.120) < 0.0015
            and abs(dims[1] - 0.070) < 0.0015
            and abs(dims[2] - 0.036) < 0.0015,
            details=f"measured dimensions in metres: {dims}",
        )
        ctx.check(
            "flat base sits on z zero",
            abs(mn[2]) < 0.001,
            details=f"minimum z: {mn[2]}",
        )
    else:
        ctx.fail("base aabb available", "Could not measure the base AABB.")

    ctx.check("single solid base part", len(object_model.parts) == 1, details=str([p.name for p in object_model.parts]))

    return ctx.report()


object_model = build_object_model()