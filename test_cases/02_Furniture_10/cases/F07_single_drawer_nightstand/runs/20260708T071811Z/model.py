from __future__ import annotations

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)


MM = 0.001


def _box(size: tuple[float, float, float], center: tuple[float, float, float]) -> cq.Workplane:
    return cq.Workplane("XY").box(*size).translate(center)


def _union_boxes(boxes: list[tuple[tuple[float, float, float], tuple[float, float, float]]]) -> cq.Workplane:
    shape = _box(*boxes[0])
    for size, center in boxes[1:]:
        shape = shape.union(_box(size, center))
    return shape


def _drawer_box_shape() -> cq.Workplane:
    width = 360 * MM
    depth = 330 * MM
    height = 120 * MM
    wall = 12 * MM
    bottom = 12 * MM

    boards = [
        ((width, depth, bottom), (0.0, 0.0, -height / 2 + bottom / 2)),
        ((wall, depth, height), (-(width / 2 - wall / 2), 0.0, 0.0)),
        ((wall, depth, height), ((width / 2 - wall / 2), 0.0, 0.0)),
        ((width, wall, height), (0.0, depth / 2 - wall / 2, 0.0)),
    ]
    return _union_boxes(boards)


def _drawer_front_shape() -> cq.Workplane:
    panel = cq.Workplane("XY").box(390 * MM, 18 * MM, 174 * MM)
    # Slight manufactured easing on the exposed slab edges.
    return panel.edges().chamfer(1.5 * MM)


def _pull_shape() -> cq.Workplane:
    # A simple U-shaped metal pull made from a continuous bar and two standoffs.
    bar = _box((120 * MM, 12 * MM, 12 * MM), (0.0, -30 * MM, 0.0))
    post_0 = _box((12 * MM, 25 * MM, 12 * MM), (-45 * MM, -12.5 * MM, 0.0))
    post_1 = _box((12 * MM, 25 * MM, 12 * MM), (45 * MM, -12.5 * MM, 0.0))
    return bar.union(post_0).union(post_1).edges().chamfer(1.0 * MM)


