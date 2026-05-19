---
title: '轴流风扇转子'
description: 'Base SDK 示例：使用 FanRotorGeometry 构建紧凑型轴流转子，带俯仰叶片与中心轮毂。'
tags:
  - sdk
  - base sdk
  - fan
  - axial fan
  - fan rotor
  - impeller
  - cooling fan
  - fanrotorgeometry
  - mesh geometry
---
# 轴流风扇转子

本 Base SDK 示例是 `FanRotorGeometry` 的最小化参考实现。它适用于紧凑型散热风扇、家电转子，以及任何需要将叶片呈现为真实几何体（而非浮雕纹理）的暴露式轴流叶轮场景。

**适用查询关键词：** `fan`、`axial fan`、`fan rotor`、`FanRotorGeometry`、`cooling fan`、`impeller`。

**几何要点：**
- 外半径 `OUTER_RADIUS = 0.070`，厚度 `THICKNESS = 0.010`。
- 5 片叶片，叶片俯仰角 `blade_pitch_deg=24.0`，扫掠角 `blade_sweep_deg=14.0`。
- 轮毂半径 `0.020`，与叶片一体由 `FanRotorGeometry` 生成。
- 通过 `mesh_from_geometry` 转为网格，材质为近黑色 `fan_black`。

**测试校验（`run_tests`）：** 检查 `fan_rotor` 零件存在、世界 AABB 存在、直径约 `2×OUTER_RADIUS`（容差 ±0.012）、厚度在 0.008–0.014 之间。

```python
from __future__ import annotations

from sdk import (
    ArticulatedObject,
    Box,
    FanRotorGeometry,
    Inertial,
    TestContext,
    TestReport,
    mesh_from_geometry,
)

OUTER_RADIUS = 0.070
THICKNESS = 0.010


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="axial_fan_rotor")
    finish = model.material("fan_black", rgba=(0.08, 0.08, 0.09, 1.0))

    fan_rotor = model.part("fan_rotor")
    fan_rotor.visual(
        mesh_from_geometry(
            FanRotorGeometry(
                OUTER_RADIUS,
                0.020,
                5,
                thickness=THICKNESS,
                blade_pitch_deg=24.0,
                blade_sweep_deg=14.0,
            ),
            "fan_rotor",
        ),
        material=finish,
        name="fan_rotor",
    )
    fan_rotor.inertial = Inertial.from_geometry(Box((0.14, 0.14, 0.012)), mass=0.12)
    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    fan_rotor = object_model.get_part("fan_rotor")
    ctx.check("fan_rotor_present", fan_rotor is not None, "Expected a fan_rotor part.")
    if fan_rotor is None:
        return ctx.report()

    aabb = ctx.part_world_aabb(fan_rotor)
    ctx.check("fan_rotor_aabb_present", aabb is not None, "Expected a world AABB for the fan rotor.")
    if aabb is None:
        return ctx.report()

    mins, maxs = aabb
    size = tuple(float(maxs[i] - mins[i]) for i in range(3))
    diameter = max(size[0], size[1])
    ctx.check("fan_rotor_diameter", abs(diameter - OUTER_RADIUS * 2.0) <= 0.012, f"size={size!r}")
    ctx.check("fan_rotor_thickness", 0.008 <= size[2] <= 0.014, f"size={size!r}")
    return ctx.report()


object_model = build_object_model()
```
