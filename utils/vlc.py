import sys
import subprocess
import atexit
import time

import socket
import telnetlib

class VLC(object):
    def __init__(self, host='localhost', port='4212'):
        self.tn = telnetlib.Telnet(host,port)

    def _do(self, cmd):
        self.tn.write(cmd+'\n')
        self.tn.read_very_eager()
        #print self.tn.read_very_eager()

    def addfile(self, filename):
        self._do('add ' + filename)
        self._do('stop')

    def volume(self, vol):
    # 0 - 256
        self._do('volume ' + str(vol))

    def play(self, idx=0):
        if idx:
            self._do('goto ' + str(idx))
        self._do('play')

    def stop(self):
        self._do('stop')

    def clear(self):
        self._do('clear')

    def quit(self):
        self._do('quit')

    def repeat(self, what):
        """Si True, reproducir indefinidamente el archivo actual """
        if what:
            self._do('repeat 1')
        else:
            self._do('repeat 0')

    def loop(self, what):
        """Si True, reproducir indefinidamente la lista de archivos """
        if what:
            self._do('loop 1')
        else:
            self._do('loop 0')

class VLCProcess(VLC):
    __port = 4212
    def __init__(self, port=None, gui=False):

        if port is None:
            port = VLCProcess.__port
            VLCProcess.__port = VLCProcess.__port + 1

        args = ['/usr/bin/vlc', '-I', 'rc', '--rc-host', 'localhost:'+str(port)]
        if gui:
            args.append('--extraintf')
            args.append('qt')

        self.child = subprocess.Popen(args, bufsize=0, universal_newlines=True)
        for x in range(10):
            time.sleep(.5)
            try:
                self.tn = telnetlib.Telnet('localhost', port)
                break
            except socket.error:
                continue

        atexit.register(self.child.kill)
