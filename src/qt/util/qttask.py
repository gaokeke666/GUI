"""
多线程任务管理器模块
主要功能：
1. 管理图像处理任务的生命周期
2. 协调多个后台线程与主线程的通信
3. 提供线程安全的任务队列和回调机制
"""

import hashlib
import os
import threading
import time
import weakref
from queue import Queue  # 线程安全的队列，用于任务调度

from PySide6.QtCore import Signal, QObject  # Qt的信号机制，用于跨线程通信

from conf import config
from src.util import Singleton, Log
from src.util.tool import CTime, ToolUtil


# ============================================================
# QtTaskQObject: Qt信号对象
# ============================================================
# 作用：提供线程安全的信号，用于从后台线程通知主线程
# 为什么需要它：Qt的信号必须定义在QObject的子类中
class QtTaskQObject(QObject):
    # 定义信号：当图像转换完成时发射，参数为任务ID
    # 这个信号会自动被Qt的事件循环调度到主线程执行
    convertBack = Signal(int)

    def __init__(self):
        super(self.__class__, self).__init__()


# ============================================================
# QtDownloadTask: 任务数据对象
# ============================================================
# 作用：封装单个图像处理任务的所有信息
# 这是一个数据容器类，存储任务的输入、输出和配置
class QtDownloadTask(object):
    def __init__(self, downloadId=0):
        # 任务唯一标识符
        self.downloadId = downloadId
        
        # 任务完成时的回调函数（由UI层提供）
        # 函数签名：callback(data, taskId, backParam, tick)
        self.downloadCompleteBack = None
        
        # 以下是一些通用字段（可能用于其他类型的任务）
        self.fileSize = 0           # 文件大小
        self.isSaveData = True      # 是否保存数据
        self.saveData = b""         # 处理后的图像数据（二进制）
        self.url = ""               # URL（如果是下载任务）
        self.path = ""              # 文件路径
        self.originalName = ""      # 原始文件名
        
        # 回调函数的额外参数（可选）
        self.backParam = None
        
        # 清理标记：用于批量取消同一组任务
        # 例如："QtImg" 表示这是图像处理界面的任务
        self.cleanFlag = ""
        
        # 任务执行耗时（秒）
        self.tick = 0

        # 图像处理相关字段
        self.imgData = b""          # 原始图像数据（二进制）
        
        # 处理模型参数
        self.model = {
            "model": 1,      # 模型类型（0=cunet, 1=photo, 2=anime_style_art_rgb）
            "scale": 2,      # 缩放倍数（2x, 3x, 4x等）
            "toH": 100,      # 目标高度（当scale<=0时使用）
            "toW": 100,      # 目标宽度（当scale<=0时使用）
        }


