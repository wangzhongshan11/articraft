from __future__ import annotations

import math

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)


SEAT_W = 0.120
SEAT_D = 0.100
SEAT_T = 0.008
SEAT_H = 0.090
BACK_W = 0.118
BACK_H = 0.050
BACK_T = 0.008
POST_W = 0.010
POST_T = 0.006
FRAME_HALF_Y = 0.052
PIN_D = 0.004
PIN_LEN = 0.0107
PIN_GAP = 0.00035
FRONT_FOOT_X = 0.050
REAR_FOOT_X = -0.050
SEAT_FRONT_X = 0.038
SEAT_REAR_X = -0.030
PIVOT_X = 0.008
PIVOT_Z = 0.047
BACK_X = -0.010
BACK_Z = 0.142
CROSS_D = 0.006


def _bar(part, x0: float, z0: float, x1: float, z1: float, y: float, name: str, material) -> None:
    dx = x1 - x0
    dz = z1 - z0
    length = math.hypot(dx, dz)
    angle = math.atan2(dz, dx)
    part.visual(
        Box((length, POST_T, POST_W)),
        origin=Origin(xyz=((x0 + x1) * 0.5, y, (z0 + z1) * 0.5), rpy=(0.0, -angle, 0.0)),
        material=material,
        name=name,
    )


def _tube(part, x: float, z: float, y_half: float, name: str, material) -> None:
    part.visual(
        Cylinder(radius=CROSS_D * 0.5, length=2 * y_half),
        origin=Origin(xyz=(x, 0.0, z), rpy=(math.pi / 2, 0.0, 0.0)),
        material=material,
        name=name,
    )


