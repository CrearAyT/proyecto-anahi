from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.Qwt5 as Qwt

from plotwindow import PlotWindow
from utils import lpfilt, diff, adsr

class DerivFilt(QMainWindow):
    name = 'Derivada, umbral, dc filtrada'

    def __init__(self, parent=None):
        super(DerivFilt, self).__init__(parent)

        self.plotw = PlotWindow(self)
        self.plotw.add_curve('Chan 1')
        self.plotw.add_curve('dChan1 / dT')
        self.plotw.add_curve('Umbral dC1/dT')
        self.plotw.add_curve('Detectado')
        self.plotw.add_curve('Nivel DC')
        self.plotw.add_curve('Componente AC (abs)')
        self.plotw.add_curve('ADSR')

        self.dx = diff()
        self.xf = lpfilt()
        self.dc = lpfilt(alfa=0.998)
        self.dxf = diff()

        self.adsr = adsr()

        self.alfa = .5
        self.umbral = 100

        self.main_frame = QWidget()
        lay = QGridLayout()
        vbox = QVBoxLayout()
        lay.addLayout(vbox, 0,0)
        lay.setColumnStretch(1,1)
        lay.addWidget(self.plotw,0,1)
        self.main_frame.setLayout(lay)
        self.setCentralWidget(self.main_frame)

        self.lbl = QLabel('alfa: 0.5')
        vbox.addWidget(self.lbl)

        sld = QSlider(Qt.Horizontal)
        sld.setRange(0,1000)
        sld.valueChanged[int].connect(self.set_alfa)
        sld.setValue(998)
        vbox.addWidget(sld)

        self.lblumb = QLabel('Umbral: 100')
        vbox.addWidget(self.lblumb)

        sld = QSlider(Qt.Horizontal)
        sld.setRange(0,400)
        sld.valueChanged[int].connect(self.set_umbral)
        sld.setValue(100)
        vbox.addWidget(sld)

        vbox.addStretch(1)

        self.setWindowTitle('Derivada, umbral filtrado')

    def set_umbral(self, value):
        self.umbral = value
        self.lblumb.setText('Umbral : %i' % value)

    def set_alfa(self, value):
        self.alfa = 0.001*value 
        self.dc.alfa = self.alfa
        self.lbl.setText('alfa: %.3f' % self.alfa)

    def new_data(self, data, *args, **kwargs):
        umb = self.umbral
        for item in data:
            x = item[1][0]
            d = self.dx(x)
            ok = 150*(abs(d)>=umb)
            dc = self.dc(x)
            ac = abs(x- dc)
            ad = self.adsr(x)
            self.plotw.add_datapoint(item[0], x, d, umb, ok, dc, ac, ad)
 
    def start(self):
        self.show()

    def stop(self):
        self.hide()

    def destroy(self):
        self.close()

