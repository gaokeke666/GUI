# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'img.ui'
##
## Created by: Qt User Interface Compiler version 6.2.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

# 导入所有需要的PySide6模块。
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QComboBox,
    QFrame, QGraphicsView, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QRadioButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

# UI定义类，负责在传入的QWidget(名为Img)上构建界面。
class Ui_Img(object):
    def setupUi(self, Img):
        if not Img.objectName():
            Img.setObjectName(u"Img")
        Img.resize(620, 559)
        # 主布局，网格布局，分为左右两部分
        self.gridLayout = QGridLayout(Img)
        self.gridLayout.setObjectName(u"gridLayout")

        # --- 左侧：图片显示区域 ---
        # 使用QGraphicsView来显示图片，支持缩放和平移
        self.graphicsView = QGraphicsView(Img)
        self.graphicsView.setObjectName(u"graphicsView")
        self.gridLayout.addWidget(self.graphicsView, 0, 0, 1, 1) # 添加到主布局的左侧 (0,0)

        # --- 右侧：控制和信息面板 ---
        # 使用一个垂直布局(QVBoxLayout)来容纳右侧所有控件
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")

        # -- 参数设置区域 --
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")

        # 复选框：是否预览waifu2x处理后的图片
        self.checkBox = QCheckBox(Img)
        self.checkBox.setObjectName(u"checkBox")
        self.checkBox.setMaximumSize(QSize(100, 16777215))
        self.checkBox.setChecked(True)
        self.verticalLayout_2.addWidget(self.checkBox)

        # 复选框：是否启用TTA模式
        self.ttaModel = QCheckBox(Img)
        self.ttaModel.setObjectName(u"ttaModel")
        self.ttaModel.setMaximumSize(QSize(70, 16777215))
        self.verticalLayout_2.addWidget(self.ttaModel)

        # -- 缩放模式选择 --
        # 使用QButtonGroup来确保“倍数放大”和“固定长宽”两个单选按钮互斥
        self.buttonGroup_2 = QButtonGroup(Img)
        self.buttonGroup_2.setObjectName(u"buttonGroup_2")

        # 水平布局：包含“倍数放大”单选按钮和输入框
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.scaleRadio = QRadioButton(Img) # “倍数放大”单选按钮
        self.buttonGroup_2.addButton(self.scaleRadio)
        self.scaleRadio.setObjectName(u"scaleRadio")
        self.scaleRadio.setMaximumSize(QSize(80, 16777215))
        self.scaleRadio.setChecked(True)
        self.horizontalLayout_3.addWidget(self.scaleRadio)
        self.scaleEdit = QLineEdit(Img) # 放大倍数输入框
        self.scaleEdit.setObjectName(u"scaleEdit")
        self.scaleEdit.setMaximumSize(QSize(160, 16777215))
        self.scaleEdit.setAlignment(Qt.AlignCenter)
        self.horizontalLayout_3.addWidget(self.scaleEdit)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        # 水平布局：包含“固定长宽”单选按钮和宽高输入框
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.heighRadio = QRadioButton(Img) # “固定长宽”单选按钮
        self.buttonGroup_2.addButton(self.heighRadio)
        self.heighRadio.setObjectName(u"heighRadio")
        self.heighRadio.setMaximumSize(QSize(80, 16777215))
        self.horizontalLayout_4.addWidget(self.heighRadio)
        self.widthEdit = QLineEdit(Img) # 宽度输入框
        self.widthEdit.setObjectName(u"widthEdit")
        self.widthEdit.setEnabled(True)
        self.widthEdit.setMaximumSize(QSize(60, 16777215))
        self.widthEdit.setAlignment(Qt.AlignCenter)
        self.horizontalLayout_4.addWidget(self.widthEdit)
        self.label_2 = QLabel(Img) # 'x' 标签
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMaximumSize(QSize(20, 16777215))
        self.horizontalLayout_4.addWidget(self.label_2)
        self.heighEdit = QLineEdit(Img) # 高度输入框
        self.heighEdit.setObjectName(u"heighEdit")
        self.heighEdit.setEnabled(True)
        self.heighEdit.setMaximumSize(QSize(60, 16777215))
        self.heighEdit.setAlignment(Qt.AlignCenter)
        self.horizontalLayout_4.addWidget(self.heighEdit)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        # -- 降噪等级选择 --
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_4 = QLabel(Img) # “降噪”标签
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMaximumSize(QSize(60, 16777215))
        self.horizontalLayout_5.addWidget(self.label_4)
        self.noiseCombox = QComboBox(Img) # 降噪等级下拉框
        self.noiseCombox.addItem("")
        self.noiseCombox.addItem("")
        self.noiseCombox.addItem("")
        self.noiseCombox.addItem("")
        self.noiseCombox.addItem("")
        self.noiseCombox.setObjectName(u"noiseCombox")
        self.noiseCombox.setMaximumSize(QSize(160, 16777215))
        self.horizontalLayout_5.addWidget(self.noiseCombox)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        # -- 模型选择 --
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_5 = QLabel(Img) # “模型”标签
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMaximumSize(QSize(60, 16777215))
        self.horizontalLayout_6.addWidget(self.label_5)
        self.comboBox = QComboBox(Img) # 模型选择下拉框
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setMaximumSize(QSize(160, 16777215))
        self.horizontalLayout_6.addWidget(self.comboBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout_6)

        # -- 转换操作 --
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.changeJpg = QPushButton(Img) # “转换JPG”按钮
        self.changeJpg.setObjectName(u"changeJpg")
        self.changeJpg.setMaximumSize(QSize(100, 16777215))
        self.horizontalLayout_7.addWidget(self.changeJpg)
        self.changePng = QPushButton(Img) # “转换PNG”按钮
        self.changePng.setObjectName(u"changePng")
        self.changePng.setMaximumSize(QSize(100, 16777215))
        self.horizontalLayout_7.addWidget(self.changePng)
        self.changeLabel = QLabel(Img) # 显示转换状态的标签
        self.changeLabel.setObjectName(u"changeLabel")
        self.changeLabel.setMaximumSize(QSize(100, 16777215))
        self.changeLabel.setAlignment(Qt.AlignCenter)
        self.horizontalLayout_7.addWidget(self.changeLabel)
        self.verticalLayout_2.addLayout(self.horizontalLayout_7)

        self.verticalLayout.addLayout(self.verticalLayout_2)

        # 分割线
        self.line_4 = QFrame(Img)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.HLine)
        self.line_4.setFrameShadow(QFrame.Sunken)
        self.verticalLayout.addWidget(self.line_4)

        # -- 信息显示区域 --
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        
        # 分辨率显示
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_8 = QLabel(Img)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setMaximumSize(QSize(60, 16777215))
        self.horizontalLayout_8.addWidget(self.label_8)
        self.resolutionLabel = QLabel(Img)
        self.resolutionLabel.setObjectName(u"resolutionLabel")
        self.resolutionLabel.setMaximumSize(QSize(160, 16777215))
        self.horizontalLayout_8.addWidget(self.resolutionLabel)
        self.verticalLayout_3.addLayout(self.horizontalLayout_8)

        # 文件大小显示
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_10 = QLabel(Img)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setMaximumSize(QSize(60, 16777215))
        self.horizontalLayout_9.addWidget(self.label_10)
        self.sizeLabel = QLabel(Img)
        self.sizeLabel.setObjectName(u"sizeLabel")
        self.sizeLabel.setMaximumSize(QSize(160, 16777215))
        self.horizontalLayout_9.addWidget(self.sizeLabel)
        self.verticalLayout_3.addLayout(self.horizontalLayout_9)

        # GPU名称显示
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(Img)
        self.label.setObjectName(u"label")
        self.label.setMaximumSize(QSize(60, 16777215))
        self.horizontalLayout.addWidget(self.label)
        self.gpuName = QLabel(Img)
        self.gpuName.setObjectName(u"gpuName")
        self.gpuName.setMaximumSize(QSize(160, 16777215))
        self.horizontalLayout.addWidget(self.gpuName)
        self.verticalLayout_3.addLayout(self.horizontalLayout)

        # 耗时显示
        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.label_6 = QLabel(Img)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setMaximumSize(QSize(60, 16777215))
        self.horizontalLayout_10.addWidget(self.label_6)
        self.tickLabel = QLabel(Img)
        self.tickLabel.setObjectName(u"tickLabel")
        self.tickLabel.setMaximumSize(QSize(160, 16777215))
        self.horizontalLayout_10.addWidget(self.tickLabel)
        self.verticalLayout_3.addLayout(self.horizontalLayout_10)

        # -- 主要操作按钮 --
        self.oepnButton = QPushButton(Img) # “打开图片”按钮
        self.oepnButton.setObjectName(u"oepnButton")
        self.oepnButton.setMaximumSize(QSize(100, 16777215))
        self.verticalLayout_3.addWidget(self.oepnButton)

        self.pushButton_3 = QPushButton(Img) # “缩小”按钮
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setMaximumSize(QSize(100, 16777215))
        self.verticalLayout_3.addWidget(self.pushButton_3)

        self.pushButton = QPushButton(Img) # “放大”按钮
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setMaximumSize(QSize(100, 16777215))
        self.verticalLayout_3.addWidget(self.pushButton)

        self.saveButton = QPushButton(Img) # “保存图片”按钮
        self.saveButton.setObjectName(u"saveButton")
        self.saveButton.setMaximumSize(QSize(100, 16777215))
        self.verticalLayout_3.addWidget(self.saveButton)

        self.verticalLayout.addLayout(self.verticalLayout_3)

        # 弹簧，用于将上面的控件推到顶部，使得布局更美观
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(self.verticalSpacer)

        # 将整个右侧面板的布局添加到主布局的右侧 (0,1)
        self.gridLayout.addLayout(self.verticalLayout, 0, 1, 1, 1)

        # 设置文本和连接信号
        self.retranslateUi(Img)

        # --- 信号与槽的连接（在Qt Designer中设置）---
        # 这一部分是Qt Designer的强大之处，它自动生成了信号与槽的连接代码。
        # 例如：self.saveButton的clicked信号连接到了Img对象的SavePicture方法。
        self.checkBox.clicked.connect(Img.SwithPicture)
        self.saveButton.clicked.connect(Img.SavePicture)
        self.heighEdit.textChanged.connect(Img.CheckScaleRadio)
        self.pushButton_3.clicked.connect(Img.ReduceScalePic)
        self.heighRadio.clicked.connect(Img.CheckScaleRadio)
        self.ttaModel.clicked.connect(Img.CheckScaleRadio)
        self.oepnButton.clicked.connect(Img.OpenPicture)
        self.widthEdit.textChanged.connect(Img.CheckScaleRadio)
        self.pushButton.clicked.connect(Img.AddScalePic)
        self.scaleEdit.textChanged.connect(Img.CheckScaleRadio)
        self.scaleRadio.clicked.connect(Img.CheckScaleRadio)
        self.comboBox.currentIndexChanged.connect(Img.ChangeModel)
        self.changeJpg.clicked.connect(Img.StartWaifu2x)
        self.noiseCombox.currentIndexChanged.connect(Img.CheckScaleRadio)
        self.changePng.clicked.connect(Img.StartWaifu2xPng)
        self.changeJpg.clicked.connect(Img.StartWaifu2xJPG)

        QMetaObject.connectSlotsByName(Img)
    # setupUi

    # 设置/更新UI控件的显示文本
    def retranslateUi(self, Img):
        Img.setWindowTitle(QCoreApplication.translate("Img", u"Form", None))
        self.checkBox.setText(QCoreApplication.translate("Img", u"waifu2x", None))
