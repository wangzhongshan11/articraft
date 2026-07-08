# 可俯仰桌面风扇（无电机功能原型）

## Articraft public basis

compact desk fan with adjustable tilt（README 明确作为生成示例）

## Why this is a complex test

风扇外壳、叶片轮毂、倾角支架、旋转与俯仰两类运动、网罩阵列

## Acceptance focus

- - radial array
- rotational kinematics
- tilt axis
- part separation
- safety clearance

## Required printable / trace outputs

- Per-part printable STL or 3MF; `model.step` if the target supports B-Rep.
- Executable source / `model.py`; URDF; semantic part and joint manifests.
- `events.jsonl`, artifact lineage, metrics, print plan, and motion probe evidence.
- A distinct `agent_generated` vs `validator_derived` provenance label for every artifact.

## Important limitation

This is a desktop-scale demonstration model. It must not be marketed or evaluated as a real load-bearing, powered, flight-capable, heating, cutting, or child-safety product.
