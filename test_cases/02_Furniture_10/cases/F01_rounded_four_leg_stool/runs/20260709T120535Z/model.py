from __future__ import annotations

import cadquery as cq

from sdk import (
    ArticulatedObject,
    Box,
    Material,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)


SEAT_SIZE = 0.320
SEAT_THICKNESS = 0.030
TOTAL_HEIGHT = 0.440
LEG_HEIGHT = TOTAL_HEIGHT - SEAT_THICKNESS
TOP_LEG_SIZE = 0.048
BOTTOM_LEG_SIZE = 0.034
POCKET_DEPTH = 0.010
POCKET_CLEARANCE = 0.003
SEAT_CORNER_RADIUS = 0.050
LEG_CORNER_RADIUS = 0.012
LEG_SPREAD_X = 0.096
LEG_SPREAD_Y = 0.096


def _seat_shape() -> cq.Workplane:
    seat = cq.Workplane("XY").box(SEAT_SIZE, SEAT_SIZE, SEAT_THICKNESS).translate((0.0, 0.0, SEAT_THICKNESS * 0.5))
    pocket_offset = SEAT_SIZE * 0.5 - LEG_SPREAD_X
    pocket_size = TOP_LEG_SIZE + POCKET_CLEARANCE * 2.0
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            seat = seat.cut(
                cq.Workplane("XY")
                .center(sx * pocket_offset, sy * pocket_offset)
                .rect(pocket_size, pocket_size)
                .extrude(POCKET_DEPTH)
            )
    return seat


def _leg_shape() -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .rect(TOP_LEG_SIZE, TOP_LEG_SIZE)
        .workplane(offset=-LEG_HEIGHT)
        .rect(BOTTOM_LEG_SIZE, BOTTOM_LEG_SIZE)
        .loft(combine=True)
    )


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="rounded_stool")

    wood = Material("oak_wood", rgba=(0.76, 0.63, 0.43, 1.0))
    seat_part = model.part("seat")
    seat_part.visual(
        mesh_from_cadquery(_seat_shape(), "seat", unit_scale=1.0),
        material=wood,
        name="seat_panel",
    )

    leg_mesh = mesh_from_cadquery(_leg_shape(), "leg", unit_scale=1.0)
    leg_positions = [
        (-LEG_SPREAD_X, -LEG_SPREAD_Y),
        (LEG_SPREAD_X, -LEG_SPREAD_Y),
        (-LEG_SPREAD_X, LEG_SPREAD_Y),
        (LEG_SPREAD_X, LEG_SPREAD_Y),
    ]
    for index, (x, y) in enumerate(leg_positions):
        leg = model.part(f"leg_{index}")
        leg.visual(leg_mesh, material=wood, name="leg_body")
        model.articulation(
            f"seat_to_leg_{index}",
            "fixed",
            parent=seat_part,
            child=leg,
            origin=Origin(xyz=(x, y, 0.0)),
        )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    seat = object_model.get_part("seat")
    legs = [object_model.get_part(f"leg_{index}") for index in range(4)]

    for index, leg in enumerate(legs):
        ctx.expect_contact(
            leg,
            seat,
            name=f"leg_{index}_meets_seat",
        )

    return ctx.report()


object_model = build_object_model()