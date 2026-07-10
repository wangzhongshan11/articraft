from __future__ import annotations

import cadquery as cq

from sdk import ArticulatedObject, ArticulationType, Material, Origin, TestContext, TestReport, mesh_from_cadquery


PANEL_LENGTH = 0.150
PANEL_HEIGHT = 0.090
PANEL_THICKNESS = 0.005
SLOT_WIDTH = 0.0054
SLOT_DEPTH = PANEL_HEIGHT / 2.0
CORNER_RADIUS = 0.004


def make_divider_panel() -> cq.Workplane:
    length_mm = PANEL_LENGTH * 1000.0
    height_mm = PANEL_HEIGHT * 1000.0
    thickness_mm = PANEL_THICKNESS * 1000.0
    slot_width_mm = SLOT_WIDTH * 1000.0
    slot_depth_mm = SLOT_DEPTH * 1000.0
    corner_radius_mm = CORNER_RADIUS * 1000.0

    panel = cq.Workplane("XY").box(length_mm, thickness_mm, height_mm)
    panel = panel.edges(">Z").fillet(corner_radius_mm)

    slot = (
        cq.Workplane("XZ")
        .center(0, height_mm / 4.0)
        .box(slot_width_mm, slot_depth_mm, thickness_mm * 3.0)
    )
    panel = panel.cut(slot)

    notch_width_mm = 6.0
    notch_depth_mm = 2.0
    notch_height_mm = 12.0
    for x in (-length_mm / 2.0 + notch_width_mm / 2.0, length_mm / 2.0 - notch_width_mm / 2.0):
        notch = (
            cq.Workplane("XZ")
            .center(x, 0)
            .box(notch_width_mm, notch_height_mm, thickness_mm * 3.0)
        )
        panel = panel.cut(notch)

    return panel


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="modular_drawer_divider")
    panel_material = Material("beige_plastic", rgba=(0.86, 0.82, 0.74, 1.0))

    panel_mesh = mesh_from_cadquery(make_divider_panel(), "divider_panel", unit_scale=0.001)

    placements = [
        ("panel_0", (0.0, -0.0375, 0.045), (0.0, 0.0, 0.0)),
        ("panel_1", (0.0, 0.0375, 0.045), (0.0, 0.0, 0.0)),
        ("panel_2", (-0.0375, 0.0, 0.045), (0.0, 0.0, 1.57079632679)),
        ("panel_3", (0.0375, 0.0, 0.045), (0.0, 0.0, 1.57079632679)),
    ]

    parts = []
    for name, xyz, rpy in placements:
        part = model.part(name)
        part.visual(panel_mesh, origin=Origin(xyz=xyz, rpy=rpy), material=panel_material, name="panel")
        parts.append(part)

    for index, child in enumerate(parts[1:], start=1):
        model.articulation(
            f"panel_mount_{index}",
            ArticulationType.FIXED,
            parent=parts[0],
            child=child,
            origin=Origin(),
        )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    panel_0 = object_model.get_part("panel_0")
    panel_1 = object_model.get_part("panel_1")
    panel_2 = object_model.get_part("panel_2")
    panel_3 = object_model.get_part("panel_3")

    ctx.allow_overlap(panel_0, panel_2, reason="Cross-lapped divider panels intentionally occupy the same central slot volume.")
    ctx.allow_overlap(panel_0, panel_3, reason="Cross-lapped divider panels intentionally occupy the same central slot volume.")
    ctx.allow_overlap(panel_1, panel_2, reason="Cross-lapped divider panels intentionally occupy the same central slot volume.")
    ctx.allow_overlap(panel_1, panel_3, reason="Cross-lapped divider panels intentionally occupy the same central slot volume.")
    ctx.expect_gap(panel_1, panel_0, axis="y", min_gap=0.063, max_gap=0.065, name="parallel divider rows are evenly spaced")
    ctx.expect_overlap(panel_0, panel_2, axes="xy", min_overlap=0.009, name="cross slots align at each intersection")
    ctx.expect_gap(panel_3, panel_2, axis="x", min_gap=0.063, max_gap=0.065, name="cross divider columns are evenly spaced")

    return ctx.report()


object_model = build_object_model()