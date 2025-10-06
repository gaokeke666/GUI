# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.2.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

# 导入所有需要的PySide6模块。这些都是构建GUI所必需的基本组件。
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QMainWindow, QMenu,
    QMenuBar, QSizePolicy, QStackedWidget, QStatusBar,
    QWidget)

# 定义一个名为 Ui_MainWindow 的类。按照惯例，所有从.ui文件生成的UI定义类都以'Ui_'开头。
# 这个类本身不是一个窗口，而是一个'object'，它负责在真正的主窗口实例上创建和布局UI元素。
class Ui_MainWindow(object):
    # setupUi方法是核心。它接收一个QMainWindow实例(名为MainWindow)作为参数，
    # 然后在这个实例上构建出在Qt Designer中设计的界面。
    def setupUi(self, MainWindow):
        # 设置主窗口的对象名，这在Qt中用于内部识别和样式表选择。
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        # 设置主窗口的初始大小。
        MainWindow.resize(353, 223)

        # --- 创建菜单栏的动作(QAction) ---
        # QAction是菜单项、工具栏按钮等可执行操作的抽象。
        self.actionsetting = QAction(MainWindow)
        self.actionsetting.setObjectName(u"actionsetting")
        self.actionabout = QAction(MainWindow)
        self.actionabout.setObjectName(u"actionabout")
        self.actionimg_convert = QAction(MainWindow)
        self.actionimg_convert.setObjectName(u"actionimg_convert")

        # --- 创建中央控件和布局 ---
        # QMainWindow的中心区域是一个QWidget，我们可以在上面放置布局和其它控件。
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        # 使用网格布局(QGridLayout)来组织中央控件的内容。
        self.gridLayout_4 = QGridLayout(self.centralwidget)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")

        # 创建一个QStackedWidget。这是UI的核心部分，用于切换不同的功能页面（如此处的图片处理界面）。
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setMinimumSize(QSize(0, 0))

        # 将stackedWidget添加到网格布局中，占据整个布局。
        self.gridLayout_3.addWidget(self.stackedWidget, 0, 0, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout_3, 0, 0, 1, 1)

        # 将配置好的中央控件设置给主窗口。
        MainWindow.setCentralWidget(self.centralwidget)

        # --- 创建菜单栏(QMenuBar)和状态栏(QStatusBar) ---
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 353, 22))
        # 创建一个名为'menuabout'的菜单(QMenu)。
        self.menuabout = QMenu(self.menubar)
        self.menuabout.setObjectName(u"menuabout")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # --- 将动作添加到菜单中 ---
        # 将'menuabout'菜单添加到菜单栏中。
        self.menubar.addAction(self.menuabout.menuAction())
        # 将'actionabout'动作（即“关于”菜单项）添加到'menuabout'菜单中。
        self.menuabout.addAction(self.actionabout)

        # 调用retranslateUi方法来设置所有控件的显示文本。
        self.retranslateUi(MainWindow)

        # 设置stackedWidget的初始显示页面为-1（即不显示任何页面）。
        self.stackedWidget.setCurrentIndex(-1)


        # 这是一个重要的Qt机制，它会根据对象名自动连接信号和槽。
        # 例如，如果一个按钮对象名为'myButton'，并且窗口有一个名为'on_myButton_clicked'的方法，
        # 那么这个调用会自动将按钮的clicked()信号连接到该方法。
        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    # retranslateUi方法负责设置或更新UI上所有面向用户的文本。
    # 这对于实现多语言支持至关重要。QCoreApplication.translate用于获取翻译后的字符串。
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Waifu2x-GUI", None))
        self.actionsetting.setText(QCoreApplication.translate("MainWindow", u"setting", None))
        self.actionabout.setText(QCoreApplication.translate("MainWindow", u"about", None))
        self.actionimg_convert.setText(QCoreApplication.translate("MainWindow", u"img convert", None))
        self.menuabout.setTitle(QCoreApplication.translate("MainWindow", u"\u5de5\u5177", None))
    # retranslateUi


