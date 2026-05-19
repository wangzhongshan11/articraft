---
title: '同轴旋转堆叠'
description: '摘自五星嵌套转台记录；展示两个旋转级共轴布置（底座、回转架、顶盘）。'
tags:
  - cadquery
  - examples
  - articulation
  - 旋转
  - 同轴
  - 转台
---
# 同轴旋转堆叠

本片段来自五星 **嵌套工业转台**记录的核心布局：接地**底座**、**回转架**与**顶盘**三级，均绕同一竖直轴（Z）旋转，形成同轴双 `REVOLUTE` 堆叠。适合学习「共轴多转盘」与分层限位/力矩配置。

**关节链：**

1. `base_to_slew`：底座 → 回转架，原点位于堆叠底部，轴 `(0,0,1)`，较大 effort 与较慢速度。
2. `slew_to_platter`：回转架 → 顶盘，原点在 Z 向抬高 0.060 m，第二级限位与速度可独立设置。

各连杆视觉由 CadQuery 网格导出，材质区分机座、轴承钢与工装橙色。

```python
from sdk import (
    ArticulatedObject,
    ArticulationType,
    Cylinder,
    Inertial,
    MotionLimits,
    Origin,
    mesh_from_cadquery,
)


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="nested_industrial_turntable", assets=ASSETS)

    model.material("machine_base", rgba=(0.20, 0.22, 0.24, 1.0))
    model.material("bearing_steel", rgba=(0.62, 0.65, 0.69, 1.0))
    model.material("tooling_orange", rgba=(0.83, 0.39, 0.10, 1.0))

    pedestal_base = model.part("pedestal_base")
    pedestal_base.visual(mesh_from_cadquery(_build_pedestal_shape(), "pedestal_base.obj", assets=ASSETS), material="machine_base")

    slew_carrier = model.part("slew_carrier")
    slew_carrier.visual(mesh_from_cadquery(_build_slew_shape(), "slew_carrier.obj", assets=ASSETS), material="bearing_steel")

    top_platter = model.part("top_platter")
    top_platter.visual(mesh_from_cadquery(_build_platter_shape(), "top_platter.obj", assets=ASSETS), material="tooling_orange")

    model.articulation(
        "base_to_slew",
        ArticulationType.REVOLUTE,
        parent=pedestal_base,
        child=slew_carrier,
        origin=Origin(),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=-PRIMARY_AXIS_LIMIT, upper=PRIMARY_AXIS_LIMIT, effort=80.0, velocity=1.2),
    )
    model.articulation(
        "slew_to_platter",
        ArticulationType.REVOLUTE,
        parent=slew_carrier,
        child=top_platter,
        origin=Origin(xyz=(0.0, 0.0, 0.060)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=-SECONDARY_AXIS_LIMIT, upper=SECONDARY_AXIS_LIMIT, effort=45.0, velocity=2.0),
    )

    return model
```
