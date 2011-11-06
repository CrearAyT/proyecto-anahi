# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.Qwt5 as Qwt

from plotwindow import PlotWindow
from utils import lpfilt, diff, adsr

import config

class ADSRDemo(QMainWindow):
    name = 'Prueba ADSR'

    def __init__(self, parent=None):
        super(ADSRDemo, self).__init__(parent)

        self.conf = config.get('adsrdemo.py')

        self.plotw = PlotWindow(self)
        self.plotw.add_curve('Chan 1')
        self.plotw.add_curve('dChan1 / dT')
        self.plotw.add_curve('Umbral dC1/dT')
        self.plotw.add_curve('Detectado')
        self.plotw.add_curve('ADSR')

        self.dx = diff()

        self.adsr = adsr()

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

        vbox.addStretch(1)

        self.setWindowTitle('Prueba ADSR')


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
        lbl.setText(nom + ': %.3f'%(value*kdisp) )
        setattr(self.adsr, attr, val) 

    def new_data(self, data, *args, **kwargs):
        umb = self.adsr.umbral
        for item in data:
            x = item[1][0]
            d = self.dx(x)
            ok = 150*(abs(d)>=umb)
            ad = self.adsr(x)
            self.plotw.add_datapoint(item[0], x, d, umb, ok, ad)
 
    def start(self):
        self.show()

    def stop(self):
        self.hide()

    def destroy(self):
        self.close()

