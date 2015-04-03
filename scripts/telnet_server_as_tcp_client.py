#!/usr/bin/env python
import os
from subprocess import Popen, PIPE
from time import sleep
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK, read
from io import BytesIO
import time

import socket
from socket import error as socket_error

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
        time.sleep(5)
        while True:
            try:
                chank = read(self.p.stdout.fileno(),1024)
                print "data chank [%s]" % chank
                buffer.write(chank)
            except OSError:
                break
        return buffer.getvalue()


class NetworkCommuticator(object):
    def __init__(self):
        pass

    def convert_data_to_uint(self,raw_data):
        byte_position_map = (2**0,2**8,2**16,2**24)
        raw_data = raw_data[::-1]
        return sum(map(lambda x:ord(x[1])*byte_position_map[x[0]], enumerate(raw_data)))

    def convert_uint_to_data(self,uint,size=4):
        if uint >= 2**(8*size):
            return chr(0xff)*4
        else:
            hex_data = (("%"+str(int(size*2))+'s') % hex(uint).replace('0x','')).replace(' ','0')
            bytes_hex = map(lambda x: x[0]+x[1], zip(hex_data[::2],hex_data[1::2]))
            return "".join(map(chr,map(lambda x: int(x,16),bytes_hex)))

    def get_uint(self,conn,size=4):
        raw_data = str(conn.recv(size))
        return self.convert_data_to_uint(raw_data) 


class Client(NetworkCommuticator):

    def __init__(self,host,port,command):
        self.host,self.port = host,port
        self.sock = socket.socket()
        self.sock.connect((host,int(port)))

        self.sock.send(command+'\n')

    def send_command(self,conn,command):
        length = len(command)
        conn.send(self.convert_uint_to_data(length))
        conn.send(command)

    def get_result(self,conn):
        result_length = self.get_uint(conn)
        result = conn.recv(result_length)
        return result


class ConsoleClient(Client):

    input_command = lambda self: raw_input("%s:%s$" % (self.host,self.port)).strip()

    def run(self):
        while True:
            command = self.input_command()
            if command == "exit":
                self.sock.close()
                break
            if command != "":
                self.send_command(self.sock, command+'\n')
                output = self.get_result(self.sock)
                print output


class AndroidConsoleClient(ConsoleClient):
    def __init__(self,host,port,command):
        self.host,self.port = host,port
        self.command = command
        self.sock = socket.socket()
        self.sock.bind(('0.0.0.0',int(self.port)))
        self.sock.listen(3)

    def run(self):
        while  True:
            conn,info = self.sock.accept()
            conn.send(self.command+'\n')
            ConsoleClient.run(self)


class Server(NetworkCommuticator):
    def __init__(self,host,port,command):
        self.sock = socket.socket()
        self.sock.bind(('127.0.0.1',int(port)))
        self.sock.listen(3)
        self.command = command

    def parse_initial_data(self,data):
        return data.split('\n')[0]

    def get_command(self,conn):
        length=self.get_uint(conn)
        command = conn.recv(length)
        return command

    def put_result(self,conn,result):
        length = len(result)
        conn.send(self.convert_uint_to_data(length))
        conn.send(result)

    def handle_new_connection(self,conn):
        initial_data = conn.recv(1024)
        command = self.parse_initial_data(initial_data)
        print "asked command = %s" % command
        if self.command != command:
            conn.close()
            return
        print "Starting process_communicator"
        process_communicator = ProcessCommunicator(command)
        process_communicator.start()
        print "process_communicator was started"
        try:
            while True:
                print "Getting command..."
                input_data = self.get_command(conn)
                print "got data [%s]" % input_data
                output = process_communicator.communicate(input=input_data)
                print "result [%s]" % output
                self.put_result(conn, output)
        except socket_error:
            conn.close()

    def run(self):
        while True:
            conn,info = self.sock.accept()
            print "New connection accepted!"
            self.handle_new_connection(conn)
            

class AndroidServer(Server):
    """
    import androidhelper
    droid = androidhelper.Android()
    response = droid.dialogGetInput("Hello", "What is your name?")
    print response
    message = 'Hello, %s!' % response.result
    droid.makeToast(message)

    """

    def __init__(self):
        droid = android.Android()
        
        response = droid.dialogGetInput("IP",'what\'s IP to connect ?','176.37.148.81')
        host = response.result

        response = droid.dialogGetInput("PORT",'what\'s port to connect ?','5555')
        port = response.result

        response = droid.dialogGetInput("COMMAND",'what\'s command to interact with ?','sh')
        command = response.result
        self.command = command

        self.host,self.port = host,port
        self.sock = socket.socket()
        self.sock.connect((host,int(port)))

    def run(self):
        self.handle_new_connection(self.sock)


def main():
    if android is None:
        script,host,port,command,client,as_android_client = os.sys.argv[:6]
        print "input args: [host = %s, port = %s, command = %s, client = %s, as_android_client = %s ] " % (host,port,command,client,as_android_client)
        client = client.lower() == "true"
        as_android_client = as_android_client.lower() == 'true'

        if as_android_client:
            print "Starting client as a server for android client"
            console_client = AndroidConsoleClient(host, port, command)
            console_client.run()

        if client :
            print "Starting client"
            console_client = ConsoleClient(host, port, command)
            console_client.run()
        else:
            print "Starting server"
            server = Server(host, port, command)
            server.run()
    else:
        android_server = AndroidServer()
        android_server.run()

if __name__ == "__main__":
    main()
