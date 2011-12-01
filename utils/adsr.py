from dsp import diff, lpfilt
from misc import Signal

class adsr(object):
    def __init__(self):
        self.umbral = 100
        self.slope_sign = 1

        self.dx = diff()
        self.lp1 = lpfilt(alfa=0.8)

        self.triggered = False
        self.samplec = 0
        self.attackl = 15
        self.sustl = 100
        self.rell = 15
        self.alfa_rel = 0.85
        self.alfa_sus = 0.85
        self.alfa_att = 0.3

        self.state = 'quiet' # quiet attack sustain release
        self._states = {'quiet':self._quiet, 'attack':self._attack, 'sustain':self._sustain, 'release':self._release}

        self.on_release = Signal()
        self.on_trigger = Signal()
        self.while_triggered = Signal()

        self.internal_state_changed = Signal()

    def reset(self):
        self.samplec = 0
        self.lp1.y = 0
        self.state = 'quiet'
        self.triggered = False
        self.on_release()
        self.internal_state_changed(0, self.triggered, self.dx.x, self.lp1.y)

    def _quiet(self, x):
        d = self.dx(x)
        ok = 150*(abs(d)>=self.umbral)
        if (ok and (d*self.slope_sign)>0):
            self.triggered = True
            self.samplec = self.attackl
            self.state = 'attack'
            self.on_trigger(x)
            return self._attack(x)
        self.internal_state_changed(0, self.triggered, self.dx.x, self.lp1.y)
        return 0

    def _attack(self, x):
        if self.samplec:
            self.lp1.alfa = self.alfa_att
            self.dx(x)
            self.samplec = self.samplec - 1
            val = self.lp1(x)
            self.while_triggered(val)
            self.internal_state_changed(val, self.triggered, self.dx.x, self.lp1.y)
            return val
        else:
            self.state = 'sustain'
            self.samplec = self.sustl
            return self._sustain(x)

    def _sustain(self, x):
        if self.samplec:
            self.lp1.alfa = self.alfa_sus
            self.dx(x)
            self.samplec = self.samplec - 1
            val = self.lp1(x)
            self.while_triggered(val)
            self.internal_state_changed(val, self.triggered, self.dx.x, self.lp1.y)
            return val
        else:
            self.state = 'release'
            self.samplec = self.rell
            return self._release(x)

    def _release(self, x):
        if self.samplec:
            self.lp1.alfa = self.alfa_rel
            self.dx(x)
            self.samplec = self.samplec - 1
            val = self.lp1(x*(1.*self.samplec/self.rell))
            self.while_triggered(val)
            self.internal_state_changed(val, self.triggered, self.dx.x, self.lp1.y)
            return val
        else:
            self.state = 'quiet'
            self.triggered = False
            self.lp1.y = 0
            self.on_release()
            self.internal_state_changed(0, self.triggered, self.dx.x, self.lp1.y)
            return 0

    def __call__(self, x):
        return self._states[self.state](x)

