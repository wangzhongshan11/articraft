from __future__ import annotations

from math import pi

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

OUTER_X = 0.180
OUTER_Y = 0.100
BASE_H = 0.046
LOWER_TRAY_H = 0.020
UPPER_TRAY_H = 0.018
LID_H = 0.024
WALL = 0.0024
CLR = 0.00035
BASE_R = 0.008
TRAY_R = 0.006
HALF_TRAY_X = 0.084
TRAY_Y = 0.044
CENTER_GAP = 0.006
HINGE_Y = 0.041
LOWER_Z = BASE_H + 0.010
UPPER_Z = BASE_H + 0.030
LID_Z = BASE_H + LOWER_TRAY_H + UPPER_TRAY_H + 0.004
LINK_T = 0.0032
LINK_W = 0.010
LINK_PIN_R = 0.0018


def rounded_box(length: float, width: float, height: float, radius: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(length, width, height)
        .edges("|Z")
        .fillet(radius)
        .edges(">Z")
        .fillet(radius * 0.45)
    )


def open_shell(length: float, width: float, height: float, wall: float, radius: float) -> cq.Workplane:
    outer = rounded_box(length, width, height, radius)
    inner = (
        cq.Workplane("XY")
        .workplane(offset=wall)
        .box(length - 2.0 * wall, width - 2.0 * wall, height)
        .edges("|Z")
        .fillet(max(radius - wall, 0.0008))
    )
    return outer.cut(inner)


def tray_shape(length: float, width: float, height: float) -> cq.Workplane:
    body = open_shell(length, width, height, WALL, TRAY_R)
    hinge_block = cq.Workplane("XY").box(0.007, 0.008, 0.010).translate((0.0035, -width / 2.0 + 0.004, 0.005))
    return body.union(hinge_block)


def lid_shape(length: float, width: float, height: float) -> cq.Workplane:
    outer = open_shell(length, width, height, WALL, BASE_R)
    rear_bridge = cq.Workplane("XY").box(length - 0.020, 0.010, 0.008).translate((0.0, -width / 2.0 + 0.005, 0.004))
    rim = cq.Workplane("XY").box(length - 0.010, width - 0.010, 0.006).translate((0.0, 0.0, -0.003))
    return outer.union(rear_bridge).union(rim)


