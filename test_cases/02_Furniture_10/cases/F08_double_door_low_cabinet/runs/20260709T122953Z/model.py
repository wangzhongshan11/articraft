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
W = 800 * MM
D = 400 * MM
H = 600 * MM
PANEL = 18 * MM
BACK = 6 * MM
FOOT_H = 40 * MM
FOOT_W = 28 * MM
DOOR_GAP = 2 * MM
REVEAL = 2 * MM
SHELF_Z = 290 * MM
HANDLE_R = 5 * MM
HANDLE_H = 120 * MM
HANDLE_PROJ = 26 * MM
HANDLE_CLEAR = 18 * MM
HINGE_INSET = 55 * MM
ROUND = 6 * MM
WOOD = (0.72, 0.56, 0.35, 1.0)
DARK = (0.18, 0.16, 0.14, 1.0)


def board_box(x: float, y: float, z: float, fillet: float = 0.0) -> cq.Workplane:
    solid = cq.Workplane("XY").box(x, y, z)
    if fillet > 0:
        solid = solid.edges().fillet(fillet)
    return solid


def build_cabinet_shell() -> cq.Workplane:
    outer = cq.Workplane("XY").box(W, D, H)
    inner = (
        cq.Workplane("XY")
        .box(W - 2 * PANEL, D - PANEL - BACK, H - 2 * PANEL)
        .translate((0, -PANEL / 2 + BACK / 2, 0))
    )
    shell = outer.cut(inner)

    shelf = (
        cq.Workplane("XY")
        .box(W - 2 * PANEL, D - PANEL - BACK, PANEL)
        .translate((0, -PANEL / 2 + BACK / 2, -H / 2 + PANEL + SHELF_Z))
    )
    shell = shell.union(shelf)

    opening = (
        cq.Workplane("XY")
        .box(W - 2 * PANEL, PANEL + 1e-4, H - 2 * PANEL)
        .translate((0, D / 2 - PANEL / 2, 0))
    )
    shell = shell.cut(opening)

    shell = shell.edges("|Z").fillet(ROUND)
    shell = shell.edges(">Z").fillet(ROUND)
    return shell


def build_door_panel(width: float) -> cq.Workplane:
    panel = cq.Workplane("XY").box(width, PANEL, H - 2 * REVEAL)
    panel = panel.edges("|Z").fillet(4 * MM)
    panel = panel.edges("<Y or >Y").fillet(1.2 * MM)
    return panel


def build_handle() -> cq.Workplane:
    stem_offset = HANDLE_PROJ / 2 - HANDLE_R
    bar = cq.Workplane("YZ").cylinder(HANDLE_H, HANDLE_R).rotate((0, 0, 0), (0, 1, 0), 90)
    post_top = cq.Workplane("XY").cylinder(HANDLE_CLEAR, HANDLE_R * 0.8).translate((0, 0, HANDLE_H / 2 - 18 * MM))
    post_bottom = cq.Workplane("XY").cylinder(HANDLE_CLEAR, HANDLE_R * 0.8).translate((0, 0, -HANDLE_H / 2 + 18 * MM))
    handle = bar.translate((stem_offset, 0, 0)).union(post_top).union(post_bottom)
    return handle


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="low_storage_cabinet")

    wood = model.material("wood", rgba=WOOD)
    metal = model.material("metal", rgba=DARK)

    cabinet = model.part("cabinet")
    cabinet.visual(
        mesh_from_cadquery(build_cabinet_shell(), "cabinet_shell", unit_scale=1.0),
        material=wood,
        name="shell",
    )

    foot_positions = [
        (-W / 2 + 55 * MM, -D / 2 + 50 * MM, -H / 2 - FOOT_H / 2),
        (W / 2 - 55 * MM, -D / 2 + 50 * MM, -H / 2 - FOOT_H / 2),
        (-W / 2 + 55 * MM, D / 2 - 50 * MM, -H / 2 - FOOT_H / 2),
        (W / 2 - 55 * MM, D / 2 - 50 * MM, -H / 2 - FOOT_H / 2),
    ]
    for i, pos in enumerate(foot_positions):
        cabinet.visual(
            mesh_from_cadquery(board_box(FOOT_W, FOOT_W, FOOT_H, fillet=3 * MM), f"foot_{i}", unit_scale=1.0),
            origin=Origin(xyz=pos),
            material=metal,
            name=f"foot_{i}",
        )

    clear_width = W - 2 * PANEL - 2 * REVEAL - DOOR_GAP
    door_width = clear_width / 2
    door_height = H - 2 * REVEAL
    door_y = D / 2 + PANEL / 2
    hinge_z = -door_height / 2

    door_0 = model.part("door_0")
    door_0.visual(
        mesh_from_cadquery(build_door_panel(door_width), "door_0_panel", unit_scale=1.0),
        origin=Origin(xyz=(door_width / 2, 0, 0)),
        material=wood,
        name="panel",
    )
    door_0.visual(
        mesh_from_cadquery(build_handle(), "door_0_pull", unit_scale=1.0),
        origin=Origin(xyz=(door_width - 32 * MM, HANDLE_CLEAR / 2, 0)),
        material=metal,
        name="pull",
    )

    door_1 = model.part("door_1")
    door_1.visual(
        mesh_from_cadquery(build_door_panel(door_width), "door_1_panel", unit_scale=1.0),
        origin=Origin(xyz=(-door_width / 2, 0, 0)),
        material=wood,
        name="panel",
    )
    door_1.visual(
        mesh_from_cadquery(build_handle(), "door_1_pull", unit_scale=1.0),
        origin=Origin(xyz=(-door_width + 32 * MM, HANDLE_CLEAR / 2, 0), rpy=(0, 0, math.pi)),
        material=metal,
        name="pull",
    )

    model.articulation(
        "cabinet_to_door_0",
        ArticulationType.REVOLUTE,
        parent=cabinet,
        child=door_0,
        origin=Origin(xyz=(-W / 2 + PANEL + REVEAL, door_y, -H / 2 + REVEAL + door_height / 2)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=1.75, effort=8.0, velocity=1.0),
    )
    model.articulation(
        "cabinet_to_door_1",
        ArticulationType.REVOLUTE,
        parent=cabinet,
        child=door_1,
        origin=Origin(xyz=(W / 2 - PANEL - REVEAL, door_y, -H / 2 + REVEAL + door_height / 2)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(lower=0.0, upper=1.75, effort=8.0, velocity=1.0),
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    cabinet = object_model.get_part("cabinet")
    door_0 = object_model.get_part("door_0")
    door_1 = object_model.get_part("door_1")
    hinge_0 = object_model.get_articulation("cabinet_to_door_0")
    hinge_1 = object_model.get_articulation("cabinet_to_door_1")

    ctx.expect_gap(door_1, door_0, axis="x", min_gap=0.0015, max_gap=0.0035, elem_a="panel", elem_b="panel", name="doors_keep_narrow_center_gap")
    ctx.expect_gap(door_0, cabinet, axis="y", min_gap=-0.0005, max_gap=0.003, positive_elem="panel", negative_elem="shell", name="doors_sit_at_front_plane")

    with ctx.pose({hinge_0: 1.2}):
        ctx.expect_overlap(door_0, cabinet, axes="z", min_overlap=0.55, elem_a="panel", elem_b="shell", name="left_door_stays_hinged_along_height")
    with ctx.pose({hinge_1: 1.2}):
        ctx.expect_overlap(door_1, cabinet, axes="z", min_overlap=0.55, elem_a="panel", elem_b="shell", name="right_door_stays_hinged_along_height")

    return ctx.report()


object_model = build_object_model()