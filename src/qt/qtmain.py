

# 导入PySide6的核心GUI模块和组件
from PySide6 import QtWidgets, QtGui  # 导入PySide6部件
from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QIcon, QPixmap, QDesktopServices, QGuiApplication
from PySide6.QtWidgets import QMessageBox

# 导入项目内部模块
from conf import config  # 导入全局配置文件
from src.qt.com.qtbubblelabel import QtBubbleLabel  # 导入自定义的气泡提示标签
from src.qt.com.qtimg import QtImg  # 导入核心的图片处理界面
from src.qt.menu.qtabout import QtAbout  # 导入“关于”对话框
from src.qt.menu.qtsetting import QtSetting  # 导入设置对话框
from src.util import Log  # 导入日志工具
from ui.main import Ui_MainWindow  # 导入由Qt Designer生成的UI定义类


# 定义主窗口类，采用多重继承
# QtWidgets.QMainWindow: 提供了标准窗口的功能（菜单栏、工具栏、状态栏等）
# Ui_MainWindow: 包含了从 .ui 文件转换来的界面元素，使得可以直接通过 self.xxx 访问
class QtMainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    # 构造函数，在创建对象时被调用
    def __init__(self):
        # 调用父类的构造函数，这是必须的步骤
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.userInfo = None

        # setupUi 方法会加载和初始化在Qt Designer中设计的UI界面
        self.setupUi(self)
        # 设置窗口标题
        self.setWindowTitle("Waifu2x-Gui")

        # 实例化各个子窗口或组件
        self.msgForm = QtBubbleLabel(self)  # 用于显示消息的气泡提示
        self.settingForm = QtSetting(self)  # 设置窗口
        self.settingForm.hide()  # 默认隐藏设置窗口
        self.settingForm.LoadSetting()  # 从配置文件加载设置

        self.aboutForm = QtAbout(self)  # “关于”窗口
        self.img = QtImg()  # 核心的图片处理和显示窗口

        # 将图片处理窗口(self.img)添加到stackedWidget中
        # QStackedWidget是一个可以包含多个子控件但一次只显示一个的容器
        self.stackedWidget.addWidget(self.img)

        # --- 信号与槽连接 ---
        # 当菜单栏的“关于”项(self.menuabout)被触发(triggered)时，调用self.OpenAbout方法
        self.menuabout.triggered.connect(self.OpenAbout)

        # 获取主屏幕的尺寸，用于后续可能的窗口居中或缩放（当前代码已注释）
        desktop = QGuiApplication.primaryScreen().geometry()

    # 重写closeEvent事件处理器，当用户关闭窗口时此方法会被自动调用
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        # 调用父类的同名方法，以确保正常的关闭流程
        super().closeEvent(a0)
        # 在退出前保存当前的设置和窗口大小
        self.settingForm.ExitSaveSetting(self.size())

    # 定义一个用于多语言翻译的方法
    def RetranslateUi(self):
        # 当语言切换时，递归地调用所有子窗口的retranslateUi方法来更新界面文本
        self.settingForm.retranslateUi(self.settingForm)
        self.img.retranslateUi(self.img)
        self.aboutForm.retranslateUi(self.aboutForm)
        # 更新主窗口自身的文本
        self.retranslateUi(self)

    # 程序核心初始化方法，在start.py中被调用
    def Init(self, app):
        # 初始化语言设置
        self.settingForm.SetLanguage(app, self)

        # 检查waifu2x核心库是否可用
        if config.CanWaifu2x:
            from waifu2x_vulkan import waifu2x_vulkan
            # 初始化waifu2x引擎
            stat = waifu2x_vulkan.init()
            if stat < 0:
                self.msgForm.ShowError("Waifu2x CPU Model")  # 初始化失败则显示错误
            waifu2x_vulkan.setDebug(True)  # 开启调试模式

            # 获取GPU和CPU信息，并传递给设置窗口用于显示和选择
            gpuInfo = waifu2x_vulkan.getGpuInfo()
            cpuNum = waifu2x_vulkan.getCpuCoreNum()
            self.settingForm.SetGpuInfos(gpuInfo, cpuNum)

            # 显示设置窗口，让用户进行初始配置
            self.settingForm.exec()
            # 根据用户的设置，再次设定语言
            self.settingForm.SetLanguage(app, self)
            # 将用户的GPU和CPU核心数选择应用到waifu2x引擎
            waifu2x_vulkan.initSet(config.Encode, config.UseCpuNum)

            # 在主界面上显示当前使用的GPU名称
            self.img.gpuName.setText(config.EncodeGpu)
            Log.Info("waifu2x init: " + str(stat) + " encode: " + str(config.Encode) + " version:" + waifu2x_vulkan.getVersion())
        else:
            # 如果核心库不可用，显示错误信息并禁用所有相关UI功能
            self.msgForm.ShowError("Waifu2x can not use, " + config.ErrorMsg)
            self.img.checkBox.setEnabled(False)
            self.img.changeJpg.setEnabled(False)
            self.img.changePng.setEnabled(False)
            self.img.comboBox.setEnabled(False)
            self.img.SetStatus(False)
            config.IsOpenWaifu = 0

        return

    # “打开关于”的槽函数
    def OpenAbout(self, action):
        # 检查触发信号的action文本是否为“about”
        if action.text() == "about":
            # 如果是，则显示“关于”窗口
            self.aboutForm.show()
        pass