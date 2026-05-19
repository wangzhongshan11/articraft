---
title: '鼠笼式鼓风机叶轮'
description: 'Base SDK 示例：使用 BlowerWheelGeometry 构建径向鼓风机叶轮，带外露叶片通道与开放内腔。'
tags:
  - sdk
  - base sdk
  - blower
  - blower wheel
  - squirrel cage
  - radial fan
  - hvac blower
  - blowerwheelgeometry
  - mesh geometry
---
# 鼠笼式鼓风机叶轮

本 Base SDK 示例是 `BlowerWheelGeometry` 的紧凑参考。当物体需要呈现为**真实径向鼓风机鼠笼**——叶片间有开放通道、可看到内腔——而非实心圆盘时，应优先参考此例。

**适用查询关键词：** `squirrel cage`、`blower wheel`、`BlowerWheelGeometry`、`radial fan`、`HVAC blower`。

**几何参数：**
- 外半径 0.080，内半径参数 0.040，宽度 0.050。
- 18 片叶片，厚度 0.004，扫掠角 `blade_sweep_deg=25.0`。
- 灰色金属质感材质 `blower_gray`。

**测试：** 直径约 `2×OUTER_RADIUS`（容差 ±0.008），宽度约 `WIDTH`（容差 ±0.004）。

```python
from __future__ import annotations

from sdk import (
    ArticulatedObject,
    BlowerWheelGeometry,
    Box,
    Inertial,
    TestContext,
    TestReport,
    mesh_from_geometry,
)

OUTER_RADIUS = 0.080
WIDTH = 0.050


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="squirrel_cage_blower")
    finish = model.material("blower_gray", rgba=(0.62, 0.65, 0.69, 1.0))

    blower_wheel = model.part("blower_wheel")
    blower_wheel.visual(
        mesh_from_geometry(
            BlowerWheelGeometry(
                OUTER_RADIUS,
                0.040,
                WIDTH,
                18,
                blade_thickness=0.004,
                blade_sweep_deg=25.0,
            ),
            "blower_wheel",
        ),
        material=finish,
        name="blower_wheel",
    )
    blower_wheel.inertial = Inertial.from_geometry(Box((0.16, 0.16, WIDTH)), mass=0.22)
    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    blower_wheel = object_model.get_part("blower_wheel")
    ctx.check("blower_wheel_present", blower_wheel is not None, "Expected a blower_wheel part.")
    if blower_wheel is None:
        return ctx.report()

    aabb = ctx.part_world_aabb(blower_wheel)
    ctx.check("blower_wheel_aabb_present", aabb is not None, "Expected a world AABB for the blower wheel.")
    if aabb is None:
        return ctx.report()

    mins, maxs = aabb
    size = tuple(float(maxs[i] - mins[i]) for i in range(3))
    diameter = max(size[0], size[1])
    ctx.check("blower_wheel_diameter", abs(diameter - OUTER_RADIUS * 2.0) <= 0.008, f"size={size!r}")
    ctx.check("blower_wheel_width", abs(size[2] - WIDTH) <= 0.004, f"size={size!r}")
    return ctx.report()


object_model = build_object_model()
```
