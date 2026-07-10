from __future__ import annotations

import math

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    Cylinder,
    Material,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TireGeometry,
    TireGroove,
    TireShoulder,
    TireSidewall,
    TireTread,
    WheelBore,
    WheelFace,
    WheelGeometry,
    WheelHub,
    WheelRim,
    WheelSpokes,
    mesh_from_geometry,
)


BLACK = Material("matte_black_printed_plastic", rgba=(0.005, 0.005, 0.004, 1.0))
DARK = Material("slightly_satin_black_tube", rgba=(0.015, 0.014, 0.012, 1.0))
RUBBER = Material("soft_black_rubber", rgba=(0.0, 0.0, 0.0, 1.0))
PIN = Material("dark_grey_pin_caps", rgba=(0.055, 0.055, 0.05, 1.0))
STEEL = Material("dark_burnished_steel_axles", rgba=(0.12, 0.12, 0.11, 1.0))
LOCK = Material("small_blue_lock_release", rgba=(0.02, 0.08, 0.36, 1.0))


def _rod_xz(part, name: str, start: tuple[float, float, float], end: tuple[float, float, float], thickness: float, material) -> None:
    """Box tube between two points in a part frame; intended for X-Z plane rods."""
    sx, sy, sz = start
    ex, ey, ez = end
    dx = ex - sx
    dz = ez - sz
    length = math.hypot(dx, dz)
    pitch = -math.atan2(dz, dx)
    part.visual(
        Box((length, thickness, thickness)),
        origin=Origin(xyz=((sx + ex) / 2.0, (sy + ey) / 2.0, (sz + ez) / 2.0), rpy=(0.0, pitch, 0.0)),
        material=material,
        name=name,
    )


