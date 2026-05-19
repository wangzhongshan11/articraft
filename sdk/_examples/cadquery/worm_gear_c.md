---
title: '蜗杆'
description: '使用内嵌 `sdk` 齿轮实现生成蜗杆实体。'
tags:
  - cadquery
  - examples
  - gear
  - worm
---
# 蜗杆

蜗杆移植保持与上游相同的紧凑构造参数形式，返回标准 CadQuery 实体，可在统一 SDK 中复用。

```python
from sdk import Worm

worm = Worm(module=1.0, lead_angle=20.0, n_threads=2, length=18.0, bore_d=4.0)
result = worm.build()
```
