class diff(object):
    def __init__(self, x0=0):
        self.x = x0
    def __call__(self, x):
        ret = x - self.x
        self.x = x
        return ret
        
class lpfilt(object):
    def __init__(self, alfa=0.5, x0=0, y0=0):
        self.alfa = alfa
        self.y=y0
    def __call__(self, x):
        y = self.alfa * self.y + (1-self.alfa)*x
        self.y = y
        return y