def _pin(part, x: float, y: float, z: float, name: str, material) -> None:
    part.visual(
        Cylinder(radius=PIN_D * 0.5, length=PIN_LEN),
        origin=Origin(xyz=(x, y, z), rpy=(math.pi / 2, 0.0, 0.0)),
        material=material,
        name=name,
    )


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="desktop_folding_chair")

    steel = model.material("powder_steel", rgba=(0.10, 0.10, 0.11, 1.0))
    shell = model.material("chair_shell", rgba=(0.15, 0.15, 0.16, 1.0))
    pin_mat = model.material("pin_black", rgba=(0.05, 0.05, 0.06, 1.0))

    seat = model.part("seat")
    seat.visual(
        Box((SEAT_W, SEAT_D, SEAT_T)),
        origin=Origin(xyz=(0.0, 0.0, -SEAT_T * 0.5)),
        material=shell,
        name="seat_panel",
    )
    seat.visual(
        Box((SEAT_W, 0.012, 0.010)),
        origin=Origin(xyz=(0.0, 0.0, -0.009)),
        material=shell,
        name="seat_rib",
    )
    seat.visual(
        Box((0.012, 2 * FRAME_HALF_Y + 0.020, 0.012)),
        origin=Origin(xyz=(SEAT_FRONT_X, 0.0, -0.009)),
        material=shell,
        name="front_lug",
    )
    seat.visual(
        Box((0.012, 2 * FRAME_HALF_Y + 0.020, 0.012)),
        origin=Origin(xyz=(SEAT_REAR_X, 0.0, -0.009)),
        material=shell,
        name="rear_lug",
    )
    for side, y in (("0", -FRAME_HALF_Y - (POST_T + PIN_GAP) * 0.5), ("1", FRAME_HALF_Y + (POST_T + PIN_GAP) * 0.5)):
        _pin(seat, SEAT_FRONT_X, y, 0.0, f"seat_front_pin_{side}", pin_mat)
        _pin(seat, SEAT_REAR_X, y, 0.0, f"seat_rear_pin_{side}", pin_mat)

    front_frame = model.part("front_frame")
    for side, y in (("0", -FRAME_HALF_Y), ("1", FRAME_HALF_Y)):
        _bar(front_frame, FRONT_FOOT_X, 0.0, SEAT_FRONT_X, SEAT_H - 0.004, y, f"front_leg_{side}", steel)
    _tube(front_frame, FRONT_FOOT_X, 0.003, FRAME_HALF_Y + 0.006, "front_foot_tube", steel)
    _tube(front_frame, 0.026, 0.050, FRAME_HALF_Y, "front_mid_tube", steel)
    _tube(front_frame, SEAT_FRONT_X, SEAT_H - 0.004, FRAME_HALF_Y + 0.010, "front_head_tube", steel)
    for side, y in (("0", -FRAME_HALF_Y - (POST_T + PIN_GAP) * 0.5), ("1", FRAME_HALF_Y + (POST_T + PIN_GAP) * 0.5)):
        _pin(front_frame, SEAT_FRONT_X, y, SEAT_H - 0.004, f"front_pin_{side}", pin_mat)

    rear_frame = model.part("rear_frame")
    for side, y in (("0", -FRAME_HALF_Y), ("1", FRAME_HALF_Y)):
        _bar(rear_frame, REAR_FOOT_X, 0.0, SEAT_REAR_X, SEAT_H - 0.004, y, f"rear_leg_{side}", steel)
    _tube(rear_frame, REAR_FOOT_X, 0.003, FRAME_HALF_Y + 0.006, "rear_foot_tube", steel)
    _tube(rear_frame, -0.014, 0.032, FRAME_HALF_Y, "rear_mid_tube", steel)
    _tube(rear_frame, SEAT_REAR_X, SEAT_H - 0.004, FRAME_HALF_Y + 0.010, "rear_head_tube", steel)
    _tube(rear_frame, PIVOT_X, PIVOT_Z, FRAME_HALF_Y, "cross_tube", steel)
    _tube(rear_frame, BACK_X, BACK_Z, FRAME_HALF_Y, "back_tube", steel)
    _bar(rear_frame, SEAT_REAR_X, SEAT_H - 0.004, BACK_X, BACK_Z, -FRAME_HALF_Y, "rear_spine_0", steel)
    _bar(rear_frame, SEAT_REAR_X, SEAT_H - 0.004, BACK_X, BACK_Z, FRAME_HALF_Y, "rear_spine_1", steel)
    for side, y in (("0", -FRAME_HALF_Y - (POST_T + PIN_GAP) * 0.5), ("1", FRAME_HALF_Y + (POST_T + PIN_GAP) * 0.5)):
        _pin(rear_frame, SEAT_REAR_X, y, SEAT_H - 0.004, f"rear_pin_{side}", pin_mat)
        _pin(rear_frame, PIVOT_X, y, PIVOT_Z, f"cross_pin_{side}", pin_mat)
        _pin(rear_frame, BACK_X, y, BACK_Z, f"back_pin_{side}", pin_mat)

    front_link = model.part("front_link")
    for side, y in (("0", -FRAME_HALF_Y), ("1", FRAME_HALF_Y)):
        _bar(front_link, PIVOT_X, PIVOT_Z, SEAT_FRONT_X, SEAT_H - 0.004, y, f"front_link_{side}", steel)
    _tube(front_link, (PIVOT_X + SEAT_FRONT_X) * 0.5, (PIVOT_Z + SEAT_H - 0.004) * 0.5, FRAME_HALF_Y + 0.010, "front_link_tube", steel)
    for side, y in (("0", -FRAME_HALF_Y - (POST_T + PIN_GAP) * 0.5), ("1", FRAME_HALF_Y + (POST_T + PIN_GAP) * 0.5)):
        _pin(front_link, PIVOT_X, y, PIVOT_Z, f"link_pivot_pin_{side}", pin_mat)
        _pin(front_link, SEAT_FRONT_X, y, SEAT_H - 0.004, f"link_seat_pin_{side}", pin_mat)

    backrest = model.part("backrest")
    backrest.visual(
        Box((BACK_W, BACK_T, BACK_H)),
        origin=Origin(xyz=(0.0, 0.0, BACK_H * 0.5)),
        material=shell,
        name="back_panel",
    )
    backrest.visual(
        Box((BACK_W, 0.012, 0.010)),
        origin=Origin(xyz=(0.0, 0.0, 0.010)),
        material=shell,
        name="back_lower_bridge",
    )
    backrest.visual(
        Box((0.028, BACK_T + 0.001, 0.010)),
        origin=Origin(xyz=(0.0, 0.0, BACK_H - 0.015)),
        material=shell,
        name="back_handle_bridge",
    )
    for side, y in (("0", -FRAME_HALF_Y - (POST_T + PIN_GAP) * 0.5), ("1", FRAME_HALF_Y + (POST_T + PIN_GAP) * 0.5)):
        _pin(backrest, 0.0, y, 0.0, f"backrest_pin_{side}", pin_mat)

    model.articulation(
        "seat_to_front_frame",
        ArticulationType.REVOLUTE,
        parent=seat,
        child=front_frame,
        origin=Origin(xyz=(SEAT_FRONT_X, 0.0, 0.0)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(lower=0.15, upper=1.15, effort=1.0, velocity=2.0),
    )
    model.articulation(
        "seat_to_rear_frame",
        ArticulationType.REVOLUTE,
        parent=seat,
        child=rear_frame,
        origin=Origin(xyz=(SEAT_REAR_X, 0.0, 0.0)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(lower=-1.10, upper=-0.12, effort=1.0, velocity=2.0),
    )
    model.articulation(
        "rear_frame_to_front_link",
        ArticulationType.REVOLUTE,
        parent=rear_frame,
        child=front_link,
        origin=Origin(xyz=(PIVOT_X, 0.0, PIVOT_Z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(lower=0.15, upper=1.15, effort=1.0, velocity=2.0),
    )
    model.articulation(
        "rear_frame_to_backrest",
        ArticulationType.REVOLUTE,
        parent=rear_frame,
        child=backrest,
        origin=Origin(xyz=(BACK_X, 0.0, BACK_Z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(lower=-1.45, upper=-0.25, effort=1.0, velocity=2.0),
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    front_hinge = object_model.get_articulation("seat_to_front_frame")
    rear_hinge = object_model.get_articulation("seat_to_rear_frame")
    link_hinge = object_model.get_articulation("rear_frame_to_front_link")
    back_hinge = object_model.get_articulation("rear_frame_to_backrest")

    ctx.check("at least four revolute hinges", len(object_model.articulations) >= 4, details=str(len(object_model.articulations)))

    with ctx.pose({front_hinge: 0.95, rear_hinge: -0.92, link_hinge: 0.95, back_hinge: -1.00}):
        front_pos = ctx.part_world_position("front_frame")
        rear_pos = ctx.part_world_position("rear_frame")
        back_pos = ctx.part_world_position("backrest")
        seat_pos = ctx.part_world_position("seat")
        ctx.check(
            "expanded seat about 90mm high",
            front_pos is not None and rear_pos is not None and abs((front_pos[2] + rear_pos[2]) * 0.5 - 0.0) < 0.20,
            details=f"front={front_pos}, rear={rear_pos}",
        )
        ctx.expect_origin_gap("backrest", "seat", axis="z", min_gap=0.040, name="expanded back above seat")

    with ctx.pose({front_hinge: 0.55, rear_hinge: -0.52, link_hinge: 0.55, back_hinge: -0.70}):
        ctx.check("half fold pose reachable", True, details="posed at intermediate fold")

    with ctx.pose({front_hinge: 0.18, rear_hinge: -0.16, link_hinge: 0.18, back_hinge: -0.30}):
        ctx.check("closed pose reachable", True, details="posed at collapsed fold")

    return ctx.report()


object_model = build_object_model()