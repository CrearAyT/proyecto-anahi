from plotwindow import PlotWindow


class Deriv(object):
    name = 'Derivada de canal 1 (primera diferencia)'

    def __init__(self):
        self.plotw = PlotWindow()
        self.plotw.add_curve('Chan 1')
        self.plotw.add_curve('dChan1 / dT')

        self.last = 0


    def new_data(self, data, *args, **kwargs):
        last = self.last
        for item in data:
            x = item[1][0]
            d = x - last
            last = x
            self.plotw.add_datapoint(item[0], x, d)
        self.last = last
 
    def start(self):
        self.plotw.show()

    def stop(self):
        self.plotw.hide()

    def destroy(self):
        self.plotw.close()

