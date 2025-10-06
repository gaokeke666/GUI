# 测试数据目录

此目录用于存放测试所需的示例文件。

## 目录结构

```
test_data/
├── sample.jpg          # 示例JPG图片
├── sample.png          # 示例PNG图片
├── sample_large.jpg    # 大尺寸图片（用于性能测试）
├── sample_small.png    # 小尺寸图片
└── README.md           # 本文件
```

## 使用方法

在测试中引用测试数据：

```python
import os

def test_load_image():
    test_dir = os.path.dirname(__file__)
    image_path = os.path.join(test_dir, "test_data", "sample.jpg")
    
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    assert len(image_data) > 0
```

## 注意事项

1. 测试数据文件应该尽量小（< 1MB），以加快测试速度
2. 不要提交大文件到Git仓库
3. 如果需要大文件测试，可以在测试中动态生成
4. 确保测试数据文件的版权合规
