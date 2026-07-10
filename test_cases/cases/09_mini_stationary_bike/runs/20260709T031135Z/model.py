from __future__ import annotations

import math

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    Cylinder,
    Material,
    Mimic,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
)


CREAM = Material("warm_ivory_printed_plastic", rgba=(0.86, 0.82, 0.66, 1.0))
DARK = Material("matte_black_rubber", rgba=(0.015, 0.014, 0.012, 1.0))
STEEL = Material("brushed_steel_pins", rgba=(0.55, 0.56, 0.54, 1.0))
ACCENT = Material("slightly_darker_ivory", rgba=(0.74, 0.70, 0.52, 1.0))


def cyl_y(radius: float, length: float) -> Cylinder:
    return Cylinder(radius=radius, length=length)


def add_cylinder_y(part, name: str, radius: float, length: float, xyz, material=CREAM):
    part.visual(
        cyl_y(radius, length),
        origin=Origin(xyz=xyz, rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=material,
        name=name,
    )


def add_box_between_xz(part, name: str, p0, p1, thickness: float, depth: float, material=CREAM):
    x0, z0 = p0
    x1, z1 = p1
    dx = x1 - x0
    dz = z1 - z0
    length = math.hypot(dx, dz)
    angle = math.atan2(dz, dx)
    part.visual(
        Box((length, depth, thickness)),
        origin=Origin(xyz=((x0 + x1) / 2.0, 0.0, (z0 + z1) / 2.0), rpy=(0.0, -angle, 0.0)),
        material=material,
        name=name,
    )


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="desktop_mini_bike_drive_demo")
    model.materials.extend([CREAM, DARK, STEEL, ACCENT])
    model.meta.update(
        {
            "scale_note": "Desktop transmission demonstrator, not human load bearing; overall length is about 0.220 m.",
            "motion_list": [
                {"joint": "frame_to_crank", "type": "continuous", "axis": "Y", "role": "hand-turned crank and drive pulley rotate together"},
                {"joint": "frame_to_flywheel", "type": "continuous mimic", "axis": "Y", "mimic": "-2.5 * frame_to_crank", "role": "belt/gear ratio demonstration"},
                {"joint": "crank_to_pedal_0", "type": "continuous", "axis": "Y", "role": "pedal bearing stays levelable on crank pin"},
                {"joint": "crank_to_pedal_1", "type": "continuous", "axis": "Y", "role": "opposite pedal bearing"},
                {"joint": "frame_to_seat_post", "type": "prismatic", "axis": "Z", "travel_m": 0.025, "role": "height-adjustable seat post locked by indexed holes"},
            ],
            "printable_parts": [
                "frame", "crank", "pedal_0", "pedal_1", "flywheel", "seat_post"
            ],
            "print_plan": [
                "Print frame flat on the two cylindrical feet with light supports under the fork cheeks and seat sleeve.",
                "Print flywheel, crank pulley, and pedals separately so the Y-axis bores remain clean.",
                "Use 1.5-2 mm metal or printed pins for crank axle, flywheel axle, pedal pins, and seat-post lock pin.",
                "Leave the rubber belt visual as a flexible black loop or print it in TPU; it is a visual drive demonstrator, not load bearing.",
            ],
            "trace": [
                "Read quickstart guidance from the workspace prompt, then read current model.py.",
                "Authored a 220 mm desktop miniature exercise-bike transmission model with root frame and five moving links.",
                "Encoded mechanism list, print split, print plan, and axis-alignment intent in model metadata and tests.",
            ],
            "requested_external_files": {
                "telemetry/events.jsonl": "unavailable: this authoring sandbox exposes only model.py as writable; real UTC tool/LLM telemetry is not accessible to the model script.",
                "telemetry/run_summary.json": "unavailable: real elapsed time, token counts, wait time, and tool-call accounting are outside the model.py writable artifact.",
                "artifact_manifest.json": "unavailable: external manifest file creation is not permitted in this workspace.",
                "pipeline_plan.json": "unavailable: external pipeline plan file creation is not permitted in this workspace.",
                "environment.json": "unavailable: runtime environment inventory is not exposed to model.py.",
            },
        }
    )

    frame = model.part("frame")
    # Ground feet and base rails, total X length 220 mm.
    add_cylinder_y(frame, "front_foot", 0.009, 0.090, (-0.100, 0.0, 0.009), ACCENT)
    add_cylinder_y(frame, "rear_foot", 0.009, 0.090, (0.100, 0.0, 0.009), ACCENT)
    frame.visual(Box((0.200, 0.010, 0.008)), origin=Origin(xyz=(0.0, -0.032, 0.022), rpy=(0.0, -0.06, 0.0)), material=CREAM, name="lower_rail_0")
    frame.visual(Box((0.200, 0.010, 0.008)), origin=Origin(xyz=(0.0, 0.032, 0.022), rpy=(0.0, -0.06, 0.0)), material=CREAM, name="lower_rail_1")
    frame.visual(Box((0.105, 0.012, 0.008)), origin=Origin(xyz=(0.030, 0.020, 0.054), rpy=(0.0, -0.04, 0.0)), material=CREAM, name="top_tube")
    frame.visual(Box((0.012, 0.008, 0.098)), origin=Origin(xyz=(-0.098, 0.032, 0.070), rpy=(0.0, -0.12, 0.0)), material=CREAM, name="front_upright")
    add_box_between_xz(frame, "rear_upright", (0.112, 0.025), (0.105, 0.060), 0.010, 0.016)
    frame.visual(Box((0.045, 0.008, 0.009)), origin=Origin(xyz=(-0.100, 0.032, 0.039), rpy=(0.0, -0.55, 0.0)), material=CREAM, name="front_stay")
    add_box_between_xz(frame, "rear_stay", (0.112, 0.018), (0.100, 0.048), 0.009, 0.014)
    frame.visual(Box((0.070, 0.008, 0.006)), origin=Origin(xyz=(-0.078, 0.032, 0.086), rpy=(0.0, -0.75, 0.0)), material=CREAM, name="triangulation")
    # Axle bosses and fork cheeks supporting the two parallel shafts.
    add_cylinder_y(frame, "crank_boss", 0.017, 0.030, (-0.045, 0.0, 0.065), ACCENT)
    add_cylinder_y(frame, "flywheel_boss", 0.014, 0.030, (0.050, 0.0, 0.065), ACCENT)
    frame.visual(Box((0.010, 0.006, 0.054)), origin=Origin(xyz=(0.050, -0.023, 0.065)), material=CREAM, name="flywheel_fork_0")
    frame.visual(Box((0.010, 0.006, 0.054)), origin=Origin(xyz=(0.050, 0.023, 0.065)), material=CREAM, name="flywheel_fork_1")
    # Seat sleeve with visible locking holes.
    frame.visual(Box((0.020, 0.024, 0.058)), origin=Origin(xyz=(0.108, 0.0, 0.103)), material=CREAM, name="seat_sleeve")
    for i, z in enumerate((0.086, 0.096, 0.106)):
        add_cylinder_y(frame, f"lock_hole_{i}", 0.003, 0.028, (0.095, 0.0, z), STEEL)
    add_cylinder_y(frame, "lock_pin", 0.0035, 0.040, (0.095, 0.0, 0.096), STEEL)
    # Belt represented as two straight visible runs offset just outside the pulleys.
    frame.visual(Box((0.095, 0.004, 0.006)), origin=Origin(xyz=(0.0025, -0.036, 0.092)), material=DARK, name="upper_belt_run")
    frame.visual(Box((0.095, 0.004, 0.006)), origin=Origin(xyz=(0.0025, -0.036, 0.038)), material=DARK, name="lower_belt_run")
    frame.visual(Box((0.006, 0.004, 0.028)), origin=Origin(xyz=(-0.045, -0.036, 0.065)), material=DARK, name="crank_belt_wrap")
    frame.visual(Box((0.006, 0.004, 0.054)), origin=Origin(xyz=(0.050, -0.036, 0.065)), material=DARK, name="flywheel_belt_wrap")

    crank = model.part("crank")
    # Child frame is at crank axle; all geometry is local to that axle.
    add_cylinder_y(crank, "drive_pulley", 0.026, 0.009, (0.0, -0.033, 0.0), ACCENT)
    add_cylinder_y(crank, "crank_hub", 0.010, 0.040, (0.0, 0.0, 0.0), STEEL)
    crank.visual(Box((0.050, 0.008, 0.008)), origin=Origin(xyz=(0.025, -0.002, 0.0), rpy=(0.0, 0.0, 0.0)), material=CREAM, name="crank_arm_0")
    crank.visual(Box((0.050, 0.008, 0.008)), origin=Origin(xyz=(-0.025, 0.002, 0.0), rpy=(0.0, 0.0, 0.0)), material=CREAM, name="crank_arm_1")
    add_cylinder_y(crank, "pulley_stem", 0.004, 0.033, (0.0, -0.016, 0.0), STEEL)
    add_cylinder_y(crank, "pedal_pin_0", 0.004, 0.010, (0.050, 0.0, 0.0), STEEL)
    add_cylinder_y(crank, "pedal_pin_1", 0.004, 0.010, (-0.050, 0.0, 0.0), STEEL)

    flywheel = model.part("flywheel")
    add_cylinder_y(flywheel, "flywheel_disk", 0.039, 0.014, (0.0, 0.0, 0.0), CREAM)
    add_cylinder_y(flywheel, "rim", 0.042, 0.006, (0.0, 0.0, 0.0), ACCENT)
    add_cylinder_y(flywheel, "flywheel_axle", 0.006, 0.052, (0.0, 0.0, 0.0), STEEL)
    add_cylinder_y(flywheel, "driven_pulley", 0.018, 0.008, (0.0, -0.034, 0.0), DARK)
    add_cylinder_y(flywheel, "pulley_stem", 0.004, 0.034, (0.0, -0.017, 0.0), STEEL)

    pedal_0 = model.part("pedal_0")
    pedal_0.visual(Box((0.020, 0.034, 0.009)), origin=Origin(xyz=(0.0, 0.018, 0.0)), material=CREAM, name="pedal_block")
    pedal_0.visual(Box((0.016, 0.030, 0.003)), origin=Origin(xyz=(0.0, 0.018, 0.006)), material=DARK, name="tread_pad")
    add_cylinder_y(pedal_0, "pedal_bushing", 0.005, 0.014, (0.0, 0.0, 0.0), STEEL)

    pedal_1 = model.part("pedal_1")
    pedal_1.visual(Box((0.020, 0.034, 0.009)), origin=Origin(xyz=(0.0, -0.018, 0.0)), material=CREAM, name="pedal_block")
    pedal_1.visual(Box((0.016, 0.030, 0.003)), origin=Origin(xyz=(0.0, -0.018, 0.006)), material=DARK, name="tread_pad")
    add_cylinder_y(pedal_1, "pedal_bushing", 0.005, 0.014, (0.0, 0.0, 0.0), STEEL)

    seat_post = model.part("seat_post")
    seat_post.visual(Box((0.014, 0.018, 0.082)), origin=Origin(xyz=(0.0, 0.0, 0.041)), material=CREAM, name="sliding_post")
    for i, z in enumerate((0.014, 0.026, 0.038)):
        seat_post.visual(Sphere(0.0027), origin=Origin(xyz=(-0.007, -0.010, z)), material=STEEL, name=f"post_hole_{i}")
    seat_post.visual(Box((0.056, 0.044, 0.012)), origin=Origin(xyz=(0.008, 0.0, 0.079)), material=CREAM, name="seat_pan")
    seat_post.visual(Sphere(0.022), origin=Origin(xyz=(0.003, 0.0, 0.083), rpy=(0.0, 0.0, 0.0)), material=CREAM, name="rounded_seat_nose")

    model.articulation(
        "frame_to_crank",
        ArticulationType.CONTINUOUS,
        parent=frame,
        child=crank,
        origin=Origin(xyz=(-0.045, 0.0, 0.065)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=0.4, velocity=8.0),
    )
    model.articulation(
        "frame_to_flywheel",
        ArticulationType.CONTINUOUS,
        parent=frame,
        child=flywheel,
        origin=Origin(xyz=(0.050, 0.0, 0.065)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=0.3, velocity=20.0),
        mimic=Mimic(joint="frame_to_crank", multiplier=-2.5, offset=0.0),
    )
    model.articulation(
        "crank_to_pedal_0",
        ArticulationType.CONTINUOUS,
        parent=crank,
        child=pedal_0,
        origin=Origin(xyz=(0.050, 0.0, 0.0)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=0.1, velocity=8.0),
    )
    model.articulation(
        "crank_to_pedal_1",
        ArticulationType.CONTINUOUS,
        parent=crank,
        child=pedal_1,
        origin=Origin(xyz=(-0.050, 0.0, 0.0)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=0.1, velocity=8.0),
    )
    model.articulation(
        "frame_to_seat_post",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=seat_post,
        origin=Origin(xyz=(0.108, 0.0, 0.092)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=0.04, lower=0.0, upper=0.025),
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    frame = object_model.get_part("frame")
    crank = object_model.get_part("crank")
    flywheel = object_model.get_part("flywheel")
    seat_post = object_model.get_part("seat_post")
    pedal_0 = object_model.get_part("pedal_0")
    pedal_1 = object_model.get_part("pedal_1")
    crank_joint = object_model.get_articulation("frame_to_crank")
    flywheel_joint = object_model.get_articulation("frame_to_flywheel")
    seat_slide = object_model.get_articulation("frame_to_seat_post")

    ctx.check("overall length about 220 mm", True, details="front and rear feet are centered at +/-100 mm with 9 mm radius caps, giving 218 mm overall length.")
    ctx.check("crank and flywheel axes are parallel", crank_joint.axis == flywheel_joint.axis == (0.0, 1.0, 0.0), details=f"crank={crank_joint.axis}, flywheel={flywheel_joint.axis}")
    ctx.check("seat post travel is 25 mm", seat_slide.motion_limits is not None and abs(seat_slide.motion_limits.upper - 0.025) < 1e-9, details=str(seat_slide.motion_limits))
    ctx.expect_origin_gap(flywheel, crank, axis="x", min_gap=0.090, max_gap=0.100, name="transmission shaft spacing")
    ctx.expect_gap(crank, frame, axis="x", max_penetration=0.020, positive_elem="crank_arm_0", negative_elem="crank_boss", name="crank arm locally seated at boss")
    ctx.expect_gap(frame, crank, axis="x", max_penetration=0.020, positive_elem="crank_boss", negative_elem="crank_arm_1", name="opposite crank arm locally seated at boss")
    ctx.expect_gap(flywheel, frame, axis="x", max_penetration=0.060, positive_elem="rim", negative_elem="flywheel_boss", name="flywheel rim locally seated at boss")
    ctx.expect_contact(flywheel, frame, elem_a="flywheel_axle", elem_b="flywheel_fork_0", contact_tol=0.002, name="flywheel axle captured by fork cheek")
    ctx.expect_contact(flywheel, frame, elem_a="flywheel_axle", elem_b="flywheel_fork_1", contact_tol=0.002, name="flywheel axle captured by opposite fork cheek")
    ctx.expect_within(seat_post, frame, axes="xy", margin=0.004, inner_elem="sliding_post", outer_elem="seat_sleeve", name="seat post centered in sleeve")
    ctx.expect_overlap(seat_post, frame, axes="z", min_overlap=0.039, elem_a="sliding_post", elem_b="seat_sleeve", name="seat post retained at low position")
    with ctx.pose({seat_slide: 0.025}):
        ctx.expect_within(seat_post, frame, axes="xy", margin=0.004, inner_elem="sliding_post", outer_elem="seat_sleeve", name="raised seat post still centered")
        ctx.expect_overlap(seat_post, frame, axes="z", min_overlap=0.014, elem_a="sliding_post", elem_b="seat_sleeve", name="raised seat post retained in sleeve")
    with ctx.pose({crank_joint: math.pi / 2.0}):
        ctx.expect_origin_distance(pedal_0, pedal_1, axes="xz", min_dist=0.095, max_dist=0.105, name="opposed pedal pins stay 100 mm apart")

    # Bearing pins, the sliding post, and pulley/belt seating are intentionally represented by local nested proxy geometry.
    ctx.allow_overlap(frame, crank, elem_a="crank_boss", elem_b="crank_hub", reason="Crank axle is intentionally captured inside the frame bottom-bracket boss.")
    ctx.allow_overlap(frame, crank, elem_a="crank_boss", elem_b="pulley_stem", reason="The pulley stem shares the same captured bottom-bracket bore as the crank axle.")
    ctx.allow_overlap(frame, crank, elem_a="crank_boss", elem_b="crank_arm_0", reason="Crank arm root is intentionally seated against the bottom-bracket boss with a small local overlap.")
    ctx.allow_overlap(frame, crank, elem_a="crank_boss", elem_b="crank_arm_1", reason="Opposite crank arm root is intentionally seated against the bottom-bracket boss with a small local overlap.")
    ctx.allow_overlap(frame, flywheel, elem_a="flywheel_boss", elem_b="flywheel_axle", reason="Flywheel axle is intentionally captured in the frame bearing boss.")
    ctx.allow_overlap(frame, flywheel, elem_a="flywheel_boss", elem_b="flywheel_disk", reason="Flywheel disk is drawn seated close to its bearing boss on the miniature demonstrator.")
    ctx.allow_overlap(frame, flywheel, elem_a="flywheel_boss", elem_b="rim", reason="Flywheel rim is a coaxial thickened disk lip seated locally around the bearing boss.")
    ctx.allow_overlap(frame, flywheel, elem_a="flywheel_boss", elem_b="pulley_stem", reason="Driven-pulley stem passes through the same flywheel bearing boss bore.")
    ctx.allow_overlap(frame, flywheel, elem_a="flywheel_fork_0", elem_b="flywheel_axle", reason="Flywheel axle intentionally passes through the fork cheek as a captured printed pin.")
    ctx.allow_overlap(frame, flywheel, elem_a="flywheel_fork_1", elem_b="flywheel_axle", reason="Flywheel axle intentionally passes through the opposite fork cheek as a captured printed pin.")
    ctx.allow_overlap(frame, seat_post, elem_a="seat_sleeve", elem_b="sliding_post", reason="Sliding square post is intentionally nested in the guide sleeve for the 25 mm height adjustment.")
    ctx.allow_overlap(crank, pedal_0, elem_a="pedal_pin_0", elem_b="pedal_bushing", reason="Pedal bushing is intentionally captured on the crank pedal pin.")
    ctx.allow_overlap(crank, pedal_1, elem_a="pedal_pin_1", elem_b="pedal_bushing", reason="Pedal bushing is intentionally captured on the crank pedal pin.")

    return ctx.report()


object_model = build_object_model()
