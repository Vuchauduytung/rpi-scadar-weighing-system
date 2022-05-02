import socket
import serial
import time
import multiprocessing as mp
from multiprocessing import Process, Pipe
from data_convert import *


class TCP_IP:
    def __init__(self, HOST="", PORT=12000):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))
        self.socket.listen(2)
        ctx = mp.get_context('spawn')
        self.queue = ctx.Queue()
        print("Waiting for client ...")
        mp.set_start_method('spawn')
        Process(target=TCP_IP.wait_and_connect_client,
                args=(self.socket, self.queue)).start()

    @classmethod
    def wait_and_connect_client(cls, socket, queue):
        while True:
            try:
                client, addr = socket.accept()
                print('Connected by', addr)
                Process(target=TCP_IP.send_data, args=(
                        client, addr, queue)).start()
            except Exception as err:
                print("Socket closed")
                print(err)
                break

    @classmethod
    def send_data(cls, client, addr, queue):
        while True:
            try:
                if not queue.empty():
                    data = queue.get()
                    data_bytes = json.dumps(data).encode('utf-8')
                    client.sendall(data_bytes)
            except (BrokenPipeError, ConnectionResetError) as err:
                print("Client {addr} disconnect"
                      .format(addr=addr))
                break

    def update_queue(self, data):
        while not self.queue.empty():
            self.queue.get()
        self.queue.put(data)


class UART:
    def __init__(self,
                 port='/dev/ttyAMA0',
                 baudrate=9600,
                 parity=serial.PARITY_NONE,
                 stopbits=serial.STOPBITS_ONE,
                 bytesize=serial.EIGHTBITS,
                 timeout=1):
        self.serial = serial.Serial(
            port=port,
            baudrate=baudrate,
            parity=parity,
            stopbits=stopbits,
            bytesize=bytesize,
            timeout=timeout)
        ctx = mp.get_context('spawn')
        self.queue = ctx.Queue()
        self.serial.close()
        self.serial.open()

    def send_data(self, data):
        try:
            serial = self.serial
            data_bytes = json.dumps(data).encode('utf-8')
            serial.write(data_bytes)
            serial.flush()
            # print("send data successfully")
            # print(data)
        except Exception as err:
            print(err)
            serial.reset_output_buffer()
            serial.close()
            serial.__del__()

