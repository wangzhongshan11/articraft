---
title: '移动副-转动副链'
description: '摘自五星检测夹具记录；展示滑台承载铰接翻板的 PR 拓扑。'
tags:
  - cadquery
  - examples
  - articulation
  - prismatic
  - revolute
  - fixture
---
# 移动副-转动副链

五星检测夹具记录适合作为该拓扑模板：基座导向运动与远端翻板转动分离清晰。

```python
from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    Inertial,
    MotionLimits,
    Origin,
    mesh_from_cadquery,
)


def build_object_model() -> ArticulatedObject:
    cq = _require_cadquery()

    model = ArticulatedObject(name="inspection_fixture", assets=ASSETS)
    model.material("fixture_base", rgba=(0.42, 0.44, 0.48, 1.0))
    model.material("fixture_carriage", rgba=(0.78, 0.46, 0.14, 1.0))
    model.material("fixture_flap", rgba=(0.92, 0.77, 0.16, 1.0))

    base = model.part("base")
    base.visual(mesh_from_cadquery(_build_base_shape(cq), MESH_DIR / "fixture_base.obj"), material="fixture_base")
    base.inertial = Inertial.from_geometry(
        Box((BASE_L, BASE_W, 0.08)),
        mass=11.0,
        origin=Origin(xyz=(0.0, 0.0, 0.03)),
    )

    carriage = model.part("carriage")
    carriage.visual(mesh_from_cadquery(_build_carriage_shape(cq), MESH_DIR / "carriage.obj"), material="fixture_carriage")

    flap = model.part("flap")
    flap.visual(mesh_from_cadquery(_build_flap_shape(cq), MESH_DIR / "inspection_flap.obj"), material="fixture_flap")

    model.articulation(
        "base_to_carriage",
        ArticulationType.PRISMATIC,
        parent="base",
        child="carriage",
        origin=Origin(xyz=(0.0, RAIL_Y, (BASE_T / 2.0) + RAIL_H)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            lower=PRISMATIC_LOWER,
            upper=PRISMATIC_UPPER,
            effort=120.0,
            velocity=0.25,
        ),
    )
    model.articulation(
        "carriage_to_flap",
        ArticulationType.REVOLUTE,
        parent="carriage",
        child="flap",
        origin=Origin(xyz=(EAR_X, -RAIL_Y, EAR_Z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=FLAP_UPPER, effort=10.0, velocity=1.5),
    )

    return model
```
