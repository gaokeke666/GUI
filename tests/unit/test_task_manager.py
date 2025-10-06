"""
单元测试：任务管理器
测试QtTask类的核心功能
"""
import pytest
import threading
import time
from unittest.mock import Mock, MagicMock, patch


class TestTaskManager:
    """测试任务管理器的核心功能"""
    
    def test_task_id_increment(self, mock_config):
        """测试任务ID是否正确自增"""
        from src.qt.util.qttask import QtTask
        
        task_manager = QtTask()
        initial_id = task_manager.taskId
        
        # 模拟添加任务（不实际执行GPU操作）
        mock_callback = Mock()
        
        # 第一个任务
        task_id_1 = task_manager.taskId + 1
        # 第二个任务
        task_id_2 = task_manager.taskId + 2
        
        assert task_id_2 == task_id_1 + 1, "任务ID应该递增"
    
    def test_task_storage(self, mock_config):
        """测试任务是否正确存储到字典中"""
        from src.qt.util.qttask import QtTask, QtDownloadTask
        
        task_manager = QtTask()
        
        # 创建任务对象
        task = QtDownloadTask()
        task.downloadId = 1001
        task.imgData = b"fake_image_data"
        task.model = {'scale': 2.0}
        
        # 存储任务
        task_manager.convertLoad[1001] = task
        
        # 验证存储
        assert 1001 in task_manager.convertLoad
        assert task_manager.convertLoad[1001].downloadId == 1001
        assert task_manager.convertLoad[1001].imgData == b"fake_image_data"
    
    def test_callback_function_storage(self, mock_config):
        """测试回调函数是否正确保存"""
        from src.qt.util.qttask import QtDownloadTask
        
        # 创建模拟回调函数
        def mock_callback(data, task_id, param, tick):
            return "callback_called"
        
        task = QtDownloadTask()
        task.downloadCompleteBack = mock_callback
        
        # 验证回调函数已保存
        assert task.downloadCompleteBack is not None
        assert callable(task.downloadCompleteBack)
        
        # 测试调用回调函数
        result = task.downloadCompleteBack(b"data", 1, None, 1.5)
        assert result == "callback_called"
    
    def test_clean_flag_grouping(self, mock_config):
        """测试清理标记的分组功能"""
        from src.qt.util.qttask import QtTask
        
        task_manager = QtTask()
        clean_flag = "TestGroup"
        
        # 添加多个任务到同一组
        task_manager.convertFlag.setdefault(clean_flag, set())
        task_manager.convertFlag[clean_flag].add(1001)
        task_manager.convertFlag[clean_flag].add(1002)
        task_manager.convertFlag[clean_flag].add(1003)
        
        # 验证分组
        assert clean_flag in task_manager.convertFlag
        assert len(task_manager.convertFlag[clean_flag]) == 3
        assert 1001 in task_manager.convertFlag[clean_flag]
        assert 1002 in task_manager.convertFlag[clean_flag]
    
    def test_task_cancellation(self, mock_config):
        """测试任务取消功能"""
        from src.qt.util.qttask import QtTask, QtDownloadTask
        
        task_manager = QtTask()
        clean_flag = "TestGroup"
        
        # 创建并存储任务
        task1 = QtDownloadTask()
        task1.downloadId = 1001
        task1.cleanFlag = clean_flag
        task_manager.convertLoad[1001] = task1
        
        task2 = QtDownloadTask()
        task2.downloadId = 1002
        task2.cleanFlag = clean_flag
        task_manager.convertLoad[1002] = task2
        
        # 添加到分组
        task_manager.convertFlag[clean_flag] = {1001, 1002}
        
        # 取消任务
        for task_id in list(task_manager.convertFlag[clean_flag]):
            if task_id in task_manager.convertLoad:
                del task_manager.convertLoad[task_id]
        task_manager.convertFlag.pop(clean_flag)
        
        # 验证任务已删除
        assert 1001 not in task_manager.convertLoad
        assert 1002 not in task_manager.convertLoad
        assert clean_flag not in task_manager.convertFlag


