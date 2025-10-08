# 测试指南 - waifu2x-ncnn-vulkan-GUI

本文档详细说明如何对项目进行单元测试、集成测试和用户验收测试。

---

## 目录

1. [测试环境准备](#测试环境准备)
2. [单元测试](#单元测试)
3. [集成测试](#集成测试)
4. [用户验收测试](#用户验收测试)
5. [运行测试](#运行测试)
6. [测试报告](#测试报告)
7. [常见问题](#常见问题)

---

## 测试环境准备

### 1. 安装测试依赖

```bash
# 激活虚拟环境
.\venv\Scripts\activate

# 安装测试框架
pip install pytest pytest-qt pytest-cov pytest-mock

# 可选：安装代码质量检查工具
pip install flake8 black mypy
```

### 2. 验证安装

```bash
pytest --version
# 应该显示：pytest 7.x.x
```

### 3. 项目结构

```
waifu2x-ncnn-vulkan-GUI-main/
├── src/                    # 源代码
├── ui/                     # UI文件
├── tests/                  # 测试目录
│   ├── unit/              # 单元测试
│   ├── integration/       # 集成测试
│   ├── uat/               # 用户验收测试
│   └── conftest.py        # pytest配置
├── pytest.ini             # pytest配置文件
└── TESTING_GUIDE.md       # 本文件
```

---

## 单元测试

### 什么是单元测试？

单元测试是对项目中**最小可测试单元**（函数、类、方法）进行独立测试。

### 测试内容

#### 1. 图像尺寸计算函数测试

**测试文件**：`tests/unit/test_image_utils.py`

**测试项目**：
- ✅ 2倍缩放计算是否准确
- ✅ 4倍缩放计算是否准确
- ✅ 缩放后宽高比是否保持
- ✅ 多种缩放场景（参数化测试）
- ✅ 固定宽高模式计算

**运行方法**：
```bash
# 运行所有图像工具测试
pytest tests/unit/test_image_utils.py -v

# 运行特定测试
pytest tests/unit/test_image_utils.py::TestImageSizeCalculation::test_scale_calculation_2x -v
```

**示例输出**：
```
tests/unit/test_image_utils.py::TestImageSizeCalculation::test_scale_calculation_2x PASSED
tests/unit/test_image_utils.py::TestImageSizeCalculation::test_scale_calculation_4x PASSED
tests/unit/test_image_utils.py::TestImageSizeCalculation::test_aspect_ratio_preservation PASSED
```

#### 2. 任务管理器测试

**测试文件**：`tests/unit/test_task_manager.py`

**测试项目**：
- ✅ 任务ID是否正确自增
- ✅ 任务是否正确存储到字典
- ✅ 回调函数是否正确保存
- ✅ 清理标记的分组功能
- ✅ 任务取消功能
- ✅ 信号发射机制
- ✅ 线程安全性

**运行方法**：
```bash
# 运行所有任务管理器测试
pytest tests/unit/test_task_manager.py -v

# 运行特定测试类
pytest tests/unit/test_task_manager.py::TestTaskManager -v
```

### 如何编写单元测试

**模板**：
```python
class TestYourFunction:
    """测试你的函数"""
    
    def test_basic_functionality(self):
        """测试基本功能"""
        # 1. 准备测试数据
        input_value = 100
        expected_output = 200
        
        # 2. 执行被测函数
        result = your_function(input_value)
        
        # 3. 验证结果
        assert result == expected_output
    
    @pytest.mark.parametrize("input,expected", [
        (1, 2),
        (2, 4),
        (3, 6),
    ])
    def test_multiple_cases(self, input, expected):
        """参数化测试多个场景"""
        assert your_function(input) == expected
```

---

## 集成测试

### 什么是集成测试？

集成测试验证**多个模块组合在一起**时是否能正常工作。

### 测试内容

**测试文件**：`tests/integration/test_workflow.py`

#### 1. 设置界面到图像处理的集成

**测试场景**：
- ✅ GPU选择是否能正确应用到图像处理模块
- ✅ 模型选择是否正确传递到处理流程

**运行方法**：
```bash
pytest tests/integration/test_workflow.py::TestSettingsToProcessing -v
```

#### 2. UI层到任务管理器的集成

**测试场景**：
- ✅ 按钮点击是否能正确创建任务
- ✅ 任务提交流程是否正常

**运行方法**：
```bash
pytest tests/integration/test_workflow.py::TestUIToTaskManager -v
```

#### 3. 任务管理器到回调函数的集成

**测试场景**：
- ✅ 回调函数是否被正确调用
- ✅ 信号到回调的完整流程

**运行方法**：
```bash
pytest tests/integration/test_workflow.py::TestTaskManagerToCallback -v
```

#### 4. 端到端工作流程

**测试场景**：
- ✅ 完整的图像处理工作流程（不含实际GPU处理）
- ✅ 多任务并发处理流程
- ✅ 错误处理和异常情况
- ✅ 任务取消功能

**运行方法**：
```bash
pytest tests/integration/test_workflow.py::TestEndToEndWorkflow -v
```

### 如何编写集成测试

**模板**：
```python
class TestModuleIntegration:
    """测试模块集成"""
    
    def test_module_a_to_module_b(self, qapp):
        """测试模块A到模块B的数据流"""
        # 1. 初始化模块A
        module_a = ModuleA()
        
        # 2. 在模块A中设置数据
        module_a.set_value(100)
        
        # 3. 将数据传递给模块B
        module_b = ModuleB()
        module_b.receive_from_a(module_a.get_value())
        
        # 4. 验证数据正确传递
        assert module_b.value == 100
```

---

## 用户验收测试 (UAT)

### 什么是UAT？

UAT模拟**真实用户的使用场景**，进行完整的操作流程测试，发现潜在的bug和体验问题。

### 测试内容

**测试文件**：`tests/uat/test_user_scenarios.py`

#### 1. 基础用户场景

**场景1：打开并处理单张图片**
```
步骤：
1. 启动应用
2. 点击"打开图片"按钮
3. 选择图片文件
4. 设置处理参数（2倍放大，降噪等级0）
5. 点击"转换为JPG"
6. 等待处理完成
7. 保存结果
```

**场景2：切换缩放模式**
```
步骤：
1. 选择缩放模式，输入2倍
2. 切换到固定尺寸模式，输入1920x1080
3. 再切换回缩放模式
4. 验证输入框的启用/禁用状态
```

**场景3：更改输出格式**
```
步骤：
1. 加载JPG图片
2. 点击"转换为PNG"
3. 验证格式参数
```

**运行方法**：
```bash
pytest tests/uat/test_user_scenarios.py::TestBasicUserScenarios -v
```

#### 2. 压力测试场景

**场景4：快速连续修改参数**
```
测试内容：
- 快速修改缩放倍数（2x -> 3x -> 4x -> 2x）
- 快速切换模型类型
- 快速修改降噪等级
- 验证程序不崩溃
```

**场景5：连续加载多张图片**
```
测试内容：
- 加载第一张图片
- 不等待处理完成，立即加载第二张
- 再加载第三张
- 验证任务取消机制工作正常
```

**运行方法**：
```bash
pytest tests/uat/test_user_scenarios.py::TestStressScenarios -v
```

#### 3. 边界情况测试

**场景6-9：**
- ✅ 极大的缩放倍数（10倍）
- ✅ 极小的缩放倍数（0.5倍）
- ✅ 无效输入处理
- ✅ 空图像数据

**运行方法**：
```bash
pytest tests/uat/test_user_scenarios.py::TestEdgeCases -v
```

#### 4. UI响应性测试

**场景10：处理过程中UI保持响应**
```
测试内容：
- 开始图像处理
- 在处理过程中尝试拖动窗口
- 尝试点击其他按钮
- 验证UI不卡顿
```

**场景11：处理过程中取消操作**
```
测试内容：
- 开始处理
- 立即加载新图片（触发取消）
- 验证旧任务被取消
```

**运行方法**：
```bash
pytest tests/uat/test_user_scenarios.py::TestUIResponsiveness -v
```

#### 5. 数据完整性测试

**场景12-13：**
- ✅ 图像数据在传递过程中不被破坏
- ✅ 回调参数的完整性

**运行方法**：
```bash
pytest tests/uat/test_user_scenarios.py::TestDataIntegrity -v
```

#### 6. 并发操作测试

**场景14：多个窗口同时处理图像**
```
测试内容：
- 打开多个图像处理窗口
- 每个窗口加载不同的图片
- 同时开始处理
- 验证任务不会互相干扰
```

**运行方法**：
```bash
pytest tests/uat/test_user_scenarios.py::TestConcurrentOperations -v
```

#### 7. 内存和性能测试

**场景15-16：**
- ✅ 任务完成后内存正确清理
- ✅ 重复操作不会导致内存泄漏

**运行方法**：
```bash
pytest tests/uat/test_user_scenarios.py::TestMemoryAndPerformance -v
```

### 如何进行手动UAT

除了自动化测试，还应该进行手动测试：

**测试清单**：

- [ ] 拖拽不同格式的图片（JPG, PNG, WebP, BMP）
- [ ] 尝试各种参数组合
  - [ ] 缩放：1.5x, 2x, 3x, 4x
  - [ ] 降噪：-1, 0, 1, 2, 3
  - [ ] 模型：cunet, photo, anime
- [ ] 反复切换缩放模式和固定尺寸模式
- [ ] 在处理过程中关闭窗口
- [ ] 在处理过程中加载新图片
- [ ] 处理超大图片（> 4K分辨率）
- [ ] 处理超小图片（< 100x100）
- [ ] 长时间运行（处理100张图片）
- [ ] 检查内存使用是否稳定
- [ ] 检查CPU/GPU使用率

---

## 运行测试

### 1. 运行所有测试

```bash
# 在项目根目录执行
pytest
```

### 2. 运行特定类型的测试

```bash
# 只运行单元测试
.\venv\Scripts\python.exe -m pytest tests/unit/test_image_utils.py -v
pytest tests/unit/ -v

# 只运行集成测试
.\venv\Scripts\python.exe -m pytest tests/integration/ -v

# 只运行UAT测试
.\venv\Scripts\python.exe -m pytest tests/uat/ -v
```

### 3. 运行特定测试文件

```bash
.\venv\Scripts\python.exe -m pytest tests/unit/test_image_utils.py -v
```

### 4. 运行特定测试类

```bash
.\venv\Scripts\python.exe -m pytest tests/unit/test_image_utils.py::TestImageSizeCalculation -v
```

### 5. 运行特定测试函数

```bash
.\venv\Scripts\python.exe -m pytest tests/unit/test_image_utils.py::TestImageSizeCalculation::test_scale_calculation_2x -v
```

### 6. 使用标记运行测试

```bash
# 运行标记为slow的测试
.\venv\Scripts\python.exe -m pytest -m slow

# 排除GPU测试
.\venv\Scripts\python.exe -m pytest -m "not gpu"
```

### 7. 显示详细输出

```bash
# 显示print输出
.\venv\Scripts\python.exe -m pytest -s

# 显示详细的assert信息
.\venv\Scripts\python.exe -m pytest -vv
```

### 8. 只运行失败的测试

```bash
# 第一次运行
pytest

# 只重新运行失败的测试
pytest --lf
```

---

## 测试报告

### 1. 生成覆盖率报告

```bash
# 生成HTML覆盖率报告
pytest --cov=src --cov-report=html

# 查看报告
# 打开 htmlcov/index.html
```

### 2. 生成测试报告

```bash
# 安装pytest-html
pip install pytest-html

# 生成HTML测试报告
pytest --html=report.html --self-contained-html
```

### 3. 查看测试统计

```bash
# 显示最慢的10个测试
pytest --durations=10
```

---

## 常见问题

### Q1: 测试运行时找不到模块

**问题**：
```
ImportError: No module named 'src'
```

**解决方案**：
确保在 `conftest.py` 中添加了项目路径：
```python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
```

### Q2: Qt相关测试失败

**问题**：
```
RuntimeError: Please destroy the QApplication singleton before creating a new QApplication instance.
```

**解决方案**：
使用 `qapp` fixture：
```python
def test_qt_widget(qapp):  # 注意这里的qapp参数
    from PySide6.QtWidgets import QPushButton
    button = QPushButton("Test")
    assert button.text() == "Test"
```

### Q3: 测试运行很慢

**解决方案**：
1. 使用并行测试（需要安装 `pytest-xdist`）：
```bash
pip install pytest-xdist
pytest -n 4  # 使用4个CPU核心
```

2. 只运行快速测试：
```bash
pytest -m "not slow"
```

### Q4: 如何跳过某些测试

```python
@pytest.mark.skip(reason="暂时跳过")
def test_something():
    pass

@pytest.mark.skipif(sys.platform == "win32", reason="Windows下跳过")
def test_linux_only():
    pass
```

---

## 测试最佳实践

1. **测试应该独立**：每个测试不应依赖其他测试的结果
2. **测试应该快速**：单元测试应该在毫秒级完成
3. **测试应该可重复**：多次运行应该得到相同结果
4. **测试应该有意义**：测试名称应该清楚说明测试内容
5. **一个测试一个断言**：尽量每个测试只验证一个行为
6. **使用Mock隔离依赖**：避免测试依赖外部资源（GPU、网络等）
7. **测试边界条件**：测试最小值、最大值、空值等
8. **保持测试简单**：测试代码应该比被测代码更简单

---

## 持续集成

建议在每次提交代码前运行测试：

```bash
# 运行所有测试
pytest

# 检查代码风格
flake8 src/

# 格式化代码
black src/

# 类型检查
mypy src/
```

---

## 总结

- **单元测试**：测试单个函数/类，快速、独立
- **集成测试**：测试模块间交互，验证数据流
- **UAT测试**：模拟用户场景，发现体验问题

**测试覆盖率目标**：
- 单元测试：> 80%
- 集成测试：覆盖主要业务流程
- UAT测试：覆盖所有用户场景

**运行频率**：
- 单元测试：每次代码修改后
- 集成测试：每次功能完成后
- UAT测试：每次发布前

祝测试顺利！🎉
