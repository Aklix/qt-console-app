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
        # self.run_Button.setAutoDefault(False)
        # self.run_Button.setDefault(False)
        self.mythread = QThread()
        self.myworker = remoteconnection.RpcQworker()
        self.run_Button.clicked.connect(self.sendcommand)
        self.lineEdit.returnPressed.connect(self.sendcommand)
        # self.check_clicked_button()

    # @pyqtSlot()
    # def check_clicked_button(self):
    #     self.run_Button.clicked.connect(self.sendcommand)



    def worker_thread(self, thread, worker, cmd):
        worker.set_command(cmd)

        worker.finished.connect(thread.quit)
        thread.start()
        worker.moveToThread(thread)
        thread.started.connect(worker.do_execute)
        worker.finished.connect(worker.disconnect)

        return worker.command_out

    # @pyqtSlot()
    def sendcommand(self):
        command = self.lineEdit.text()
        ssh_thread = self.worker_thread(self.mythread, self.myworker, command)
        ssh_thread.connect(self.setoutputext)
        # self.myworker.set_command(command)
        # self.myworker.command_out.connect(self.setoutputext)
        # self.myworker.start()
        ssh_out = remoteconnection.server_execute_command(command)
        print(ssh_out)
        print('sad')



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
