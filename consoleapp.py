from PyQt5.QtCore import QThread, pyqtSlot
import remoteconnection
from console import Ui_MainWindow
from PyQt5 import QtWidgets


class ConsoleApp(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(ConsoleApp, self).__init__(parent)
        self.setupUi(self)

        self.mythread = QThread()
        self.run_Button.setDisabled(True)
        self.plainTextEdit.setDisabled(True)
        self.command_lineEdit.setDisabled(True)

        self.connect_Button.clicked.connect(self.connect_server)
        self.password_lineEdit.returnPressed.connect(self.connect_server)
        self.run_Button.clicked.connect(self.sendcommand)
        self.command_lineEdit.returnPressed.connect(self.sendcommand)

    def enable_console(self):
        self.run_Button.setEnabled(True)
        self.plainTextEdit.setEnabled(True)
        self.command_lineEdit.setEnabled(True)
        self.plainTextEdit.clear()

    def connect_server(self):
        remoteconnection.server_hostname = self.ipaddress_lineEdit.text()
        remoteconnection.server_username = self.username_lineEdit.text()
        remoteconnection.server_password = self.password_lineEdit.text()
        ssh_connect = remoteconnection.check_server_connection()
        if not ssh_connect:
            self.enable_console()
        else:
            self.plainTextEdit.insertPlainText(str(ssh_connect))

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
        command = self.command_lineEdit.text()
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
