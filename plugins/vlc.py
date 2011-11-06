import telnetlib

class VLC(object):
    def __init__(self, host='localhost', port='4212'):
        self.tn = telnetlib.Telnet(host,port)

    def _do(self, cmd):
        self.tn.write(cmd+'\n')
        print self.tn.read_very_eager()

    def addfile(self, filename):
        self._do('add ' + filename)
        self._do('stop')

    def volume(self, vol):
    # 0 - 256
        self._do('volume ' + str(vol))

    def play(self, idx=0):
        if idx:
            self._do('goto ' + str(idx))
        else:
            self._do('play')

    def stop(self):
        self._do('stop')

    def quit(self):
        self._do('quit')
