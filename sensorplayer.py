# -*- coding: utf-8 -*-

from utils.adsr import adsr
from utils.misc import Signal
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
                    ret = orig(s, *args)
                    s.changed()
                    return ret
                return inner
            setattr(self, n, wrapper(n))


class SensorPlayer(object):
    def __init__(self):

        self._playlist = Playlist()
        self._playlist.changed.connect(self.__update_playlist)

        self._vlc = None
        self._repeat = False
        self._loop = False

        self.adsr = adsr()



    @property
    def playlist(self):
        return self._playlist

    def __update_playlist(self):
        if self._vlc is None:
            return

        self._vlc.clear()
        for f in self._playlist:
            self._vlc.addfile(f)

    def start(self):
        if self._vlc is None:
            self._vlc = VLCProcess(gui=True)
            self.__update_playlist()
        self._vlc.play()

    def stop(self):
        if self._vlc is not None:
            self._vlc.stop()

    @property
    def repeat(self):
        """Si True, reproducir indefinidamente el archivo actual"""
        return self._repeat

    @repeat.setter
    def repeat(self, what):
        if what:
            self._repeat = True
        else:
            self._repeat = False

        if self._vlc:
            self._vlc.repeat(what)

    @property
    def loop(self):
        """Si True, reproducir indefinidamente la lista de archivos"""
        return self._loop

    @loop.setter
    def loop(self, what):
        if what:
            self._loop = True
        else:
            self._loop = False

        if self._vlc:
            self._vlc.loop(what)


if __name__ == '__main__':
    from time import sleep

    p = SensorPlayer()
    p.start()
    p._playlist.append('/home/pardo/musica/Eric_Clapton-Bad_Love.mp3')
    p._playlist.append('/home/pardo/musica/Manu Chao Amadou Et Mariam - Senegal Fast Food.ogg')

    p.start()

    while True:
        sleep(1)
