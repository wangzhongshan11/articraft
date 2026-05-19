# 错误（Errors）

SDK 中所有公开错误均派生自 `sdk.SDKError`。

## `SDKError`

```python
from sdk import SDKError
```

关节物体 SDK 的基类异常。

## `ValidationError`

```python
from sdk import ValidationError
```

当关节物体定义或 QC 检查无效、不一致或无法求值时抛出。

## 导入错误

若出现针对 `sdk.placement`、`sdk.testing` 或 `sdk.core_types` 等的 `ModuleNotFoundError`，常见原因是把**文档主题名**当成了 **Python 子模块**。

应从顶层 `sdk` 导入公开创作辅助函数：

```python
# 正确
from sdk import TestContext, ValidationError, place_on_face

# 错误
from sdk.testing import TestContext
from sdk.placement import place_on_face
```
