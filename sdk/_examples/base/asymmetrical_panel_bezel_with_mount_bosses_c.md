---
title: '带安装凸台的不对称面板边框'
description: 'Base SDK 示例：使用 BezelGeometry 展示偏移面板边框，含不对称壁厚、后部凸台与边缘切口细节。'
tags:
  - sdk
  - base sdk
  - bezel
  - panel bezel
  - control panel
  - instrument bezel
  - mount bosses
  - recessed frame
  - trim frame
  - mesh geometry
---
# 带安装凸台的不对称面板边框

本 Base SDK 示例是 `BezelGeometry` 在**非完全对称**装饰框场景下的强参考。它在紧凑的单零件示例中同时展示了：四边不对称壁厚、后部安装凸台（bosses）、右侧边缘切口，以及底部凹槽（notch）特征。

**适用查询关键词：** `bezel`、`panel bezel`、`BezelGeometry`、`mount bosses`、`control panel`、`instrument bezel`。

**建模模式值得借鉴：**
- `BezelGeometry` 一次性定义内开窗、外轮廓、深度与圆角。
- `wall=(0.012, 0.020, 0.010, 0.014)` 分别对应四边壁厚，制造视觉上的不对称感。
- `BezelMounts(style="bosses", ...)` 在背面生成 4 个带凸台的安装孔。
- `BezelCutout(edge="right", ...)` 与 `BezelEdgeFeature(style="notch", edge="bottom", ...)` 叠加边缘工艺细节。

**尺寸与测试：** 外廓约 0.112×0.082，深度约 0.012；`run_tests` 校验宽度 0.108–0.118、高度 0.078–0.086、深度 0.010–0.018。

```python
from __future__ import annotations

from sdk import (
    ArticulatedObject,
    BezelCutout,
    BezelEdgeFeature,
    BezelGeometry,
    BezelMounts,
    Box,
    Inertial,
    TestContext,
    TestReport,
    mesh_from_geometry,
)

OUTER_SIZE = (0.112, 0.082)
DEPTH = 0.012


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="asym_panel_bezel")
    finish = model.material("panel_bezel_blue", rgba=(0.20, 0.28, 0.36, 1.0))

    bezel = model.part("bezel")
    bezel.visual(
        mesh_from_geometry(
            BezelGeometry(
                (0.070, 0.044),
                OUTER_SIZE,
                DEPTH,
                outer_corner_radius=0.008,
                wall=(0.012, 0.020, 0.010, 0.014),
                mounts=BezelMounts(
                    style="bosses",
                    hole_count=4,
                    hole_diameter=0.003,
                    boss_diameter=0.007,
                    setback=0.004,
                ),
                cutouts=(BezelCutout(edge="right", width=0.016, depth=0.004),),
                edge_features=(
                    BezelEdgeFeature(
                        style="notch",
                        edge="bottom",
                        size=0.004,
                        extent=0.016,
                    ),
                ),
            ),
            "asym_panel_bezel",
        ),
        material=finish,
        name="bezel_shell",
    )
    bezel.inertial = Inertial.from_geometry(Box((OUTER_SIZE[0], OUTER_SIZE[1], 0.016)), mass=0.12)
    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    bezel = object_model.get_part("bezel")
    ctx.check("bezel_part_present", bezel is not None, "Expected a bezel part.")
    if bezel is None:
        return ctx.report()

    aabb = ctx.part_world_aabb(bezel)
    ctx.check("bezel_aabb_present", aabb is not None, "Expected a world AABB for the bezel.")
    if aabb is None:
        return ctx.report()

    mins, maxs = aabb
    size = tuple(float(maxs[i] - mins[i]) for i in range(3))
    ctx.check("bezel_width", 0.108 <= size[0] <= 0.118, f"size={size!r}")
    ctx.check("bezel_height", 0.078 <= size[1] <= 0.086, f"size={size!r}")
    ctx.check("bezel_depth", 0.010 <= size[2] <= 0.018, f"size={size!r}")
    return ctx.report()


object_model = build_object_model()
```
