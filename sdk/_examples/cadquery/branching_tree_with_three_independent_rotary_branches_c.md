---
title: '三分支独立旋转树'
description: '摘自五星三分支旋转树记录；展示如何围绕单一轮毂用循环重复布置多条独立旋转臂。'
tags:
  - cadquery
  - examples
  - articulation
  - 分支
  - 旋转
  - 轮毂
---
# 三分支独立旋转树

该示例摘自高质量（5 星）**三分支旋转树**记录的核心片段，说明如何用**小循环**扩展分支拓扑，而无需为每条关节手写重复代码。中心轮毂固定，三条臂在圆周上按预设角度布置，每条臂与轮毂之间为独立的 `REVOLUTE` 关节。

**设计要点：**

- `ArticulatedObject` 统一管理网格资产、材质与关节。
- 轮毂与臂的几何分别由 `_build_hub_shape` / `_build_arm_shape` 生成并 `mesh_from_cadquery` 导出。
- `zip(BRANCH_NAMES, BRANCH_ANGLES)` 驱动分支命名与关节原点（极坐标偏移 + 绕 Z 的 rpy）。
- 旋转轴为 `(0, -1, 0)`，运动限位由 `ARM_LIMITS` 约束。

适合作为「星形/轮辐式」多自由度机构的模板。

```python
from math import cos, sin

from sdk import ArticulatedObject, ArticulationType, Cylinder, Inertial, Origin, mesh_from_cadquery


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="rotary_tree_mechanism", assets=ASSETS)

    model.material("hub_gray", rgba=(0.58, 0.60, 0.63, 1.0))
    model.material("arm_blue", rgba=(0.23, 0.45, 0.72, 1.0))

    hub_mesh = mesh_from_cadquery(_build_hub_shape(), "rotary_tree_hub.obj", assets=ASSETS)
    arm_mesh = mesh_from_cadquery(_build_arm_shape(), "rotary_tree_arm.obj", assets=ASSETS)

    hub = model.part("hub")
    hub.visual(hub_mesh, material="hub_gray")
    hub.inertial = Inertial.from_geometry(Cylinder(radius=HUB_RADIUS, length=HUB_HEIGHT), mass=1.15)

    for name, angle in zip(BRANCH_NAMES, BRANCH_ANGLES):
        branch = _add_branch_part(model, arm_mesh, name)
        model.articulation(
            f"hub_to_{name}",
            ArticulationType.REVOLUTE,
            parent=hub,
            child=branch,
            origin=Origin(xyz=(JOINT_RADIUS * cos(angle), JOINT_RADIUS * sin(angle), 0.0), rpy=(0.0, 0.0, angle)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=ARM_LIMITS,
        )

    return model
```
