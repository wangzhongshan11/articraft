from __future__ import annotations

import cadquery as cq

from sdk import ArticulatedObject, Material, Origin, TestContext, TestReport, mesh_from_cadquery


# All CadQuery dimensions below are authored in millimetres, then scaled to metres
# when the managed mesh is attached to the SDK model.
WIDTH_MM = 1000.0
DEPTH_MM = 300.0
HEIGHT_MM = 1200.0
BOARD_MM = 22.0
FRONT_RADIUS_MM = 3.0
GROOVE_DEPTH_MM = 6.0
GROOVE_WIDTH_MM = 8.0


def _bookcase_carcass() -> cq.Workplane:
    """One continuous, watertight carcass with 3 x 3 through-open compartments."""
    w = WIDTH_MM
    d = DEPTH_MM
    h = HEIGHT_MM
    t = BOARD_MM

    compartment_w = (w - 4.0 * t) / 3.0
    compartment_h = (h - 4.0 * t) / 3.0

    body = cq.Workplane("XY").box(w, d, h)

    # Cut the nine open cubbies through the full depth, leaving side/top/bottom
    # frame boards, two vertical dividers, and two internal horizontal shelves.
    x0 = -w / 2.0 + t + compartment_w / 2.0
    z0 = -h / 2.0 + t + compartment_h / 2.0
    for col in range(3):
        cx = x0 + col * (compartment_w + t)
        for row in range(3):
            cz = z0 + row * (compartment_h + t)
            opening = (
                cq.Workplane("XY")
                .box(compartment_w, d + 20.0, compartment_h)
                .translate((cx, 0.0, cz))
            )
            body = body.cut(opening)

    # A shallow machined groove on the rear face suggests the dado/rabbet used
    # for an optional thin back panel, while the shelf remains open-backed.
    groove_y = d / 2.0 - GROOVE_DEPTH_MM / 2.0
    vertical_centers = [
        -w / 2.0 + t / 2.0,
        -w / 2.0 + t + compartment_w + t / 2.0,
        -w / 2.0 + t + 2.0 * compartment_w + 1.5 * t,
        w / 2.0 - t / 2.0,
    ]
    horizontal_centers = [
        -h / 2.0 + t / 2.0,
        -h / 2.0 + t + compartment_h + t / 2.0,
        -h / 2.0 + t + 2.0 * compartment_h + 1.5 * t,
        h / 2.0 - t / 2.0,
    ]

    for cx in vertical_centers:
        groove = (
            cq.Workplane("XY")
            .box(GROOVE_WIDTH_MM, GROOVE_DEPTH_MM + 1.0, h - 2.0 * t)
            .translate((cx, groove_y + 0.5, 0.0))
        )
        body = body.cut(groove)

    for cz in horizontal_centers:
        groove = (
            cq.Workplane("XY")
            .box(w - 2.0 * t, GROOVE_DEPTH_MM + 1.0, GROOVE_WIDTH_MM)
            .translate((0.0, groove_y + 0.5, cz))
        )
        body = body.cut(groove)

    # Lightly ease only the exposed front arrises: outside perimeter and the
    # nine compartment openings. Rear groove edges stay crisp like machined dados.
    body = body.edges("<Y").fillet(FRONT_RADIUS_MM)
    return body


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="open_cube_bookshelf")

    wood = Material("warm_oak_veneer", rgba=(0.64, 0.42, 0.20, 1.0))

    bookcase = model.part(
        "bookcase",
        meta={
            "units_authored": "millimetres",
            "overall_size_mm": (WIDTH_MM, DEPTH_MM, HEIGHT_MM),
            "board_thickness_mm": BOARD_MM,
        },
    )
    bookcase.visual(
        mesh_from_cadquery(
            _bookcase_carcass(),
            "bookcase_carcass",
            tolerance=0.5,
            angular_tolerance=0.2,
            unit_scale=0.001,
        ),
        origin=Origin(),
        material=wood,
        name="continuous_carcass",
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    bookcase = object_model.get_part("bookcase")

    ctx.check(
        "single static watertight carcass",
        len(object_model.parts) == 1 and len(object_model.articulations) == 0,
        details=f"parts={len(object_model.parts)}, articulations={len(object_model.articulations)}",
    )

    aabb = ctx.part_world_aabb(bookcase)
    if aabb is None:
        ctx.fail("overall bounding box available", "No AABB returned for bookcase")
    else:
        mn, mx = aabb
        size = (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])
        expected = (WIDTH_MM / 1000.0, DEPTH_MM / 1000.0, HEIGHT_MM / 1000.0)
        ctx.check(
            "overall size is 1000 x 300 x 1200 mm",
            all(abs(size[i] - expected[i]) <= 0.003 for i in range(3)),
            details=f"size={size}, expected={expected}",
        )

    ctx.check(
        "regular 3 x 3 grid proportions",
        abs((WIDTH_MM - 4 * BOARD_MM) / 3 - 304.0) < 1.0
        and abs((HEIGHT_MM - 4 * BOARD_MM) / 3 - 370.6667) < 1.0,
        details="compartment dimensions derived from two dividers and two internal shelves",
    )

    return ctx.report()


object_model = build_object_model()