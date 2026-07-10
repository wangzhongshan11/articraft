from __future__ import annotations

import cadquery as cq

from sdk import ArticulatedObject, Material, Origin, TestContext, TestReport, mesh_from_cadquery


MM = 0.001


def mm(value: float) -> float:
    return value * MM


def wood_material() -> Material:
    return Material("oak", color=(0.73, 0.57, 0.34, 1.0))


def build_chair_shape() -> cq.Workplane:
    width = 430.0
    depth = 460.0
    height = 860.0
    seat_height = 440.0
    seat_thickness = 32.0
    rear_top = height
    front_leg_top = seat_height - 4.0

    leg_section = 32.0
    rear_upright_depth = 36.0
    side_inset_x = 30.0
    front_y = depth / 2.0 - 28.0
    rear_y = -depth / 2.0 + 36.0
    seat_y = 0.0

    front_leg_x = width / 2.0 - side_inset_x - leg_section / 2.0
    rear_leg_x = width / 2.0 - side_inset_x - leg_section / 2.0

    seat = (
        cq.Workplane("XY")
        .rect(width - 10.0, depth - 30.0)
        .extrude(seat_thickness)
        .edges("|Z").fillet(8.0)
        .edges(">Z").fillet(4.5)
        .translate((0.0, seat_y, seat_height - seat_thickness))
    )

    front_leg = (
        cq.Workplane("XY")
        .rect(leg_section, leg_section)
        .extrude(front_leg_top)
        .edges("|Z").fillet(4.0)
    )
    front_leg_left = front_leg.translate((-front_leg_x, front_y, 0.0))
    front_leg_right = front_leg.translate((front_leg_x, front_y, 0.0))

    rear_leg = (
        cq.Workplane("XY")
        .rect(leg_section, rear_upright_depth)
        .extrude(rear_top)
        .edges("|Z").fillet(4.0)
    )
    rear_leg_left = rear_leg.translate((-rear_leg_x, rear_y, 0.0))
    rear_leg_right = rear_leg.translate((rear_leg_x, rear_y, 0.0))

    side_stretch_top = 172.0
    side_stretch_bottom = 144.0
    side_stretch_width = 18.0
    side_stretch_thickness = 22.0

    stretcher_left_face = -front_leg_x + leg_section / 2.0 - 2.0
    stretcher_right_face = front_leg_x - leg_section / 2.0 + 2.0
    stretcher_span = stretcher_right_face - stretcher_left_face

    front_stretcher = (
        cq.Workplane("YZ")
        .rect(20.0, 22.0)
        .extrude(stretcher_span)
        .translate((stretcher_left_face, front_y - 10.0, 182.0))
        .edges("|X").fillet(2.0)
    )

    rear_stretcher = (
        cq.Workplane("YZ")
        .rect(18.0, 22.0)
        .extrude(stretcher_span)
        .translate((stretcher_left_face, rear_y + 34.0, 150.0))
        .edges("|X").fillet(2.0)
    )

    side_brace_path = [
        (-front_leg_x + 8.0, front_y - 12.0),
        (0.0, 0.0),
        (-rear_leg_x + 10.0, rear_y + rear_upright_depth - 6.0),
    ]
    center_side_brace = (
        cq.Workplane("XY")
        .polyline(side_brace_path)
        .offset2D(9.0)
        .extrude(20.0)
        .translate((0.0, 0.0, 158.0))
        .edges("|Z").fillet(2.0)
    )

    slat_section = 16.0
    slat_depth = 12.0
    slat_bottom = seat_height + 10.0
    slat_top = 748.0
    slat_height = slat_top - slat_bottom
    slat_span = 214.0
    slat_spacing = slat_span / 4.0
    slat_positions = [-slat_span / 2.0 + i * slat_spacing for i in range(5)]

    slats = []
    for x in slat_positions:
        slat = (
            cq.Workplane("XY")
            .rect(slat_section, slat_depth)
            .extrude(slat_height)
            .edges("|Z").fillet(2.5)
            .translate((x, rear_y + 26.0, slat_bottom))
        )
        slats.append(slat)

    lower_back_rail = (
        cq.Workplane("XY")
        .rect(300.0, 22.0)
        .extrude(24.0)
        .edges("|Z").fillet(3.0)
        .translate((0.0, rear_y + 22.0, seat_height - 8.0))
    )

    top_rail = (
        cq.Workplane("XZ")
        .moveTo(-160.0, 0.0)
        .threePointArc((0.0, 22.0), (160.0, 0.0))
        .lineTo(160.0, 30.0)
        .threePointArc((0.0, 50.0), (-160.0, 30.0))
        .close()
        .extrude(28.0)
        .translate((0.0, rear_y + 18.0, 810.0))
        .edges("|Y").fillet(4.0)
    )

    chair = seat
    for shape in [
        front_leg_left,
        front_leg_right,
        rear_leg_left,
        rear_leg_right,
        front_stretcher,
        rear_stretcher,
        center_side_brace,
        lower_back_rail,
        top_rail,
        *slats,
    ]:
        chair = chair.union(shape)

    return chair



def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="dining_chair")
    chair = model.part("chair")
    chair.visual(
        mesh_from_cadquery(build_chair_shape(), "chair", unit_scale=MM),
        origin=Origin(),
        material=wood_material(),
        name="chair_body",
    )
    return model



def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    chair = object_model.get_part("chair")

    ctx.expect_origin_gap(chair, chair, axis="z", min_gap=0.0, max_gap=0.0, name="chair part exists")

    return ctx.report()


object_model = build_object_model()
