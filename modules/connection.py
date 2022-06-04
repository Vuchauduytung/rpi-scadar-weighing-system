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
        print("Socket {addr} is opened."\
            .format(addr=self.socket.getsockname()))
        ctx = mp.get_context('spawn')
        self.client_queue = ctx.Queue()
        self.client_list = []
        print("Waiting for client ...")
        try:
            mp.set_start_method('spawn')
        except RuntimeError:
            pass
        self.p = Process(target=TCP_IP.wait_and_connect_client,
                    args=(self.client_queue, self.socket))
        self.p.start()

    # def __del__(self):
    #     try:
    #         self.socket.close()
    #         self.p.TerminateProcess()
    #         self.p.close() 
    #     except:
    #         pass           

    @staticmethod
    def wait_and_connect_client(client_queue, socket):
        while True:
            try:
                client, addr = socket.accept()
                print('Connected by', addr)
                client_queue.put((client, addr))
                print("Client {addr} is connected."\
                    .format(addr=(client, addr)))
            except Exception as err:
                socket.close()
                print("Socket {port} is closed"\
                    .format(addr=socket.getsockname()))
                print(err)
                raise err
                # break

    def send_data(self, data):
        data_bytes = json.dumps(data).encode('utf-8')
        while not self.client_queue.empty():
            client = self.client_queue.get()
            self.client_list.append(client)
        for client, addr in self.client_list:
            try:
                client.sendall(data_bytes)
            except (BrokenPipeError, ConnectionResetError):
                print("Client {addr} disconnected."\
                    .format(addr=addr))
                self.client_list.remove((client, addr))


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
        try:
            self.serial.open()
        except serial.SerialException:
            pass
        if self.serial.isOpen():
            print("Port \"{port}\" is opened"\
                .format(port=self.serial.name))

    def send_data(self, data):
        try:
            serial = self.serial
            data_bytes = json.dumps(data).encode('utf-8')
            serial.write(data_bytes)
            serial.flush()
            # print("send data successfully")
            # print(data)
        except Exception as err:
            serial.reset_output_buffer()
            serial.close()
            serial.__del__()
            raise err

