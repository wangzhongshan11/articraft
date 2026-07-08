# 微型健身车传动演示模型

## Articraft public basis

stationary exercise bikes（论文的数据集类别示例）

## Why this is a complex test

车架、曲柄、踏板、飞轮、皮带/齿轮传动近似、座椅调节

## Acceptance focus

- - rotational transmission layout
- mixed joint types
- parallel-axis accuracy
- repeated pedals
- printable assembly

## Required printable / trace outputs

- Per-part printable STL or 3MF; `model.step` if the target supports B-Rep.
- Executable source / `model.py`; URDF; semantic part and joint manifests.
- `events.jsonl`, artifact lineage, metrics, print plan, and motion probe evidence.
- A distinct `agent_generated` vs `validator_derived` provenance label for every artifact.

## Important limitation

This is a desktop-scale demonstration model. It must not be marketed or evaluated as a real load-bearing, powered, flight-capable, heating, cutting, or child-safety product.
