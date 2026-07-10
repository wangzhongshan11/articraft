from __future__ import annotations

from math import pi

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    Cylinder,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)


FRAME_Y = 0.0
CRANK_X = -0.018
DRIVE_X = 0.056
AXIS_Z = 0.044
SEAT_X = 0.074
SEAT_BASE_Z = 0.072


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="desktop_mini_exercise_bike")

    cream = model.material("cream", rgba=(0.93, 0.91, 0.84, 1.0))
    warm_white = model.material("warm_white", rgba=(0.97, 0.96, 0.92, 1.0))
    steel = model.material("steel", rgba=(0.62, 0.64, 0.67, 1.0))
    dark = model.material("dark", rgba=(0.17, 0.17, 0.18, 1.0))
    rubber = model.material("rubber", rgba=(0.09, 0.09, 0.10, 1.0))
    saddle = model.material("saddle", rgba=(0.89, 0.88, 0.83, 1.0))

    frame = model.part("frame")
    frame.visual(Box((0.22, 0.018, 0.014)), origin=Origin(xyz=(0.0, 0.0, 0.007)), material=cream, name="base_rail")
    frame.visual(Cylinder(radius=0.013, length=0.046), origin=Origin(xyz=(-0.086, 0.0, 0.013), rpy=(0.0, pi / 2.0, 0.0)), material=cream, name="rear_foot")
    frame.visual(Cylinder(radius=0.013, length=0.046), origin=Origin(xyz=(0.090, 0.0, 0.013), rpy=(0.0, pi / 2.0, 0.0)), material=cream, name="front_foot")
    frame.visual(Box((0.028, 0.016, 0.078)), origin=Origin(xyz=(-0.050, 0.0, 0.053)), material=cream, name="head_tube")
    frame.visual(Box((0.092, 0.016, 0.016)), origin=Origin(xyz=(-0.008, 0.0, 0.088)), material=cream, name="top_tube")
    frame.visual(Box((0.100, 0.018, 0.016)), origin=Origin(xyz=(0.016, 0.0, 0.054)), material=cream, name="down_tube")
    frame.visual(Box((0.084, 0.016, 0.014)), origin=Origin(xyz=(0.038, 0.0, 0.022)), material=cream, name="chain_stay")
    frame.visual(Box((0.044, 0.016, 0.014)), origin=Origin(xyz=(0.058, 0.0, 0.067)), material=cream, name="seat_stay")
    frame.visual(Box((0.018, 0.016, 0.054)), origin=Origin(xyz=(SEAT_X, 0.0, 0.054)), material=cream, name="seat_tube")
    frame.visual(Box((0.010, 0.016, 0.016)), origin=Origin(xyz=(CRANK_X - 0.010, 0.0, AXIS_Z)), material=cream, name="bottom_bracket")
    frame.visual(Box((0.018, 0.016, 0.024)), origin=Origin(xyz=(-0.050, 0.0, 0.099)), material=cream, name="stem")
    frame.visual(Cylinder(radius=0.007, length=0.056), origin=Origin(xyz=(-0.050, 0.0, 0.111), rpy=(0.0, pi / 2.0, 0.0)), material=cream, name="handlebar")
    frame.visual(Cylinder(radius=0.0045, length=0.020), origin=Origin(xyz=(-0.067, 0.0, 0.111), rpy=(0.0, pi / 2.0, 0.0)), material=rubber, name="grip_0")
    frame.visual(Cylinder(radius=0.0045, length=0.020), origin=Origin(xyz=(-0.033, 0.0, 0.111), rpy=(0.0, pi / 2.0, 0.0)), material=rubber, name="grip_1")
    frame.visual(Cylinder(radius=0.026, length=0.004), origin=Origin(xyz=(CRANK_X - 0.010, 0.0, AXIS_Z), rpy=(0.0, pi / 2.0, 0.0)), material=warm_white, name="guard")
    frame.visual(Cylinder(radius=0.010, length=0.004), origin=Origin(xyz=(DRIVE_X, 0.0, AXIS_Z), rpy=(0.0, pi / 2.0, 0.0)), material=warm_white, name="drive_pulley")
    frame.visual(Box((0.064, 0.002, 0.008)), origin=Origin(xyz=(0.020, 0.007, 0.051)), material=dark, name="belt_top")
    frame.visual(Box((0.064, 0.002, 0.008)), origin=Origin(xyz=(0.020, 0.007, 0.037)), material=dark, name="belt_bottom")
    frame.visual(Cylinder(radius=0.004, length=0.010), origin=Origin(xyz=(CRANK_X, 0.0, AXIS_Z), rpy=(0.0, pi / 2.0, 0.0)), material=steel, name="crank_bearing")
    frame.visual(Cylinder(radius=0.004, length=0.010), origin=Origin(xyz=(DRIVE_X, 0.0, AXIS_Z), rpy=(0.0, pi / 2.0, 0.0)), material=steel, name="flywheel_bearing")
    for z in (0.072, 0.080, 0.088, 0.096):
        frame.visual(Cylinder(radius=0.0018, length=0.012), origin=Origin(xyz=(SEAT_X, 0.0, z), rpy=(0.0, pi / 2.0, 0.0)), material=dark, name=f"seat_hole_{int(round(z * 1000))}")

    crank = model.part("crank")
    crank.visual(Cylinder(radius=0.015, length=0.008), origin=Origin(rpy=(0.0, pi / 2.0, 0.0)), material=warm_white, name="chainring")
    crank.visual(Box((0.040, 0.008, 0.008)), origin=Origin(xyz=(0.020, 0.0, 0.0)), material=cream, name="arm_0")
    crank.visual(Box((0.040, 0.008, 0.008)), origin=Origin(xyz=(-0.020, 0.0, 0.0)), material=cream, name="arm_1")
    crank.visual(Cylinder(radius=0.0035, length=0.028), origin=Origin(rpy=(0.0, pi / 2.0, 0.0)), material=steel, name="axle")
    crank.visual(Cylinder(radius=0.003, length=0.006), origin=Origin(xyz=(0.040, 0.0, 0.0), rpy=(0.0, pi / 2.0, 0.0)), material=steel, name="stub_0")
    crank.visual(Cylinder(radius=0.003, length=0.006), origin=Origin(xyz=(-0.040, 0.0, 0.0), rpy=(0.0, pi / 2.0, 0.0)), material=steel, name="stub_1")

    pedal_0 = model.part("pedal_0")
    pedal_0.visual(Box((0.016, 0.010, 0.010)), origin=Origin(xyz=(0.010, 0.0, 0.0)), material=cream, name="body")
    pedal_0.visual(Cylinder(radius=0.0025, length=0.010), origin=Origin(rpy=(0.0, pi / 2.0, 0.0)), material=steel, name="spindle")

    pedal_1 = model.part("pedal_1")
    pedal_1.visual(Box((0.016, 0.010, 0.010)), origin=Origin(xyz=(-0.010, 0.0, 0.0)), material=cream, name="body")
    pedal_1.visual(Cylinder(radius=0.0025, length=0.010), origin=Origin(rpy=(0.0, pi / 2.0, 0.0)), material=steel, name="spindle")

    flywheel = model.part("flywheel")
    flywheel.visual(Cylinder(radius=0.016, length=0.008), origin=Origin(rpy=(0.0, pi / 2.0, 0.0)), material=warm_white, name="rim")
    flywheel.visual(Cylinder(radius=0.010, length=0.010), origin=Origin(rpy=(0.0, pi / 2.0, 0.0)), material=cream, name="hub")
    flywheel.visual(Cylinder(radius=0.0035, length=0.014), origin=Origin(rpy=(0.0, pi / 2.0, 0.0)), material=steel, name="shaft")

    seat_post = model.part("seat_post")
    seat_post.visual(Box((0.010, 0.010, 0.060)), origin=Origin(xyz=(0.0, 0.0, 0.010)), material=cream, name="post")
    for z in (0.000, 0.008, 0.016, 0.024):
        seat_post.visual(Cylinder(radius=0.0016, length=0.010), origin=Origin(xyz=(0.0, 0.0, z), rpy=(0.0, pi / 2.0, 0.0)), material=dark, name=f"lock_hole_{int(round((z + 0.010) * 1000))}")
    seat_post.visual(Box((0.016, 0.012, 0.006)), origin=Origin(xyz=(0.0, 0.0, 0.041)), material=steel, name="clamp")

    seat = model.part("seat")
    seat.visual(Box((0.044, 0.032, 0.010)), origin=Origin(xyz=(0.0, 0.0, 0.005)), material=saddle, name="cushion")
    seat.visual(Box((0.018, 0.016, 0.008)), origin=Origin(xyz=(-0.010, 0.0, -0.004)), material=saddle, name="tail")
    seat.visual(Cylinder(radius=0.0035, length=0.018), origin=Origin(xyz=(0.0, 0.0, -0.009), rpy=(pi / 2.0, 0.0, 0.0)), material=steel, name="rail")

    model.articulation(
        "crank_spin",
        ArticulationType.CONTINUOUS,
        parent=frame,
        child=crank,
        origin=Origin(xyz=(CRANK_X, 0.0, AXIS_Z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=12.0),
    )
    model.articulation(
        "pedal_0_spin",
        ArticulationType.CONTINUOUS,
        parent=crank,
        child=pedal_0,
        origin=Origin(xyz=(0.040, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=12.0),
    )
    model.articulation(
        "pedal_1_spin",
        ArticulationType.CONTINUOUS,
        parent=crank,
        child=pedal_1,
        origin=Origin(xyz=(-0.040, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=12.0),
    )
    model.articulation(
        "flywheel_spin",
        ArticulationType.CONTINUOUS,
        parent=frame,
        child=flywheel,
        origin=Origin(xyz=(DRIVE_X, 0.0, AXIS_Z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=18.0),
        mimic=Mimic("crank_spin", multiplier=-1.5, offset=0.0),
    )
    model.articulation(
        "seat_post_slide",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=seat_post,
        origin=Origin(xyz=(SEAT_X, 0.0, SEAT_BASE_Z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=10.0, velocity=0.05, lower=0.0, upper=0.025),
    )
    model.articulation(
        "seat_mount",
        ArticulationType.FIXED,
        parent=seat_post,
        child=seat,
        origin=Origin(xyz=(0.0, 0.0, 0.050)),
    )

    model.meta["motion_list"] = [
        {"joint": "crank_spin", "type": "continuous", "function": "曲柄绕横向轴持续旋转"},
        {"joint": "pedal_0_spin", "type": "continuous", "function": "踏板 0 绕自身轴自转"},
        {"joint": "pedal_1_spin", "type": "continuous", "function": "踏板 1 绕自身轴自转"},
        {"joint": "flywheel_spin", "type": "continuous", "function": "飞轮沿与曲柄平行的轴旋转，并通过皮带轮关系联动"},
        {"joint": "seat_post_slide", "type": "prismatic", "function": "座杆竖直调节，行程 25 mm"},
    ]
    model.meta["shaft_alignment_check"] = {
        "crank_origin": [CRANK_X, 0.0, AXIS_Z],
        "flywheel_origin": [DRIVE_X, 0.0, AXIS_Z],
        "axis": [1.0, 0.0, 0.0],
        "result": "aligned_parallel_shafts",
    }
    model.meta["printable_parts"] = ["frame", "crank", "pedal_0", "pedal_1", "flywheel", "seat_post", "seat"]
    model.meta["print_plan"] = {
        "frame": "底脚朝下打印，车架整体单件",
        "crank": "平放打印，减少支撑",
        "pedal_0": "平放打印",
        "pedal_1": "平放打印",
        "flywheel": "侧放打印以保持圆盘平整",
        "seat_post": "竖直打印以保持定位孔清晰",
        "seat": "底面朝下打印",
    }
    model.meta["trace"] = "unavailable"

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    frame = object_model.get_part("frame")
    crank = object_model.get_part("crank")
    flywheel = object_model.get_part("flywheel")
    seat_post = object_model.get_part("seat_post")
    seat = object_model.get_part("seat")
    crank_spin = object_model.get_articulation("crank_spin")
    seat_post_slide = object_model.get_articulation("seat_post_slide")

    ctx.allow_overlap("frame", "seat_post", elem_a="seat_tube", elem_b="post", reason="The seat post is intentionally represented as sliding inside the seat tube sleeve.")
    ctx.expect_overlap(crank, frame, axes="y", min_overlap=0.006, elem_a="axle", elem_b="crank_bearing", name="crank shaft aligns with frame bearing")
    ctx.expect_overlap(flywheel, frame, axes="y", min_overlap=0.006, elem_a="shaft", elem_b="flywheel_bearing", name="flywheel shaft aligns with frame bearing")
    ctx.expect_within(seat_post, frame, axes="xy", margin=0.004, inner_elem="post", outer_elem="seat_tube", name="seat post remains centered in seat tube")
    with ctx.pose({seat_post_slide: 0.025}):
        ctx.expect_overlap(seat_post, frame, axes="z", min_overlap=0.020, elem_a="post", elem_b="seat_tube", name="seat post keeps retained insertion")
        ctx.expect_origin_gap(seat, frame, axis="z", min_gap=0.09, name="seat rises above frame at full extension")
    with ctx.pose({crank_spin: 1.0}):
        ctx.expect_origin_distance(crank, flywheel, axes="yz", max_dist=0.001, name="crank and flywheel axes stay aligned")

    return ctx.report()


object_model = build_object_model()
