# 折叠式工具推车/婴儿车骨架模型（非承载）

## Articraft public basis

strollers（论文列举的典型铰接日常物件）

## Why this is a complex test

四轮架、折叠推杆、车斗框、交叉连杆、轮轴、展开锁止

## Acceptance focus

- - multi-body hierarchy
- wheel/hinge coexistence
- folding mechanism
- repeated parts
- assembly trace

## Required printable / trace outputs

- Per-part printable STL or 3MF; `model.step` if the target supports B-Rep.
- Executable source / `model.py`; URDF; semantic part and joint manifests.
- `events.jsonl`, artifact lineage, metrics, print plan, and motion probe evidence.
- A distinct `agent_generated` vs `validator_derived` provenance label for every artifact.

## Important limitation

This is a desktop-scale demonstration model. It must not be marketed or evaluated as a real load-bearing, powered, flight-capable, heating, cutting, or child-safety product.
