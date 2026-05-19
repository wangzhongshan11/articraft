---
title: '对置双滑台夹爪'
description: '摘自五星夹爪记录；展示从共用本体伸出、沿相反棱柱轴滑动的镜像夹爪。'
tags:
  - cadquery
  - examples
  - articulation
  - prismatic
  - gripper
  - mirrored
---
# 对置双滑台夹爪

该五星夹爪记录是镜像运动学的良好参考：本体承载两只夹爪，行程相等但关节轴方向相反，便于理解对夹与同步开合。

```python
from sdk import ArticulatedObject, ArticulationType, Box, Inertial, MotionLimits, Origin, mesh_from_cadquery


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="twin_slide_gripper", assets=ASSETS)

    body_mat = model.material("body_anodized", rgba=(0.23, 0.25, 0.28, 1.0))
    rail_mat = model.material("rail_steel", rgba=(0.67, 0.69, 0.72, 1.0))
    jaw_mat = model.material("jaw_black", rgba=(0.16, 0.17, 0.19, 1.0))
    plate_mat = model.material("mount_plate", rgba=(0.52, 0.54, 0.58, 1.0))

    body = model.part("body")
    body.visual(mesh_from_cadquery(_body_shape(), "body_shell.obj", assets=ASSETS), name="body_shell", material=body_mat)

    left_jaw = model.part("left_jaw")
    left_jaw.visual(mesh_from_cadquery(_jaw_shape("left"), "left_jaw.obj", assets=ASSETS), name="jaw_shell", material=jaw_mat)

    right_jaw = model.part("right_jaw")
    right_jaw.visual(mesh_from_cadquery(_jaw_shape("right"), "right_jaw.obj", assets=ASSETS), name="jaw_shell", material=jaw_mat)

    model.articulation(
        "body_to_left_jaw",
        ArticulationType.PRISMATIC,
        parent=body,
        child=left_jaw,
        origin=Origin(xyz=(LEFT_JAW_OPEN_X, JAW_ORIGIN_Y, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=120.0, velocity=0.15, lower=0.0, upper=JAW_TRAVEL),
    )
    model.articulation(
        "body_to_right_jaw",
        ArticulationType.PRISMATIC,
        parent=body,
        child=right_jaw,
        origin=Origin(xyz=(RIGHT_JAW_OPEN_X, JAW_ORIGIN_Y, 0.0)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=120.0, velocity=0.15, lower=0.0, upper=JAW_TRAVEL),
    )

    return model
```
