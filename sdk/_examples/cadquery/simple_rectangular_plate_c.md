---
title: '简单矩形板'
description: '几乎最简单的示例：矩形盒体。'
tags:
  - cadquery
  - examples
  - simple
  - rectangular
  - plate
---
# 简单矩形板

几乎最简单的 CadQuery 入门示例：拉伸一个矩形盒体。

```python
result = cadquery.Workplane("front").box(2.0, 2.0, 0.5)
```
