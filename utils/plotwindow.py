from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.Qwt5 as Qwt

colors = 'red green blue cyan white magenta yellow lightGray darkRed darkGreen darkBlue darkMagenta darkCyan darkYellow darkGray'.split()

class PlotWindow(QMainWindow):
    def __init__(self, parent=None):
        super(PlotWindow, self).__init__(parent)
        
        self.samples = []
        self.xdata = []
        self.max_samples = 200
        self._axis = ()
        self._curves = []
        self.plot = None
        self.tags = []

        self.initialized = False

        self.axis()
        self.create_plot()
        self.create_main_frame()


    def axis(self, xmin=0, xmax=20, xlabel='T', ymin=0, ymax=1024, ylabel='Valor'):
        self._axis = (xmin, xmax, xlabel, ymin, ymax, ylabel)

        if self.plot is None:
            return
        
        self.plot.setAxisTitle(Qwt.QwtPlot.xBottom, xlabel)
        self.plot.setAxisScale(Qwt.QwtPlot.xBottom, xmin, xmax, ((xmax-xmin)/20))
        self.plot.setAxisTitle(Qwt.QwtPlot.yLeft, ylabel)
        self.plot.setAxisScale(Qwt.QwtPlot.yLeft, ymin, ymax, ((ymax-ymin)/10))

        
    def create_plot(self):
        plot = Qwt.QwtPlot(self)
        plot.setCanvasBackground(Qt.black)

        legend = Qwt.QwtLegend()
        legend.setItemMode(Qwt.QwtLegend.ClickableItem)
        plot.insertLegend(legend, Qwt.QwtPlot.LeftLegend)

        def toggleVisibility(plotItem):
            """Toggle the visibility of a plot item
            """
            plotItem.setVisible(not plotItem.isVisible())
            plot.replot()

        plot.connect(plot, SIGNAL("legendClicked(QwtPlotItem*)"), toggleVisibility)

        plot.replot()
        self.plot = plot


    def create_main_frame(self):
        plot_layout = QVBoxLayout()
        plot_layout.addWidget(self.plot)
        
        self.main_frame = QWidget()
        self.main_frame.setLayout(plot_layout)
        
        self.setCentralWidget(self.main_frame)

        
    def add_curve(self, name):
        self.tags.append(name)
        self.samples.append([])

        curve = Qwt.QwtPlotCurve(name)
        curve.setRenderHint(Qwt.QwtPlotItem.RenderAntialiased)
        pen = QPen(QColor(colors[len(self._curves)]))
        pen.setWidth(2)
        curve.setPen(pen)
        curve.attach(self.plot)
        self._curves.append(curve)

    
    def add_datapoint(self, x, *ydata):

        self.xdata.append(x)
        for idx in range(min(len(ydata), len(self._curves))):
            self.samples[idx].append(ydata[idx])

        if len(self.samples[0]) > self.max_samples:
            self.xdata.pop(0)
            for col in self.samples:
            # puede pasar si agregamos menos datos que la cantidad de curvas
                if col:
                    col.pop(0)

        self.plot.setAxisScale(Qwt.QwtPlot.xBottom, self.xdata[0], max(self._axis[1], x))
        for idx,curve in enumerate(self._curves):
            curve.setData(self.xdata, self.samples[idx])
               
        self.plot.replot()

    def replot(self):
        for idx,curve in enumerate(self._curves):
            curve.setData(self.xdata, self.samples[idx])
               
        self.plot.replot()
            
    def clear(self):
        self.xdata = []
        self.samples = [ [] for x in self._curves ]

def main():
    import sys, math
    app = QApplication(sys.argv)
    form = PlotWindow()
    form.show()
    
    xdata = range(0,360)
    ysin  = [math.sin(x*math.pi/180) for x in xdata]
    ycos  = [math.cos(x*math.pi/180) for x in xdata]

    form.samples = [xdata, ysin, ycos]
    form.axis(0,360,'wt',-1.3,1.3,'f(wt)')
    form.add_curve('Seno')
    form.add_curve('Coseno')
    form.replot()

    app.exec_()


if __name__ == "__main__":
    main()
