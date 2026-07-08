# 折叠三脚架手机/相机支架

## Articraft public basis

tripod-mounted devices（论文的数据集类别示例）

## Why this is a complex test

三脚架腿、中心滑环、云台俯仰、夹具、球/销轴近似机构

## Acceptance focus

- - radial repetition
- mixed revolute/prismatic joints
- stability geometry
- multi-state validation
- functional sizing

## Required printable / trace outputs

- Per-part printable STL or 3MF; `model.step` if the target supports B-Rep.
- Executable source / `model.py`; URDF; semantic part and joint manifests.
- `events.jsonl`, artifact lineage, metrics, print plan, and motion probe evidence.
- A distinct `agent_generated` vs `validator_derived` provenance label for every artifact.

## Important limitation

This is a desktop-scale demonstration model. It must not be marketed or evaluated as a real load-bearing, powered, flight-capable, heating, cutting, or child-safety product.