# ============================================================
# QtTask: 多线程任务管理器（核心类）
# ============================================================
# 设计模式：
# 1. 单例模式（Singleton）：全局只有一个任务管理器实例
# 2. 生产者-消费者模式：使用队列协调任务的提交和处理
# 3. 观察者模式：通过Qt信号通知任务完成
#
# 线程架构：
# - 主线程（UI线程）：负责UI更新，接收信号回调
# - convertThread（任务提交线程）：从队列取任务，提交给GPU处理
# - convertThread2（结果接收线程）：从GPU获取处理结果，发射信号
class QtTask(Singleton, threading.Thread):

    def __init__(self):
        # 初始化单例和线程基类
        Singleton.__init__(self)
        threading.Thread.__init__(self)
        
        # ===== 任务队列 =====
        # 线程安全的队列，用于存储待处理的任务ID
        # UI线程通过AddConvertTask添加任务，convertThread从这里取出
        self._inQueue = Queue()
        
        # ===== 主窗口引用 =====
        # 使用弱引用避免循环引用导致的内存泄漏
        self._owner = None
        
        # ===== Qt信号对象 =====
        # 创建信号对象并连接到处理函数
        self.taskObj = QtTaskQObject()
        # 当convertBack信号发射时，会在主线程调用HandlerConvertTask
        self.taskObj.convertBack.connect(self.HandlerConvertTask)

        # ===== 后台线程1：任务提交线程 =====
        # 职责：从队列取出任务，调用waifu2x_vulkan.add()提交给GPU
        self.convertThread = threading.Thread(target=self.RunLoad)
        self.convertThread.setDaemon(True)  # 守护线程，主程序退出时自动结束
        self.convertThread.start()

        # ===== 后台线程2：结果接收线程 =====
        # 职责：调用waifu2x_vulkan.load()获取GPU处理结果，发射信号
        self.convertThread2 = threading.Thread(target=self.RunLoad2)
        self.convertThread2.setDaemon(True)
        self.convertThread2.start()

        # ===== 任务存储字典 =====
        self.downloadTask = {}   # 下载任务字典（预留，当前未使用）
        self.convertLoad = {}    # 转换任务字典：{taskId: QtDownloadTask对象}
        self.convertId = 1000000 # 转换任务起始ID（预留）

        self.taskId = 0          # 任务ID计数器，每添加一个任务自增1
        self.tasks = {}          # 通用任务字典（预留）

        # ===== 任务分组管理 =====
        self.flagToIds = {}      # 预留字段
        # 清理标记到任务ID集合的映射：{cleanFlag: set(taskId1, taskId2, ...)}
        # 用于批量取消同一组任务，例如：{"QtImg": {1001, 1002, 1003}}
        self.convertFlag = {}

    # ===== 属性访问器 =====
    # 提供对信号对象的便捷访问
    @property
    def convertBack(self):
        """返回转换完成信号，外部可以连接自定义槽函数"""
        return self.taskObj.convertBack

    @property
    def taskBack(self):
        """预留：通用任务完成信号"""
        return self.taskObj.taskBack

    @property
    def downloadBack(self):
        """预留：下载完成信号"""
        return self.taskObj.downloadBack

    @property
    def owner(self):
        """获取主窗口的强引用（从弱引用转换）"""
        from src.qt.qtmain import QtMainWindow
        assert isinstance(self._owner(), QtMainWindow)
        return self._owner()

    def SetOwner(self, owner):
        """设置主窗口的弱引用，避免循环引用"""
        self._owner = weakref.ref(owner)

    # ============================================================
    # 添加图像转换任务（主线程调用）
    # ============================================================
    def AddConvertTask(self, imgData, model, completeCallBack, backParam=None, cleanFlag=""):
        """
        添加一个图像处理任务到队列
        
        参数：
            imgData: 原始图像的二进制数据（bytes）
            model: 处理参数字典，包含：
                - model: 模型类型（0=cunet, 1=photo, 2=anime_style_art_rgb）
                - scale: 缩放倍数（>0时使用）或0（使用固定宽高）
                - width/high: 目标宽高（当scale<=0时使用）
                - format: 输出格式（"jpg" 或 "png"）
            completeCallBack: 完成时的回调函数
                函数签名：callback(data, taskId, backParam, tick)
            backParam: 传递给回调函数的额外参数（可选）
            cleanFlag: 清理标记，用于批量取消任务（可选）
        
        返回：
            taskId: 任务的唯一标识符
        """
        # 创建任务对象
        info = QtDownloadTask()
        info.downloadCompleteBack = completeCallBack  # 保存回调函数
        info.backParam = backParam                    # 保存额外参数
        
        # 生成唯一的任务ID
        self.taskId += 1
        self.convertLoad[self.taskId] = info         # 加入任务字典
        info.downloadId = self.taskId
        
        # 保存任务数据
        info.imgData = imgData
        info.model = model
        
        # 如果指定了清理标记，加入分组管理
        if cleanFlag:
            info.cleanFlag = cleanFlag
            # setdefault: 如果key不存在则创建空set，然后返回该set
            taskIds = self.convertFlag.setdefault(cleanFlag, set())
            taskIds.add(self.taskId)  # 将任务ID加入该组
        
        # 将任务ID放入队列，convertThread会取出处理
        self._inQueue.put(self.taskId)
        
        return self.taskId

    # ============================================================
    # 处理转换完成的任务（主线程调用）
    # ============================================================
    def HandlerConvertTask(self, taskId):
        """
        处理完成的转换任务，调用用户提供的回调函数
        
        注意：这个函数虽然是由后台线程发射的信号触发，
               但Qt会自动将它调度到主线程执行，因此可以安全地更新UI
        
        参数：
            taskId: 任务ID
        """
        # 检查任务是否还存在（可能已被取消）
        if taskId not in self.convertLoad:
            return
        
        # 计时器，用于性能分析
        t1 = CTime()
        info = self.convertLoad[taskId]
        assert isinstance(info, QtDownloadTask)

        # 从分组中移除该任务（如果有清理标记）
        if info.cleanFlag:
            taskIds = self.convertFlag.get(info.cleanFlag, set())
            taskIds.discard(info.downloadId)  # discard不会抛异常，即使元素不存在
        
        # 调用用户提供的回调函数，传递处理结果
        # 回调函数在主线程执行，可以安全更新UI
        info.downloadCompleteBack(info.saveData, taskId, info.backParam, info.tick)
        
        # 再次从分组中移除（双重保障）
        if info.cleanFlag:
            taskIds = self.convertFlag.get(info.cleanFlag, set())
            taskIds.discard(info.downloadId)
        
        # 从任务字典中删除，释放内存
        del self.convertLoad[taskId]
        
        # 记录执行时间
        t1.Refresh("RunLoad")

    # ============================================================
    # 从底层引擎加载处理结果（后台线程调用）
    # ============================================================
    def LoadData(self):
        """
        从waifu2x_vulkan引擎获取一个处理完成的结果
        
        返回：
            None: 如果引擎不可用或没有结果
            tuple: (data, convertId, taskId, tick)
                - data: 处理后的图像数据（bytes）
                - convertId: 转换ID（底层引擎的内部ID）
                - taskId: 任务ID（与我们的taskId对应）
                - tick: 处理耗时（秒）
        
        注意：waifu2x_vulkan.load(0)是阻塞调用，会等待直到有结果返回
        """
        if not config.CanWaifu2x:
            return None
        from waifu2x_vulkan import waifu2x_vulkan
        return waifu2x_vulkan.load(0)  # 阻塞等待GPU处理结果

    # ============================================================
    # 后台线程1：任务提交线程（在convertThread中运行）
    # ============================================================
    def RunLoad(self):
        """
        持续从任务队列中取出任务，提交给GPU处理
        
        工作流程：
        1. 从队列中阻塞式获取任务ID
        2. 根据任务参数调用waifu2x_vulkan.add()提交给GPU
        3. 如果提交失败，立即发射信号通知主线程
        
        注意：这是一个无限循环，在独立线程中运行
        """
        while True:  # 无限循环，持续监听队列
            try:
                # 从队列中获取任务ID（阻塞式，队列为空时等待）
                taskId = self._inQueue.get(True)
                
                # 检查任务是否还存在（可能已被取消）
                if taskId not in self.convertLoad:
                    continue
                
                # 获取任务对象
                task = self.convertLoad.get(taskId)
                
                if config.CanWaifu2x:
                    from waifu2x_vulkan import waifu2x_vulkan
                    
                    # 获取缩放参数
                    scale = task.model.get("scale", 0)
                    
                    # 根据scale参数选择不同的调用方式
                    if scale <= 0:
                        # 使用固定宽高模式
                        sts = waifu2x_vulkan.add(
                            task.imgData,                    # 原始图像数据
                            task.model.get('model', 0),      # 模型类型
                            task.downloadId,                 # 任务ID
                            task.model.get("width", 0),      # 目标宽度
                            task.model.get("high", 0),       # 目标高度
                            task.model.get("format", "jpg")  # 输出格式
                        )
                    else:
                        # 使用缩放倍数模式
                        sts = waifu2x_vulkan.add(
                            task.imgData,                    # 原始图像数据
                            task.model.get('model', 0),      # 模型类型
                            task.downloadId,                 # 任务ID
                            scale,                           # 缩放倍数
                            task.model.get("format", "jpg")  # 输出格式
                        )

                    # Log.Warn("add convert info, taskId: {}, model:{}, sts:{}".format(str(task.taskId), task.model,
                    #                                                                          str(sts)))
                else:
                    # waifu2x引擎不可用
                    sts = -1
                
                # 如果提交失败（sts <= 0），立即发射信号通知主线程
                if sts <= 0:
                    self.convertBack.emit(taskId)
                    continue
                    
            except Exception as es:
                # 捕获所有异常，避免线程崩溃
                continue

    # ============================================================
    # 后台线程2：结果接收线程（在convertThread2中运行）
    # ============================================================
    def RunLoad2(self):
        """
        持续从GPU获取处理完成的结果，并发射信号通知主线程
        
        工作流程：
        1. 调用LoadData()阻塞等待GPU处理结果
        2. 将结果保存到任务对象中
        3. 发射convertBack信号，触发主线程的HandlerConvertTask
        
        注意：这是一个无限循环，在独立线程中运行
        """
        while True:  # 无限循环，持续监听GPU结果
            # 阻塞式获取GPU处理结果
            info = self.LoadData()
            
            # 如果返回None，说明引擎不可用或已停止
            if not info:
                break
            
            # 计时器，用于性能分析
            t1 = CTime()
            
            # 解包结果
            data, convertId, taskId, tick = info
            
            # 检查任务是否还存在（可能已被取消）
            if taskId not in self.convertLoad:
                continue
            
            # 计算数据长度（用于日志）
            if not data:
                lenData = 0
            else:
                lenData = len(data)

            # 记录处理成功的日志
            Log.Warn("convert suc, taskId: {}, dataLen:{}, sts:{} tick:{}".format(
                str(taskId), lenData, str(convertId), str(tick)
            ))
            
            # 将处理结果保存到任务对象中
            info = self.convertLoad[taskId]
            assert isinstance(info, QtDownloadTask)
            info.saveData = data  # 处理后的图像数据
            info.tick = tick      # 处理耗时
            
            # 发射信号，任务ID号，通知主线程任务完成
            # Qt会自动将这个信号调度到主线程的事件循环中
            # 最终会触发HandlerConvertTask方法的执行
            self.convertBack.emit(taskId)
            
            # 记录执行时间
            t1.Refresh("RunLoad")

    # ============================================================
    # 批量取消任务（主线程调用）
    # ============================================================
    def CancelConver(self, cleanFlag):
        """
        根据清理标记批量取消一组任务
        
        使用场景：
        - 用户切换到其他界面时，取消当前界面的所有待处理任务
        - 用户打开新图片时，取消之前图片的所有处理任务
        
        参数：
            cleanFlag: 清理标记，例如"QtImg"
        
        工作流程：
        1. 从convertFlag字典中获取该标记对应的所有任务ID
        2. 从convertLoad字典中删除这些任务
        3. 通知底层引擎取消GPU上的处理
        """
        # 获取该标记对应的所有任务ID
        taskIds = self.convertFlag.get(cleanFlag, set())
        
        # 如果没有任务，直接返回
        if not taskIds:
            return
        
        # 遍历所有任务ID，从任务字典中删除
        for taskId in taskIds:
            if taskId in self.convertLoad:
                del self.convertLoad[taskId]  # 删除任务，释放内存
        
        # 记录日志
        Log.Info("cancel convert taskId, {}".format(taskIds))
        
        # 从分组字典中移除该标记
        self.convertFlag.pop(cleanFlag)
        
        # 通知底层引擎取消GPU上的处理
        if config.CanWaifu2x:
            from waifu2x_vulkan import waifu2x_vulkan
            waifu2x_vulkan.remove(list(taskIds))  # 取消GPU上的任务
