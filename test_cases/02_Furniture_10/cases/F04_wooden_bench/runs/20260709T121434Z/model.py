from __future__ import annotations

import cadquery as cq

from sdk import ArticulatedObject, Material, Origin, TestContext, TestReport, mesh_from_cadquery


WOOD = Material("wood_oak", color=(0.76, 0.60, 0.39, 1.0))


MM = 0.001
SEAT_W = 1000.0
SEAT_D = 300.0
SEAT_T = 30.0
BENCH_H = 440.0
LEG_W = 40.0
LEG_T = 30.0
FRAME_INSET = 95.0
FRAME_TOP_RAIL_T = 30.0
FRAME_CLEAR_W = 210.0
STRETCHER_W = 50.0
STRETCHER_T = 28.0
FLOOR_CLEARANCE = 85.0


def mm_shape_to_mesh(shape: cq.Workplane | cq.Shape, name: str):
    return mesh_from_cadquery(shape, name, unit_scale=MM)


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="wooden_bench")

    seat_part = model.part("seat")
    seat = (
        cq.Workplane("XY")
        .box(SEAT_W, SEAT_D, SEAT_T)
        .edges("|X and >Z").fillet(14.0)
        .edges("|X and <Z").fillet(6.0)
        .translate((0, 0, BENCH_H - SEAT_T / 2.0))
    )
    seat_part.visual(
        mm_shape_to_mesh(seat, "seat"),
        material=WOOD,
        name="seat",
    )

    top_rail_z = BENCH_H - SEAT_T - FRAME_TOP_RAIL_T / 2.0
    leg_bottom_z = 0.0
    rail_y = SEAT_D / 2.0 - LEG_T / 2.0 - 18.0
    leg_spread = 22.0

    frame_parts = []
    for side, x_sign in (("frame_0", -1.0), ("frame_1", 1.0)):
        frame_part = model.part(side)
        frame_parts.append(frame_part)
        x_center = x_sign * (SEAT_W / 2.0 - FRAME_INSET)
        x0 = x_center - FRAME_CLEAR_W / 2.0
        x1 = x_center + FRAME_CLEAR_W / 2.0
        y0 = rail_y - LEG_T / 2.0

        front_leg = (
            cq.Workplane("XZ")
            .center(x0, 0)
            .polyline(
                [
                    (0.0, leg_bottom_z),
                    (-leg_spread, leg_bottom_z),
                    (-10.0, top_rail_z + FRAME_TOP_RAIL_T / 2.0),
                    (LEG_W - 10.0, top_rail_z + FRAME_TOP_RAIL_T / 2.0),
                    (LEG_W, leg_bottom_z),
                ]
            )
            .close()
            .extrude(LEG_T)
            .translate((0, y0, 0))
            .edges("|Y").fillet(4.0)
            .edges("<Z").fillet(3.0)
        )
        rear_leg = (
            cq.Workplane("XZ")
            .center(x1, 0)
            .polyline(
                [
                    (0.0, leg_bottom_z),
                    (leg_spread, leg_bottom_z),
                    (10.0, top_rail_z + FRAME_TOP_RAIL_T / 2.0),
                    (-LEG_W + 10.0, top_rail_z + FRAME_TOP_RAIL_T / 2.0),
                    (-LEG_W, leg_bottom_z),
                ]
            )
            .close()
            .extrude(LEG_T)
            .translate((0, y0, 0))
            .edges("|Y").fillet(4.0)
            .edges("<Z").fillet(3.0)
        )
        top_rail = (
            cq.Workplane("XY")
            .box(FRAME_CLEAR_W + LEG_W, LEG_T, FRAME_TOP_RAIL_T)
            .translate((x_center, rail_y, top_rail_z))
            .edges("|Y").fillet(4.0)
        )
        brace_z0 = FLOOR_CLEARANCE + 45.0
        brace_z1 = top_rail_z - 25.0
        front_brace = (
            cq.Workplane("XZ")
            .polyline(
                [
                    (x_center - FRAME_CLEAR_W / 2.0 + 18.0, brace_z0),
                    (x_center - FRAME_CLEAR_W / 2.0 + 52.0, brace_z0),
                    (x_center + FRAME_CLEAR_W / 2.0 - 18.0, brace_z1),
                    (x_center + FRAME_CLEAR_W / 2.0 - 52.0, brace_z1),
                ]
            )
            .close()
            .extrude(LEG_T)
            .translate((0, y0, 0))
            .edges("|Y").fillet(3.0)
        )
        rear_brace = front_brace.translate((0, LEG_T, 0))
        frame_part.visual(
            mm_shape_to_mesh(front_leg, f"{side}_front_leg"),
            material=WOOD,
            name="front_leg",
        )
        frame_part.visual(
            mm_shape_to_mesh(rear_leg, f"{side}_rear_leg"),
            material=WOOD,
            name="rear_leg",
        )
        frame_part.visual(
            mm_shape_to_mesh(top_rail, f"{side}_top_rail"),
            material=WOOD,
            name="top_rail",
        )
        frame_part.visual(
            mm_shape_to_mesh(front_brace, f"{side}_front_brace"),
            material=WOOD,
            name="front_brace",
        )
        frame_part.visual(
            mm_shape_to_mesh(rear_brace, f"{side}_rear_brace"),
            material=WOOD,
            name="rear_brace",
        )

    stretcher_part = model.part("stretcher")
    stretcher = (
        cq.Workplane("XY")
        .box(SEAT_W - 2 * (FRAME_INSET + 16.0), 30.0, STRETCHER_T)
        .edges("|X").fillet(4.0)
        .translate((0, rail_y, FLOOR_CLEARANCE + STRETCHER_T / 2.0))
    )
    stretcher_part.visual(
        mm_shape_to_mesh(stretcher, "stretcher"),
        material=WOOD,
        name="stretcher",
    )

    for frame_part in frame_parts:
        model.articulation(
            f"seat_to_{frame_part.name}",
            "fixed",
            parent=seat_part,
            child=frame_part,
            origin=Origin(),
        )
    model.articulation(
        "seat_to_stretcher",
        "fixed",
        parent=seat_part,
        child=stretcher_part,
        origin=Origin(),
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    return ctx.report()


object_model = build_object_model()