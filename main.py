#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
from PyQt4 import QtCore, QtGui, uic

from utils.adsr import adsrList
from sensorplayer import SensorPlayer
from utils.adsrwidget import adsrWidget
from utils.plotwindow import PlotWindow

class mainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        uifile = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'ui_data', 'main.ui')
        uic.loadUi(uifile, self)

        self.adsrw = adsrWidget()
        self.adsrList = adsrList()
        self.adsrw.adsr = self.adsrList
        self.adsrWidgetContainer.addWidget(self.adsrw)

        self.players = []
        self.sounds = []

        self.plotw = PlotWindow()
        self.plotWindowContainer.addWidget(self.plotw)
        self.plotw.show()

    @QtCore.pyqtSlot()
    def on_sensorAdd_clicked(self):
        play = SensorPlayer(gui=False)
        self.players.append(play)
        self.adsrList.append(play.adsr)

        self.sensorList.addItem('Sensor %i'%len(self.adsrList))

    @QtCore.pyqtSlot()
    def on_sensorDelete_clicked(self):
        idx = self.sensorList.count()
        if idx == 0:
            return

        item = self.sensorList.takeItem(idx-1)
        del item
        self.adsrList.pop()
        p = self.players.pop()
        #FIXME: matar el vlc hijo
        p.stop()

    @QtCore.pyqtSlot(bool)
    def on_plotWindowGroup_clicked(self, checked):
        #FIXME: desconectar el grafico  y borrar datos
        pass

    @QtCore.pyqtSlot(int)
    def on_sldVolumen_valueChanged(self, value):
        for player in self.players:
            player.default_volume = value

    @QtCore.pyqtSlot()
    def on_soundAdd_clicked(self):
        fn = QtGui.QFileDialog.getOpenFileName()
        if fn:
            self.sounds.append(fn)
            self.soundList.addItem(fn)

    @QtCore.pyqtSlot()
    def on_soundDelete_clicked(self):
        idx = self.soundList.currentRow()
        if idx == -1:
            return
        item = self.soundList.takeItem(idx)
        del item
        del self.sounds[idx]

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mainw = mainWindow()
    mainw.show()
    sys.exit(app.exec_())
