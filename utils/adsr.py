from dsp import diff, lpfilt
from misc import Signal


#           atributo adsr : [ nombre ,              min, max,  k,       kdisp,   default]
adsr_params = {  'attackl':['Duracion Ataque',      0,   200,  1./10,   1./100,  150 ],
                 'sustl':['Duracion Sustain',       0,   900,  1,       1./10,   100 ],
                 'rell':['Duracion Release',        0,   300,  1,       1./10,   15  ],
                 'alfa_att':['alfa Ataque',         0,   1000, 1./1000, 1./1000, 300 ],
                 'alfa_sus':['alfa Sustain',        0,   1000, 1./1000, 1./1000, 850 ],
                 'alfa_rel':['alfa Release',        0,   1000, 1./1000, 1./1000, 850 ],
                 'umbral':['umbral deteccion',      0,   400,  1,       1,       100 ],
                 'slope_sign':['pendiente umbral', -1,   1,    1,       1,       1   ]
             }


class adsr(object):
    def __init__(self):
        self.umbral = 100
        self._slope_sign = 1

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

    @property
    def slope_sign(self):
        return self._slope_sign

    @slope_sign.setter
    def slope_sign(self, x):
        if x >= 0:
            self._slope_sign = 1
        else:
            self._slope_sign = -1

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
        if (ok and (d*self._slope_sign)>0):
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

class adsrList(list):
    def __init__(self, iterable=None):
        if iterable is not None:
            super(adsrList, self).__init__(iterable)
        else:
            super(adsrList, self).__init__()

        for attr,v in adsr_params.iteritems():
            nombre, vmin, vmax, k, kdisp, default = v
            self.__dict__[attr] =  k*default

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        if name in adsr_params:
            for adsr in self:
                setattr(adsr, name, value)

    def _update_child(self,child):
        for name in adsr_params:
            setattr(child, name, self.__dict__[name])

    def insert(self, index, item):
        list.insert(self, index, item)
        self._update_child(item)

    def append(self, item):
        list.append(self,item)
        self._update_child(item)

    def extend(self, iterable):
        list.extend(self, iterable)
        for child in iterable:
            self._update_child(child)

