#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

FENCE = re.compile(r"(```[\s\S]*?```)")
REPO = Path(__file__).resolve().parents[1]
D = REPO / "sdk" / "_examples" / "cadquery"

CREATED = [
    "offsetaxis_rotary_stack",
    "offsetting_wires_in_2d",
    "opposed_twinslide_gripper",
    "orthogonal_xy_stage",
    "panel_with_various_connector_holes",
    "parametric_pin_header",
    "pitray_clip",
    "plate_with_hole",
    "polygons",
    "polylines",
    "portal_gantry_with_vertical_slide",
    "prismaticrevolute_chain",
    "prismaticrevoluterevolute_chain",
    "rack_and_pinion",
    "raspberry_pi_3_model_b_assembly",
    "reinforcing_a_junction_with_a_fillet",
    "remote_enclosure",
    "resin_mold",
    "revoluteprismatic_chain",
    "revoluteprismaticrevolute_chain",
    "ring_gears_and_planetary_gearsets",
    "rj45_surface_mount_jack",
    "rotary_base_with_vertical_slide",
    "rotated_workplanes",
    "rounding_corners_with_fillet",
    "shelling_to_create_thin_features",
    "simple_rectangular_plate",
    "single_continuous_rotary_shaft",
    "single_pitch_axis_module",
    "single_prismatic_slider",
    "single_revolute_hinge",
    "single_roll_axis_module",
    "single_yaw_axis_module",
    "splitting_an_object",
    "spur_helical_herringbone_gears",
    "tagging_objects",
    "the_classic_occ_bottle",
    "thread",
    "threejoint_revolute_chain",
    "threestage_telescoping_slide",
    "twojoint_revolute_chain",
    "twostage_telescoping_slide",
    "using_construction_geometry",
    "using_point_lists",
    "vane_array_with_independent_pivots",
    "vertical_slide_with_wrist_hinge",
    "wall_vent_with_louvered_grille",
    "worm_gear",
    "xyz_cartesian_stage",
    "yawpitchroll_wrist",
]


def main() -> int:
    errors: list[str] = []
    for stem in CREATED:
        en = (D / f"{stem}.md").read_text(encoding="utf-8")
        zh = (D / f"{stem}_c.md").read_text(encoding="utf-8")
        en_c = FENCE.findall(en)
        zh_c = FENCE.findall(zh)
        if en_c != zh_c:
            errors.append(stem)
            print(f"FAIL {stem}: en={len(en_c)} zh={len(zh_c)}")
            if len(en_c) == len(zh_c):
                for i, (a, b) in enumerate(zip(en_c, zh_c)):
                    if a != b:
                        print(f"  block {i} len {len(a)} vs {len(b)}")
    if errors:
        return 1
    print(f"OK: {len(CREATED)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
