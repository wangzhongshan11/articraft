---
title: '单转动铰链'
description: '摘自五星壁挂柜记录；展示柜体、门扇与铰链布局。'
tags:
  - cadquery
  - examples
  - articulation
  - revolute
  - hinge
  - cabinet
---
# 单转动铰链

保留五星橱柜示例的真实零件拆分与铰链位置；此处省略辅助网格与尺寸常量，对象逻辑不变。

关键符号约定：关门时门扇沿铰链线局部 `+X` 伸出，故 `axis=(0, 0, 1)` 使关节角增大时自由边摆向局部/前方 `+Y`，而非撞入柜体。

```python
from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    Inertial,
    MotionLimits,
    Origin,
)


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="wall_mounted_cabinet", assets=ASSETS)

    carcass_finish = model.material("carcass_finish", rgba=(0.93, 0.94, 0.95, 1.0))
    door_finish = model.material("door_finish", rgba=(0.90, 0.91, 0.92, 1.0))
    handle_finish = model.material("handle_finish", rgba=(0.10, 0.10, 0.11, 1.0))

    body = model.part("cabinet_body")
    body.visual(_body_mesh(), material=carcass_finish)
    body.inertial = Inertial.from_geometry(
        Box((CABINET_WIDTH, CABINET_DEPTH, CABINET_HEIGHT)),
        mass=8.5,
    )

    door = model.part("door")
    door.visual(_door_panel_mesh(), material=door_finish)
    door.visual(_door_handle_mesh(), material=handle_finish)
    door.inertial = Inertial.from_geometry(
        Box((DOOR_WIDTH, DOOR_THICKNESS, DOOR_HEIGHT)),
        mass=2.6,
        origin=Origin(xyz=(DOOR_WIDTH / 2.0, DOOR_THICKNESS / 2.0, 0.0)),
    )

    model.articulation(
        "body_to_door",
        ArticulationType.REVOLUTE,
        parent="cabinet_body",
        child="door",
        origin=Origin(
            xyz=(
                -CABINET_WIDTH / 2.0 - HINGE_SIDE_OFFSET,
                CABINET_DEPTH / 2.0 + FRONT_GAP,
                0.0,
            )
        ),
        # Closed door geometry extends along +X from the hinge line.
        # Positive q around +Z swings the free edge outward toward +Y.
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=1.85, effort=10.0, velocity=1.5),
    )

    return model
```
