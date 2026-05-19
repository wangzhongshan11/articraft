---
title: '乐高砖'
description: '参数化生成标准矩形乐高砖；底面柱/管逻辑随凸点行列数变化。'
tags:
  - cadquery
  - examples
  - 乐高
  - 砖块
---
# 乐高砖

本脚本可生成任意**长×宽凸点**的标准矩形乐高（Lego™）砖。难点主要在**底面**结构：1×1 无柱、单行/单列用实心柱、多×多用套管（外柱挖内孔）等，需按 `lbumps` / `wbumps` 分支处理。

**常量（乐高比例）：**

- `pitch = 8.0`：凸点中心距；`clearance`：装配间隙。
- `bumpDiam` / `bumpHeight`：顶面圆柱凸点。
- `thin`：薄砖 3.2 mm，厚砖 9.6 mm。
- 先 `box` 再底面 `shell` 向内抽壳，顶面 `rarray` 布凸点；底面 `invert=True` 工作平面再布柱或管。

```python
# Inputs
lbumps = 6  # number of bumps long
wbumps = 2  # number of bumps wide
thin = True  # True for thin, False for thick

# Lego Brick Constants-- these make a Lego brick a Lego :)
pitch = 8.0
clearance = 0.1
bumpDiam = 4.8
bumpHeight = 1.8
if thin:
    height = 3.2
else:
    height = 9.6

t = (pitch - (2 * clearance) - bumpDiam) / 2.0
postDiam = pitch - t  # works out to 6.5
total_length = lbumps * pitch - 2.0 * clearance
total_width = wbumps * pitch - 2.0 * clearance

# make the base
s = cq.Workplane("XY").box(total_length, total_width, height)

# shell inwards not outwards
s = s.faces("<Z").shell(-1.0 * t)

# make the bumps on the top
s = (
    s.faces(">Z")
    .workplane()
    .rarray(pitch, pitch, lbumps, wbumps, True)
    .circle(bumpDiam / 2.0)
    .extrude(bumpHeight)
)

# add posts on the bottom. posts are different diameter depending on geometry
# solid studs for 1 bump, tubes for multiple, none for 1x1
tmp = s.faces("<Z").workplane(invert=True)

if lbumps > 1 and wbumps > 1:
    tmp = (
        tmp.rarray(pitch, pitch, lbumps - 1, wbumps - 1, center=True)
        .circle(postDiam / 2.0)
        .circle(bumpDiam / 2.0)
        .extrude(height - t)
    )
elif lbumps > 1:
    tmp = (
        tmp.rarray(pitch, pitch, lbumps - 1, 1, center=True)
        .circle(t)
        .extrude(height - t)
    )
elif wbumps > 1:
    tmp = (
        tmp.rarray(pitch, pitch, 1, wbumps - 1, center=True)
        .circle(t)
        .extrude(height - t)
    )
else:
    tmp = s
```
