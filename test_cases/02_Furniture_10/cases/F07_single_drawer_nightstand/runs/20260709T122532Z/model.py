from __future__ import annotations

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    Cylinder,
    Material,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)


MM = 0.001


def mm(value: float) -> float:
    return value * MM


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="single_drawer_nightstand")

    width = mm(450.0)
    depth = mm(400.0)
    height = mm(560.0)
    panel = mm(20.0)
    foot_h = mm(18.0)
    top_overhang = mm(8.0)
    side_h = height - foot_h - panel
    inner_w = width - 2 * panel
    inner_d = depth - 2 * panel
    shelf_clear_h = mm(230.0)
    shelf_t = panel
    shelf_z = foot_h + panel + shelf_clear_h + shelf_t / 2.0
    drawer_open_h = mm(147.0)
    drawer_center_z = shelf_z + shelf_t / 2.0 + drawer_open_h / 2.0
    rail_h = mm(40.0)
    drawer_front_gap = mm(2.0)

    wood = model.material("wood", color=(0.73, 0.58, 0.38, 1.0))
    drawer_wood = model.material("drawer_wood", color=(0.70, 0.55, 0.36, 1.0))
    metal = model.material("metal", color=(0.35, 0.30, 0.24, 1.0))
    runner = model.material("runner", color=(0.15, 0.15, 0.15, 1.0))

    cabinet = model.part("cabinet")
    cabinet.visual(
        Box((panel, depth, side_h)),
        origin=Origin(xyz=(-(width - panel) / 2.0, 0.0, foot_h + side_h / 2.0)),
        material=wood,
        name="side_0",
    )
    cabinet.visual(
        Box((panel, depth, side_h)),
        origin=Origin(xyz=((width - panel) / 2.0, 0.0, foot_h + side_h / 2.0)),
        material=wood,
        name="side_1",
    )
    cabinet.visual(
        Box((width + 2 * top_overhang, depth + 2 * top_overhang, panel)),
        origin=Origin(xyz=(0.0, 0.0, height - panel / 2.0)),
        material=wood,
        name="top",
    )
    cabinet.visual(
        Box((inner_w, depth, panel)),
        origin=Origin(xyz=(0.0, 0.0, foot_h + panel / 2.0)),
        material=wood,
        name="bottom",
    )
    cabinet.visual(
        Box((inner_w, inner_d, shelf_t)),
        origin=Origin(xyz=(0.0, 0.0, shelf_z)),
        material=wood,
        name="shelf",
    )
    cabinet.visual(
        Box((inner_w, panel, side_h - panel)),
        origin=Origin(xyz=(0.0, (depth - panel) / 2.0, foot_h + panel + (side_h - panel) / 2.0)),
        material=wood,
        name="back",
    )
    cabinet.visual(
        Box((inner_w, panel, rail_h)),
        origin=Origin(xyz=(0.0, -(depth - panel) / 2.0, height - panel - rail_h / 2.0)),
        material=wood,
        name="top_rail",
    )
    cabinet.visual(
        Box((inner_w, panel, shelf_clear_h)),
        origin=Origin(xyz=(0.0, -(depth - panel) / 2.0, foot_h + panel + shelf_clear_h / 2.0)),
        material=wood,
        name="lower_rail",
    )

    foot_r = mm(10.0)
    foot_y = depth / 2.0 - mm(35.0)
    foot_x = width / 2.0 - panel / 2.0
    for i, sx in enumerate((-1.0, 1.0)):
        for j, sy in enumerate((-1.0, 1.0)):
            cabinet.visual(
                Cylinder(radius=foot_r, length=foot_h),
                origin=Origin(xyz=(sx * foot_x, sy * foot_y, foot_h / 2.0)),
                material=wood,
                name=f"foot_{i}_{j}",
            )

    drawer = model.part("drawer")
    drawer_w = mm(365.0)
    drawer_d = mm(320.0)
    drawer_h = mm(105.0)
    side_t = mm(12.0)
    bottom_t = mm(6.0)
    box_front_y = mm(152.0)

    drawer.visual(
        Box((drawer_w, side_t, drawer_h)),
        origin=Origin(xyz=(0.0, box_front_y + drawer_d / 2.0 - side_t / 2.0, drawer_h / 2.0)),
        material=drawer_wood,
        name="box_back",
    )
    drawer.visual(
        Box((side_t, drawer_d - side_t, drawer_h - mm(24.0))),
        origin=Origin(xyz=(-(drawer_w - side_t) / 2.0, box_front_y + side_t / 2.0, (drawer_h - mm(24.0)) / 2.0)),
        material=drawer_wood,
        name="box_side_0",
    )
    drawer.visual(
        Box((side_t, drawer_d - side_t, drawer_h - mm(24.0))),
        origin=Origin(xyz=((drawer_w - side_t) / 2.0, box_front_y + side_t / 2.0, (drawer_h - mm(24.0)) / 2.0)),
        material=drawer_wood,
        name="box_side_1",
    )
    drawer.visual(
        Box((drawer_w - 2 * side_t, drawer_d - side_t, bottom_t)),
        origin=Origin(xyz=(0.0, box_front_y + side_t / 2.0, bottom_t / 2.0)),
        material=drawer_wood,
        name="box_bottom",
    )
    drawer.visual(
        Box((mm(404.0), mm(20.0), drawer_open_h)),
        origin=Origin(xyz=(0.0, -drawer_front_gap - mm(10.0), drawer_open_h / 2.0)),
        material=wood,
        name="front_panel",
    )
    drawer.visual(
        Box((mm(16.0), mm(16.0), mm(18.0))),
        origin=Origin(xyz=(-mm(29.0), -drawer_front_gap - mm(9.0), drawer_open_h / 2.0)),
        material=wood,
        name="pull_mount_0",
    )
    drawer.visual(
        Box((mm(16.0), mm(16.0), mm(18.0))),
        origin=Origin(xyz=(mm(29.0), -drawer_front_gap - mm(9.0), drawer_open_h / 2.0)),
        material=wood,
        name="pull_mount_1",
    )
    drawer.visual(
        Box((mm(86.0), mm(14.0), mm(10.0))),
        origin=Origin(xyz=(0.0, -drawer_front_gap - mm(27.0), drawer_open_h / 2.0)),
        material=metal,
        name="pull_bar",
    )
    drawer.visual(
        Cylinder(radius=mm(4.0), length=mm(14.0)),
        origin=Origin(xyz=(-mm(29.0), -drawer_front_gap - mm(20.0), drawer_open_h / 2.0)),
        material=metal,
        name="pull_post_0",
    )
    drawer.visual(
        Cylinder(radius=mm(4.0), length=mm(14.0)),
        origin=Origin(xyz=(mm(29.0), -drawer_front_gap - mm(20.0), drawer_open_h / 2.0)),
        material=metal,
        name="pull_post_1",
    )
    drawer.visual(
        Box((mm(349.0), mm(12.0), mm(35.0))),
        origin=Origin(xyz=(0.0, mm(316.0), drawer_h / 2.0)),
        material=runner,
        name="runner_block",
    )

    model.articulation(
        "cabinet_to_drawer",
        ArticulationType.PRISMATIC,
        parent=cabinet,
        child=drawer,
        origin=Origin(xyz=(0.0, -depth / 2.0, drawer_center_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=mm(180.0), effort=80.0, velocity=0.25),
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    cabinet = object_model.get_part("cabinet")
    drawer = object_model.get_part("drawer")
    slide = object_model.get_articulation("cabinet_to_drawer")

    ctx.allow_overlap(
        drawer,
        cabinet,
        elem_a="runner_block",
        elem_b="lower_rail",
        reason="A simplified central runner block is captured inside the cabinet opening to represent the drawer slide support.",
    )
    ctx.allow_isolated_part(
        drawer,
        reason="The articulated drawer is mounted with a small face clearance and simplified hidden slide support rather than a continuously contacting rail model.",
    )
    ctx.expect_gap(
        drawer,
        cabinet,
        axis="z",
        min_gap=mm(62.0),
        max_gap=mm(75.0),
        positive_elem="front_panel",
        negative_elem="shelf",
        name="drawer front sits above lower shelf opening",
    )
    ctx.expect_within(
        drawer,
        cabinet,
        axes="x",
        margin=mm(4.0),
        inner_elem="front_panel",
        outer_elem="top_rail",
        name="drawer front is centered within cabinet width",
    )
    with ctx.pose({slide: mm(180.0)}):
        ctx.expect_gap(
            cabinet,
            drawer,
            axis="y",
            min_gap=mm(150.0),
            positive_elem="back",
            negative_elem="front_panel",
            name="drawer extends outward from cabinet",
        )
        ctx.expect_overlap(
            drawer,
            cabinet,
            axes="y",
            min_overlap=mm(110.0),
            elem_a="box_bottom",
            elem_b="shelf",
            name="drawer box remains retained when open",
        )

    return ctx.report()


object_model = build_object_model()