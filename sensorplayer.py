from utils.adsr import adsr
from utils.signal import Signal
from utils.vlc import VLCProcess

class Playlist(list):
    def __init__(self, iterable=None):
        if iterable is not None:
            super(Playlist, self).__init__(iterable)
        else:
            super(Playlist, self).__init__()

        self.changed = Signal()

        for n in '''__setitem__ __delitem__  append extend insert pop remove reverse sort'''.split():
            def wrapper(nom):
                orig = getattr(list, nom)
                def inner(*args):
                    s = self
                    s.changed()
                    return orig(s, *args)
                return inner
            setattr(self, n, wrapper(n))

