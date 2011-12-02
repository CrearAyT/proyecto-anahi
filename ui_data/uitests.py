#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
from PyQt4 import QtCore, QtGui, uic

sys.path.append('../')
from utils.adsrwidget import adsrWidget

class mainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        uifile = 'main.ui'
        uic.loadUi(uifile, self)

        self.adsrw = adsrWidget()
        self.adsrWidgetContainer.addWidget(self.adsrw)


    @QtCore.pyqtSlot()
    def on_sensorAdd_clicked(self):
        print 'add'

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mainw = mainWindow()
    mainw.show()
    sys.exit(app.exec_())
