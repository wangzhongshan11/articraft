from __future__ import annotations

import cadquery as cq

from sdk import ArticulatedObject, Material, TestContext, TestReport, mesh_from_cadquery


MM = 0.001

OUTER_X = 160.0
OUTER_Y = 120.0
HEIGHT = 90.0
WALL = 3.0
BOTTOM = 3.5
DRAFT = 1.8
R_OUT = 9.0
TOP_FLANGE = 4.0
TOP_BAND = 6.0
LABEL_W = 64.0
LABEL_H = 28.0
LABEL_DEPTH = 1.2
STACK_RECESS_DEPTH = 2.4
STACK_RECESS_MARGIN = 7.0
FOOT_W = 18.0
FOOT_D = 18.0
FOOT_H = 2.4


def rrect(workplane: cq.Workplane, x: float, y: float, r: float) -> cq.Workplane:
    return workplane.rect(x - 2 * r, y - 2 * r).vertices().fillet(r)


def build_bin_shape() -> cq.Workplane:
    outer_bottom_x = OUTER_X - 2.0 * DRAFT
    outer_bottom_y = OUTER_Y - 2.0 * DRAFT
    inner_top_x = OUTER_X - 2.0 * WALL
    inner_top_y = OUTER_Y - 2.0 * WALL
    inner_bottom_x = outer_bottom_x - 2.0 * WALL
    inner_bottom_y = outer_bottom_y - 2.0 * WALL

    shell = (
        cq.Workplane("XY")
        .box(outer_bottom_x, outer_bottom_y, HEIGHT)
        .edges("|Z")
        .fillet(R_OUT - 1.5)
    )
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=BOTTOM)
        .box(inner_bottom_x, inner_bottom_y, HEIGHT)
        .edges("|Z")
        .fillet(max(R_OUT - WALL - 1.0, 3.0))
    )
    shell = shell.cut(cavity)

    lip = (
        cq.Workplane("XY")
        .workplane(offset=HEIGHT / 2.0 - TOP_BAND / 2.0)
        .box(OUTER_X + 2.0 * TOP_FLANGE, OUTER_Y + 2.0 * TOP_FLANGE, TOP_BAND)
        .edges("|Z")
        .fillet(R_OUT)
    )
    lip_open = (
        cq.Workplane("XY")
        .workplane(offset=HEIGHT / 2.0 - TOP_BAND / 2.0)
        .box(inner_top_x, inner_top_y, TOP_BAND + 1.0)
        .edges("|Z")
        .fillet(max(R_OUT - WALL, 3.0))
    )
    shell = shell.union(lip.cut(lip_open))

    label_cut = (
        cq.Workplane("XZ")
        .workplane(offset=OUTER_Y / 2.0 - LABEL_DEPTH / 2.0)
        .center(0.0, 40.0)
        .box(LABEL_W, LABEL_DEPTH, LABEL_H)
    )
    shell = shell.cut(label_cut)

    scoop = (
        cq.Workplane("YZ")
        .workplane(offset=0.0)
        .center(OUTER_Y / 2.0 - 1.0, HEIGHT - 10.0)
        .box(18.0, 58.0, 18.0)
    )
    shell = shell.cut(scoop)

    recess_outer = (
        cq.Workplane("XY")
        .box(outer_bottom_x - 2.0 * STACK_RECESS_MARGIN, outer_bottom_y - 2.0 * STACK_RECESS_MARGIN, STACK_RECESS_DEPTH)
        .edges("|Z")
        .fillet(4.0)
    )
    recess_inner = (
        cq.Workplane("XY")
        .box(outer_bottom_x - 2.0 * STACK_RECESS_MARGIN - 12.0, outer_bottom_y - 2.0 * STACK_RECESS_MARGIN - 12.0, STACK_RECESS_DEPTH + 0.2)
        .edges("|Z")
        .fillet(2.0)
    )
    shell = shell.cut(recess_outer.cut(recess_inner))


    return shell.translate((0.0, 0.0, 0.0))


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="stackable_parts_bin")
    plastic = Material(name="bin_plastic", rgba=(0.43, 0.49, 0.57, 1.0))

    body = model.part("bin")
    body.visual(
        mesh_from_cadquery(build_bin_shape(), "bin_body", unit_scale=MM),
        material=plastic,
        name="body",
    )
    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    return ctx.report()


object_model = build_object_model()