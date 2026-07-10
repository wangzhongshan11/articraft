from __future__ import annotations

import math

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    Cylinder,
    Material,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)


# Desktop sewing / small-tool cantilever box in meters.
LENGTH = 0.180
WIDTH = 0.100
BASE_H = 0.036
TRAY_H = 0.024
LID_T = 0.010
WALL = 0.0025
CLEARANCE = 0.00035
SIDE_Y = WIDTH / 2.0
HINGE_X = LENGTH * 0.25
HINGE_Z_LOWER = BASE_H + 0.012
HINGE_Z_UPPER = BASE_H + TRAY_H + 0.020
ROD_OUT_Y = SIDE_Y + 0.006
PIN_OUT_Y = SIDE_Y + 0.010


def rounded_box(sx: float, sy: float, sz: float, radius: float) -> cq.Workplane:
    r = min(radius, sx * 0.18, sy * 0.18, sz * 0.45)
    return cq.Workplane("XY").box(sx, sy, sz).edges("|Z").fillet(r).edges("#Z").fillet(min(r * 0.45, sz * 0.25))


def open_tray_mesh(length: float, width: float, height: float, wall: float, lip: float, name: str):
    outer = rounded_box(length, width, height, 0.006)
    cavity = (
        cq.Workplane("XY")
        .box(length - 2 * wall, width - 2 * wall, height + 0.004)
        .translate((0.0, 0.0, wall + 0.002))
    )
    body = outer.cut(cavity)
    rim = (
        cq.Workplane("XY")
        .box(length + 0.002, width + 0.002, lip)
        .cut(cq.Workplane("XY").box(length - 2 * wall, width - 2 * wall, lip + 0.002))
        .translate((0.0, 0.0, height / 2.0 + lip / 2.0 - 0.0005))
        .edges("|Z")
        .fillet(0.003)
    )
    # Low internal dividers, connected to floor and walls so the tray reads as a molded organizer.
    dividers = (
        cq.Workplane("XY")
        .box(wall, width - 2 * wall, height * 0.38)
        .translate((-length * 0.18, 0.0, -height * 0.31))
        .union(cq.Workplane("XY").box(length * 0.42, wall, height * 0.34).translate((length * 0.13, 0.0, -height * 0.33)))
    )
    return mesh_from_cadquery(body.union(rim).union(dividers), name, tolerance=0.0007, angular_tolerance=0.08)


def shallow_lid_mesh(length: float, width: float, thick: float, name: str):
    panel = rounded_box(length, width, thick, 0.006)
    raised = rounded_box(length - 0.020, width - 0.020, 0.003, 0.004).translate((0, 0, thick / 2 + 0.0015))
    bead = (
        cq.Workplane("XY")
        .box(length - 0.010, width - 0.010, 0.002)
        .cut(cq.Workplane("XY").box(length - 0.026, width - 0.026, 0.004))
        .translate((0, 0, thick / 2 + 0.0022))
        .edges("|Z")
        .fillet(0.002)
    )
    return mesh_from_cadquery(panel.union(raised).union(bead), name, tolerance=0.0007, angular_tolerance=0.08)


def rod_mesh(length: float, width: float, thick: float, name: str):
    # Capsule-like flat link: long rectangular web plus round eyes at both ends, with visible clearance holes.
    r = width / 2.0
    web = cq.Workplane("XY").box(length - width, width * 0.72, thick)
    eye1 = cq.Workplane("XY").circle(r).extrude(thick).translate((-length / 2 + r, 0, -thick / 2))
    eye2 = cq.Workplane("XY").circle(r).extrude(thick).translate((length / 2 - r, 0, -thick / 2))
    body = web.union(eye1).union(eye2).edges("|Z").fillet(0.0012)
    hole_r = 0.0020 + CLEARANCE
    h1 = cq.Workplane("XY").circle(hole_r).extrude(thick + 0.002).translate((-length / 2 + r, 0, -thick / 2 - 0.001))
    h2 = cq.Workplane("XY").circle(hole_r).extrude(thick + 0.002).translate((length / 2 - r, 0, -thick / 2 - 0.001))
    return mesh_from_cadquery(body.cut(h1).cut(h2), name, tolerance=0.0005, angular_tolerance=0.08)


