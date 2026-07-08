from __future__ import annotations

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Material,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)


# Dimensions are authored in millimetres in CadQuery, then scaled to metres when
# attached to the SDK model.  The enclosure is centred in X/Y and rests on Z=0.
WALL = 2.8
CLEARANCE = 0.35


def _rounded_block(length: float, width: float, height: float, z_min: float, radius: float) -> cq.Workplane:
    """Rounded-rectangle prism with vertical corner radii."""
    return (
        cq.Workplane("XY")
        .box(length, width, height)
        .edges("|Z")
        .fillet(radius)
        .translate((0, 0, z_min + height / 2.0))
    )


def _tray_shell() -> cq.Workplane:
    tray_l = 153.5
    tray_w = 113.5
    tray_h = 17.0
    corner_r = 8.0

    shell = _rounded_block(tray_l, tray_w, tray_h, 0.0, corner_r)

    # Open top cavity: 2.8 mm bottom and walls, with matching internal corner radii.
    inner = (
        cq.Workplane("XY")
        .box(tray_l - 2 * WALL, tray_w - 2 * WALL, tray_h * 2.0)
        .edges("|Z")
        .fillet(max(0.5, corner_r - WALL))
        .translate((0, 0, WALL + tray_h))
    )
    shell = shell.cut(inner)

    # Rounded side connector cutout on the front wall, clear of the bottom floor.
    connector_cut = (
        cq.Workplane("XZ")
        .center(0, 9.5)
        .slot2D(26.0, 10.0)
        .extrude(14.0)
        .translate((0, -tray_w / 2.0 - 7.0, 0))
    )
    shell = shell.cut(connector_cut)

    # Four internal screw bosses and small reinforcing ribs, all fused to the tray floor.
    boss_positions = [(-60.0, -40.0), (-60.0, 40.0), (60.0, -40.0), (60.0, 40.0)]
    boss_outer_r = 4.3
    boss_inner_r = 1.65
    boss_h = 12.0
    for x, y in boss_positions:
        boss = cq.Workplane("XY").circle(boss_outer_r).extrude(boss_h).translate((x, y, WALL))
        # Rib pair ties the boss to adjacent walls and makes the boss location readable.
        sx = 1.0 if x > 0 else -1.0
        sy = 1.0 if y > 0 else -1.0
        rib_x_len = (tray_l / 2.0 - WALL) - abs(x) - boss_outer_r + 0.6
        rib_y_len = (tray_w / 2.0 - WALL) - abs(y) - boss_outer_r + 0.6
        rib_x = (
            cq.Workplane("XY")
            .box(max(1.0, rib_x_len), 1.8, 7.0)
            .translate((x + sx * (boss_outer_r + rib_x_len / 2.0 - 0.3), y, WALL + 3.5))
        )
        rib_y = (
            cq.Workplane("XY")
            .box(1.8, max(1.0, rib_y_len), 7.0)
            .translate((x, y + sy * (boss_outer_r + rib_y_len / 2.0 - 0.3), WALL + 3.5))
        )
        shell = shell.union(boss).union(rib_x).union(rib_y)
        pilot = cq.Workplane("XY").circle(boss_inner_r).extrude(boss_h + 1.0).translate((x, y, WALL + 1.0))
        shell = shell.cut(pilot)

    # Subtle outside bottom round-over after the major boolean work.
    return shell


