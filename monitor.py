import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.Qwt5 as Qwt
import Queue

from com_monitor import ComMonitorThread
from eblib.serialutils import full_port_name, enumerate_serial_ports
from eblib.utils import get_all_from_queue, get_item_from_queue
from livedatafeed import LiveDataFeed

DEFAULT_PORT = '/dev/ttyACM0'

class DataMonitor(QMainWindow):
    def __init__(self, parent=None):
        super(DataMonitor, self).__init__(parent)
       
        self.timer = QTimer() 
        self.com_monitor = None    
        
        self.main_frame = QWidget()
        main_layout = QVBoxLayout()
        self.main_frame.setLayout(main_layout)
        self.setCentralWidget(self.main_frame)

        
        hl = QHBoxLayout()
        sb = QPushButton('Iniciar')
        sb.setCheckable(True)
        hl.addWidget(sb)

        self.connect(sb, SIGNAL('toggled(bool)'), self.onoff)

        self.portname = QLineEdit(DEFAULT_PORT)
        hl.addWidget(self.portname)

        main_layout.addLayout(hl)

        self.modules = QListWidget()
        
        main_layout.addWidget(self.modules)
    

    def onoff(self, checked):
        print checked
        if checked:
            self.on_start()
        else:
            self.on_stop()


    def on_stop(self):
        """ Stop the monitor
        """
        if self.com_monitor is not None:
            self.com_monitor.join(0.01)
            self.com_monitor = None

        self.monitor_active = False
        self.timer.stop()
        
    
    def on_start(self):
        """ Start the monitor: com_monitor thread and the update
            timer
        """
        if self.com_monitor is not None or self.portname.text() == '':
            return
        
        self.data_q = Queue.Queue()
        self.error_q = Queue.Queue()
        self.com_monitor = ComMonitorThread(
            self.data_q,
            self.error_q,
            full_port_name(str(self.portname.text())),
            115200)
        self.com_monitor.start()
        
        com_error = get_item_from_queue(self.error_q)
        if com_error is not None:
            QMessageBox.critical(self, 'ComMonitorThread error',
                com_error)
            self.com_monitor = None

        self.monitor_active = True
        
        self.timer = QTimer()
        self.connect(self.timer, SIGNAL('timeout()'), self.on_timer)
        
        update_freq = 10
        if update_freq > 0:
            self.timer.start(1000.0 / update_freq)
        


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = DataMonitor()
    form.show()
    app.exec_()
