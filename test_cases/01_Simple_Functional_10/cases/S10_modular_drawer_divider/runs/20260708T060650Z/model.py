from __future__ import annotations

import math

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    Cylinder,
    Material,
    Origin,
    TestContext,
    TestReport,
)


# Real divider dimensions, expressed in millimetres here and converted to metres
# for the SDK.  Each slotted panel is about 150 x 90 x 5 mm.
PANEL_LENGTH_MM = 150.0
PANEL_HEIGHT_MM = 90.0
PANEL_THICKNESS_MM = 5.0
SLOT_WIDTH_MM = 5.0
SLOT_DEPTH_MM = 46.0
SLOT_POSITIONS_MM = (-37.5, 37.5)
GRID_SPACING_MM = 75.0


def _m(value_mm: float) -> float:
    return value_mm * 0.001


def _visual_box(part, name: str, size_mm: tuple[float, float, float], center_mm: tuple[float, float, float], material: Material) -> None:
    part.visual(
        Box(tuple(_m(v) for v in size_mm)),
        origin=Origin(xyz=tuple(_m(v) for v in center_mm)),
        material=material,
        name=name,
    )


def _add_panel(
    model: ArticulatedObject,
    name: str,
    slot_opening: str,
    material: Material,
):
    """Build one modular divider from connected manufactured features."""
    panel = model.part(name)

    # The slot positions divide the lower/upper portion into three solid spans.
    spans = [
        (-PANEL_LENGTH_MM / 2.0, SLOT_POSITIONS_MM[0] - SLOT_WIDTH_MM / 2.0),
        (SLOT_POSITIONS_MM[0] + SLOT_WIDTH_MM / 2.0, SLOT_POSITIONS_MM[1] - SLOT_WIDTH_MM / 2.0),
        (SLOT_POSITIONS_MM[1] + SLOT_WIDTH_MM / 2.0, PANEL_LENGTH_MM / 2.0),
    ]

    if slot_opening == "bottom":
        _visual_box(
            panel,
            "upper_bridge",
            (PANEL_LENGTH_MM, PANEL_THICKNESS_MM, PANEL_HEIGHT_MM - SLOT_DEPTH_MM),
            (0.0, 0.0, SLOT_DEPTH_MM + (PANEL_HEIGHT_MM - SLOT_DEPTH_MM) / 2.0),
            material,
        )
        lower_height = SLOT_DEPTH_MM
        for idx, (x0, x1) in enumerate(spans):
            _visual_box(
                panel,
                f"lower_span_{idx}",
                (x1 - x0, PANEL_THICKNESS_MM, lower_height),
                ((x0 + x1) / 2.0, 0.0, lower_height / 2.0),
                material,
            )
    elif slot_opening == "top":
        lower_height = PANEL_HEIGHT_MM - SLOT_DEPTH_MM
        _visual_box(
            panel,
            "lower_bridge",
            (PANEL_LENGTH_MM, PANEL_THICKNESS_MM, lower_height),
            (0.0, 0.0, lower_height / 2.0),
            material,
        )
        upper_height = SLOT_DEPTH_MM
        for idx, (x0, x1) in enumerate(spans):
            _visual_box(
                panel,
                f"upper_span_{idx}",
                (x1 - x0, PANEL_THICKNESS_MM, upper_height),
                ((x0 + x1) / 2.0, 0.0, lower_height + upper_height / 2.0),
                material,
            )
    else:
        raise ValueError(f"unsupported slot opening: {slot_opening}")

    # Small raised end stops make the divider ends legible and give a molded,
    # handled look.  They are overlapped into the panel body so each part remains
    # a single supported object rather than a collection of floating details.
    for side, x in (("neg", -PANEL_LENGTH_MM / 2.0 + 3.0), ("pos", PANEL_LENGTH_MM / 2.0 - 3.0)):
        _visual_box(
            panel,
            f"end_stop_{side}",
            (6.0, PANEL_THICKNESS_MM, 10.0),
            (x, 0.0, PANEL_HEIGHT_MM + 3.0),
            material,
        )
        # Round the exposed top corner with a small through-thickness barrel.
        panel.visual(
            Cylinder(radius=_m(2.5), length=_m(PANEL_THICKNESS_MM)),
            origin=Origin(xyz=(_m(x), 0.0, _m(PANEL_HEIGHT_MM + 8.0)), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=material,
            name=f"rounded_stop_{side}",
        )

    return panel


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="modular_drawer_divider")
    warm_plastic = Material("warm_beige_plastic", rgba=(0.78, 0.70, 0.56, 1.0))

    # Two lengthwise panels use bottom-opening half slots.  The two perpendicular
    # panels use matching top-opening half slots, so identical thin dividers can
    # interlock at right angles without solid intersections.
    panel_0 = _add_panel(model, "panel_0", "bottom", warm_plastic)
    panel_1 = _add_panel(model, "panel_1", "bottom", warm_plastic)
    cross_panel_0 = _add_panel(model, "cross_panel_0", "top", warm_plastic)
    cross_panel_1 = _add_panel(model, "cross_panel_1", "top", warm_plastic)

    s = _m(GRID_SPACING_MM)
    model.articulation(
        "panel_0_to_panel_1",
        ArticulationType.FIXED,
        parent=panel_0,
        child=panel_1,
        origin=Origin(xyz=(0.0, s, 0.0)),
    )
    model.articulation(
        "panel_0_to_cross_panel_0",
        ArticulationType.FIXED,
        parent=panel_0,
        child=cross_panel_0,
        origin=Origin(xyz=(-s / 2.0, s / 2.0, 0.0), rpy=(0.0, 0.0, math.pi / 2.0)),
    )
    model.articulation(
        "panel_0_to_cross_panel_1",
        ArticulationType.FIXED,
        parent=panel_0,
        child=cross_panel_1,
        origin=Origin(xyz=(s / 2.0, s / 2.0, 0.0), rpy=(0.0, 0.0, math.pi / 2.0)),
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)

    panel_names = ("panel_0", "panel_1", "cross_panel_0", "cross_panel_1")
    ctx.check(
        "four separate divider panels",
        len(object_model.parts) == 4 and all(object_model.get_part(name) is not None for name in panel_names),
        details=f"parts={[part.name for part in object_model.parts]}",
    )
    ctx.check(
        "fixed assembled grid",
        len(object_model.articulations) == 3
        and all(j.articulation_type == ArticulationType.FIXED for j in object_model.articulations),
        details=f"joints={[j.name for j in object_model.articulations]}",
    )

    for name in panel_names:
        panel = object_model.get_part(name)
        ctx.expect_overlap(panel, "panel_0", axes="z", min_overlap=0.085, name=f"{name} full height panel")

    ctx.expect_contact("panel_0", "cross_panel_0", name="first cross panel interlocks with panel 0")
    ctx.expect_contact("panel_1", "cross_panel_0", name="first cross panel interlocks with panel 1")
    ctx.expect_contact("panel_0", "cross_panel_1", name="second cross panel interlocks with panel 0")
    ctx.expect_contact("panel_1", "cross_panel_1", name="second cross panel interlocks with panel 1")
    ctx.expect_overlap("panel_0", "cross_panel_0", axes="xy", min_overlap=0.004, name="first cross slot alignment")
    ctx.expect_overlap("panel_1", "cross_panel_1", axes="xy", min_overlap=0.004, name="second cross slot alignment")

    return ctx.report()


object_model = build_object_model()
