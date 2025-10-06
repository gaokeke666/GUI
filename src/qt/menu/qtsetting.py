# 导入PySide6及项目内部模块  设置界面的类
from PySide6 import QtWidgets
from PySide6.QtCore import QSettings, Qt, QSize, QLocale, QTranslator
from PySide6.QtWidgets import QFileDialog

from conf import config
from src.qt.com.qtbubblelabel import QtBubbleLabel
from src.util import Log
from ui.setting import Ui_Setting


# 设置对话框类，继承自QDialog和自动生成的Ui_Setting
class QtSetting(QtWidgets.QDialog, Ui_Setting):
    def __init__(self, owner):
        super(self.__class__, self).__init__()
        Ui_Setting.__init__(self)
        self.setupUi(self)

        # 使用QSettings来方便地读写.ini格式的配置文件
        self.settings = QSettings('config.ini', QSettings.IniFormat)
        
        # 初始化一些成员变量
        self.mainSize = QSize(1500, 1100) # 默认主窗口大小
        self.gpuInfos = [] # 存储获取到的GPU信息列表
        self.translate = QTranslator() # 用于实现多语言翻译的翻译家对象

    # 重写show方法，在显示窗口前先加载设置
    def show(self):
        self.LoadSetting()
        super(self.__class__, self).show()

    # 重写exec方法（用于模态对话框），在显示窗口前先加载设置
    def exec(self):
        self.LoadSetting()
        super(self.__class__, self).exec()

    # 一个通用的从QSettings获取值的辅助函数，带类型转换和默认值处理
    def GetSettingV(self, key, defV=None):
        v = self.settings.value(key)
        try:
            if v:
                if isinstance(defV, int):
                    # 特殊处理布尔字符串到整数的转换
                    if v.lower() == "true": return 1
                    if v.lower() == "false": return 0
                    return int(v)
                elif isinstance(defV, float):
                    return float(v)
                else:
                    return v
            return defV
        except Exception as es:
            Log.Error(es)
        return v

    # 从config.ini加载所有设置到全局的config对象和UI控件中
    def LoadSetting(self):
        # 加载上次的窗口大小
        x = self.settings.value("MainSize_x")
        y = self.settings.value("MainSize_y")
        if x and y:
            self.mainSize = QSize(int(x), int(y))

        # 使用GetSettingV加载各项配置
        config.SelectEncodeGpu = self.GetSettingV("Waifu2x/SelectEncodeGpu", "")
        config.UseCpuNum = self.GetSettingV("Waifu2x/UseCpuNum", 0)
        config.Language = self.GetSettingV("Waifu2x/Language", 0)
        
        # 将加载的配置应用到UI上
        self.languageSelect.setCurrentIndex(config.Language)
        # 遍历GPU下拉框，找到并选中上次保存的GPU
        for index in range(self.encodeSelect.count()):
            if config.SelectEncodeGpu == self.encodeSelect.itemText(index):
                self.encodeSelect.setCurrentIndex(index)
        return

    # 在主窗口关闭时，保存主窗口的大小
    def ExitSaveSetting(self, mainQsize):
        self.settings.setValue("MainSize_x", mainQsize.width())
        self.settings.setValue("MainSize_y", mainQsize.height())

    # 当用户点击“保存”按钮时调用此方法
    def SaveSetting(self):
        # 从UI控件中获取当前用户的选择
        config.Encode = self.encodeSelect.currentIndex()
        config.UseCpuNum = int(self.threadSelect.currentIndex())
        config.Language = int(self.languageSelect.currentIndex())
        config.SelectEncodeGpu = self.encodeSelect.currentText()

        # 使用QSettings将新的配置写入config.ini文件
        self.settings.setValue("Waifu2x/SelectEncodeGpu", config.SelectEncodeGpu)
        self.settings.setValue("Waifu2x/UseCpuNum", config.UseCpuNum)
        self.settings.setValue("Waifu2x/Language", config.Language)
        
        # 提示用户保存成功并关闭设置窗口
        QtBubbleLabel.ShowMsgEx(self, "Save Success")
        self.close()

    # 接收GPU和CPU信息，并填充到UI的下拉框中
    def SetGpuInfos(self, gpuInfo, cpuNum):
        self.gpuInfos = gpuInfo
        config.EncodeGpu = config.SelectEncodeGpu

        # 如果没有检测到GPU
        if not self.gpuInfos:
            config.EncodeGpu = "CPU"
            config.Encode = -1
            self.encodeSelect.addItem(config.EncodeGpu)
            self.encodeSelect.setCurrentIndex(0)
            return

        # 如果保存的GPU信息无效，则默认选择第一个GPU
        if not config.EncodeGpu or (config.EncodeGpu != "CPU" and config.EncodeGpu not in self.gpuInfos):
            config.EncodeGpu = self.gpuInfos[0]
            config.Encode = 0

        # 遍历GPU列表，添加到下拉框，并选中上次保存的GPU
        index = 0
        for info in self.gpuInfos:
            self.encodeSelect.addItem(info)
            if info == config.EncodeGpu:
                self.encodeSelect.setCurrentIndex(index)
                config.Encode = index
            index += 1

        # 最后添加“CPU”选项
        self.encodeSelect.addItem("CPU")
        if config.EncodeGpu == "CPU":
            config.Encode = -1
            self.encodeSelect.setCurrentIndex(index)

        # 填充CPU线程数下拉框
        if config.UseCpuNum > cpuNum:
            config.UseCpuNum = cpuNum
        for i in range(cpuNum):
            self.threadSelect.addItem(str(i + 1))
        self.threadSelect.setCurrentIndex(config.UseCpuNum)
        Log.Info(f"waifu2x GPU: {self.gpuInfos}, select: {config.EncodeGpu}, use cpu num: {config.UseCpuNum}")
        return

    # 获取当前选择的GPU名称
    def GetGpuName(self):
        return config.EncodeGpu

    # 设置应用程序的语言
    def SetLanguage(self, app, owner):
        language = config.Language

        # 如果设置为“自动”，则根据操作系统语言来判断
        if language == 0:
            locale = QLocale.system().name() # 获取系统语言环境，如 'zh_CN'
            Log.Info(f"Init translate {locale}")
            if locale.lower().startswith("zh_"):
                language = 1 if locale.lower() == "zh_cn" else 2 # 简体中文或繁体中文
            else:
                language = 3 # 英文

        # 根据最终的语言选项加载不同的.qm翻译文件
        if language == 1: # 简体中文 (默认，无需加载翻译文件)
            app.removeTranslator(self.translate)
        elif language == 2: # 繁体中文
            self.translate.load(":/tr_hk.qm") # 从资源文件中加载
            app.installTranslator(self.translate)
        else: # 英文
            self.translate.load(":/tr_en.qm")
            app.installTranslator(self.translate)
        
        # 调用主窗口的RetranslateUi方法来刷新整个界面的文本
        owner.RetranslateUi()