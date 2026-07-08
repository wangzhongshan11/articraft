# 折叠椅结构模型（非承载）

## Articraft public basis

folding chairs（论文列举的典型铰接日常物件）

## Why this is a complex test

X 形连杆、座面、靠背、四腿、多个共轴销、开合干涉检查

## Acceptance focus

- - scissor linkage
- coaxial pivots
- folded-volume constraint
- pose tests
- safe use labeling

## Required printable / trace outputs

- Per-part printable STL or 3MF; `model.step` if the target supports B-Rep.
- Executable source / `model.py`; URDF; semantic part and joint manifests.
- `events.jsonl`, artifact lineage, metrics, print plan, and motion probe evidence.
- A distinct `agent_generated` vs `validator_derived` provenance label for every artifact.

## Important limitation

This is a desktop-scale demonstration model. It must not be marketed or evaluated as a real load-bearing, powered, flight-capable, heating, cutting, or child-safety product.
