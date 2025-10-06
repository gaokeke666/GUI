# 测试文档

## 测试结构

```
tests/
├── unit/                    # 单元测试
│   ├── test_image_utils.py    # 图像工具函数测试
│   └── test_task_manager.py   # 任务管理器测试
├── integration/             # 集成测试
│   └── test_workflow.py       # 工作流程测试
├── uat/                     # 用户验收测试
│   └── test_user_scenarios.py # 用户场景测试
├── conftest.py              # pytest配置和fixture
└── README.md                # 本文件
```

---

## 快速开始

### 1. 安装测试依赖

```bash
pip install pytest pytest-qt pytest-cov
```

### 2. 运行所有测试

```bash
# 在项目根目录执行
pytest
```

### 3. 运行特定类型的测试

```bash
# 只运行单元测试
pytest tests/unit/

# 只运行集成测试
pytest tests/integration/

# 只运行用户验收测试
pytest tests/uat/
```

### 4. 运行特定测试文件

```bash
pytest tests/unit/test_image_utils.py
```

### 5. 运行特定测试函数

```bash
pytest tests/unit/test_image_utils.py::TestImageSizeCalculation::test_scale_calculation_2x
```

---

## 测试类型说明

### 单元测试 (Unit Tests)

**目的**：测试单个函数或类的功能是否正确

**特点**：
- 测试粒度最小
- 运行速度快
- 不依赖外部资源（数据库、GPU等）
- 使用Mock模拟依赖

**示例**：
```python
def test_scale_calculation_2x(self):
    """测试2倍缩放计算是否准确"""
    original_width = 800
    original_height = 600
    scale = 2.0
    
    result_width = int(original_width * scale)
    result_height = int(original_height * scale)
    
    assert result_width == 1600
    assert result_height == 1200
```

**运行**：
```bash
pytest tests/unit/ -v
```

---

### 集成测试 (Integration Tests)

**目的**：测试多个模块组合在一起时是否能正常工作

**特点**：
- 测试模块间的交互
- 可能需要部分真实环境
- 运行时间较长
- 验证数据流和控制流

**示例**：
```python
def test_gpu_selection_integration(self, qapp, mock_config):
    """测试GPU选择是否能正确应用到图像处理模块"""
    from conf import config
    
    # 模拟设置界面选择GPU
    selected_gpu = 0
    config.Gpu = selected_gpu
    
    # 验证配置已更新
    assert config.Gpu == selected_gpu
    
    # 模拟图像处理模块读取配置
    gpu_for_processing = config.Gpu
    assert gpu_for_processing == selected_gpu
```

**运行**：
```bash
pytest tests/integration/ -v
```

---

### 用户验收测试 (UAT - User Acceptance Testing)

**目的**：模拟真实用户的使用场景，发现潜在的bug和体验问题

**特点**：
- 测试完整的用户流程
- 关注用户体验
- 测试边界情况和异常场景
- 可能需要真实环境

**示例**：
```python
def test_open_and_process_single_image(self, qapp):
    """
    场景：用户打开一张图片并进行处理
    步骤：
    1. 启动应用
    2. 点击"打开图片"按钮
    3. 选择图片文件
    4. 设置处理参数
    5. 点击"转换"
    6. 等待处理完成
    7. 保存结果
    """
    from src.qt.com.qtimg import QtImg
    
    img_widget = QtImg()
    img_widget.show()
    
    # 模拟用户操作...
    img_widget.data = b"fake_image_data"
    img_widget.scaleEdit.setText("2.0")
    
    # 验证结果...
    assert img_widget.data is not None
    
    img_widget.close()
```

**运行**：
```bash
pytest tests/uat/ -v
```

---

## 高级用法

### 1. 使用标记运行特定测试

```bash
# 运行标记为slow的测试
pytest -m slow

# 排除GPU测试
pytest -m "not gpu"
```

### 2. 生成测试覆盖率报告

```bash
# 生成HTML覆盖率报告
pytest --cov=src --cov-report=html

# 查看报告
# 打开 htmlcov/index.html
```

### 3. 并行运行测试（需要安装pytest-xdist）

```bash
pip install pytest-xdist

# 使用4个CPU核心并行运行
pytest -n 4
```

### 4. 只运行失败的测试

```bash
# 第一次运行
pytest

# 只重新运行失败的测试
pytest --lf
```

### 5. 详细输出

```bash
# 显示print输出
pytest -s

# 显示详细的assert信息
pytest -vv
```

---

## 编写新测试的指南

### 1. 命名规范

- 测试文件：`test_*.py`
- 测试类：`Test*`
- 测试函数：`test_*`

### 2. 测试结构

```python
def test_function_name(self):
    """测试描述"""
    # 1. 准备 (Arrange)
    input_data = "test"
    
    # 2. 执行 (Act)
    result = function_to_test(input_data)
    
    # 3. 断言 (Assert)
    assert result == expected_value
```

### 3. 使用Fixture

```python
@pytest.fixture
def sample_data():
    """提供测试数据"""
    return {"key": "value"}

def test_with_fixture(sample_data):
    """使用fixture的测试"""
    assert sample_data["key"] == "value"
```

### 4. 参数化测试

```python
@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
])
def test_square(input, expected):
    """测试平方计算"""
    assert input ** 2 == expected
```

---

## 常见问题

### Q1: 测试运行时找不到模块

**解决方案**：确保项目根目录在Python路径中
```python
# 在conftest.py中添加
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
```

### Q2: Qt相关测试失败

**解决方案**：确保使用了qapp fixture
```python
def test_qt_widget(qapp):  # 注意这里的qapp参数
    from PySide6.QtWidgets import QPushButton
    button = QPushButton("Test")
    assert button.text() == "Test"
```

### Q3: 如何跳过某些测试

```python
@pytest.mark.skip(reason="暂时跳过")
def test_something():
    pass

@pytest.mark.skipif(sys.platform == "win32", reason="Windows下跳过")
def test_linux_only():
    pass
```

---

## 持续集成 (CI)

### GitHub Actions 示例

创建 `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-qt pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

---

## 测试最佳实践

1. **测试应该独立**：每个测试不应依赖其他测试的结果
2. **测试应该快速**：单元测试应该在毫秒级完成
3. **测试应该可重复**：多次运行应该得到相同结果
4. **测试应该有意义**：测试名称应该清楚说明测试内容
5. **一个测试一个断言**：尽量每个测试只验证一个行为
6. **使用Mock隔离依赖**：避免测试依赖外部资源
7. **测试边界条件**：测试最小值、最大值、空值等
8. **保持测试简单**：测试代码应该比被测代码更简单

---

## 测试覆盖率目标

- **单元测试**：目标覆盖率 > 80%
- **集成测试**：覆盖主要业务流程
- **UAT测试**：覆盖所有用户场景

---

## 参考资源

- [pytest官方文档](https://docs.pytest.org/)
- [pytest-qt文档](https://pytest-qt.readthedocs.io/)
- [测试驱动开发(TDD)](https://en.wikipedia.org/wiki/Test-driven_development)
