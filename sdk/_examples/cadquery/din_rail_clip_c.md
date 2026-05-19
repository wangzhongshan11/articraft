---
title: 'DIN 导轨卡扣'
description: '塑料 DIN 导轨卡扣：标记工作平面、沉头孔与选择器倒角。'
tags:
  - cadquery
  - examples
  - din
  - rail
  - clip
  - cskHole
  - workplaneFromTagged
  - 导轨
  - 卡扣
---
# DIN 导轨卡扣

本示例复现 `cq-electronics` 的 **DIN 导轨卡扣**模型，综合演示：

- 在底面（`<<Z`）开顶帽导轨槽（`rect` + `cutBlind`）。
- `tag` / `workplaneFromTagged` 在后续步骤回到已标记平面。
- 外侧与导轨开口面分别布 **沉头孔**（`cskHole`）。
- 用边选择器 `|Z and (>X or <X)` 对外竖边倒角。

M4  clearance / 沉头直径与角度、安装孔间距、圆角等均以变量给出，便于改规格。

```python
import cadquery as cq

top_hat_width = 35

m_countersink_angle = 90
m4_clearance_normal_diameter = 4.5
m4_countersink_diameter = 9.4

length = 76
width = 20
height = 8
between_mount_holes = 63
rail_aperture_depth = 4
corner_chamfer = 3

half_length = length / 2
rail_aperture_offset = half_length - 30
half_between_mount_holes = between_mount_holes / 2
rail_aperture_center = (-rail_aperture_offset, 0)

outer_mount_hole_centers = [
    (half_between_mount_holes, 0),
    (-half_between_mount_holes, 0),
]

result = (
    cq.Workplane()
    .box(length, width, height)
    .faces("<<Z")
    .workplane()
    .tag("workplane__rail_face")
    .pushPoints([rail_aperture_center])
    .rect(top_hat_width, width)
    .cutBlind(-rail_aperture_depth)
    .workplaneFromTagged("workplane__rail_face")
    .pushPoints(outer_mount_hole_centers)
    .cskHole(
        m4_clearance_normal_diameter,
        m4_countersink_diameter,
        m_countersink_angle,
    )
    .faces(">Z[1]")
    .workplane(centerOption="CenterOfBoundBox")
    .tag("workplane__rail_aperture_face")
    .cskHole(
        m4_clearance_normal_diameter,
        m4_countersink_diameter,
        m_countersink_angle,
    )
    .edges("|Z and (>X or <X)")
    .chamfer(corner_chamfer)
)
```