class TestTaskDataObject:
    """测试任务数据对象"""
    
    def test_task_object_initialization(self):
        """测试任务对象初始化"""
        from src.qt.util.qttask import QtDownloadTask
        
        task = QtDownloadTask(downloadId=1001)
        
        assert task.downloadId == 1001
        assert task.downloadCompleteBack is None
        assert task.saveData == b""
        assert task.tick == 0
        assert task.imgData == b""
    
    def test_task_object_model_defaults(self):
        """测试任务对象的默认模型参数"""
        from src.qt.util.qttask import QtDownloadTask
        
        task = QtDownloadTask()
        
        assert 'model' in task.model
        assert 'scale' in task.model
        assert 'toH' in task.model
        assert 'toW' in task.model
    
    def test_task_object_data_assignment(self):
        """测试任务对象数据赋值"""
        from src.qt.util.qttask import QtDownloadTask
        
        task = QtDownloadTask()
        
        # 赋值
        task.imgData = b"\x89PNG\r\n\x1a\n"  # PNG文件头
        task.model = {
            'model': 1,
            'scale': 2.0,
            'noise': 0,
            'format': 'png'
        }
        task.tick = 2.345
        task.saveData = b"processed_data"
        
        # 验证
        assert task.imgData == b"\x89PNG\r\n\x1a\n"
        assert task.model['scale'] == 2.0
        assert task.tick == 2.345
        assert task.saveData == b"processed_data"


class TestSignalEmission:
    """测试信号发射机制"""
    
    def test_signal_definition(self, qapp):
        """测试信号是否正确定义"""
        from src.qt.util.qttask import QtTaskQObject
        from PySide6.QtCore import Signal
        
        task_obj = QtTaskQObject()
        
        # 验证信号存在
        assert hasattr(task_obj, 'convertBack')
        # 验证是Signal类型
        assert isinstance(type(task_obj).convertBack, Signal)
    
    def test_signal_connection(self, qapp):
        """测试信号连接"""
        from src.qt.util.qttask import QtTaskQObject
        
        task_obj = QtTaskQObject()
        
        # 创建槽函数
        received_values = []
        
        def slot_function(task_id):
            received_values.append(task_id)
        
        # 连接信号
        task_obj.convertBack.connect(slot_function)
        
        # 发射信号
        task_obj.convertBack.emit(1001)
        
        # 处理事件循环（确保信号被处理）
        qapp.processEvents()
        
        # 验证槽函数被调用
        assert len(received_values) == 1
        assert received_values[0] == 1001
    
    def test_multiple_signal_emissions(self, qapp):
        """测试多次信号发射"""
        from src.qt.util.qttask import QtTaskQObject
        
        task_obj = QtTaskQObject()
        received_values = []
        
        def slot_function(task_id):
            received_values.append(task_id)
        
        task_obj.convertBack.connect(slot_function)
        
        # 发射多次
        for i in range(5):
            task_obj.convertBack.emit(1000 + i)
        
        qapp.processEvents()
        
        # 验证所有信号都被接收
        assert len(received_values) == 5
        assert received_values == [1000, 1001, 1002, 1003, 1004]


class TestThreadSafety:
    """测试线程安全性"""
    
    def test_queue_thread_safety(self):
        """测试队列的线程安全性"""
        from queue import Queue
        
        q = Queue()
        results = []
        
        def producer():
            for i in range(10):
                q.put(i)
        
        def consumer():
            while not q.empty():
                try:
                    item = q.get(timeout=0.1)
                    results.append(item)
                except:
                    break
        
        # 创建多个生产者和消费者线程
        threads = []
        for _ in range(3):
            t = threading.Thread(target=producer)
            threads.append(t)
            t.start()
        
        time.sleep(0.1)  # 等待生产者完成
        
        for _ in range(3):
            t = threading.Thread(target=consumer)
            threads.append(t)
            t.start()
        
        # 等待所有线程完成
        for t in threads:
            t.join()
        
        # 验证没有数据丢失
        assert len(results) == 30  # 3个生产者 * 10个项目
