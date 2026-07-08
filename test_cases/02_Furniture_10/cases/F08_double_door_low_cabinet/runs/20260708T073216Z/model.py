from __future__ import annotations

import math

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


# Cabinet design dimensions are expressed in metres (SDK units); values match the
# requested millimetre envelope: 800 W x 400 D x 600 H.
W = 800 * MM
D = 400 * MM
H = 600 * MM
FOOT_H = 40 * MM
BOARD = 18 * MM
DOOR_T = 16 * MM
DOOR_BOTTOM = 75 * MM
DOOR_H = 490 * MM
SIDE_REVEAL = 12 * MM
CENTER_GAP = 4 * MM
DOOR_W = (W - 2.0 * SIDE_REVEAL - CENTER_GAP) / 2.0
LEFT_HINGE_X = -W / 2.0 + SIDE_REVEAL
RIGHT_HINGE_X = W / 2.0 - SIDE_REVEAL
FRONT_Y = -D / 2.0


def _rounded_box(size: tuple[float, float, float], radius: float) -> cq.Workplane:
    """Return a modestly filleted rectangular solid centered on the origin."""
    solid = cq.Workplane("XY").box(*size)
    if radius > 0.0:
        solid = solid.edges().fillet(radius)
    return solid


def _at(shape: cq.Workplane, xyz: tuple[float, float, float]) -> cq.Workplane:
    return shape.translate(xyz)


def _cabinet_carcass() -> cq.Workplane:
    """Board-built enclosure with back, shelf, recessed short feet, and rounded edges."""
    r_outer = 3 * MM
    r_inner = 1.5 * MM
    case_h = H - FOOT_H
    case_z = FOOT_H + case_h / 2.0

    left_side = _at(
        _rounded_box((BOARD, D, case_h), r_outer),
        (-W / 2.0 + BOARD / 2.0, 0.0, case_z),
    )
    right_side = _at(
        _rounded_box((BOARD, D, case_h), r_outer),
        (W / 2.0 - BOARD / 2.0, 0.0, case_z),
    )
    top = _at(
        _rounded_box((W, D, BOARD), r_outer),
        (0.0, 0.0, H - BOARD / 2.0),
    )
    bottom = _at(
        _rounded_box((W, D, BOARD), r_outer),
        (0.0, 0.0, FOOT_H + BOARD / 2.0),
    )
    back = _at(
        _rounded_box((W - 2.0 * BOARD, BOARD, case_h - 2.0 * BOARD), r_inner),
        (0.0, D / 2.0 - BOARD / 2.0, FOOT_H + case_h / 2.0),
    )

    # One full-width internal shelf set just above mid-height, stopped behind the
    # closed doors and let into the sides/back for a manufacturable support path.
    shelf_t = 16 * MM
    shelf = _at(
        _rounded_box((W - 2.0 * BOARD + 2 * MM, D - 3.0 * BOARD, shelf_t), r_inner),
        (0.0, BOARD / 2.0, 315 * MM),
    )

    carcass = left_side.union(right_side).union(top).union(bottom).union(back).union(shelf)

    foot_size = (42 * MM, 42 * MM, FOOT_H + 3 * MM)
    for x in (-W / 2.0 + 72 * MM, W / 2.0 - 72 * MM):
        for y in (FRONT_Y + 58 * MM, D / 2.0 - 58 * MM):
            foot = _at(_rounded_box(foot_size, 2 * MM), (x, y, foot_size[2] / 2.0))
            carcass = carcass.union(foot)

    # A shallow front underside rail ties the feet visually to the base without
    # adding unrelated decoration.
    rail = _at(
        _rounded_box((W - 90 * MM, 18 * MM, 34 * MM), 2 * MM),
        (0.0, FRONT_Y + 18 * MM, FOOT_H / 2.0 + 4 * MM),
    )
    carcass = carcass.union(rail)
    return carcass


def _door_panel(extents_positive_x: bool) -> cq.Workplane:
    """Door slab in a hinge-line local frame; one side extends +X, the other -X."""
    x_center = DOOR_W / 2.0 if extents_positive_x else -DOOR_W / 2.0
    return _at(
        _rounded_box((DOOR_W, DOOR_T, DOOR_H), 3 * MM),
        (x_center, -DOOR_T / 2.0, DOOR_H / 2.0),
    )