#if QT_CONFIG(tooltip)
        self.ttaModel.setToolTip(QCoreApplication.translate("Img", u"画质提升，耗时增加", None))
#endif // QT_CONFIG(tooltip)
        self.ttaModel.setText(QCoreApplication.translate("Img", u"tta模式", None))
        self.scaleRadio.setText(QCoreApplication.translate("Img", u"倍数放大", None))
        self.scaleEdit.setText(QCoreApplication.translate("Img", u"2", None))
        self.heighRadio.setText(QCoreApplication.translate("Img", u"固定长宽", None))
        self.label_2.setText(QCoreApplication.translate("Img", u"x", None))
        self.label_4.setText(QCoreApplication.translate("Img", u"降噪：", None))
        self.noiseCombox.setItemText(0, QCoreApplication.translate("Img", u"3", None))
        self.noiseCombox.setItemText(1, QCoreApplication.translate("Img", u"2", None))
        self.noiseCombox.setItemText(2, QCoreApplication.translate("Img", u"1", None))
        self.noiseCombox.setItemText(3, QCoreApplication.translate("Img", u"0", None))
        self.noiseCombox.setItemText(4, QCoreApplication.translate("Img", u"-1", None))

        self.label_5.setText(QCoreApplication.translate("Img", u"模型：", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("Img", u"cunet", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("Img", u"photo", None))
        self.comboBox.setItemText(2, QCoreApplication.translate("Img", u"anime_style_art_rgb", None))

        self.changeJpg.setText(QCoreApplication.translate("Img", u"转换JPG", None))
        self.changePng.setText(QCoreApplication.translate("Img", u"转换PNG", None))
        self.changeLabel.setText("")
        self.label_8.setText(QCoreApplication.translate("Img", u"分辨率：", None))
        self.resolutionLabel.setText(QCoreApplication.translate("Img", u"TextLabel", None))
        self.label_10.setText(QCoreApplication.translate("Img", u"大 小：", None))
        self.sizeLabel.setText(QCoreApplication.translate("Img", u"TextLabel", None))
        self.label.setText(QCoreApplication.translate("Img", u"GPU:", None))
        self.gpuName.setText(QCoreApplication.translate("Img", u"TextLabel", None))
        self.label_6.setText(QCoreApplication.translate("Img", u"耗时：", None))
        self.tickLabel.setText("")
        self.oepnButton.setText(QCoreApplication.translate("Img", u"打开图片", None))
        self.pushButton_3.setText(QCoreApplication.translate("Img", u"缩小", None))
        self.pushButton.setText(QCoreApplication.translate("Img", u"放大", None))
        self.saveButton.setText(QCoreApplication.translate("Img", u"保存图片", None))
    # retranslateUi