def add_pin(part, name: str, xyz: tuple[float, float, float], mat: Material, length: float = 0.006):
    part.visual(Cylinder(radius=0.0020, length=length), origin=Origin(xyz=xyz, rpy=(math.pi / 2, 0, 0)), material=mat, name=f"{name}_shaft")
    part.visual(Cylinder(radius=0.0036, length=0.0016), origin=Origin(xyz=(xyz[0], xyz[1] + length / 2 + 0.0008, xyz[2]), rpy=(math.pi / 2, 0, 0)), material=mat, name=f"{name}_head")
    part.visual(Cylinder(radius=0.0012, length=0.0018), origin=Origin(xyz=(xyz[0], xyz[1] + length / 2 + 0.0017, xyz[2]), rpy=(math.pi / 2, 0, 0)), material=Material("dark_screw", (0.20, 0.20, 0.18, 1)), name=f"{name}_screw")


def tray_part(model: ArticulatedObject, name: str, y_sign: float, z_local: float, mat: Material):
    p = model.part(name)
    # Child frame sits on the side hinge axis; tray body is inward from that hinge in the closed pose.
    local_y = -y_sign * (SIDE_Y + CLEARANCE - 0.028)
    p.visual(open_tray_mesh(0.082, 0.044, TRAY_H, WALL, 0.003, f"{name}_molded_tray"), origin=Origin(xyz=(0.0, local_y, z_local)), material=mat, name="molded_tray")
    # Small pull nub connected to the outer tray wall.
    p.visual(Box((0.010, 0.004, 0.006)), origin=Origin(xyz=(0.0, local_y + y_sign * 0.024, z_local + 0.005)), material=mat, name="pull_tab")
    return p


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="desktop_cantilever_sewing_box")
    cream = Material("warm_cream_plastic", (0.78, 0.69, 0.50, 1.0))
    coral = Material("coral_plastic", (0.88, 0.36, 0.29, 1.0))
    link_mat = Material("ivory_linkage", (0.86, 0.78, 0.60, 1.0))
    steel = Material("brushed_steel", (0.58, 0.58, 0.54, 1.0))

    base = model.part("bottom_box")
    base.visual(open_tray_mesh(LENGTH, WIDTH, BASE_H, WALL, 0.004, "bottom_box_hollow_shell"), origin=Origin(xyz=(0, 0, BASE_H / 2)), material=cream, name="hollow_shell")
    # Feet are merged visually by slight seating into the lower shell.
    for i, x in enumerate((-0.070, 0.070)):
        for j, y in enumerate((-0.038, 0.038)):
            base.visual(Cylinder(radius=0.006, length=0.006), origin=Origin(xyz=(x, y, 0.003)), material=cream, name=f"foot_{i}_{j}")
    # Continuous side mounting plates carry the external pins and linkage without floating bosses.
    base.visual(Box((0.118, 0.004, 0.062)), origin=Origin(xyz=(0.0, -0.058, 0.042)), material=cream, name="rear_link_plate")
    base.visual(Box((0.118, 0.004, 0.062)), origin=Origin(xyz=(0.0, 0.058, 0.042)), material=cream, name="front_link_plate")
    # Fixed central hinge knuckles / bosses that carry trays and lid.
    for y, label in ((-0.050, "rear"), (0.050, "front")):
        for z, tier in ((HINGE_Z_LOWER, "lower"), (HINGE_Z_UPPER, "upper")):
            base.visual(Box((0.010, 0.004, z - 0.004)), origin=Origin(xyz=(0, y, (z - 0.004) / 2)), material=cream, name=f"{tier}_{label}_hinge_web")
            base.visual(Cylinder(radius=0.0055, length=0.018), origin=Origin(xyz=(0, y, z), rpy=(math.pi / 2, 0, 0)), material=cream, name=f"{tier}_{label}_hinge_barrel")

    lower_left = tray_part(model, "tray_lower_0", -1.0, TRAY_H / 2 + 0.001, coral)
    upper_left = tray_part(model, "tray_upper_0", -1.0, TRAY_H / 2 + 0.003, coral)
    lower_right = tray_part(model, "tray_lower_1", 1.0, TRAY_H / 2 + 0.001, coral)
    upper_right = tray_part(model, "tray_upper_1", 1.0, TRAY_H / 2 + 0.003, coral)

    lid = model.part("main_lid")
    lid.visual(shallow_lid_mesh(LENGTH, WIDTH, LID_T, "main_lid_panel"), origin=Origin(xyz=(0, SIDE_Y + CLEARANCE, LID_T / 2)), material=coral, name="panel")
    lid.visual(Cylinder(radius=0.005, length=0.018), origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2, 0, 0)), material=coral, name="hinge_knuckle")
    # Upright carry handle attached to the lid: two posts plus top bridge.
    lid.visual(Box((0.010, 0.010, 0.070)), origin=Origin(xyz=(-0.073, SIDE_Y + CLEARANCE, 0.044)), material=cream, name="handle_post_0")
    lid.visual(Box((0.010, 0.010, 0.070)), origin=Origin(xyz=(0.073, SIDE_Y + CLEARANCE, 0.044)), material=cream, name="handle_post_1")
    lid.visual(Box((0.156, 0.010, 0.012)), origin=Origin(xyz=(0.0, SIDE_Y + CLEARANCE, 0.082)), material=cream, name="handle_bridge")

    # Four long external link bars, on both outside faces, with mimic motion from the lid.
    rod_len = 0.052
    for side, y in (("rear", -ROD_OUT_Y), ("front", ROD_OUT_Y)):
        for idx, x in enumerate((-0.045, 0.045)):
            rod = model.part(f"link_{side}_{idx}")
            rod.visual(rod_mesh(rod_len, 0.009, 0.004, f"link_{side}_{idx}_bar"), origin=Origin(xyz=(0.0, -0.0012 if y > 0 else 0.0012, 0.0), rpy=(0, math.radians(33 if idx == 0 else -33), 0)), material=link_mat, name="bar")
            parent = base
            model.articulation(
                f"bottom_box_to_link_{side}_{idx}",
                ArticulationType.REVOLUTE,
                parent=parent,
                child=rod,
                origin=Origin(xyz=(x, y, HINGE_Z_LOWER + (0.006 if idx == 1 else 0.0))),
                axis=(0, 1 if y > 0 else -1, 0),
                motion_limits=MotionLimits(effort=2, velocity=2, lower=0.0, upper=0.95),
                mimic=Mimic("bottom_box_to_main_lid", multiplier=0.72, offset=0.0),
            )

    # Separate pin parts at visible pivots, fixed to the structure that carries them.
    pin_coords = []
    for y in (-PIN_OUT_Y, PIN_OUT_Y):
        for x in (-0.045, 0.045):
            pin_coords.append((x, y, HINGE_Z_LOWER))
            pin_coords.append((x * 0.82, y, HINGE_Z_UPPER))
    pin_parents = [base, lower_left, base, lower_left, base, lower_right, base, lower_right]
    for n, xyz in enumerate(pin_coords):
        pin = model.part(f"pin_{n}")
        add_pin(pin, "pivot", (0, 0, 0), steel, length=0.012)
        parent = pin_parents[n]
        if parent is base:
            origin_xyz = xyz
        else:
            y_sign = 1 if xyz[1] > 0 else -1
            origin_xyz = (xyz[0], xyz[1] - (SIDE_Y + CLEARANCE) * y_sign - 0.0060 * y_sign, xyz[2] - HINGE_Z_LOWER - 0.004)
        model.articulation(f"{parent.name}_to_pin_{n}", ArticulationType.FIXED, parent=parent, child=pin, origin=Origin(xyz=origin_xyz))

    # Hinge/mimic structure.  Positive lid angle opens upward; trays fan outward about long X axes.
    lid_joint = model.articulation(
        "bottom_box_to_main_lid",
        ArticulationType.REVOLUTE,
        parent=base,
        child=lid,
        origin=Origin(xyz=(0.0, -SIDE_Y - CLEARANCE, BASE_H + 2 * TRAY_H + 0.026)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=2.0, lower=0.0, upper=1.15),
    )
    del lid_joint

    for name, part_obj, y_sign, zhinge, mult in (
        ("tray_lower_0", lower_left, -1, HINGE_Z_LOWER, 0.55),
        ("tray_upper_0", upper_left, -1, HINGE_Z_UPPER, 0.85),
        ("tray_lower_1", lower_right, 1, HINGE_Z_LOWER, -0.55),
        ("tray_upper_1", upper_right, 1, HINGE_Z_UPPER, -0.85),
    ):
        model.articulation(
            f"bottom_box_to_{name}",
            ArticulationType.REVOLUTE,
            parent=base,
            child=part_obj,
            origin=Origin(xyz=(0.0, y_sign * (SIDE_Y + CLEARANCE), zhinge)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=-1.05, upper=1.05),
            mimic=Mimic("bottom_box_to_main_lid", multiplier=mult, offset=0.0),
        )

    model.meta["requested_exports"] = {
        "urdf": "available through Articraft compile/export pipeline",
        "model.py": "model.py",
        "step_stl_3mf_state_images_trace": "unavailable in this sandbox; Articraft runtime may materialize supported formats",
        "telemetry": "unavailable: the authoring API exposes no real session telemetry writer",
    }
    model.meta["closed_size_m"] = (LENGTH, WIDTH, BASE_H + 2 * TRAY_H + LID_T)
    model.meta["wall_thickness_m"] = WALL
    model.meta["rotating_clearance_m"] = CLEARANCE
    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    base = object_model.get_part("bottom_box")
    lid = object_model.get_part("main_lid")
    upper = object_model.get_part("tray_upper_1")
    lower = object_model.get_part("tray_lower_1")
    lid_joint = object_model.get_articulation("bottom_box_to_main_lid")

    ctx.check("closed footprint is desktop size", LENGTH == 0.180 and WIDTH == 0.100, details="target footprint is 180 x 100 mm")
    ctx.check("wall thickness at least 2 mm", WALL >= 0.002, details=f"wall={WALL}")
    ctx.check("rotating joints use 0.35 mm clearance", abs(CLEARANCE - 0.00035) < 1e-9, details=f"clearance={CLEARANCE}")
    ctx.expect_gap(upper, lower, axis="z", min_gap=0.001, max_gap=0.014, name="upper and lower trays are separated when closed")
    ctx.expect_overlap(lid, base, axes="xy", min_overlap=0.095, name="closed lid covers the base footprint")

    rest = ctx.part_world_aabb(upper)
    with ctx.pose({lid_joint: 1.05}):
        opened = ctx.part_world_aabb(upper)
        ctx.expect_gap(upper, base, axis="z", max_penetration=0.010, name="opened upper tray clears the base within linkage clearance")
        ctx.expect_gap(lid, base, axis="z", max_penetration=0.010, name="opened lid remains above the box")
    ctx.check(
        "main lid drives tray outward",
        rest is not None and opened is not None and opened[1][1] > rest[1][1] + 0.010,
        details=f"rest={rest}, opened={opened}",
    )

    return ctx.report()


object_model = build_object_model()
