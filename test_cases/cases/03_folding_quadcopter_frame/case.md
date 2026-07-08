# 折叠式四旋翼无人机机架（无电子件）

## Articraft public basis

drones（论文的数据集类别示例）

## Why this is a complex test

四向对称、4 个折叠臂关节、锁止结构、机身壳体与螺旋桨安装位

## Acceptance focus

- - circular symmetry
- repeated joints
- folded/open states
- locking geometry
- assembly completeness

## Required printable / trace outputs

- Per-part printable STL or 3MF; `model.step` if the target supports B-Rep.
- Executable source / `model.py`; URDF; semantic part and joint manifests.
- `events.jsonl`, artifact lineage, metrics, print plan, and motion probe evidence.
- A distinct `agent_generated` vs `validator_derived` provenance label for every artifact.

## Important limitation

This is a desktop-scale demonstration model. It must not be marketed or evaluated as a real load-bearing, powered, flight-capable, heating, cutting, or child-safety product.
