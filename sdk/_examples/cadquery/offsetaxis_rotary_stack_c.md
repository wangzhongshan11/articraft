---
title: '偏轴旋转堆叠'
description: '摘自五星偏轴旋转堆叠记录；展示各级旋转模块在空间中侧向错开、仍保持明确串联关系的布局。'
tags:
  - cadquery
  - examples
  - articulation
  - revolute
  - offset
  - stack
---
# 偏轴旋转堆叠

与同轴堆叠不同，本五星示例在三维空间中逐段偏移每一级旋转关节，同时仍显式保留级间串联拓扑，便于学习“错轴多转盘”与分层限位配置。

```python
from sdk import ArticulatedObject, ArticulationType, Box, Inertial, MotionLimits, Origin


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="offset_axis_rotary_stack", assets=ASSETS)

    model.material("frame_dark", rgba=(0.16, 0.18, 0.20, 1.0))
    model.material("module_gray", rgba=(0.44, 0.46, 0.49, 1.0))
    model.material("accent_blue", rgba=(0.18, 0.38, 0.74, 1.0))
    model.material("tool_light", rgba=(0.73, 0.76, 0.80, 1.0))

    base = model.part("base_frame")
    _export_visual(base, _build_base_frame_shape(), "base_frame.obj", "frame_dark")

    stage1 = model.part("stage1_carrier")
    _export_visual(stage1, _build_stage1_shape(), "stage1_carrier.obj", "module_gray")

    stage2 = model.part("stage2_carrier")
    _export_visual(stage2, _build_stage2_shape(), "stage2_carrier.obj", "accent_blue")

    stage3 = model.part("stage3_platform")
    _export_visual(stage3, _build_stage3_shape(), "stage3_platform.obj", "tool_light")

    model.articulation("base_to_stage1", ArticulationType.REVOLUTE, parent=base, child=stage1, origin=Origin(xyz=(0.0, 0.0, 0.0)), axis=(0.0, 1.0, 0.0), motion_limits=MotionLimits(lower=-1.15, upper=1.20, effort=18.0, velocity=2.4))
    model.articulation("stage1_to_stage2", ArticulationType.REVOLUTE, parent=stage1, child=stage2, origin=Origin(xyz=(0.135, 0.0, 0.045)), axis=(0.0, 1.0, 0.0), motion_limits=MotionLimits(lower=-1.35, upper=1.05, effort=15.0, velocity=2.8))
    model.articulation("stage2_to_stage3", ArticulationType.REVOLUTE, parent=stage2, child=stage3, origin=Origin(xyz=(0.110, 0.0, -0.038)), axis=(0.0, 1.0, 0.0), motion_limits=MotionLimits(lower=-1.00, upper=1.35, effort=10.0, velocity=3.0))

    return model
```
