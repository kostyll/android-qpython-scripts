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


def main():
    if android is None:
        host,port = os.sys.argv[:2]
    else:
        pass