def _cover_shell() -> cq.Workplane:
    cover_l = 160.0
    cover_w = 120.0
    cover_z0 = 15.0
    cover_h = 15.0
    top_thick = 2.8
    corner_r = 8.5

    cover = _rounded_block(cover_l, cover_w, cover_h, cover_z0, corner_r)

    # Open bottom cavity.  Inner size leaves about 0.35 mm side clearance over the tray.
    inner_l = 153.5 + 2.0 * CLEARANCE
    inner_w = 113.5 + 2.0 * CLEARANCE
    cavity = (
        cq.Workplane("XY")
        .box(inner_l, inner_w, cover_h - top_thick + 1.0)
        .edges("|Z")
        .fillet(max(0.5, corner_r - WALL))
        .translate((0, 0, cover_z0 - 0.5 + (cover_h - top_thick + 1.0) / 2.0))
    )
    cover = cover.cut(cavity)

    # Shallow recessed rectangular field for the ventilation array.
    recess = (
        cq.Workplane("XY")
        .box(104.0, 62.0, 0.8)
        .edges("|Z")
        .fillet(3.0)
        .translate((0, 0, 29.75))
    )
    cover = cover.cut(recess)

    # Through-hole ventilation pattern on the cover top.
    points = []
    cols = 12
    rows = 7
    pitch_x = 7.6
    pitch_y = 7.0
    for row in range(rows):
        for col in range(cols):
            points.append(((col - (cols - 1) / 2.0) * pitch_x, (row - (rows - 1) / 2.0) * pitch_y))
    vents = cq.Workplane("XY").pushPoints(points).circle(2.0).extrude(8.0).translate((0, 0, 24.0))
    cover = cover.cut(vents)

    # Four short cover-side receiving sleeves aligned with the tray bosses.
    for x, y in [(-60.0, -40.0), (-60.0, 40.0), (60.0, -40.0), (60.0, 40.0)]:
        # A cover standoff extends down to seat on the matching tray boss; it is
        # slightly fused into the top skin so it remains one manufacturable cover.
        sleeve = cq.Workplane("XY").circle(4.8).extrude(14.4).translate((x, y, 14.6))
        sleeve_hole = cq.Workplane("XY").circle(2.3).extrude(15.2).translate((x, y, 14.2))
        cover = cover.union(sleeve).cut(sleeve_hole)

    return cover


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="compact_protective_enclosure")

    tray_mat = Material("slightly_darker_molded_abs", rgba=(0.46, 0.46, 0.52, 1.0))
    cover_mat = Material("light_gray_molded_abs", rgba=(0.68, 0.68, 0.75, 1.0))
    model.materials.extend([tray_mat, cover_mat])

    tray = model.part("lower_tray")
    tray.visual(
        mesh_from_cadquery(_tray_shell(), "lower_tray_shell", tolerance=0.08, angular_tolerance=0.18, unit_scale=0.001),
        material=tray_mat,
        name="tray_shell",
    )

    cover = model.part("upper_cover")
    cover.visual(
        mesh_from_cadquery(_cover_shell(), "upper_cover_shell", tolerance=0.08, angular_tolerance=0.18, unit_scale=0.001),
        material=cover_mat,
        name="cover_shell",
    )

    model.articulation(
        "tray_to_cover",
        ArticulationType.FIXED,
        parent=tray,
        child=cover,
        origin=Origin(),
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    tray = object_model.get_part("lower_tray")
    cover = object_model.get_part("upper_cover")

    # The cover is a close-fitting cap around the tray, not a fused single block.
    ctx.expect_within(
        tray,
        cover,
        axes="xy",
        margin=0.004,
        name="tray footprint fits inside cover clearance envelope",
    )
    ctx.expect_overlap(
        tray,
        cover,
        axes="z",
        min_overlap=0.001,
        name="cover skirt overlaps tray height at assembled seam",
    )

    tray_aabb = ctx.part_world_aabb(tray)
    cover_aabb = ctx.part_world_aabb(cover)
    if tray_aabb is not None and cover_aabb is not None:
        mins = [min(tray_aabb[0][i], cover_aabb[0][i]) for i in range(3)]
        maxs = [max(tray_aabb[1][i], cover_aabb[1][i]) for i in range(3)]
        size = [maxs[i] - mins[i] for i in range(3)]
        ctx.check(
            "assembled size is 160 by 120 by 30 mm",
            abs(size[0] - 0.160) < 0.002 and abs(size[1] - 0.120) < 0.002 and abs(size[2] - 0.030) < 0.002,
            details=f"assembled size={size}",
        )
    else:
        ctx.fail("assembled size is 160 by 120 by 30 mm", "missing part AABB")

    return ctx.report()


object_model = build_object_model()
