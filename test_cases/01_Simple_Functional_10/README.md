# Simple Functional Components — S01–S10

This package is organized as standalone benchmark task folders. Every case includes a task card, a directly usable English prompt, and one matching visual reference crop.

## Per-case contents

- `task_card.md` — bilingual benchmark task, metadata, required features, and evaluation checks
- `prompt_en.txt` — English-only prompt for cross-platform CAD-agent evaluation
- `reference_<case>.png` — visual reference crop retaining title, views, and nominal dimensions
- `reference_note.md` — scope and priority of the image reference

**Priority rule:** task-card text and explicit dimensions are authoritative. The image guides form, component relationships, and overall proportion.

---

# Simple Functional Cases (S01–S10)

These ten benchmark tasks test basic but practical CAD generation: hollow shells, cutouts, arrays, fillets, basic fit, and light assembly relationships.

## How to run
1. Use the English text under **Benchmark input prompt** from each `.md` file as the exact agent input.
2. Keep the same model, system prompt, time cap, temperature/thinking settings, and output contract across all agents.
3. Collect the native source/code where available, STEP, STL, assembly/part structure, runtime, errors, and a standardized render.
4. Score the result with the embedded **Must be present** and **Evaluation checks** rather than visual resemblance alone.

## Prompt design basis
The wording keeps the Articraft-style sequence of object identity → major visible parts → part connection / function, while adding nominal dimensions and exportability needed for a CAD benchmark. It intentionally avoids prescribing a specific CAD operation such as “perform a Boolean cut,” so the test measures whether the agent can infer and execute the required geometry.