def _foot_shape() -> cq.Workplane:
    return cq.Workplane("XY").box(44 * MM, 44 * MM, 45 * MM).edges("|Z").chamfer(3 * MM)


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="single_drawer_nightstand")

    wood = model.material("warm_oak", rgba=(0.72, 0.47, 0.23, 1.0))
    inner_wood = model.material("unfinished_oak", rgba=(0.78, 0.57, 0.34, 1.0))
    metal = model.material("dark_bronze", rgba=(0.22, 0.16, 0.10, 1.0))

    cabinet = model.part("cabinet")
    # The carcass is modeled from individual board solids so the drawer and open
    # shelf remain physically hollow rather than a single blocking proxy.
    cabinet.visual(Box((22 * MM, 400 * MM, 515 * MM)), origin=Origin(xyz=(-214 * MM, 0.0, 302.5 * MM)), material=wood, name="side_panel_0")
    cabinet.visual(Box((22 * MM, 400 * MM, 515 * MM)), origin=Origin(xyz=(214 * MM, 0.0, 302.5 * MM)), material=wood, name="side_panel_1")
    cabinet.visual(Box((450 * MM, 400 * MM, 24 * MM)), origin=Origin(xyz=(0.0, 0.0, 548 * MM)), material=wood, name="top_panel")
    cabinet.visual(Box((406 * MM, 356 * MM, 22 * MM)), origin=Origin(xyz=(0.0, -3 * MM, 56 * MM)), material=wood, name="bottom_shelf")
    cabinet.visual(Box((406 * MM, 356 * MM, 22 * MM)), origin=Origin(xyz=(0.0, -3 * MM, 335 * MM)), material=wood, name="drawer_divider")
    cabinet.visual(Box((406 * MM, 12 * MM, 469 * MM)), origin=Origin(xyz=(0.0, 194 * MM, 302.5 * MM)), material=wood, name="back_panel")
    cabinet.visual(Box((23 * MM, 310 * MM, 10 * MM)), origin=Origin(xyz=(-191.5 * MM, -15 * MM, 376 * MM)), material=wood, name="drawer_runner_0")
    cabinet.visual(Box((23 * MM, 310 * MM, 10 * MM)), origin=Origin(xyz=(191.5 * MM, -15 * MM, 376 * MM)), material=wood, name="drawer_runner_1")
    cabinet.visual(Box((406 * MM, 22 * MM, 42 * MM)), origin=Origin(xyz=(0.0, -189 * MM, 66 * MM)), material=wood, name="front_kick")

    foot_positions = [
        (-180 * MM, -155 * MM, 22.5 * MM),
        (180 * MM, -155 * MM, 22.5 * MM),
        (-180 * MM, 155 * MM, 22.5 * MM),
        (180 * MM, 155 * MM, 22.5 * MM),
    ]
    for idx, pos in enumerate(foot_positions):
        foot = model.part(f"foot_{idx}")
        foot.visual(
            mesh_from_cadquery(_foot_shape(), f"foot_{idx}", tolerance=0.0008, angular_tolerance=0.12),
            material=wood,
            name="foot_block",
        )
        model.articulation(
            f"cabinet_to_foot_{idx}",
            ArticulationType.FIXED,
            parent=cabinet,
            child=foot,
            origin=Origin(xyz=pos),
        )

    drawer_box = model.part("drawer_box")
    drawer_box.visual(
        mesh_from_cadquery(_drawer_box_shape(), "drawer_box", tolerance=0.0008, angular_tolerance=0.12),
        material=inner_wood,
        name="drawer_box_shell",
    )
    drawer_slide = model.articulation(
        "cabinet_to_drawer_box",
        ArticulationType.PRISMATIC,
        parent=cabinet,
        child=drawer_box,
        # Front is -Y; positive travel pulls the drawer outward.
        origin=Origin(xyz=(0.0, -35 * MM, 441 * MM)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=60.0, velocity=0.35, lower=0.0, upper=220 * MM),
    )

    drawer_front = model.part("drawer_front")
    drawer_front.visual(
        mesh_from_cadquery(_drawer_front_shape(), "drawer_front", tolerance=0.0008, angular_tolerance=0.12),
        material=wood,
        name="front_panel",
    )
    model.articulation(
        "drawer_box_to_front",
        ArticulationType.FIXED,
        parent=drawer_box,
        child=drawer_front,
        origin=Origin(xyz=(0.0, -174 * MM, 0.0)),
    )

    pull = model.part("pull")
    pull.visual(
        mesh_from_cadquery(_pull_shape(), "center_pull", tolerance=0.0008, angular_tolerance=0.12),
        material=metal,
        name="pull_handle",
    )
    model.articulation(
        "front_to_pull",
        ArticulationType.FIXED,
        parent=drawer_front,
        child=pull,
        origin=Origin(xyz=(0.0, -9 * MM, 0.0)),
    )

    # Keep the slide object referenced so tests can resolve the exact joint name.
    drawer_slide.meta["purpose"] = "single upper drawer slide"
    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    cabinet = object_model.get_part("cabinet")
    drawer_box = object_model.get_part("drawer_box")
    drawer_front = object_model.get_part("drawer_front")
    pull = object_model.get_part("pull")
    slide = object_model.get_articulation("cabinet_to_drawer_box")

    cab_aabb = ctx.part_world_aabb(cabinet)
    if cab_aabb is not None:
        mn, mx = cab_aabb
        dims = (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])
        ctx.check(
            "cabinet carcass is 450 by 400 mm and reaches 560 mm height",
            abs(dims[0] - 0.450) < 0.002 and abs(dims[1] - 0.400) < 0.002 and abs(mx[2] - 0.560) < 0.002,
            details=f"dims={dims}, top={mx[2]}",
        )

    # The front panel is visibly separate, centered in the upper opening, and
    # clear of the cabinet face frame on X/Z while touching the drawer box front.
    ctx.expect_within(
        drawer_front,
        cabinet,
        axes="xz",
        margin=0.004,
        name="drawer front sits within the cabinet opening with clearance",
    )
    ctx.expect_contact(
        drawer_front,
        drawer_box,
        elem_a="front_panel",
        elem_b="drawer_box_shell",
        contact_tol=0.002,
        name="front panel is attached to the drawer box",
    )
    ctx.expect_contact(
        pull,
        drawer_front,
        elem_a="pull_handle",
        elem_b="front_panel",
        contact_tol=0.0015,
        name="center pull mounts to the drawer front",
    )

    rest_pos = ctx.part_world_position(drawer_box)
    with ctx.pose({slide: 220 * MM}):
        ctx.expect_within(
            drawer_box,
            cabinet,
            axes="xz",
            margin=0.006,
            name="extended drawer remains guided between side panels",
        )
        ctx.expect_overlap(
            drawer_box,
            cabinet,
            axes="y",
            min_overlap=0.070,
            name="extended drawer keeps retained insertion in the cabinet",
        )
        extended_pos = ctx.part_world_position(drawer_box)

    ctx.check(
        "drawer pulls outward along the front direction",
        rest_pos is not None and extended_pos is not None and extended_pos[1] < rest_pos[1] - 0.18,
        details=f"rest={rest_pos}, extended={extended_pos}",
    )

    return ctx.report()


object_model = build_object_model()