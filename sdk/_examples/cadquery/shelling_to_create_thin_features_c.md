---
title: '抽壳生成薄壁特征'
description: '抽壳将实心体变为等厚度薄壳。'
tags:
  - cadquery
  - examples
  - shelling
  - to
  - create
  - thin
  - features
---
# 抽壳生成薄壁特征

抽壳将实心体变为等厚度薄壳。

要对零件“挖空”内腔，向 `Workplane.shell()` 传入**负**厚度。

```python
result = cq.Workplane("front").box(2, 2, 2).shell(-0.1)
```

**正**厚度会在外侧包裹一层带圆角的壳体，原实体成为被掏空部分。

```python
result = cq.Workplane("front").box(2, 2, 2).shell(0.1)
```

可用面选择器指定要从空心结果中移除的面。

```python
result = cq.Workplane("front").box(2, 2, 2).faces("+Z").shell(0.1)
```

也可用更复杂的选择器一次移除多个面。

```python
result = cq.Workplane("front").box(2, 2, 2).faces("+Z or -X or +X").shell(0.1)
```
