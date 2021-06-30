from io import StringIO
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import paramiko

server_hostname = "127.0.0.1" # change this
server_username = "usr"  # change this
server_password = "pwd"  # change this
port = 22
timeout = 4
ssh_key = ""


def server_ssh_connect(ssh_key=None):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if ssh_key is not None:
        ssh_key = paramiko.RSAKey.from_private_key(StringIO(ssh_key))
    ssh.connect(hostname=server_hostname, username=server_username, password=server_password, port=port, pkey=ssh_key)
    return ssh


class RpcQworker(QtCore.QObject):
    command_out = pyqtSignal(dict)
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.command = ""

    @pyqtSlot(str, name='setting command')
    def set_command(self, cmd):
        self.command = cmd

    @pyqtSlot(name='execute')
    def do_execute(self):
        sudo = False
        if self.command.startswith('sudo'):
            sudo = True
        ssh_client = self.server_execute_command(self.command, sudo)
        self.command_out.emit(ssh_client)
        self.finished.emit()


    def server_execute_command(self, command, sudo=False):
        client = server_ssh_connect()
        if sudo:
            command = 'sudo -S -- ' + command + '\n'
        stdin, stdout, stderr = client.exec_command(command)
        if sudo:
            stdin.write(server_password + '\n')
            stdin.flush()
        exit_status = stdout.channel.recv_exit_status()  # Blocking call
        stdout.flush()
        stderr.flush()
        client.close()
        return {'out': stdout.read().decode("utf8"),
                               'err': stderr.read().decode("utf8"),
                               'retval': exit_status}

def server_execute_command(command, sudo=False):
    client = server_ssh_connect()
    session = client.get_transport().open_session()
    session.set_combine_stderr(True)
    session.get_pty()
    if sudo:
        command = 'sudo -S -- ' + command + '\n'
    session.exec_command(command)
    stdin = session.makefile_stdin('wb', -1)
    stdout = session.makefile('rb', -1)
    # stderr = session.makefile_stderr('rb', -1)
    if sudo:
        stdin.write(server_password + '\n')
        stdin.flush()
    # stdin.channel.shutdown_write()
    exit_status = session.recv_exit_status()  # wait for exec_command to finish
    session.close()
    return {'out': stdout.read().decode("utf8"), 'retval': exit_status}
