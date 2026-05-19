---
title: '双分支独立旋转 Y 形树'
description: '摘自五星 Y 形树记录；展示从单一主干分出两条彼此独立驱动的旋转分支。'
tags:
  - cadquery
  - examples
  - articulation
  - 分支
  - 旋转
  - 树形
---
# 双分支独立旋转 Y 形树

本片段保留五星 **Y 形树**记录中真实的「主干 + 左右两支」分解方式，是理解**非串联**关节图（articulation graph）的最简清晰范例：两条分支均直接连在主干上，而非首尾串联。

**结构：**

- `trunk`：深色机架/主干，带碰撞与视觉网格。
- `left_branch` / `right_branch`：对称绿色分支，各自独立网格。
- 两个 `REVOLUTE` 关节共享 Y 轴旋转，原点位于主干两侧 hub 位置（`±HUB_X`, `HUB_Z`）。
- `MotionLimits` 限制摆角、力矩与速度，便于仿真与规划。

```python
from sdk import ArticulatedObject, ArticulationType, Box, Inertial, MotionLimits, Origin, mesh_from_cadquery


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="mechanical_y_tree", assets=ASSETS)

    model.material("frame_dark", rgba=(0.22, 0.24, 0.27, 1.0))
    model.material("branch_green", rgba=(0.31, 0.54, 0.36, 1.0))

    trunk = model.part("trunk")
    trunk.visual(mesh_from_cadquery(_build_trunk_shape(), "trunk.obj", assets=ASSETS), material="frame_dark")

    left_branch = model.part("left_branch")
    left_branch.visual(mesh_from_cadquery(_build_branch_shape("left"), "left_branch.obj", assets=ASSETS), material="branch_green")

    right_branch = model.part("right_branch")
    right_branch.visual(mesh_from_cadquery(_build_branch_shape("right"), "right_branch.obj", assets=ASSETS), material="branch_green")

    model.articulation("trunk_to_left_branch", ArticulationType.REVOLUTE, parent=trunk, child=left_branch, origin=Origin(xyz=(-HUB_X, 0.0, HUB_Z)), axis=(0.0, 1.0, 0.0), motion_limits=MotionLimits(lower=-0.24, upper=0.24, effort=4.0, velocity=1.5))
    model.articulation("trunk_to_right_branch", ArticulationType.REVOLUTE, parent=trunk, child=right_branch, origin=Origin(xyz=(HUB_X, 0.0, HUB_Z)), axis=(0.0, 1.0, 0.0), motion_limits=MotionLimits(lower=-0.24, upper=0.24, effort=4.0, velocity=1.5))

    return model
```