def _pin_disc(part, name: str, xyz: tuple[float, float, float], radius: float = 0.010, width: float = 0.006) -> None:
    part.visual(
        Cylinder(radius=radius, length=width),
        origin=Origin(xyz=xyz, rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=PIN,
        name=name,
    )


def _tube_x(part, name: str, x: float, y: float, z: float, length: float, thickness: float = 0.010, material=DARK) -> None:
    part.visual(Box((length, thickness, thickness)), origin=Origin(xyz=(x, y, z)), material=material, name=name)


def _tube_y(part, name: str, x: float, y: float, z: float, length: float, thickness: float = 0.010, material=DARK) -> None:
    part.visual(Box((thickness, length, thickness)), origin=Origin(xyz=(x, y, z)), material=material, name=name)


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(
        name="desktop_folding_utility_cart_frame",
        meta={
            "scale": "desktop 3D-print mechanism test only; not for child or load carrying",
            "expanded_size_m": [0.220, 0.140, 0.200],
            "printable_split": "Each semantic link is authored as a printable subassembly: chassis, basket frame, handle, four wheels, four X links, and the lock latch.",
            "state_trace": [
                {"state": "expanded", "basket_fold": 0.0, "handle_fold": 0.0, "lock_release": 0.0, "x_links": "within revolute limits"},
                {"state": "folded", "basket_fold": 0.95, "handle_fold": -1.05, "lock_release": 0.55, "x_links": "rotated toward chassis"},
            ],
            "requested_external_files": {
                "telemetry/events.jsonl": "unavailable in this sandbox; model.py cannot write workspace files",
                "telemetry/run_summary.json": "unavailable in this sandbox; token/tool timing counters are not exposed",
                "artifact_manifest.json": "unavailable in this sandbox; Articraft manages exports outside model.py",
                "pipeline_plan.json": "unavailable in this sandbox",
                "environment.json": "unavailable in this sandbox",
            },
        },
    )

    chassis = model.part("chassis")
    # Lower rectangular deck frame, 200 x 118 mm, with axle/fork structure underneath.
    _tube_x(chassis, "deck_side_0", 0.0, -0.054, 0.058, 0.190, 0.010, DARK)
    _tube_x(chassis, "deck_side_1", 0.0, 0.054, 0.058, 0.190, 0.010, DARK)
    _tube_y(chassis, "deck_front", 0.095, 0.0, 0.058, 0.118, 0.010, DARK)
    _tube_y(chassis, "deck_rear", -0.095, 0.0, 0.058, 0.118, 0.010, DARK)
    # Lightweight printable lattice in the lower tray floor.
    for i, x in enumerate((-0.060, -0.030, 0.000, 0.030, 0.060)):
        _tube_y(chassis, f"floor_slat_y_{i}", x, 0.0, 0.053, 0.104, 0.0035, BLACK)
    for i, y in enumerate((-0.036, -0.018, 0.000, 0.018, 0.036)):
        _tube_x(chassis, f"floor_slat_x_{i}", 0.0, y, 0.053, 0.166, 0.0035, BLACK)

    # Front and rear wheel axles and four printable fork legs tied into the frame.
    for x, label in ((0.088, "front"), (-0.088, "rear")):
        chassis.visual(
            Cylinder(radius=0.0042, length=0.146),
            origin=Origin(xyz=(x, 0.0, 0.026), rpy=(-math.pi / 2.0, 0.0, 0.0)),
            material=STEEL,
            name=f"{label}_axle",
        )
        for y, side in ((-0.064, "side_0"), (0.064, "side_1")):
            chassis.visual(
                Box((0.010, 0.008, 0.036)),
                origin=Origin(xyz=(x, y, 0.043)),
                material=DARK,
                name=f"{label}_{side}_fork_leg",
            )
            _pin_disc(chassis, f"{label}_{side}_axle_cap", (x, y, 0.026), radius=0.007, width=0.004)

    # Small bosses where folding pivots bolt to the lower frame.
    for x, xr in ((0.074, "front"), (-0.074, "rear")):
        for y, side in ((-0.060, "side_0"), (0.060, "side_1")):
            chassis.visual(
                Box((0.018, 0.012, 0.018)),
                origin=Origin(xyz=(x, y, 0.064)),
                material=BLACK,
                name=f"{xr}_{side}_lower_boss",
            )
            _pin_disc(chassis, f"{xr}_{side}_lower_pin", (x, y, 0.070), radius=0.007, width=0.005)

    # Fixed rear hinge blocks for basket and handle.
    chassis.visual(Box((0.026, 0.010, 0.050)), origin=Origin(xyz=(-0.094, -0.047, 0.083)), material=BLACK, name="rear_side_0_upper_boss")
    _pin_disc(chassis, "rear_side_0_upper_pin", (-0.094, -0.047, 0.112), radius=0.008, width=0.005)
    chassis.visual(Box((0.026, 0.010, 0.050)), origin=Origin(xyz=(-0.094, 0.047, 0.083)), material=BLACK, name="rear_side_1_upper_boss")
    _pin_disc(chassis, "rear_side_1_upper_pin", (-0.094, 0.047, 0.112), radius=0.008, width=0.005)
    for y, side in ((-0.066, "side_0"), (0.066, "side_1")):
        chassis.visual(Box((0.018, 0.014, 0.060)), origin=Origin(xyz=(-0.096, y, 0.086)), material=BLACK, name=f"handle_{side}_hinge_stand")

    # Four rolling wheels.
    wheel_mesh = mesh_from_geometry(
        WheelGeometry(
            0.020,
            0.014,
            rim=WheelRim(inner_radius=0.010, flange_height=0.002, flange_thickness=0.0015, bead_seat_depth=0.001),
            hub=WheelHub(radius=0.006, width=0.012, cap_style="domed"),
            face=WheelFace(dish_depth=0.002, front_inset=0.001, rear_inset=0.001),
            spokes=WheelSpokes(style="straight", count=6, thickness=0.0018, window_radius=0.004),
            bore=WheelBore(style="round", diameter=0.0045),
        ),
        "small_spoked_wheel",
    )
    tire_mesh = mesh_from_geometry(
        TireGeometry(
            0.026,
            0.018,
            inner_radius=0.020,
            tread=TireTread(style="block", depth=0.0015, count=18, land_ratio=0.55),
            grooves=(TireGroove(center_offset=0.0, width=0.002, depth=0.001),),
            sidewall=TireSidewall(style="rounded", bulge=0.04),
            shoulder=TireShoulder(width=0.002, radius=0.001),
        ),
        "small_block_tire",
    )

    for x, xr in ((0.088, "front"), (-0.088, "rear")):
        for y, side in ((-0.076, "side_0"), (0.076, "side_1")):
            w = model.part(f"{xr}_wheel_{side}")
            w.visual(tire_mesh, origin=Origin(rpy=(0.0, 0.0, math.pi / 2.0)), material=RUBBER, name="tire")
            w.visual(wheel_mesh, origin=Origin(rpy=(0.0, 0.0, math.pi / 2.0)), material=PIN, name="spoked_hub")
            model.articulation(
                f"{xr}_wheel_{side}_spin",
                ArticulationType.CONTINUOUS,
                parent=chassis,
                child=w,
                origin=Origin(xyz=(x, y, 0.026)),
                axis=(0.0, 1.0, 0.0),
                motion_limits=MotionLimits(effort=0.6, velocity=8.0),
            )

    # Rectangular basket frame: rear-hinged upper tray frame, folds down toward chassis.
    basket = model.part("basket_frame")
    _tube_x(basket, "basket_side_0", 0.082, -0.048, 0.019, 0.164, 0.009, DARK)
    _tube_x(basket, "basket_side_1", 0.082, 0.048, 0.019, 0.164, 0.009, DARK)
    _tube_y(basket, "basket_front", 0.164, 0.0, 0.019, 0.106, 0.009, DARK)
    _tube_y(basket, "basket_rear", 0.000, 0.0, 0.025, 0.106, 0.009, DARK)
    for x in (0.041, 0.082, 0.123):
        _tube_y(basket, f"basket_cross_{int(x*1000)}", x, 0.0, 0.018, 0.092, 0.0045, BLACK)
    for y, side in ((-0.048, "side_0"), (0.048, "side_1")):
        _pin_disc(basket, f"{side}_rear_hinge_eye", (0.0, y, 0.004), radius=0.006, width=0.004)
        _pin_disc(basket, f"{side}_front_link_eye", (0.155, y, 0.018), radius=0.007, width=0.006)
    basket_joint = model.articulation(
        "basket_fold",
        ArticulationType.REVOLUTE,
        parent=chassis,
        child=basket,
        origin=Origin(xyz=(-0.094, 0.0, 0.112)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=1.2, velocity=1.5, lower=0.0, upper=0.95),
        meta={"trace_role": "main tray frame folds down toward the lower chassis"},
    )

    # Folding push handle with two side uprights and a rounded-looking cross grip.
    handle = model.part("push_handle")
    for y, side in ((-0.066, "side_0"), (0.066, "side_1")):
        _rod_xz(handle, f"{side}_upright", (0.0, y, 0.0), (-0.040, y, 0.080), 0.010, DARK)
        _pin_disc(handle, f"{side}_hinge_eye", (0.0, y, 0.0), radius=0.008, width=0.006)
    handle.visual(
        Cylinder(radius=0.008, length=0.142),
        origin=Origin(xyz=(-0.040, 0.0, 0.080), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=BLACK,
        name="rounded_grip",
    )
    handle_joint = model.articulation(
        "handle_fold",
        ArticulationType.REVOLUTE,
        parent=chassis,
        child=handle,
        origin=Origin(xyz=(-0.096, 0.0, 0.120)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=1.3, lower=-1.05, upper=0.0),
        meta={"trace_role": "handle rotates down/back so the grip approaches the basket frame"},
    )

    # Two side groups of X links.  Each link has hinge eyes at the printed pivots.
    link_specs = [
        ("x_link_0", -0.060, 0.074, (-0.148, 0.0, 0.060), "front_to_rear"),
        ("x_link_1", -0.052, -0.074, (0.148, 0.0, 0.060), "rear_to_front"),
        ("x_link_2", 0.052, 0.074, (-0.148, 0.0, 0.060), "front_to_rear"),
        ("x_link_3", 0.060, -0.074, (0.148, 0.0, 0.060), "rear_to_front"),
    ]
    for name, y, x0, end_vec, role in link_specs:
        link = model.part(name)
        lower_z = 0.008 if x0 > 0 else 0.018
        _rod_xz(link, "flat_bar", (0.006 if x0 > 0 else -0.018, 0.0, lower_z), end_vec, 0.0075, DARK)
        _pin_disc(link, "lower_eye", (0.0, 0.0, 0.006), radius=0.0055, width=0.004)
        _pin_disc(link, "upper_eye", end_vec, radius=0.0075, width=0.006)
        _pin_disc(link, "center_rivet", (end_vec[0] / 2.0, 0.0, end_vec[2] / 2.0), radius=0.006, width=0.005)
        model.articulation(
            f"{name}_pivot",
            ArticulationType.REVOLUTE,
            parent=chassis,
            child=link,
            origin=Origin(xyz=(x0, y, 0.070)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=0.8, velocity=1.5, lower=-0.75, upper=0.75),
            meta={"trace_role": role, "fold_sample_rad": 0.55 if x0 > 0 else -0.55},
        )

    # Blue lock lever at the central X-link rivet line; it swings clear before folding.
    lock = model.part("lock_latch")
    lock.visual(Box((0.008, 0.006, 0.028)), origin=Origin(xyz=(0.012, 0.000, -0.018)), material=LOCK, name="release_tab")
    lock.visual(Cylinder(radius=0.006, length=0.014), origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)), material=PIN, name="pivot_bushing")
    lock_joint = model.articulation(
        "lock_release",
        ArticulationType.REVOLUTE,
        parent=chassis,
        child=lock,
        origin=Origin(xyz=(-0.094, 0.052, 0.096)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=0.25, velocity=2.0, lower=0.0, upper=0.60),
        meta={"trace_role": "spring latch rotates outward to free the X-link center rivets"},
    )

    # Explicitly keep references alive for trace-oriented tests and metadata readability.
    model.meta["primary_joints"] = [basket_joint.name, handle_joint.name, lock_joint.name]
    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)

    chassis = object_model.get_part("chassis")
    basket = object_model.get_part("basket_frame")
    handle = object_model.get_part("push_handle")
    lock = object_model.get_part("lock_latch")
    basket_joint = object_model.get_articulation("basket_fold")
    handle_joint = object_model.get_articulation("handle_fold")
    lock_joint = object_model.get_articulation("lock_release")

    ctx.check("four independent wheel links", len([p for p in object_model.parts if "wheel" in p.name]) == 4)
    ctx.check("two X link side groups", len([p for p in object_model.parts if p.name.startswith("x_link_")]) == 4)
    ctx.check("state trace stored on model", "state_trace" in object_model.meta and len(object_model.meta["state_trace"]) >= 2)

    ctx.allow_overlap(
        "chassis",
        "lock_latch",
        elem_a="rear_side_1_upper_boss",
        elem_b="pivot_bushing",
        reason="The latch pivot bushing is intentionally seated through the rear printed hinge boss.",
    )
    for link_name, boss_name in (
        ("x_link_0", "front_side_0_lower_boss"),
        ("x_link_2", "front_side_1_lower_boss"),
    ):
        ctx.allow_overlap(
            "chassis",
            link_name,
            elem_a=boss_name,
            elem_b="lower_eye",
            reason="The X-link lower eye is intentionally captured on the printed pivot boss and pin.",
        )

    # Expanded pose: basket and handle are upright/usable, with a footprint near the requested 220 x 140 x 200 mm envelope.
    with ctx.pose({basket_joint: 0.0, handle_joint: 0.0, lock_joint: 0.0}):
        ctx.expect_overlap(basket, chassis, axes="xy", min_overlap=0.090, name="basket sits over lower chassis")
        ctx.expect_overlap(handle, chassis, axes="xy", min_overlap=0.015, name="expanded handle hinges from rear chassis")
        ctx.expect_contact(lock, chassis, contact_tol=0.003, elem_a="pivot_bushing", elem_b="rear_side_1_upper_boss", name="lock lever is mounted to chassis boss")

    # Folded pose: handle and basket rotate toward the lower frame instead of drifting away.
    rest_handle = ctx.part_world_aabb(handle)
    rest_basket = ctx.part_world_aabb(basket)
    with ctx.pose({basket_joint: 0.95, handle_joint: -1.05, lock_joint: 0.55}):
        folded_handle = ctx.part_world_aabb(handle)
        folded_basket = ctx.part_world_aabb(basket)
        ctx.expect_overlap(basket, chassis, axes="xy", min_overlap=0.040, name="folded basket remains over chassis")
        ctx.expect_overlap(handle, chassis, axes="xy", min_overlap=0.015, name="folded handle stays near frame footprint")

    ctx.check(
        "basket fold lowers front rail",
        rest_basket is not None and folded_basket is not None and folded_basket[1][2] < rest_basket[1][2] + 0.005,
        details=f"rest={rest_basket}, folded={folded_basket}",
    )
    ctx.check(
        "handle fold brings grip down",
        rest_handle is not None and folded_handle is not None and folded_handle[1][2] < rest_handle[1][2] - 0.015,
        details=f"rest={rest_handle}, folded={folded_handle}",
    )

    return ctx.report()


object_model = build_object_model()