---
title: '旋转底座与垂直滑台'
description: '摘自五星旋转升降模块记录；展示偏航底座上的垂直棱柱级。'
tags:
  - cadquery
  - examples
  - articulation
  - revolute
  - prismatic
  - lift
---
# 旋转底座与垂直滑台

保留五星旋转升降记录的双轴机床模块布局：一级转动底座 + 其上的垂直移动副。

```python
from sdk import ArticulatedObject, ArticulationType, Box, Inertial, MotionLimits, Origin


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="rotary_lift_module", assets=ASSETS)

    model.material("base_paint", rgba=(0.26, 0.29, 0.31, 1.0))
    model.material("machined_steel", rgba=(0.76, 0.78, 0.80, 1.0))
    model.material("safety_orange", rgba=(0.92, 0.46, 0.12, 1.0))

    base = model.part("base_frame")
    base.visual(_export_visual(_make_base_shape(), "base_frame.obj"), material="base_paint")
    base.inertial = Inertial.from_geometry(Box((0.30, 0.24, 0.07)), mass=12.0)

    rotary = model.part("rotary_head")
    rotary.visual(_export_visual(_make_rotary_head_shape(), "rotary_head.obj"), material="machined_steel")

    carriage = model.part("carriage")
    carriage.visual(_export_visual(_make_carriage_shape(), "carriage.obj"), material="safety_orange")

    model.articulation(
        "base_yaw",
        ArticulationType.REVOLUTE,
        parent=base,
        child=rotary,
        origin=Origin(xyz=(0.0, 0.0, ROTARY_JOINT_Z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=-2.5, upper=2.5, effort=25.0, velocity=1.5),
    )
    model.articulation(
        "column_lift",
        ArticulationType.PRISMATIC,
        parent=rotary,
        child=carriage,
        origin=Origin(xyz=LIFT_JOINT_ORIGIN),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=LIFT_TRAVEL, effort=120.0, velocity=0.25),
    )

    return model
```
