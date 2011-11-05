from deriv import Deriv

class SinkTest(object):
    name = 'Volcar datos a stdout'

    def __init__(self):
        pass

    def new_data(self, data, *args, **kwargs):
        print 'sink ', data
    
    def start(self):
        print 'sink start'

    def stop(self):
        print 'sink stop'

    def destroy(self):
        print 'sink destroy'

class PlotTest(object):
    name = 'Test de PlotWindow solo'

    def __init__(self):
        from plotwindow import PlotWindow
        self.plotw = PlotWindow()
        self.plotw.add_curve('Chan 1')
        self.plotw.add_curve('Chan 2')
        self.plotw.add_curve('Chan 3')
        self.plotw.add_curve('Chan 4')


    def new_data(self, data, *args, **kwargs):
        for item in data:
            self.plotw.add_datapoint(item[0], *item[1])
    
    def start(self):
        self.plotw.show()

    def stop(self):
        self.plotw.hide()

    def destroy(self):
        self.plotw.close()

all = [SinkTest, PlotTest, Deriv]
