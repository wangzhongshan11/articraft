---
title: '直线滑台与独立旋转末端'
description: '摘自五星轨装主轴记录；滑台棱柱运动与主轴旋转关节分离。'
tags:
  - cadquery
  - examples
  - articulation
  - 棱柱
  - 旋转
  - 主轴
---
# 直线滑台与独立旋转末端

本片段保留五星 **轨装主轴**记录中的真实分解：**导轨基座**上为 `PRISMATIC` 滑台，滑台再承载独立 `REVOLUTE` **主轴**（法兰、杆身与侧向模块等多段视觉）。滑动与旋转自由度解耦，是机床/执行器类机构的常见模式。

**关节：**

- `rail_to_carriage`：沿 X 平移，原点含 `PRISMATIC_HOME_Z`，限位 ±0.14 m。
- `carriage_to_spindle`：绕 Y 轴旋转，原点位于滑台上的关节偏移 `(SPINDLE_JOINT_Y, SPINDLE_JOINT_Z)`。

主轴由圆柱与盒体组合近似真实几何，并配置惯性与材质。

```python
from math import pi

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    Cylinder,
    Inertial,
    MotionLimits,
    Origin,
    mesh_from_cadquery,
)


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="linear_carriage_spindle", assets=ASSETS)

    model.material("anodized_aluminum", rgba=(0.74, 0.76, 0.80, 1.0))
    model.material("dark_polymer", rgba=(0.16, 0.17, 0.20, 1.0))
    model.material("tool_steel", rgba=(0.56, 0.57, 0.60, 1.0))

    rail_base = model.part("rail_base")
    rail_base.visual(mesh_from_cadquery(_rail_shape(), "rail_base.obj", assets=ASSETS), material="anodized_aluminum")

    carriage = model.part("carriage")
    carriage.visual(mesh_from_cadquery(_carriage_shape(), "carriage.obj", assets=ASSETS), material="dark_polymer")

    spindle = model.part("spindle")
    spindle.visual(Cylinder(radius=SPINDLE_FLANGE_RADIUS, length=SPINDLE_FLANGE_LENGTH), origin=Origin(xyz=(0.0, SPINDLE_FLANGE_LENGTH / 2.0, 0.0), rpy=(-pi / 2.0, 0.0, 0.0)), material="tool_steel")
    spindle.visual(Cylinder(radius=SPINDLE_BODY_RADIUS, length=SPINDLE_BODY_LENGTH), origin=Origin(xyz=(0.0, SPINDLE_FLANGE_LENGTH + (SPINDLE_BODY_LENGTH / 2.0), 0.0), rpy=(-pi / 2.0, 0.0, 0.0)), material="tool_steel")
    spindle.visual(Box((SPINDLE_SIDE_MODULE_X, SPINDLE_SIDE_MODULE_Y, SPINDLE_SIDE_MODULE_Z)), origin=Origin(xyz=(0.0, SPINDLE_FLANGE_LENGTH + 0.022, SPINDLE_FLANGE_RADIUS + 0.012)), material="dark_polymer")

    model.articulation(
        "rail_to_carriage",
        ArticulationType.PRISMATIC,
        parent=rail_base,
        child=carriage,
        origin=Origin(xyz=(0.0, 0.0, PRISMATIC_HOME_Z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(lower=-0.14, upper=0.14, effort=150.0, velocity=0.5),
    )
    model.articulation(
        "carriage_to_spindle",
        ArticulationType.REVOLUTE,
        parent=carriage,
        child=spindle,
        origin=Origin(xyz=(0.0, SPINDLE_JOINT_Y, SPINDLE_JOINT_Z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(lower=-1.4, upper=1.4, effort=12.0, velocity=8.0),
    )

    return model
```
