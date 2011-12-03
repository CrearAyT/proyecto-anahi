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
    def __init__(self, gui=True):

        self._playlist = Playlist()
        self._playlist.changed.connect(self.__update_playlist)

        self._use_gui = gui
        self._vlc = None
        self._repeat = False
        self._loop = False

        self.adsr = adsr()

        self._trigger_light = True
        self._invert_control = False

        # Volumen predeterminado, 0-256 (256-512 -> 100%-200%)
        self._default_volume = 100
        self.adsr.while_triggered.connect(self.control_cb)

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
            self._vlc = VLCProcess(gui=self._use_gui)
            self.__update_playlist()
            self._vlc.repeat(self._repeat)
            self._vlc.loop(self._loop)
        self._vlc.play()

    def stop(self):
        if self._vlc is not None:
            self._vlc.stop()

    def control_cb(self, x):
        if self._vlc is None:
            return

        if self._invert_control:
            x = 1024 - x

        self._vlc.volume(x/4)

    def release_cb(self):
        if self._vlc is None:
            return
        self._vlc.volume(self._default_volume)

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

    @property
    def trigger_on_light(self):
        """Si True, dispararse al iluminar el sensor. Si False al oscurecerlo"""
        return self._triggerlight

    @trigger_on_light.setter
    def trigger_on_light(self, what):
        if what:
            self._trigger_light = True
            self.adsr.slope_sign = 1
        else:
            self._trigger_light = False
            self.adsr.slope_sign = -1

    @property
    def invert_control(self):
        """Si True, mas luz menos volumen. Si False mas luz mas volumen"""
        return self._invert_control

    @invert_control.setter
    def invert_control(self, what):
        if what:
            self._invert_control = True
        else:
            self._invert_control = False

    @property
    def default_volume(self):
        return self._default_volume

    @default_volume.setter
    def default_volume(self, volume):
        self._default_volume = volume
        if self._vlc is None:
            return
        self._vlc.volume(volume)

if __name__ == '__main__':
    from time import sleep

    p = SensorPlayer()
    p.start()
    p._playlist.append('/home/pardo/musica/Eric_Clapton-Bad_Love.mp3')
    p._playlist.append('/home/pardo/musica/Manu Chao Amadou Et Mariam - Senegal Fast Food.ogg')

    p.start()

    while True:
        sleep(1)
