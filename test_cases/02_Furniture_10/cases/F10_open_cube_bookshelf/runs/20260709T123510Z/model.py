from __future__ import annotations

import cadquery as cq

from sdk import ArticulatedObject, Material, TestContext, TestReport, mesh_from_cadquery


WIDTH = 1.000
DEPTH = 0.300
HEIGHT = 1.200
PANEL = 0.022
GROOVE_DEPTH = 0.006
EDGE_RADIUS = 0.003

CELL_WIDTH = (WIDTH - 4 * PANEL) / 3
CELL_HEIGHT = (HEIGHT - 4 * PANEL) / 3


def _bookshelf_shape() -> cq.Workplane:
    outer = cq.Workplane("XY").box(WIDTH, DEPTH, HEIGHT)
    inner = (
        cq.Workplane("XY")
        .box(WIDTH - 2 * PANEL, DEPTH - PANEL, HEIGHT - 2 * PANEL)
        .translate((0.0, PANEL * 0.5, 0.0))
    )
    shell = outer.cut(inner)

    groove_y = -DEPTH / 2 + GROOVE_DEPTH / 2
    groove = (
        cq.Workplane("XY")
        .box(WIDTH - 2 * PANEL, GROOVE_DEPTH, HEIGHT - 2 * PANEL)
        .translate((0.0, groove_y, 0.0))
    )
    shell = shell.cut(groove)

    shelf_span = WIDTH - 2 * PANEL
    for i in range(2):
        z = -HEIGHT / 2 + PANEL + CELL_HEIGHT * (i + 1) + PANEL * i + PANEL / 2
        shelf = cq.Workplane("XY").box(shelf_span, DEPTH - PANEL, PANEL).translate((0.0, PANEL * 0.5, z))
        shell = shell.union(shelf)

    divider_height = HEIGHT - 2 * PANEL
    for i in range(2):
        x = -WIDTH / 2 + PANEL + CELL_WIDTH * (i + 1) + PANEL * i + PANEL / 2
        divider = (
            cq.Workplane("XY")
            .box(PANEL, DEPTH - PANEL, divider_height)
            .translate((x, PANEL * 0.5, 0.0))
        )
        shell = shell.union(divider)

    return shell.edges("|Z and >Y").fillet(EDGE_RADIUS)


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="open_cube_bookshelf")
    oak = model.material("oak", rgba=(0.72, 0.58, 0.38, 1.0))

    frame = model.part("bookshelf")
    frame.visual(
        mesh_from_cadquery(_bookshelf_shape(), "open_cube_bookshelf", unit_scale=1.0),
        material=oak,
        name="carcass",
    )
    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    shelf = object_model.get_part("bookshelf")
    aabb = ctx.part_world_aabb(shelf)
    ctx.check("bookshelf_present", shelf is not None, "Bookshelf part missing.")
    ctx.check("bookshelf_aabb_present", aabb is not None, "Bookshelf AABB missing.")
    if aabb is None:
        return ctx.report()

    mins, maxs = aabb
    size = tuple(maxs[i] - mins[i] for i in range(3))
    ctx.check("width_1000mm", abs(size[0] - WIDTH) < 0.005, f"size={size!r}")
    ctx.check("depth_300mm", abs(size[1] - DEPTH) < 0.005, f"size={size!r}")
    ctx.check("height_1200mm", abs(size[2] - HEIGHT) < 0.005, f"size={size!r}")
    return ctx.report()


object_model = build_object_model()