def _vertical_pull(extents_positive_x: bool) -> cq.Workplane:
    """Small vertical front pull near the meeting edge, with two proud mounting pads."""
    sign = 1.0 if extents_positive_x else -1.0
    pull_x = sign * (DOOR_W - 35 * MM)
    pull_h = 125 * MM
    bar = _at(
        _rounded_box((11 * MM, 12 * MM, pull_h), 4 * MM),
        (pull_x, -DOOR_T - 5.5 * MM, DOOR_H / 2.0),
    )
    for z in (DOOR_H / 2.0 - 43 * MM, DOOR_H / 2.0 + 43 * MM):
        pad = _at(
            _rounded_box((16 * MM, 5 * MM, 22 * MM), 2 * MM),
            (pull_x, -DOOR_T - 1.5 * MM, z),
        )
        bar = bar.union(pad)
    return bar


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="low_storage_cabinet")

    wood = Material("warm_oak", rgba=(0.72, 0.50, 0.28, 1.0))
    pull_mat = Material("slightly_darker_wood", rgba=(0.50, 0.33, 0.17, 1.0))

    cabinet = model.part("enclosure")
    cabinet.visual(
        mesh_from_cadquery(_cabinet_carcass(), "enclosure_boards", tolerance=0.0006, angular_tolerance=0.08),
        material=wood,
        name="enclosure_boards",
    )

    left_door = model.part("door_0")
    left_door.visual(
        mesh_from_cadquery(_door_panel(True), "door_0_panel", tolerance=0.0005, angular_tolerance=0.08),
        material=wood,
        name="door_panel",
    )
    left_door.visual(
        mesh_from_cadquery(_vertical_pull(True), "door_0_pull", tolerance=0.0005, angular_tolerance=0.08),
        material=pull_mat,
        name="vertical_pull",
    )

    right_door = model.part("door_1")
    right_door.visual(
        mesh_from_cadquery(_door_panel(False), "door_1_panel", tolerance=0.0005, angular_tolerance=0.08),
        material=wood,
        name="door_panel",
    )
    right_door.visual(
        mesh_from_cadquery(_vertical_pull(False), "door_1_pull", tolerance=0.0005, angular_tolerance=0.08),
        material=pull_mat,
        name="vertical_pull",
    )

    left_hinge = model.articulation(
        "enclosure_to_door_0",
        ArticulationType.REVOLUTE,
        parent=cabinet,
        child=left_door,
        origin=Origin(xyz=(LEFT_HINGE_X, FRONT_Y, DOOR_BOTTOM)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=1.2, lower=0.0, upper=math.radians(105.0)),
    )
    right_hinge = model.articulation(
        "enclosure_to_door_1",
        ArticulationType.REVOLUTE,
        parent=cabinet,
        child=right_door,
        origin=Origin(xyz=(RIGHT_HINGE_X, FRONT_Y, DOOR_BOTTOM)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=1.2, lower=0.0, upper=math.radians(105.0)),
    )
    left_hinge.meta["description"] = "Concealed left-side cabinet hinge; q=0 is the closed reference pose."
    right_hinge.meta["description"] = "Concealed right-side cabinet hinge; q=0 is the closed reference pose."

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    cabinet = object_model.get_part("enclosure")
    door_0 = object_model.get_part("door_0")
    door_1 = object_model.get_part("door_1")
    hinge_0 = object_model.get_articulation("enclosure_to_door_0")
    hinge_1 = object_model.get_articulation("enclosure_to_door_1")

    aabb = ctx.part_world_aabb(cabinet)
    if aabb is not None:
        lo, hi = aabb
        dims = (hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2])
        ctx.check(
            "enclosure matches 800 by 400 by 600 mm envelope",
            abs(dims[0] - W) < 0.006 and abs(dims[1] - D) < 0.006 and abs(dims[2] - H) < 0.006,
            details=f"dims={dims}",
        )

    with ctx.pose({hinge_0: 0.0, hinge_1: 0.0}):
        ctx.expect_gap(
            door_1,
            door_0,
            axis="x",
            min_gap=0.003,
            max_gap=0.006,
            positive_elem="door_panel",
            negative_elem="door_panel",
            name="closed doors keep a narrow central reveal",
        )

    closed_box_0 = ctx.part_world_aabb(door_0)
    closed_box_1 = ctx.part_world_aabb(door_1)
    with ctx.pose({hinge_0: math.radians(70.0), hinge_1: math.radians(70.0)}):
        open_box_0 = ctx.part_world_aabb(door_0)
        open_box_1 = ctx.part_world_aabb(door_1)

    ctx.check(
        "both doors swing outward from the front",
        closed_box_0 is not None
        and closed_box_1 is not None
        and open_box_0 is not None
        and open_box_1 is not None
        and open_box_0[0][1] < closed_box_0[0][1] - 0.05
        and open_box_1[0][1] < closed_box_1[0][1] - 0.05,
        details=f"closed=({closed_box_0}, {closed_box_1}), open=({open_box_0}, {open_box_1})",
    )

    return ctx.report()


object_model = build_object_model()
