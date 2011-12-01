# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.Qwt5 as Qwt


class adsrWidget(QMainWindow):
    def __init__(self, parent=None):
        super(adsrWidget, self).__init__(parent)
        
        self._adsr = None

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
        vbox = QVBoxLayout()
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)

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

    def set_param(self, value):
        (nom, lbl, attr, k, kdisp) = self.sender().params
        val = k*value
        if attr in ['attackl','sustl', 'rell']:
            val = int(val)
        lbl.setText(nom + ': %.3f'%(value*kdisp) )
        if self._adsr is not None:
            setattr(self._adsr, attr, val) 

    @property
    def adsr(self):
        return self._adsr

    @adsr.setter
    def adsr(self, adsr):
        if adsr is None:
            # FIXME: deshabilitar widget
            return

        self._adsr = adsr
        for sld in self.sliders:
            (nom, lbl, attr, k, kdisp) = sld.params
            try:
                val = getattr(adsr, attr)
                sld.setValue(int(val/k))
            except AttributeError:
                continue
