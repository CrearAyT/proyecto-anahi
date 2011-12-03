#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
from PyQt4 import QtCore, QtGui, uic
import PyQt4.Qwt5 as Qwt
import Queue

from utils.adsr import adsrList, adsr_params
from sensorplayer import SensorPlayer
from utils.adsrwidget import adsrWidget
from utils.plotwindow import PlotWindow

from utils import config

from com_monitor import ComMonitorThread
from eblib.serialutils import full_port_name, enumerate_serial_ports
from eblib.utils import get_all_from_queue, get_item_from_queue
from livedatafeed import LiveDataFeed

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
        self.invert_control = False
        self.trigger_shadow = False
        self.sounds = []

        self.plotw = PlotWindow()
        self.plotw.plot.setAxisScale(Qwt.QwtPlot.yLeft, 0, 1024, 1024/8)
        self.plotw.plot.setAxisScale(Qwt.QwtPlot.xBottom, 0, 20, 20./10)
        self.plotWindowContainer.addWidget(self.plotw)

        for curve in 'Entrada d/dT Umbral Salida'.split():
            self.plotw.add_curve(curve)

        self._idx = 0

        self.plotw.show()

        self.timer = QtCore.QTimer()

        self.open_port()

        self.load_config()

    def load_config(self):
        config.load()

        adsrconf = config.get('adsr')
        if adsrconf:
            for k,v in adsrconf.iteritems():
                setattr(self.adsrList, k, v)
            self.adsrw.adsr = self.adsrList

        sounds = config.get('sounds')
        if sounds:
            for snd in sounds['files']:
                self.add_sound(str(snd))

        globs = config.get('globals')
        if globs:
            self.invert_control = globs['invert_control']
            self.trigger_shadow = globs['trigger_shadow']
            if self.invert_control:
                self.invert.setCheckState(QtCore.Qt.Checked)
            if self.trigger_shadow:
                self.invert_slope.setCheckState(QtCore.Qt.Checked)

            self.sldVolumen.setValue(globs['default_volume'])

            for x in xrange(globs['sensor_count']):
                self.add_sensor()

    def closeEvent(self, event):
        self.save_config()
        event.accept()

    def save_config(self):
        adsrconf = config.get('adsr')
        for param in adsr_params.keys():
            adsrconf[param] = getattr(self.adsrList, param)

        sounds = config.get('sounds')
        sounds['files'] = self.sounds[:]

        globs = config.get('globals')
        globs['invert_control'] = self.invert_control
        globs['trigger_shadow'] = self.trigger_shadow
        globs['default_volume'] = self.sldVolumen.value()
        globs['sensor_count'] = len(self.players)

        config.save()

    def add_sensor(self):
        play = SensorPlayer(gui=False)
        self.players.append(play)
        self.adsrList.append(play.adsr)

        play.invert_control = self.invert_control
        play.trigger_on_light = not self.trigger_shadow

        self.sensorList.addItem('Sensor %i'%len(self.adsrList))

    @QtCore.pyqtSlot()
    def on_sensorAdd_clicked(self):
        self.add_sensor()

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
    def on_invert_stateChanged(self, state):
        if state:
            self.invert_control = True
        else:
            self.invert_control = False

        for player in self.players:
            player.invert_control = self.invert_control

    @QtCore.pyqtSlot(int)
    def on_invert_slope_stateChanged(self, state):
        if state:
            self.trigger_shadow = True
        else:
            self.trigger_shadow = False

        for player in self.players:
            player.trigger_on_light = not self.trigger_shadow

    @QtCore.pyqtSlot(int)
    def on_sldVolumen_valueChanged(self, value):
        for player in self.players:
            player.default_volume = value

    def add_sound(self, filename):
            self.sounds.append(filename)
            self.soundList.addItem(filename)

    @QtCore.pyqtSlot()
    def on_soundAdd_clicked(self):
        fn = QtGui.QFileDialog.getOpenFileName()
        if fn:
            fn = str(fn)
            self.add_sound(fn)

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

    def connect_adsr(self, adsr=None):
        if self.monitor_adsr:
            self.plotw.clear()
            self._idx = 0
            if adsr is not None and adsr is not self.current_adsr:
                if self.current_adsr:
                    self.current_adsr.internal_state_changed.disconnect(self.adsr_internal_cb)
                self.current_adsr = adsr
                self.current_adsr.internal_state_changed.connect(self.adsr_internal_cb)
            else:
                if self.current_adsr:
                    self.current_adsr.internal_state_changed.connect(self.adsr_internal_cb)
        else:
            if self.current_adsr:
                self.current_adsr.internal_state_changed.disconnect(self.adsr_internal_cb)

    def adsr_internal_cb(self, *args, **kwargs):
        salida, trig, entrada, dx = args
        idx = self._idx + .1
        self._idx = idx
        self.plotw.add_datapoint(idx, entrada, abs(dx), self.adsrList.umbral, salida)

    def open_port(self):
        self.data_q = Queue.Queue()
        self.error_q = Queue.Queue()
        self.com_monitor = ComMonitorThread(
            self.data_q,
            self.error_q,
            '/dev/ttyACM0',
            115200)
        self.com_monitor.start()
        com_error = get_item_from_queue(self.error_q)
        if com_error is not None:
            QtGui.QMessageBox.critical(self, 'ComMonitorThread error',
                com_error)
            self.com_monitor = None

        self.monitor_active = True

        self.connect(self.timer, QtCore.SIGNAL('timeout()'), self.on_timer)

        self.timer.start(1000.0 / 10)

    def on_timer(self, *args):
        data = list(get_all_from_queue(self.data_q))
        # (timestamp, [x0, x1, x2, etc])
        if (len(data)==0):
            return

        for row in data:
           for idx in xrange(min(len(row[1]), len(self.players))):
                self.players[idx].adsr(row[1][idx])

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mainw = mainWindow()
    mainw.show()
    sys.exit(app.exec_())
