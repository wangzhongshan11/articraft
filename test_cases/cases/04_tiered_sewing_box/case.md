# 多层铰接缝纫收纳盒

## Articraft public basis

sewing boxes with hinged lids（论文的数据集类别示例）

## Why this is a complex test

主盖铰链、两层联动托盘、连杆、开合轨迹、容器壁厚与装配间隙

## Acceptance focus

- - multi-part hierarchy
- linked opening mechanism
- thin-wall enclosure
- collision-free deployment
- BOM traceability

## Required printable / trace outputs

- Per-part printable STL or 3MF; `model.step` if the target supports B-Rep.
- Executable source / `model.py`; URDF; semantic part and joint manifests.
- `events.jsonl`, artifact lineage, metrics, print plan, and motion probe evidence.
- A distinct `agent_generated` vs `validator_derived` provenance label for every artifact.

## Important limitation

This is a desktop-scale demonstration model. It must not be marketed or evaluated as a real load-bearing, powered, flight-capable, heating, cutting, or child-safety product.
