# Furniture Components — F01–F10

This package is organized as standalone benchmark task folders. Every case includes a task card, a directly usable English prompt, and one matching visual reference crop.

## Per-case contents

- `task_card.md` — bilingual benchmark task, metadata, required features, and evaluation checks
- `prompt_en.txt` — English-only prompt for cross-platform CAD-agent evaluation
- `reference_<case>.png` — visual reference crop retaining title, views, and nominal dimensions
- `reference_note.md` — scope and priority of the image reference

**Priority rule:** task-card text and explicit dimensions are authoritative. The image guides form, component relationships, and overall proportion.

---

# Furniture Cases (F01–F10)

These ten benchmark tasks test furniture-oriented CAD composition: board and leg construction, symmetry, repetition, rounded edges, cabinet/drawer/door relations, and stable assembly.

## How to run
1. Use the English text under **Benchmark input prompt** from each `.md` file as the exact agent input.
2. Keep the same model, system prompt, time cap, temperature/thinking settings, and output contract across all agents.
3. Collect the native source/code where available, STEP, STL, assembly/part structure, runtime, errors, and a standardized render.
4. Score the result with the embedded **Must be present** and **Evaluation checks** rather than visual resemblance alone.

## Prompt design basis
The wording keeps the Articraft-style sequence of object identity → major visible parts → part connection / function, while adding nominal dimensions and exportability needed for a CAD benchmark. It deliberately avoids requiring a specific implementation route, allowing the benchmark to reveal each agent’s actual capability.
