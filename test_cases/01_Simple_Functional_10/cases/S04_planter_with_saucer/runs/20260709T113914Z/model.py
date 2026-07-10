from __future__ import annotations

import cadquery as cq

from sdk import ArticulatedObject, ArticulationType, Material, Origin, TestContext, TestReport, mesh_from_cadquery


MM = 0.001


def build_planter_shape() -> cq.Workplane:
    outer_h = 130.0
    wall = 3.0
    top_outer_d = 120.0
    bottom_outer_d = 82.0
    fillet_r = 2.0
    drain_d = 10.0

    outer = (
        cq.Workplane("XZ")
        .moveTo(bottom_outer_d / 2.0, 0.0)
        .lineTo(top_outer_d / 2.0, outer_h)
        .lineTo(0.0, outer_h)
        .lineTo(0.0, 0.0)
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
    )
    outer = outer.edges(">Z").fillet(fillet_r)

    inner = (
        cq.Workplane("XZ")
        .moveTo(bottom_outer_d / 2.0 - wall, wall)
        .lineTo(top_outer_d / 2.0 - wall, outer_h - wall)
        .lineTo(0.0, outer_h - wall)
        .lineTo(0.0, wall)
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
    )

    drain = cq.Workplane("XY").circle(drain_d / 2.0).extrude(12.0, both=True)

    planter = outer.cut(inner).cut(drain)
    return planter.translate((0.0, 0.0, -outer_h / 2.0))



def build_saucer_shape() -> cq.Workplane:
    height = 18.0
    outer_d = 140.0
    base_d = 108.0
    floor_t = 4.0
    lip_r = 2.0

    outer = (
        cq.Workplane("XZ")
        .moveTo(base_d / 2.0, 0.0)
        .lineTo(outer_d / 2.0, height * 0.72)
        .lineTo(outer_d / 2.0, height)
        .lineTo(0.0, height)
        .lineTo(0.0, 0.0)
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
    )
    outer = outer.edges(">Z").fillet(lip_r)

    recess = (
        cq.Workplane("XZ")
        .moveTo(0.0, floor_t)
        .lineTo(52.0, floor_t)
        .lineTo(56.0, 10.0)
        .lineTo(58.0, 14.0)
        .lineTo(0.0, 14.0)
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
    )

    saucer = outer.cut(recess)
    return saucer.translate((0.0, 0.0, -height / 2.0))



def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="planter_with_saucer")

    ceramic = Material("ceramic_beige", color=(0.83, 0.77, 0.66, 1.0))

    planter = model.part("planter")
    planter.visual(
        mesh_from_cadquery(build_planter_shape(), "planter", unit_scale=MM),
        material=ceramic,
        name="body",
    )

    saucer = model.part("saucer")
    saucer.visual(
        mesh_from_cadquery(build_saucer_shape(), "saucer", unit_scale=MM),
        material=ceramic,
        name="dish",
    )

    model.articulation(
        "planter_to_saucer",
        ArticulationType.FIXED,
        parent=planter,
        child=saucer,
        origin=Origin(xyz=(0.0, 0.0, -0.074)),
    )

    return model



def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    planter = object_model.get_part("planter")
    saucer = object_model.get_part("saucer")

    ctx.expect_gap(planter, saucer, axis="z", min_gap=0.0, max_gap=0.008, positive_elem="body", negative_elem="dish", name="planter sits just above saucer")
    ctx.expect_overlap(planter, saucer, axes="xy", elem_a="body", elem_b="dish", min_overlap=0.08, name="planter nests over saucer recess")

    return ctx.report()


object_model = build_object_model()