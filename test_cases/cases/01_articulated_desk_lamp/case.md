# 双臂可调台灯

## Articraft public basis

desk lamps（论文列举的典型铰接日常物件；README 也用台灯作为生成示例）

## Why this is a complex test

2 个串联转动关节 + 灯头俯仰关节 + 底座 + 线缆导槽 + 关节限位

## Acceptance focus

- - part hierarchy
- serial joint axes
- range limits
- collision-free poses
- printable pivots

## Required printable / trace outputs

- Per-part printable STL or 3MF; `model.step` if the target supports B-Rep.
- Executable source / `model.py`; URDF; semantic part and joint manifests.
- `events.jsonl`, artifact lineage, metrics, print plan, and motion probe evidence.
- A distinct `agent_generated` vs `validator_derived` provenance label for every artifact.

## Important limitation

This is a desktop-scale demonstration model. It must not be marketed or evaluated as a real load-bearing, powered, flight-capable, heating, cutting, or child-safety product.
