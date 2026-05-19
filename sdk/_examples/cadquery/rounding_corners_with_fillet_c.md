---
title: '用圆角倒圆角'
description: '选择实体边并调用圆角函数完成倒角。'
tags:
  - cadquery
  - examples
  - rounding
  - corners
  - with
  - fillet
---
# 用圆角倒圆角

对实体边执行圆角：先选边，再 `fillet()`。

下面对简单板的全部边做圆角。

```python
result = cq.Workplane("XY").box(3, 3, 0.5).edges("|Z").fillet(0.125)
```
