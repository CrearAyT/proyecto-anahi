# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.Qwt5 as Qwt

from plotwindow import PlotWindow
from utils import lpfilt, diff, adsr

import config

from vlc import VLC

class adsr_vlc(adsr):
    def on_release_cb(self):
        if self.vlc is None:
            return
        try:
            self.vlc.volume(25)
        except:
            self.vlc = None

    def on_trigger_cb(self,x):
        if self.vlc is None:
            return
        try:
            self.vlc.volume(x/2)
        except:
            self.vlc = None

    def while_triggered_cb(self, x):
        if self.vlc is None:
            return
        try:
            self.vlc.volume(x/2)
        except:
            self.vlc = None


class ADSRDemo4C(QMainWindow):
    name = 'Prueba cuatro canales'

    def __init__(self, parent=None):
        super(ADSRDemo4C, self).__init__(parent)

        self.conf = config.get('adsrdemo.py')

        self.vlc = []

        self.plotw = PlotWindow(self)
        self.plotw.add_curve('Chan 1')
        self.plotw.add_curve('Chan 2')
        self.plotw.add_curve('Chan 3')
        self.plotw.add_curve('Chan 4')

        self.plotw.add_curve('ADSR1')
        self.plotw.add_curve('ADSR2')
        self.plotw.add_curve('ADSR3')
        self.plotw.add_curve('ADSR4')

        self.dx = diff()

        self.adsr = [adsr_vlc() for x in range(4)]

        # atributo adsr : [nombre ,                    min, max,  k,       kdisp,   default]
        self.params = {  'attackl':['Duracion Ataque', 0,   200,  1./10,   1./100,  150 ],
                         'sustl':['Duracion Sustain',  0,   900,  1,       1./10,   100 ],
                         'rell':['Duracion Release',   0,   300,  1,       1./10,   15  ],
                         'alfa_att':['alfa Ataque',    0,   1000, 1./1000, 1./1000, 300 ],
                         'alfa_sus':['alfa Sustain',   0,   1000, 1./1000, 1./1000, 850 ],
                         'alfa_rel':['alfa Release',   0,   1000, 1./1000, 1./1000, 850 ],
                         'umbral':['umbral deteccion', 0,   400,  1,       1,       100 ]
                       }


        self.main_frame = QWidget()
        lay = QGridLayout()
        vbox = QVBoxLayout()
        lay.addLayout(vbox, 0,0)
        lay.setColumnStretch(1,1)
        lay.addWidget(self.plotw,0,1)
        self.main_frame.setLayout(lay)
        self.setCentralWidget(self.main_frame)

        hb = QHBoxLayout()
        vbox.addLayout(hb)
        b = QPushButton('Guardar')
        b.clicked.connect(self.guardar)
        hb.addWidget(b)
        b = QPushButton('Cargar')
        b.clicked.connect(self.cargar)
        hb.addWidget(b)

        b = QPushButton('Conectar con vlc')
        b.clicked.connect(self.vlc_connect)
        vbox.addWidget(b)

        self.sliders = []
        for attr,params  in self.params.iteritems():
            (nom, xmin, xmax, k, kdisp, default) = params
            lbl = QLabel(nom)
            sld = QSlider(Qt.Horizontal)
            sld.setRange(xmin, xmax)
            sld.valueChanged[int].connect(self.set_param)
            sld.params = (nom, lbl, attr, k, kdisp)
            sld.setValue(default) 
            vbox.addWidget(lbl)
            vbox.addWidget(sld)
            self.sliders.append(sld)

        b = QPushButton('Resetear ADSR')
        b.clicked.connect(self.reset_adsr)
        vbox.addWidget(b)

        vbox.addStretch(1)

        self.setWindowTitle('Prueba ADSR')

    def reset_adsr(self):
        for ad in self.adsr:
            ad.reset()


    def guardar(self):
        for sld in self.sliders:
            (nom, lbl, attr, k, kdisp) = sld.params
            self.conf[attr] = sld.value()

    def cargar(self):
        for sld in self.sliders:
            (nom, lbl, attr, k, kdisp) = sld.params
            if attr in self.conf:
                sld.setValue(self.conf[attr])

    def set_param(self, value):
        (nom, lbl, attr, k, kdisp) = self.sender().params
        val = k*value
        if attr in ['attackl','sustl', 'rell']:
            val = int(val)
        lbl.setText(nom + ': %.3f'%(value*kdisp) )
        for adsr in self.adsr:
            setattr(adsr, attr, val) 

    def new_data(self, data, *args, **kwargs):
        for item in data:
            res = item[1][:]
            for idx,x in enumerate( item[1]):
                res.append(self.adsr[idx](x))
                
            self.plotw.add_datapoint(item[0], *res)
 
    def start(self):
        self.show()

    def stop(self):
        self.hide()

    def destroy(self):
        self.close()

    def vlc_connect(self):
        self.vlc = []
        try:
            for idx in range(4):
                vlc = VLC(port=4210+idx)
                self.adsr[idx].vlc = vlc

        except:
            print 'error conexion vlc'
            for adsr in self.adsr:
                adsr.vlc = None

