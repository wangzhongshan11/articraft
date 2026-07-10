from __future__ import annotations

import math

import cadquery as cq

from sdk import ArticulatedObject, Material, Origin, TestContext, TestReport, mesh_from_cadquery


def _wood_material(name: str = "oak") -> Material:
    return Material(name=name, color=(0.76, 0.62, 0.42, 1.0))


UPHOLSTERY = Material(name="seat_fabric", color=(0.70, 0.70, 0.70, 1.0))
WOOD = _wood_material()


SEAT_W = 0.420
SEAT_D = 0.440
SEAT_T = 0.028
SEAT_Z = 0.450
TOP_Z = SEAT_Z + SEAT_T
CHAIR_H = 0.880
OUTER_W = 0.420
OUTER_D = 0.480
LEG_W = 0.032
LEG_D = 0.032
FRONT_LEG_H = SEAT_Z
BACK_POST_RISE = CHAIR_H - TOP_Z
POST_TILT_DEG = 4.0
BACKREST_W = 0.340
BACKREST_H = 0.130
BACKREST_T = 0.022
BACKREST_BOTTOM_Z = 0.690
SIDE_STRETCHER_Z = 0.170
SIDE_STRETCHER_H = 0.025
SIDE_STRETCHER_T = 0.020
APRON_TOP_Z = SEAT_Z - 0.008
APRON_H = 0.055
APRON_T = 0.020
CUSHION_W = 0.376
CUSHION_D = 0.396
CUSHION_T = 0.022
CUSHION_Z = SEAT_Z + SEAT_T + CUSHION_T / 2.0


LEG_X = OUTER_W / 2.0 - LEG_W / 2.0
LEG_Y = OUTER_D / 2.0 - LEG_D / 2.0
SEAT_BOTTOM_Z = SEAT_Z + SEAT_T / 2.0
POST_TOP_Z = TOP_Z + BACK_POST_RISE / 2.0
POST_Y_SHIFT = math.tan(math.radians(POST_TILT_DEG)) * BACK_POST_RISE / 2.0
POST_REAR_FACE_Y = -OUTER_D / 2.0 + LEG_D / 2.0 - POST_Y_SHIFT
BACKREST_CENTER_Y = POST_REAR_FACE_Y + BACKREST_T / 2.0 + 0.002
BACKREST_CENTER_Z = BACKREST_BOTTOM_Z + BACKREST_H / 2.0



def _rounded_box(size_x: float, size_y: float, size_z: float, fillet: float) -> cq.Workplane:
    return cq.Workplane("XY").box(size_x, size_y, size_z).edges("|Z").fillet(fillet)



def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="wooden_dining_chair")
    chair = model.part("chair")

    seat_panel = (
        cq.Workplane("XY")
        .box(SEAT_W, SEAT_D, SEAT_T)
        .edges("|Z")
        .fillet(0.010)
        .translate((0.0, 0.0, SEAT_BOTTOM_Z))
    )

    cushion = (
        cq.Workplane("XY")
        .box(CUSHION_W, CUSHION_D, CUSHION_T)
        .edges("|Z")
        .fillet(0.012)
        .translate((0.0, 0.0, CUSHION_Z))
    )

    front_leg_r = _rounded_box(LEG_W, LEG_D, FRONT_LEG_H, 0.004).translate((LEG_X, LEG_Y, FRONT_LEG_H / 2.0))
    front_leg_l = _rounded_box(LEG_W, LEG_D, FRONT_LEG_H, 0.004).translate((-LEG_X, LEG_Y, FRONT_LEG_H / 2.0))

    rear_leg_r = (
        _rounded_box(LEG_W, LEG_D, FRONT_LEG_H + BACK_POST_RISE, 0.004)
        .rotate((0, 0, TOP_Z), (1, 0, TOP_Z), -POST_TILT_DEG)
        .translate((LEG_X, -LEG_Y - POST_Y_SHIFT, (FRONT_LEG_H + BACK_POST_RISE) / 2.0))
    )
    rear_leg_l = (
        _rounded_box(LEG_W, LEG_D, FRONT_LEG_H + BACK_POST_RISE, 0.004)
        .rotate((0, 0, TOP_Z), (1, 0, TOP_Z), -POST_TILT_DEG)
        .translate((-LEG_X, -LEG_Y - POST_Y_SHIFT, (FRONT_LEG_H + BACK_POST_RISE) / 2.0))
    )

    left_stretcher = _rounded_box(LEG_W, OUTER_D - 2 * LEG_D, SIDE_STRETCHER_H, 0.003).translate((LEG_X, 0.0, SIDE_STRETCHER_Z))
    right_stretcher = _rounded_box(LEG_W, OUTER_D - 2 * LEG_D, SIDE_STRETCHER_H, 0.003).translate((-LEG_X, 0.0, SIDE_STRETCHER_Z))

    front_apron = _rounded_box(SEAT_W - 2 * LEG_W, APRON_T, APRON_H, 0.003).translate(
        (0.0, OUTER_D / 2.0 - LEG_D - APRON_T / 2.0, APRON_TOP_Z - APRON_H / 2.0)
    )
    rear_apron = _rounded_box(SEAT_W - 2 * LEG_W, APRON_T, APRON_H, 0.003).translate(
        (0.0, -OUTER_D / 2.0 + LEG_D + APRON_T / 2.0, APRON_TOP_Z - APRON_H / 2.0)
    )
    left_apron = _rounded_box(APRON_T, OUTER_D - 2 * LEG_D - 2 * APRON_T, APRON_H, 0.003).translate(
        (OUTER_W / 2.0 - LEG_W - APRON_T / 2.0, 0.0, APRON_TOP_Z - APRON_H / 2.0)
    )
    right_apron = _rounded_box(APRON_T, OUTER_D - 2 * LEG_D - 2 * APRON_T, APRON_H, 0.003).translate(
        (-OUTER_W / 2.0 + LEG_W + APRON_T / 2.0, 0.0, APRON_TOP_Z - APRON_H / 2.0)
    )

    backrest = (
        cq.Workplane("XY")
        .box(BACKREST_W, BACKREST_T, BACKREST_H)
        .edges("|X")
        .fillet(0.008)
        .rotate((0, 0, 0), (1, 0, 0), -POST_TILT_DEG)
        .translate((0.0, BACKREST_CENTER_Y, BACKREST_CENTER_Z))
    )

    frame = seat_panel
    for piece in [
        front_leg_r,
        front_leg_l,
        rear_leg_r,
        rear_leg_l,
        left_stretcher,
        right_stretcher,
        front_apron,
        rear_apron,
        left_apron,
        right_apron,
        backrest,
    ]:
        frame = frame.union(piece)

    chair.visual(mesh_from_cadquery(frame, "chair_frame"), material=WOOD, name="chair_frame")
    chair.visual(mesh_from_cadquery(seat_panel, "seat_panel"), material=WOOD, name="seat_panel")
    chair.visual(mesh_from_cadquery(cushion, "seat_cushion"), material=UPHOLSTERY, name="seat_cushion")

    return model



def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    chair = object_model.get_part("chair")

    ctx.expect_gap(
        chair,
        chair,
        axis="z",
        positive_elem="seat_cushion",
        negative_elem="seat_panel",
        min_gap=0.0,
        max_gap=0.001,
        name="cushion sits on seat panel",
    )
    ctx.expect_overlap(
        chair,
        chair,
        axes="xy",
        elem_a="seat_cushion",
        elem_b="seat_panel",
        min_overlap=0.30,
        name="cushion overlaps seat footprint",
    )

    return ctx.report()


object_model = build_object_model()