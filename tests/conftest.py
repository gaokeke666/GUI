"""
pytest配置文件
提供测试所需的fixture（测试夹具）
"""
import sys
import os
import pytest
from PySide6.QtWidgets import QApplication

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="session")
def qapp():
    """
    创建QApplication实例（整个测试会话只创建一次）
    所有需要Qt环境的测试都依赖这个fixture
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    # 测试结束后清理（可选）


@pytest.fixture
def sample_image_path():
    """
    提供测试用的示例图片路径
    """
    test_dir = os.path.dirname(__file__)
    return os.path.join(test_dir, "test_data", "sample.jpg")


@pytest.fixture
def mock_config():
    """
    模拟配置对象
    """
    from conf import config
    original_can_waifu2x = config.CanWaifu2x
    
    # 设置测试配置
    config.CanWaifu2x = False  # 测试时禁用GPU，避免依赖硬件
    
    yield config
    
    # 恢复原始配置
    config.CanWaifu2x = original_can_waifu2x
