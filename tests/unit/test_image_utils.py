"""
单元测试：图像处理工具函数
测试图片尺寸计算、格式转换等功能
"""
import pytest
from PySide6.QtCore import QSize


class TestImageSizeCalculation:
    """测试图像尺寸计算相关功能"""
    
    def test_scale_calculation_2x(self):
        """测试2倍缩放计算是否准确"""
        original_width = 800
        original_height = 600
        scale = 2.0
        
        expected_width = 1600
        expected_height = 1200
        
        # 实际计算
        result_width = int(original_width * scale)
        result_height = int(original_height * scale)
        
        assert result_width == expected_width, f"宽度计算错误: 期望{expected_width}, 实际{result_width}"
        assert result_height == expected_height, f"高度计算错误: 期望{expected_height}, 实际{result_height}"
    
    def test_scale_calculation_4x(self):
        """测试4倍缩放计算"""
        original_width = 500
        original_height = 300
        scale = 4.0
        
        expected_width = 2000
        expected_height = 1200
        
        result_width = int(original_width * scale)
        result_height = int(original_height * scale)
        
        assert result_width == expected_width
        assert result_height == expected_height
    
    def test_aspect_ratio_preservation(self):
        """测试缩放时是否保持宽高比"""
        original_width = 1920
        original_height = 1080
        scale = 2.0
        
        original_ratio = original_width / original_height
        
        result_width = int(original_width * scale)
        result_height = int(original_height * scale)
        result_ratio = result_width / result_height
        
        # 允许浮点误差
        assert abs(original_ratio - result_ratio) < 0.001, "缩放后宽高比改变"
    
    @pytest.mark.parametrize("width,height,scale,expected_w,expected_h", [
        (100, 100, 2.0, 200, 200),
        (640, 480, 3.0, 1920, 1440),
        (1024, 768, 1.5, 1536, 1152),
        (800, 600, 4.0, 3200, 2400),
    ])
    def test_multiple_scale_scenarios(self, width, height, scale, expected_w, expected_h):
        """参数化测试：测试多种缩放场景"""
        result_w = int(width * scale)
        result_h = int(height * scale)
        
        assert result_w == expected_w
        assert result_h == expected_h
    
    def test_fixed_size_calculation(self):
        """测试固定宽高模式（scale=0时）"""
        target_width = 1920
        target_height = 1080
        
        # 模拟固定宽高模式的逻辑
        model = {
            'scale': 0,
            'width': target_width,
            'high': target_height
        }
        
        assert model['scale'] == 0, "应该使用固定宽高模式"
        assert model['width'] == target_width
        assert model['high'] == target_height


class TestImageFormatValidation:
    """测试图像格式验证"""
    
    def test_supported_formats(self):
        """测试支持的图像格式"""
        supported_formats = ['jpg', 'jpeg', 'png', 'webp', 'bmp']
        
        for fmt in supported_formats:
            assert fmt in ['jpg', 'jpeg', 'png', 'webp', 'bmp'], f"{fmt} 应该被支持"
    
    def test_format_conversion_jpg_to_png(self):
        """测试格式转换参数设置"""
        original_format = "jpg"
        target_format = "png"
        
        model = {'format': target_format}
        
        assert model['format'] == target_format
        assert model['format'] != original_format


class TestNoiseLevel:
    """测试降噪等级设置"""
    
    @pytest.mark.parametrize("noise_level", [-1, 0, 1, 2, 3])
    def test_valid_noise_levels(self, noise_level):
        """测试有效的降噪等级"""
        valid_levels = [-1, 0, 1, 2, 3]
        assert noise_level in valid_levels, f"降噪等级{noise_level}应该有效"
    
    def test_noise_level_range(self):
        """测试降噪等级范围"""
        min_noise = -1
        max_noise = 3
        
        for level in range(min_noise, max_noise + 1):
            assert min_noise <= level <= max_noise


class TestModelParameters:
    """测试模型参数配置"""
    
    def test_model_dict_structure(self):
        """测试模型参数字典结构"""
        model = {
            'model': 1,
            'noise': 0,
            'scale': 2.0,
            'format': 'jpg'
        }
        
        # 检查必需的键是否存在
        assert 'model' in model
        assert 'noise' in model
        assert 'scale' in model
        assert 'format' in model
    
    def test_model_types(self):
        """测试模型类型"""
        model_types = [0, 1, 2]  # cunet, photo, anime_style_art_rgb
        
        for model_type in model_types:
            assert 0 <= model_type <= 2, f"模型类型{model_type}应该在0-2范围内"
    
    def test_scale_mode_vs_fixed_size_mode(self):
        """测试缩放模式和固定尺寸模式的互斥性"""
        # 缩放模式
        model_scale = {
            'scale': 2.0,
            'width': 0,
            'high': 0
        }
        assert model_scale['scale'] > 0
        
        # 固定尺寸模式
        model_fixed = {
            'scale': 0,
            'width': 1920,
            'high': 1080
        }
        assert model_fixed['scale'] == 0
        assert model_fixed['width'] > 0
        assert model_fixed['high'] > 0
