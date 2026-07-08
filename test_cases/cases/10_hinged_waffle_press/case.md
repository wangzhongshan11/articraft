# 铰接式压板/华夫饼机外观机构模型（无加热）

## Articraft public basis

waffle makers（论文的数据集类别示例）

## Why this is a complex test

上盖铰链、锁扣、上下压板、开闭限位、格纹阵列、壳体与内部间隙

## Acceptance focus

- - hinged enclosure
- latch semantics
- pattern array
- motion limits
- separable plates

## Required printable / trace outputs

- Per-part printable STL or 3MF; `model.step` if the target supports B-Rep.
- Executable source / `model.py`; URDF; semantic part and joint manifests.
- `events.jsonl`, artifact lineage, metrics, print plan, and motion probe evidence.
- A distinct `agent_generated` vs `validator_derived` provenance label for every artifact.

## Important limitation

This is a desktop-scale demonstration model. It must not be marketed or evaluated as a real load-bearing, powered, flight-capable, heating, cutting, or child-safety product.
