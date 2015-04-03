import os
from subprocess import Popen, PIPE
from time import sleep
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK, read
from io import BytesIO

import socket

try:
    import androidhelper as android
except ImportError:
    try:
        import android
    except ImportError:
        android = None


class ProcessCommunicator(object):
    def __init__(self,command):
        self.command = command

    def start(self,command = None):
        if command is None:
            command = self.command
        if command is None:
            raise ValueError('command cann\'t be a None value')
        self.p = Popen([command, ], stdin = PIPE, stdout = PIPE, stderr = PIPE, shell = False)
        # set the O_NONBLOCK flag of p.stdout file descriptor:
        flags = fcntl(self.p.stdout, F_GETFL) # get current p.stdout flags
        fcntl(self.p.stdout, F_SETFL, flags | O_NONBLOCK)

    def communicate(self,input=None):
        buffer = BytesIO()
        if input is not None:
            self.p.stdin.write(input)
        while True:
            try:
                buffer.write(read(self.p.stdout.fileno(),1024))
            except OSError:
                return buffer.getvalue()


class Client(object):

    def __init__(self,host,port,command):
        self.sock = socket.socket()
        self.sock.connect((host,port))

        self.sock.send(command+'\n')

class Server(object):
    def __init__(self,host,port,command):
        self.sock = socket.socket()
        self.sock.bind(('127.0.0.1',int(port)))
        self.sock.listen()

    def parse_initial_data(self,data):
        return data.split('\n')[0]

    def get_command(self,conn):
        data = conn.read(4096)
        length,dummy,buffer = data.partition('\n')
        length = int(length)

    def run(self):
        while True:
            conn,info = self.sock.accept()
            initial_data = conn.read(1024)
            command = self.parse_initial_data(initial_data)
            process_communicator = ProcessCommunicator(command)
            try:
                while True:
                    input_data = self.get_command(conn)
                    output = process_communicator.communicate(input=input_data)
                    conn.write(output)


def main():
    if android is None:
        host,port,command,client = os.sys.argv[:4]
        client = client.lower() == "true":
    else:
        pass



