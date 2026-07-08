# S07 · 挂桌耳机支架 / Desk-clamp headphone hook

> **Visual reference**: `reference_S07_desk_clamp_headphone_hook.png`  \
> Use the reference image for overall form, component relationship, feature placement, and proportional reading. The English benchmark prompt and task-card dimensions remain the authoritative requirements for scoring.

## Benchmark input prompt (English)

Create a realistic, manufacturable 3D CAD model in millimetres. Build only the described object; do not add logos, text labels, or unrelated decorative features. Keep the construction readable and mechanically credible, with clean continuous faces where appropriate. Export semantic parts as a small assembly when more than one part is specified; otherwise export one watertight solid. The result should be suitable for STEP and STL export.

Create a one-piece headphone hook that hangs from a desk edge. The object is about 90 mm wide, 60 mm deep, and 110 mm high. Form a downward-facing clamp slot sized to fit a 25–35 mm thick desk edge, with a short internal retaining ledge. Extend a rounded hook below the clamp so a headphone headband can hang from it. Use broad fillets at the hook-to-body transition and avoid thin unsupported decorative features.

## 中文对照

请以毫米为单位创建真实、可制造的 3D CAD 模型。仅建模所述对象，不添加 Logo、文字标签或无关装饰。构造关系应清晰、符合基本制造逻辑；在应为连续制造面的位置保持连续面。若包含多个部件，请作为小型装配输出并使用语义化部件名称；若仅含一个部件，则输出一个封闭实体。结果应可用于 STEP 与 STL 导出。

创建一个可挂在桌边的一体式耳机支架，整体约宽 90 mm、深 60 mm、高 110 mm。形成向下开口、可夹持 25–35 mm 厚桌板边缘的夹槽，并在内侧设置短定位边。夹槽下方延伸出圆润挂钩，用于悬挂耳机头梁；挂钩与主体交接处采用较大圆角，避免细薄且无支撑的装饰特征。

## Case metadata

- **Group**: simple_functional
- **Reference dimensions**: 90 × 60 × 110 mm; fits a 25–35 mm desk edge
- **Target capability tags**: single part, clamp slot, hook, fillets

## Must be present

- single part
- desk-edge clamp slot
- retaining ledge
- rounded hanging hook
- large transition fillets

## Evaluation checks

- one watertight solid
- slot accessible from below
- hook has continuous support
- no floating geometry

## Benchmark note

Use the English prompt above as the cross-platform input. The Chinese section is a human-readable equivalent and should not be concatenated into the same test prompt. Reference dimensions are nominal: a system may make small manufacturing-minded adjustments only where needed to preserve valid geometry, but must preserve the stated object type, part relations, and key feature locations.
