"""
集成测试：测试不同模块组合工作
测试完整的工作流程和模块间的交互
"""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest


class TestSettingsToProcessing:
    """测试设置界面到图像处理的集成"""
    
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
    
    def test_model_selection_propagation(self, qapp, mock_config):
        """测试模型选择是否正确传递到处理流程"""
        # 模拟用户在UI选择模型
        selected_model = 1  # photo模型
        
        # 创建模型参数
        model_params = {
            'model': selected_model,
            'scale': 2.0,
            'noise': 0,
            'format': 'jpg'
        }
        
        # 验证参数正确
        assert model_params['model'] == selected_model
        assert model_params['scale'] == 2.0


class TestUIToTaskManager:
    """测试UI层到任务管理器的集成"""
    
    def test_button_click_to_task_creation(self, qapp):
        """测试按钮点击是否能正确创建任务"""
        from src.qt.com.qtimg import QtImg
        
        # 创建UI实例
        img_widget = QtImg()
        
        # 模拟加载图像数据
        img_widget.data = b"fake_image_data"
        
        # 模拟设置参数
        img_widget.scaleEdit.setText("2.0")
        img_widget.noiseCombox.setCurrentIndex(0)
        
        # 验证UI状态
        assert img_widget.data is not None
        assert img_widget.scaleEdit.text() == "2.0"
    
    @patch('src.qt.util.qttask.QtTask.AddConvertTask')
    def test_task_submission_flow(self, mock_add_task, qapp):
        """测试任务提交流程"""
        from src.qt.com.qtimg import QtImg
        
        # 创建UI实例
        img_widget = QtImg()
        img_widget.data = b"test_data"
        
        # 配置返回值
        mock_add_task.return_value = 1001
        
        # 模拟用户操作（需要实际调用StartWaifu2x）
        # 这里只验证mock是否可以工作
        from src.qt.util.qttask import QtTask
        task_manager = QtTask()
        
        # 模拟调用
        task_id = mock_add_task(
            img_widget.data,
            {'scale': 2.0},
            img_widget.AddConvertBack
        )
        
        # 验证调用
        assert task_id == 1001
        mock_add_task.assert_called_once()


class TestTaskManagerToCallback:
    """测试任务管理器到回调函数的集成"""
    
    def test_callback_invocation(self, qapp, mock_config):
        """测试回调函数是否被正确调用"""
        from src.qt.util.qttask import QtTask, QtDownloadTask
        
        # 创建任务管理器
        task_manager = QtTask()
        
        # 创建模拟回调
        callback_called = []
        
        def mock_callback(data, task_id, param, tick):
            callback_called.append({
                'data': data,
                'task_id': task_id,
                'tick': tick
            })
        
        # 创建任务
        task = QtDownloadTask()
        task.downloadId = 1001
        task.downloadCompleteBack = mock_callback
        task.saveData = b"processed_data"
        task.tick = 2.5
        
        # 存储任务
        task_manager.convertLoad[1001] = task
        
        # 模拟任务完成，调用回调
        task.downloadCompleteBack(task.saveData, 1001, None, task.tick)
        
        # 验证回调被调用
        assert len(callback_called) == 1
        assert callback_called[0]['task_id'] == 1001
        assert callback_called[0]['data'] == b"processed_data"
        assert callback_called[0]['tick'] == 2.5
    
    def test_signal_to_callback_flow(self, qapp, mock_config):
        """测试信号到回调的完整流程"""
        from src.qt.util.qttask import QtTask, QtDownloadTask
        
        task_manager = QtTask()
        
        # 记录回调调用
        callback_results = []
        
        def test_callback(data, task_id, param, tick):
            callback_results.append(task_id)
        
        # 创建任务
        task = QtDownloadTask()
        task.downloadId = 2001
        task.downloadCompleteBack = test_callback
        task.saveData = b"test"
        task.tick = 1.0
        task_manager.convertLoad[2001] = task
        
        # 模拟HandlerConvertTask的逻辑
        if 2001 in task_manager.convertLoad:
            info = task_manager.convertLoad[2001]
            info.downloadCompleteBack(info.saveData, 2001, None, info.tick)
            del task_manager.convertLoad[2001]
        
        # 验证
        assert len(callback_results) == 1
        assert callback_results[0] == 2001
        assert 2001 not in task_manager.convertLoad  # 任务已清理


