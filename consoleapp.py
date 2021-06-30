import time

from PyQt5.QtCore import QThread, pyqtSlot
from PyQt5 import QtCore
import remoteconnection
from console import Ui_MainWindow
from PyQt5 import QtWidgets


class ConsoleApp(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(ConsoleApp, self).__init__(parent)
        self.setupUi(self)

        self.mythread = QThread()
        self.run_Button.clicked.connect(self.sendcommand)
        self.lineEdit.returnPressed.connect(self.sendcommand)




    def worker_thread(self, thread, worker, cmd):
        worker.set_command(cmd)
        worker.moveToThread(thread)
        worker.finished.connect(thread.quit)
        thread.started.connect(worker.do_execute)
        # worker.finished.connect(worker.disconnect)
        thread.start()
        return worker.command_out

    @pyqtSlot()
    def sendcommand(self):
        self.run_worker = remoteconnection.RpcQworker()
        command = self.lineEdit.text()
        ssh_thread = self.worker_thread(self.mythread, self.run_worker, command)
        ssh_thread.connect(self.setoutputext)




    @pyqtSlot(dict)
    def setoutputext(self, ssh_out):
        if ssh_out.get('out'):
            self.plainTextEdit.insertPlainText(str(ssh_out.get('out').splitlines()) + '\n')
        if ssh_out.get('err'):
            self.plainTextEdit.insertPlainText(str(ssh_out.get('err').splitlines()) + '\n')



if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    ui = ConsoleApp()
    ui.show()
    app.exec_()
