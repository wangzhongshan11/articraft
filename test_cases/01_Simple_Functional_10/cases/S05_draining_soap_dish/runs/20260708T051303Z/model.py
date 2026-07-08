from __future__ import annotations

import cadquery as cq

from sdk import ArticulatedObject, Material, Origin, TestContext, TestReport, mesh_from_cadquery


MM = 0.001


def _rounded_prism(width: float, depth: float, radius: float, height: float, z0: float) -> cq.Workplane:
    """Rounded rectangle extrusion in millimetres, centered on X/Y and extruded upward."""
    prism = cq.Workplane("XY").rect(width, depth).extrude(height)
    if radius > 0.0:
        prism = prism.edges("|Z").fillet(radius)
    return prism.translate((0.0, 0.0, z0))


def _build_soap_dish_cad() -> cq.Workplane:
    # Dimensions are authored in millimetres and converted to metres at mesh export.
    length = 130.0
    width = 90.0
    foot_height = 7.5
    tray_bottom_z = 7.0
    tray_height = 23.0
    top_z = tray_bottom_z + tray_height

    # Single printable tray shell: broad rounded rectangular outside with a raised rim.
    body = _rounded_prism(length, width, 14.0, tray_height, tray_bottom_z)

    # Hollow, shallow basin. The cut leaves a continuous perimeter wall and a structural floor.
    body = (
        body.faces(">Z")
        .workplane(centerOption="CenterOfMass")
        .rect(112.0, 72.0)
        .cutBlind(-17.0)
    )

    # A very shallow, rounded depression in the floor helps keep a soap bar centered.
    basin_recess = (
        cq.Workplane("XY")
        .rect(94.0, 54.0)
        .extrude(3.2)
        .edges("|Z")
        .fillet(10.0)
        .translate((0.0, 0.0, top_z - 17.0 - 1.8))
    )
    body = body.cut(basin_recess)

    # Five parallel rounded drainage slots through the tray floor.
    for y in (-22.0, -11.0, 0.0, 11.0, 22.0):
        slot_cutter = (
            cq.Workplane("XY")
            .center(0.0, y)
            .slot2D(58.0, 7.0)
            .extrude(22.0)
            .translate((0.0, 0.0, 2.0))
        )
        body = body.cut(slot_cutter)

    # Four short integral feet raise the underside for drainage airflow.
    for x in (-43.0, 43.0):
        for y in (-27.0, 27.0):
            foot = _rounded_prism(20.0, 14.0, 4.0, foot_height, 0.0).translate((x, y, 0.0))
            body = body.union(foot)

    # Small manufacturable softening on horizontal outside/foot edges where CadQuery can solve it.
    try:
        body = body.edges("<Z or >Z").fillet(1.2)
    except Exception:
        pass

    return body


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="draining_soap_dish")

    ceramic_sage = Material("matte_sage_green_plastic", rgba=(0.62, 0.69, 0.60, 1.0))

    dish = model.part("soap_dish")
    dish.visual(
        mesh_from_cadquery(
            _build_soap_dish_cad(),
            "soap_dish_shell",
            tolerance=0.35,
            angular_tolerance=0.08,
            unit_scale=MM,
        ),
        origin=Origin(),
        material=ceramic_sage,
        name="single_printed_body",
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    dish = object_model.get_part("soap_dish")

    aabb = ctx.part_world_aabb(dish)
    if aabb is not None:
        lo, hi = aabb
        size = (hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2])
        ctx.check(
            "soap dish footprint is 130 by 90 mm",
            abs(size[0] - 0.130) < 0.003 and abs(size[1] - 0.090) < 0.003,
            details=f"measured size={size}",
        )
        ctx.check(
            "short feet lift the basin above the counter",
            0.006 <= size[2] <= 0.040,
            details=f"measured height={size[2]}",
        )
    else:
        ctx.fail("soap dish has measurable bounds", "part_world_aabb returned None")

    return ctx.report()


object_model = build_object_model()
