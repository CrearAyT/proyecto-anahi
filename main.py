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

        self.current_adsr = None
        self.monitor_adsr = True

        self.players = []
        self.sounds = []

        self.plotw = PlotWindow()
        self.plotWindowContainer.addWidget(self.plotw)

        for curve in 'Entrada d/dT Umbral Salida'.split():
            self.plotw.add_curve(curve)

        self._idx = 0

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
        if checked:
            self.monitor_adsr = True
        else:
            self.monitor_adsr = False

        self.connect_adsr()

    @QtCore.pyqtSlot(int)
    def on_sldVolumen_valueChanged(self, value):
        for player in self.players:
            player.default_volume = value

    @QtCore.pyqtSlot()
    def on_soundAdd_clicked(self):
        fn = QtGui.QFileDialog.getOpenFileName()
        if fn:
            fn = str(fn)
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

    @QtCore.pyqtSlot(bool)
    def on_Start_clicked(self, checked):
        if checked:
            for idx in xrange(min(len(self.players), len(self.sounds))):
                player = self.players[idx]
                player.playlist.clear()
                player.default_volume = self.sldVolumen.value()
                player.playlist.append(self.sounds[idx])
                player.start()
        else:
            for player in self.players:
                player.stop()

    @QtCore.pyqtSlot(int)
    def on_sensorList_currentRowChanged(self, row):
        self.connect_adsr(self.adsrList[row])

    def clear_plot(self):
        data = [ [0] ] * 5
        self.plotw.samples = data
        self.plotw.replot()

    def connect_adsr(self, adsr=None):
        if self.monitor_adsr:
            if adsr is not None and adsr is not self.current_adsr:
                if self.current_adsr:
                    self.current_adsr.internal_state_changed.disconnect(self.adsr_internal_cb)
                self.current_adsr = adsr
                self.clear_plot()
                self._idx = 0
                self.current_adsr.internal_state_changed.connect(self.adsr_internal_cb)
        else:
            if self.current_adsr:
                self.current_adsr.internal_state_changed.disconnect(self.adsr_internal_cb)

    def adsr_internal_cb(self, *args, **kwargs):
        salida, trig, entrada, dx = args
        idx = self._idx + 1
        self._idx = idx
        self.plotw.add_datapoint(idx, entrada, dx, self.adsrList.umbral, salida)

    def open_port(self):
        pass

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mainw = mainWindow()
    mainw.show()
    sys.exit(app.exec_())
