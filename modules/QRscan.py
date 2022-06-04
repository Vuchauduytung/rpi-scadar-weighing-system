from pyzbar import pyzbar
import cv2
import time
import multiprocessing as mp
from multiprocessing import Process, Pipe


class QRscanner:
    def __init__(self, cameraId: int = 0):
        ctx = mp.get_context('spawn')
        self.barcodeData_queue = ctx.Queue()
        try:
            mp.set_start_method('spawn')
        except RuntimeError:
            pass
        p = Process(target=QRscanner.scan_for_QR,
                    args=(self.barcodeData_queue,))
        p.start()

    # def __del__(self):
    #     pass

    @staticmethod
    def scan_for_QR(barcodeData_queue):
        capture = cv2.VideoCapture(0)
        while True:
            ret, frame = capture.read()
            frame = cv2.flip(frame, 1)
            barcodes = pyzbar.decode(frame)
            for barcode in barcodes:
                barcodeData = barcode.data.decode("utf-8")
                barcodeData_queue.put(barcodeData)
                print(f"\033[34mBarcode : \033[0m{barcodeData}")

    def get_QR_code(self):
        return self.barcodeData_queue.get()

    def isQueueEmpty(self):
        return self.barcodeData_queue.empty()

        