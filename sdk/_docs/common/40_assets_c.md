# 资源辅助（Asset Helpers）

## 用途

当你需要为已创作的网格或输入网格指定**显式资源根目录**（在托管 harness 默认行为之外）时使用这些辅助函数。

在常规虚拟工作区流程中，通常**不需要**本页。编写可复用的本地脚本、测试或需要稳定磁盘网格路径的工具流时，再使用 `AssetContext`。

## 导入

```python
from sdk import AssetContext, ArticulatedObject
```

## 推荐 API

- `AssetContext(...)`
- `AssetContext.from_script(...)`
- `ArticulatedObject(..., assets=...)`

## `AssetContext`

```python
AssetContext(
    root: str | Path,
    mesh_subdir: str = "assets/meshes",
)
```

- `root`：脚本或测试的资源根目录。
- `mesh_subdir`：`root` 下的相对网格目录。默认为 `"assets/meshes"`。

### `AssetContext.from_script(...)`

```python
AssetContext.from_script(
    script_path: str | Path,
) -> AssetContext
```

- 解析给定脚本路径的父目录。
- 这是独立 `model.py` 风格脚本的常规入口。

### 属性

```python
asset_root: Path
mesh_dir: Path
```

- `asset_root`：所有相对网格查找的已解析根目录。
- `mesh_dir`：应写入托管网格输出的已解析目录。

### 方法

```python
ensure_mesh_dir() -> Path
mesh_path(filename: str | Path, *, ensure_dir: bool = True) -> Path
mesh_ref(filename: str | Path) -> str
```

- `ensure_mesh_dir()`：按需创建 `mesh_dir` 并返回。
- `mesh_path(...)`：返回 `mesh_dir` 下的磁盘路径。
- `mesh_ref(...)`：返回相对于资源根的 SDK 网格文件名字符串，例如 `"assets/meshes/bracket.obj"`。

## `assets=` 的使用位置

以下公开接口接受显式资源所有者或根：

- `ArticulatedObject(..., assets=...)`
- `export_cadquery_mesh(..., assets=...)`
- `export_cadquery_components(..., assets=...)`
- `mesh_from_cadquery(..., assets=...)`
- `mesh_components_from_cadquery(..., assets=...)`

若对象模型已携带 `assets=...`，优先使用 `TestContext(model)`，而不要重复传入 `asset_root=...`。

## 推荐模式

```python
from sdk import AssetContext, ArticulatedObject, TestContext

ASSETS = AssetContext.from_script(__file__)

model = ArticulatedObject(name="example", assets=ASSETS)
ctx = TestContext(model)
```

## 写入托管网格

```python
from sdk import AssetContext, BoxGeometry, mesh_from_geometry

ASSETS = AssetContext.from_script(__file__)

mesh = mesh_from_geometry(
    BoxGeometry((0.10, 0.04, 0.02)),
    ASSETS.mesh_path("body.obj"),
)
```

- 需要可写路径时，对辅助函数使用 `mesh_path(...)`。
- 仅需 SDK 网格引用字符串时，使用 `mesh_ref(...)`。

## 说明

- `AssetContext` 为公开 API，但在 harness 内属于**高级**脚本/运行时辅助，而非默认创作路径。
- 相对网格引用相对于 `asset_root` 解析。
- 每个已创作模型尽量使用单一、一致的资源根。