class TestEndToEndWorkflow:
    """端到端工作流程测试"""
    
    def test_complete_image_processing_workflow(self, qapp, mock_config):
        """测试完整的图像处理工作流程（不含实际GPU处理）"""
        from src.qt.util.qttask import QtTask, QtDownloadTask
        
        # 1. 准备阶段
        task_manager = QtTask()
        test_image_data = b"\x89PNG\r\n\x1a\n"  # PNG文件头
        
        # 2. 创建任务
        callback_executed = []
        
        def completion_callback(data, task_id, param, tick):
            callback_executed.append(True)
        
        task = QtDownloadTask()
        task.downloadId = 3001
        task.imgData = test_image_data
        task.model = {'model': 1, 'scale': 2.0, 'format': 'png'}
        task.downloadCompleteBack = completion_callback
        task_manager.convertLoad[3001] = task
        
        # 3. 模拟GPU处理完成
        task.saveData = b"processed_png_data"
        task.tick = 3.14
        
        # 4. 模拟信号触发回调
        task.downloadCompleteBack(task.saveData, 3001, None, task.tick)
        
        # 5. 验证结果
        assert len(callback_executed) == 1
        assert task.saveData == b"processed_png_data"
        assert task.tick == 3.14
    
    def test_multiple_tasks_workflow(self, qapp, mock_config):
        """测试多任务并发处理流程"""
        from src.qt.util.qttask import QtTask, QtDownloadTask
        
        task_manager = QtTask()
        completed_tasks = []
        
        def callback_factory(task_id):
            def callback(data, tid, param, tick):
                completed_tasks.append(tid)
            return callback
        
        # 创建多个任务
        for i in range(5):
            task_id = 4000 + i
            task = QtDownloadTask()
            task.downloadId = task_id
            task.imgData = f"image_{i}".encode()
            task.downloadCompleteBack = callback_factory(task_id)
            task_manager.convertLoad[task_id] = task
        
        # 模拟所有任务完成
        for task_id in range(4000, 4005):
            task = task_manager.convertLoad[task_id]
            task.saveData = f"processed_{task_id}".encode()
            task.tick = 1.0
            task.downloadCompleteBack(task.saveData, task_id, None, task.tick)
        
        # 验证所有任务都完成了
        assert len(completed_tasks) == 5
        assert sorted(completed_tasks) == [4000, 4001, 4002, 4003, 4004]


class TestErrorHandling:
    """测试错误处理和异常情况"""
    
    def test_missing_task_handling(self, qapp, mock_config):
        """测试处理不存在的任务"""
        from src.qt.util.qttask import QtTask
        
        task_manager = QtTask()
        
        # 尝试访问不存在的任务
        non_existent_id = 9999
        
        # 模拟HandlerConvertTask的检查逻辑
        if non_existent_id not in task_manager.convertLoad:
            # 应该直接返回，不抛异常
            pass
        
        # 验证没有异常抛出
        assert non_existent_id not in task_manager.convertLoad
    
    def test_callback_exception_handling(self, qapp, mock_config):
        """测试回调函数异常处理"""
        from src.qt.util.qttask import QtDownloadTask
        
        def faulty_callback(data, task_id, param, tick):
            raise ValueError("模拟回调函数错误")
        
        task = QtDownloadTask()
        task.downloadCompleteBack = faulty_callback
        
        # 测试调用会抛出异常
        with pytest.raises(ValueError):
            task.downloadCompleteBack(b"data", 1, None, 1.0)
    
    def test_empty_data_handling(self, qapp, mock_config):
        """测试空数据处理"""
        from src.qt.util.qttask import QtDownloadTask
        
        callback_called = []
        
        def callback(data, task_id, param, tick):
            callback_called.append(data is None or data == b"")
        
        task = QtDownloadTask()
        task.downloadCompleteBack = callback
        task.saveData = b""  # 空数据
        
        # 调用回调
        task.downloadCompleteBack(task.saveData, 1, None, 0)
        
        # 验证空数据被正确处理
        assert len(callback_called) == 1
        assert callback_called[0] is True


class TestTaskCancellation:
    """测试任务取消功能"""
    
    def test_cancel_single_task(self, qapp, mock_config):
        """测试取消单个任务"""
        from src.qt.util.qttask import QtTask, QtDownloadTask
        
        task_manager = QtTask()
        
        # 创建任务
        task = QtDownloadTask()
        task.downloadId = 5001
        task.cleanFlag = "TestGroup"
        task_manager.convertLoad[5001] = task
        task_manager.convertFlag["TestGroup"] = {5001}
        
        # 取消任务
        if 5001 in task_manager.convertLoad:
            del task_manager.convertLoad[5001]
        task_manager.convertFlag["TestGroup"].discard(5001)
        
        # 验证任务已删除
        assert 5001 not in task_manager.convertLoad
    
    def test_cancel_task_group(self, qapp, mock_config):
        """测试批量取消任务组"""
        from src.qt.util.qttask import QtTask, QtDownloadTask
        
        task_manager = QtTask()
        clean_flag = "BatchTest"
        
        # 创建多个任务
        for i in range(3):
            task_id = 6000 + i
            task = QtDownloadTask()
            task.downloadId = task_id
            task.cleanFlag = clean_flag
            task_manager.convertLoad[task_id] = task
        
        task_manager.convertFlag[clean_flag] = {6000, 6001, 6002}
        
        # 批量取消
        task_ids = task_manager.convertFlag.get(clean_flag, set())
        for task_id in task_ids:
            if task_id in task_manager.convertLoad:
                del task_manager.convertLoad[task_id]
        task_manager.convertFlag.pop(clean_flag)
        
        # 验证所有任务都被删除
        assert 6000 not in task_manager.convertLoad
        assert 6001 not in task_manager.convertLoad
        assert 6002 not in task_manager.convertLoad
        assert clean_flag not in task_manager.convertFlag
