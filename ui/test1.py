# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'test1.ui'
##
## Created by: Qt User Interface Compiler version 6.1.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *  # type: ignore
from PySide6.QtGui import *  # type: ignore
from PySide6.QtWidgets import *  # type: ignore


class Ui_Test1(object):
    def setupUi(self, Test1):
        if not Test1.objectName():
            Test1.setObjectName(u"Test1")
        Test1.resize(400, 300)
        self.horizontalLayoutWidget = QWidget(Test1)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(10, 40, 371, 80))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.checkBox = QCheckBox(self.horizontalLayoutWidget)
        self.checkBox.setObjectName(u"checkBox")

        self.horizontalLayout.addWidget(self.checkBox)

        self.lineEdit = QLineEdit(self.horizontalLayoutWidget)
        self.lineEdit.setObjectName(u"lineEdit")

        self.horizontalLayout.addWidget(self.lineEdit)

        self.pushButton = QPushButton(self.horizontalLayoutWidget)
        self.pushButton.setObjectName(u"pushButton")

        self.horizontalLayout.addWidget(self.pushButton)

        self.formLayoutWidget = QWidget(Test1)
        self.formLayoutWidget.setObjectName(u"formLayoutWidget")
        self.formLayoutWidget.setGeometry(QRect(59, 180, 281, 80))
        self.formLayout = QFormLayout(self.formLayoutWidget)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.confirm = QPushButton(Test1)
        self.confirm.setObjectName(u"confirm")
        self.confirm.setGeometry(QRect(90, 140, 75, 24))
        self.radioButton = QRadioButton(Test1)
        self.radioButton.setObjectName(u"radioButton")
        self.radioButton.setGeometry(QRect(190, 140, 92, 20))
        self.xiala = QComboBox(Test1)
        self.xiala.addItem("")
        self.xiala.addItem("")
        self.xiala.addItem("")
        self.xiala.addItem("")
        self.xiala.setObjectName(u"xiala")
        self.xiala.setEnabled(True)
        self.xiala.setGeometry(QRect(10, 140, 68, 22))

        self.retranslateUi(Test1)
        self.checkBox.clicked.connect(Test1.chose)
        self.confirm.clicked.connect(Test1.confirm)
        self.lineEdit.textEdited.connect(Test1.chageword)
        self.xiala.currentIndexChanged.connect(Test1.xiala)

        self.xiala.setCurrentIndex(3)


        QMetaObject.connectSlotsByName(Test1)
    # setupUi

    def retranslateUi(self, Test1):
        Test1.setWindowTitle(QCoreApplication.translate("Test1", u"Form", None))
        self.checkBox.setText(QCoreApplication.translate("Test1", u"CheckBox", None))
        self.pushButton.setText(QCoreApplication.translate("Test1", u"PushButton", None))
        self.confirm.setText(QCoreApplication.translate("Test1", u"\u786e\u8ba4", None))
        self.radioButton.setText(QCoreApplication.translate("Test1", u"RadioButton", None))
        self.xiala.setItemText(0, QCoreApplication.translate("Test1", u"1", None))
        self.xiala.setItemText(1, QCoreApplication.translate("Test1", u"2", None))
        self.xiala.setItemText(2, QCoreApplication.translate("Test1", u"3", None))
        self.xiala.setItemText(3, QCoreApplication.translate("Test1", u"4", None))

        self.xiala.setCurrentText(QCoreApplication.translate("Test1", u"4", None))
    # retranslateUi