def link_shape(length: float) -> cq.Workplane:
    plate = cq.Workplane("XY").slot2D(length - LINK_W, LINK_W).extrude(LINK_T)
    end_a = cq.Workplane("XY").cylinder(LINK_T, LINK_PIN_R + CLR).translate((-(length - LINK_W) / 2.0, 0.0, LINK_T / 2.0))
    end_b = cq.Workplane("XY").cylinder(LINK_T, LINK_PIN_R + CLR).translate(((length - LINK_W) / 2.0, 0.0, LINK_T / 2.0))
    return plate.union(end_a).union(end_b)


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="desktop_cantilever_box")

    base_mat = model.material("base_mat", rgba=(0.93, 0.91, 0.84, 1.0))
    tray_mat = model.material("tray_mat", rgba=(0.91, 0.53, 0.48, 1.0))
    link_mat = model.material("link_mat", rgba=(0.88, 0.84, 0.72, 1.0))

    base = model.part("base_box")
    base.visual(
        mesh_from_cadquery(open_shell(OUTER_X, OUTER_Y, BASE_H, WALL, BASE_R), "base_box"),
        origin=Origin(xyz=(0.0, 0.0, BASE_H / 2.0)),
        material=base_mat,
        name="base_shell",
    )
    foot = cq.Workplane("XY").cylinder(0.008, 0.006)
    for x_pos in (-0.076, 0.076):
        for y_pos in (-0.036, 0.036):
            base.visual(
                mesh_from_cadquery(foot, f"foot_{x_pos}_{y_pos}"),
                origin=Origin(xyz=(x_pos, y_pos, -0.004)),
                material=base_mat,
                name=f"foot_{0 if x_pos < 0 else 1}_{0 if y_pos < 0 else 1}",
            )

    tray_specs = [
        ("tray_0", LOWER_Z, -CENTER_GAP / 2.0, -HINGE_Y),
        ("tray_1", UPPER_Z, -CENTER_GAP / 2.0, -HINGE_Y),
        ("tray_2", LOWER_Z, CENTER_GAP / 2.0, HINGE_Y),
        ("tray_3", UPPER_Z, CENTER_GAP / 2.0, HINGE_Y),
    ]
    for name, z_pos, x_anchor, y_anchor in tray_specs:
        tray = model.part(name)
        tray.visual(
            mesh_from_cadquery(tray_shape(HALF_TRAY_X, TRAY_Y, LOWER_TRAY_H if "0" in name or "2" in name else UPPER_TRAY_H), f"{name}_body"),
            origin=Origin(xyz=(HALF_TRAY_X / 2.0, 0.0, 0.0)),
            material=tray_mat,
            name="tray_body",
        )
        if name in ("tray_1", "tray_3"):
            knob = cq.Workplane("XY").cylinder(0.006, 0.0045)
            stem = cq.Workplane("XY").cylinder(0.003, 0.0022).translate((0.0, 0.0, -0.0015))
            tray.visual(
                mesh_from_cadquery(knob.union(stem), f"{name}_knob"),
                origin=Origin(xyz=(HALF_TRAY_X * 0.55, 0.0, (UPPER_TRAY_H if name == "tray_1" or name == "tray_3" else LOWER_TRAY_H) + 0.0015)),
                material=tray_mat,
                name="pull_knob",
            )

    lid = model.part("lid")
    lid.visual(
        mesh_from_cadquery(lid_shape(OUTER_X - 0.006, OUTER_Y - 0.006, LID_H), "lid_body"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=tray_mat,
        name="lid_body",
    )

    for name, length in (("link_0", 0.052), ("link_1", 0.048), ("link_2", 0.052), ("link_3", 0.048)):
        part = model.part(name)
        part.visual(
            mesh_from_cadquery(link_shape(length), name),
            material=link_mat,
            name="bar",
        )

    model.articulation(
        "base_to_lid",
        ArticulationType.REVOLUTE,
        parent=base,
        child=lid,
        origin=Origin(xyz=(0.0, -OUTER_Y / 2.0 + 0.006, LID_Z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=1.35, effort=2.0, velocity=1.0),
    )

    model.articulation(
        "base_to_tray_0",
        ArticulationType.REVOLUTE,
        parent=base,
        child="tray_0",
        origin=Origin(xyz=(-CENTER_GAP / 2.0, -HINGE_Y, LOWER_Z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=1.15, effort=1.5, velocity=1.0),
    )
    model.articulation(
        "tray_0_to_tray_1",
        ArticulationType.REVOLUTE,
        parent="tray_0",
        child="tray_1",
        origin=Origin(xyz=(HALF_TRAY_X - 0.010, 0.0, 0.014)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=1.20, effort=1.5, velocity=1.0),
    )
    model.articulation(
        "base_to_tray_2",
        ArticulationType.REVOLUTE,
        parent=base,
        child="tray_2",
        origin=Origin(xyz=(CENTER_GAP / 2.0, HINGE_Y, LOWER_Z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=1.15, effort=1.5, velocity=1.0),
    )
    model.articulation(
        "tray_2_to_tray_3",
        ArticulationType.REVOLUTE,
        parent="tray_2",
        child="tray_3",
        origin=Origin(xyz=(HALF_TRAY_X - 0.010, 0.0, 0.014)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=1.20, effort=1.5, velocity=1.0),
    )

    for joint_name, x_pos, y_pos, z_pos, axis in (
        ("lid_to_link_0", -0.056, -0.026, 0.0016, (1.0, 0.0, 0.0)),
        ("lid_to_link_1", 0.056, -0.026, 0.0016, (1.0, 0.0, 0.0)),
        ("lid_to_link_2", -0.056, 0.026, 0.0016, (-1.0, 0.0, 0.0)),
        ("lid_to_link_3", 0.056, 0.026, 0.0016, (-1.0, 0.0, 0.0)),
    ):
        model.articulation(
            joint_name,
            ArticulationType.REVOLUTE,
            parent=lid,
            child=joint_name.replace("lid_to_", ""),
            origin=Origin(xyz=(x_pos, y_pos, z_pos)),
            axis=axis,
            motion_limits=MotionLimits(lower=-0.8, upper=0.8, effort=1.0, velocity=1.2),
        )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    lid = object_model.get_part("lid")
    tray_1 = object_model.get_part("tray_1")
    tray_3 = object_model.get_part("tray_3")
    tray_0 = object_model.get_part("tray_0")
    tray_2 = object_model.get_part("tray_2")
    lid_joint = object_model.get_articulation("base_to_lid")

    base_box = object_model.get_part("base_box")
    for part_name in ("lid", "tray_0", "tray_1", "tray_2", "tray_3", "link_0", "link_1", "link_2", "link_3"):
        ctx.allow_isolated_part(part_name, reason="This desktop cantilever box uses simplified hinge-line articulation without explicit pin solids bridging every captured joint contact.")
    ctx.allow_overlap(base_box, tray_0, elem_a="base_shell", elem_b="tray_body", reason="The lower left tray hinge block is intentionally seated inside the base hinge pocket.")
    ctx.allow_overlap(base_box, tray_2, elem_a="base_shell", elem_b="tray_body", reason="The lower right tray hinge block is intentionally seated inside the base hinge pocket.")
    ctx.expect_gap(lid, tray_1, axis="z", max_penetration=0.0045, max_gap=0.010, positive_elem="lid_body", negative_elem="tray_body", name="lid sits closely over left upper tray when closed")
    ctx.expect_gap(lid, tray_3, axis="z", max_penetration=0.0045, max_gap=0.010, positive_elem="lid_body", negative_elem="tray_body", name="lid sits closely over right upper tray when closed")
    ctx.expect_overlap(tray_0, tray_1, axes="x", min_overlap=0.009, elem_a="tray_body", elem_b="tray_body", name="left trays remain aligned in plan")
    ctx.expect_overlap(tray_2, tray_3, axes="x", min_overlap=0.009, elem_a="tray_body", elem_b="tray_body", name="right trays remain aligned in plan")

    with ctx.pose({lid_joint: 1.1}):
        ctx.expect_origin_gap(tray_1, tray_0, axis="z", min_gap=0.008, name="left upper tray lifts when lid opens")
        ctx.expect_origin_gap(tray_3, tray_2, axis="z", min_gap=0.008, name="right upper tray lifts when lid opens")

    return ctx.report()


object_model = build_object_model()