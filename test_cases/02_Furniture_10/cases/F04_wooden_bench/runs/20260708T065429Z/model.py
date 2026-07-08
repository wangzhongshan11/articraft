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


MM = 0.001


def _rounded_box_mm(sx: float, sy: float, sz: float, radius: float, edge_selector: str) -> cq.Workplane:
    """Create a rounded rectangular timber member in millimetres."""
    body = cq.Workplane("XY").box(sx, sy, sz)
    if radius > 0:
        body = body.edges(edge_selector).fillet(radius)
    return body


def _seat_shape() -> cq.Workplane:
    # 1000 x 300 x 30 mm slab, with the four long arrises softened like a real timber seat.
    return (
        cq.Workplane("XY")
        .box(1000.0, 300.0, 30.0)
        .edges("|X")
        .fillet(12.0)
        .translate((0.0, 0.0, 425.0))
    )


def _leg_frame_shape() -> cq.Workplane:
    # One end frame: two square legs, a broad top rail directly under the seat,
    # and a lower cross rail that receives the longitudinal stretcher.
    top_rail = _rounded_box_mm(50.0, 252.0, 40.0, 4.0, "|Y").translate((0.0, 0.0, 390.0))
    lower_rail = _rounded_box_mm(46.0, 190.0, 32.0, 3.0, "|Y").translate((0.0, 0.0, 140.0))
    front_leg = _rounded_box_mm(42.0, 42.0, 374.0, 5.0, "|Z").translate((0.0, 112.0, 187.0))
    rear_leg = _rounded_box_mm(42.0, 42.0, 374.0, 5.0, "|Z").translate((0.0, -112.0, 187.0))

    return top_rail.union(lower_rail).union(front_leg).union(rear_leg)


def _stretcher_shape() -> cq.Workplane:
    # Long lower stretcher spans between the inner faces of the two end frames.
    # Its square shoulders touch the lower rails rather than floating below them.
    return _rounded_box_mm(734.0, 46.0, 46.0, 4.0, "|X").translate((0.0, 0.0, 116.0))


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(
        name="wooden_bench",
        meta={"units_authored": "millimetres", "overall_size_mm": (1000, 300, 440)},
    )

    wood = model.material("warm_beech_wood", rgba=(0.72, 0.46, 0.22, 1.0))
    end_grain = model.material("slightly_darker_end_grain", rgba=(0.58, 0.34, 0.16, 1.0))

    seat = model.part("seat")
    seat.visual(
        mesh_from_cadquery(_seat_shape(), "rounded_seat", tolerance=0.35, angular_tolerance=0.08, unit_scale=MM),
        material=wood,
        name="rounded_seat",
    )

    end_frame_0 = model.part("end_frame_0")
    end_frame_0.visual(
        mesh_from_cadquery(_leg_frame_shape(), "end_frame_0", tolerance=0.35, angular_tolerance=0.08, unit_scale=MM),
        material=wood,
        name="frame_joinery",
    )

    end_frame_1 = model.part("end_frame_1")
    end_frame_1.visual(
        mesh_from_cadquery(_leg_frame_shape(), "end_frame_1", tolerance=0.35, angular_tolerance=0.08, unit_scale=MM),
        material=wood,
        name="frame_joinery",
    )

    stretcher = model.part("lower_stretcher")
    stretcher.visual(
        mesh_from_cadquery(_stretcher_shape(), "lower_stretcher", tolerance=0.35, angular_tolerance=0.08, unit_scale=MM),
        material=end_grain,
        name="long_stretcher",
    )

    # Static, manufacturable bench assembly.  The seat is the root; the timber
    # members are fixed in their assembled positions with face-to-face joinery.
    model.articulation(
        "seat_to_end_frame_0",
        ArticulationType.FIXED,
        parent=seat,
        child=end_frame_0,
        origin=Origin(xyz=(-0.390, 0.0, 0.0)),
    )
    model.articulation(
        "seat_to_end_frame_1",
        ArticulationType.FIXED,
        parent=seat,
        child=end_frame_1,
        origin=Origin(xyz=(0.390, 0.0, 0.0)),
    )
    model.articulation(
        "seat_to_lower_stretcher",
        ArticulationType.FIXED,
        parent=seat,
        child=stretcher,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    seat = object_model.get_part("seat")
    end_frame_0 = object_model.get_part("end_frame_0")
    end_frame_1 = object_model.get_part("end_frame_1")
    stretcher = object_model.get_part("lower_stretcher")

    def coord(v, i: int) -> float:
        if hasattr(v, "__getitem__"):
            return float(v[i])
        return float((v.x, v.y, v.z)[i])

    aabbs = [ctx.part_world_aabb(part) for part in (seat, end_frame_0, end_frame_1, stretcher)]
    if all(aabb is not None for aabb in aabbs):
        mins = [min(coord(aabb[0], i) for aabb in aabbs if aabb is not None) for i in range(3)]
        maxs = [max(coord(aabb[1], i) for aabb in aabbs if aabb is not None) for i in range(3)]
        dims = [maxs[i] - mins[i] for i in range(3)]
        ctx.check(
            "overall bench dimensions are 1000 x 300 x 440 mm",
            abs(dims[0] - 1.000) < 0.003 and abs(dims[1] - 0.300) < 0.003 and abs(dims[2] - 0.440) < 0.003,
            details=f"dims={dims}",
        )
        ctx.check("feet sit on the floor plane", abs(mins[2]) < 0.002, details=f"min_z={mins[2]}")
    else:
        ctx.fail("overall bench dimensions are measurable", f"aabbs={aabbs}")

    ctx.expect_gap(
        seat,
        end_frame_0,
        axis="z",
        max_gap=0.002,
        max_penetration=0.0,
        name="first end frame bears against underside of seat",
    )
    ctx.expect_gap(
        seat,
        end_frame_1,
        axis="z",
        max_gap=0.002,
        max_penetration=0.0,
        name="second end frame bears against underside of seat",
    )
    ctx.expect_contact(
        stretcher,
        end_frame_0,
        contact_tol=0.002,
        name="stretcher shoulders contact first end frame",
    )
    ctx.expect_contact(
        stretcher,
        end_frame_1,
        contact_tol=0.002,
        name="stretcher shoulders contact second end frame",
    )
    ctx.expect_overlap(
        end_frame_0,
        seat,
        axes="y",
        min_overlap=0.20,
        name="end frames are wide enough for stable seat support",
    )

    return ctx.report()


object_model = build_object_model()
