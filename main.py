import modules
from modules.raspIO import *
from modules.data_convert import *
from modules.connection import *
from modules.QRscan import *
import time
import os
import gc
import sys
import signal
from subprocess import call
from multiprocessing import *
from functools import partial
from state_machine import *



# #GPIO Mode (BOARD / BCM)
# GPIO.setmode(GPIO.BCM)
# path = os.path.dirname(os.path.abspath(__file__))
# audio_path = os.path.abspath(os.path.join(path, "audio"))
# backward_wav_path = os.path.abspath(os.path.join(audio_path, "backward.wav"))
# forward_wav_path = os.path.abspath(os.path.join(audio_path, "forward.wav"))
# pass_wav_path = os.path.abspath(os.path.join(audio_path, "pass.wav"))
# QR_scan_wav_path = os.path.abspath(os.path.join(audio_path, "QR_scan.wav"))

# def test_distanSensor():
#     sensor1 = DistanceSensor(trigger_pin=18, echo_pin=23)
#     while True:
#         print(sensor1.distance())
#         time.sleep(1)

# def test_HX711():
#     hx = HX711(referenceUnit=-230, 
#             DT=4, 
#             SCK=17, 
#             take_zero_point_pin=27)
#     while True:
#         print(hx.read_value())
#         time.sleep(1)

# def test_OLED():
#     oled = OLED()
#     while True:
#         oled.print_text("Hello")

# def test_TCP_IP():
#     tcp = TCP_IP()
#     data = json2dict("/home/pi/Luan-van/test/demo_data.json")
#     while True:
#         tcp.send_data(data)
#         data["mass"] = str(int(data.get("mass")) + 1)
#         time.sleep(0.01)

# def test_UART():
#     uart = UART()
#     data = json2dict("/home/pi/Luan-van/test/demo_data.json")
#     while True:
#         uart.update_queue(data)
#         data["mass"] = str(int(data.get("mass")) + 1)
#         time.sleep(0.2)

# def test_QRscanner():
#     print("hello ...")
#     qr_scan = QRscanner()
#     time.sleep(1)
#     print("QR code: {result}"\
#         .format(result=qr_scan.get_QR_code()))

def test():
    signal.setitimer(signal.ITIMER_REAL, 10, 4)
    sensor1 = DistanceSensor(trigger_pin=18, echo_pin=23, reference_distance=10)
    sensor2 = DistanceSensor(trigger_pin=24, echo_pin=25, reference_distance=10)
    hx = HX711(referenceUnit=-230, 
                DT=4, 
                SCK=17)
                # take_zero_point_pin=27,
                # zero_set_blink_led=12)
    qr_scan = QRscanner()
    oled = OLED()
    tcp = TCP_IP()
    uart = UART()

    def handler(signum, frame):
        print('Signal handler called with signal', signum)
        # try:
        #     if sensor1_status or sensor2_status:
        #         if sensor1_status and sensor2_status:
        #             if not QR_status:
        #                 call(["omxplayer", QR_scan_wav_path], stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
        #             else:
        #                 call(["omxplayer", pass_wav_path], stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
        #         elif sensor1_status:
        #             call(["omxplayer", forward_wav_path], stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
        #         elif sensor2_status:
        #             call(["omxplayer", backward_wav_path], stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
        # except:
        #     pass
        # # finally:
        # #     sys.exit()
        
    signal.signal(signal.SIGALRM, handler)
    
    try:
        switch = False
        while True:
            sensor1_status = sensor1.get_status()
            sensor2_status = sensor2.get_status()
            if sensor1_status:
                sensor1_display = "ON"
            else:
                sensor1_display = "OFF"
            if sensor2_status:
                sensor2_display = "ON"
            else:
                sensor2_display = "OFF"
            loadcell_val = round(hx.read_value())
            oled_text = "Mass: {value}\nSensor 1: {S1}\nSensor 2: {S2}"\
                .format(value=loadcell_val,
                        S1=sensor1_display,
                        S2=sensor2_display)
            oled.print_text(oled_text)
            if not qr_scan.isQueueEmpty():
                QR_code = qr_scan.get_QR_code()
                data = QRData_to_dict(QR_code)
                QR_status = True
            else:
                data = {}
                QR_status = False

            data.update({
                "mass": str(loadcell_val),
                "sensor_1": sensor1_status,
                "sensor_2": sensor2_status
            })
            if switch:
                tcp.send_data(data)
            else:
                uart.send_data(data)
            switch = not switch
            # time.sleep(0.1)
    except (KeyboardInterrupt, SystemExit):
        print("Cleaning...")
        GPIO.cleanup()
        oled.clear_display()
        gc.collect()
        sys.exit(0)  

def main():
    try:
        setup()
        while True:
            loop()
    except (KeyboardInterrupt, SystemExit):
        print("Cleaning...")
        GPIO.cleanup()
        oled.clear_display()
        gc.collect()
        sys.exit(0)  

def setup():
    # Global variable
    global sensor1
    global sensor2
    global scale1
    global qr_scan
    global oled
    global tcp
    global uart
    global reset
    global delta_w
    global min_w
    global zeropoint_led
    global zeropoint_button
    global state
    # GPIO Mode (BOARD / BCM)
    GPIO.setmode(GPIO.BCM)
    # Path
    path = os.path.dirname(os.path.abspath(__file__))
    audio_path = os.path.abspath(os.path.join(path, "audio"))
    backward_wav_path = os.path.abspath(os.path.join(audio_path, "backward.wav"))
    forward_wav_path = os.path.abspath(os.path.join(audio_path, "forward.wav"))
    pass_wav_path = os.path.abspath(os.path.join(audio_path, "pass.wav"))
    QR_scan_wav_path = os.path.abspath(os.path.join(audio_path, "QR_scan.wav"))
    # Timer
    # signal.setitimer(signal.ITIMER_REAL, 10, 4)
    # Distance sensor
    sensor1 = DistanceSensor(trigger_pin=18, echo_pin=23, reference_distance=10)
    sensor2 = DistanceSensor(trigger_pin=24, echo_pin=25, reference_distance=10)
    # Scale
    scale1 = HX711(referenceUnit=-230, 
                   DT=4, 
                   SCK=17)
                    # take_zero_point_pin=27,
                    # zero_set_blink_led=12)
    # QR scanner
    qr_scan = QRscanner()
    # Screen display
    oled = OLED()
    # TCP transfer
    tcp = TCP_IP()
    # UART transfer
    uart = UART()
    # Initial state
    reset = 0
    delta_w = 0
    min_w = read_scale(scale_1=scale1)
    # Button set zero point
    zeropoint_led = 12
    zeropoint_button = 27
    # Interrupt
    setup_interrupt_for_take_zero_point()
    # State
    state = STATE.S0


def loop():
    global state
    global min_w
    global qr_scan
    global oled
    ss1 = sensor1.get_status()
    ss2 = sensor2.get_status()
    w = read_scale(scale_1=scale1)
    QR = not qr_scan.isQueueEmpty()
    if reset:
        min_w = w
    else:
        if w < min_w:
            min_w = w
    delta_w = w - min_w
    state = next_state(state=state,
                       ss1=ss1,
                       ss2=ss2,
                       delta_w=delta_w,
                       QR=QR)
    oled_text = "Mass: {value}\nSensor 1: {S1}\nSensor 2: {S2}\nState: {state}"\
                .format(value=w,
                        S1=ss1,
                        S2=ss2,
                        state=state.name)
    oled.print_text(oled_text)

    


def read_scale(scale_1: HX711, scale_2: HX711 = None, scale_3: HX711 = None, scale_4: HX711 = None):
    w = scale_1.readCount()
    if scale_2 is not None:
        w = w + scale_2.readCount()
    if scale_3 is not None:
        w = w + scale_3.readCount()
    if scale_4 is not None:
        w = w + scale_4.readCount()
    return w


def setup_interrupt_for_take_zero_point():
    global zeropoint_button
    global zeropoint_led
    GPIO.setup(zeropoint_led, GPIO.OUT)
    GPIO.setup(zeropoint_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(zeropoint_button, 
                          GPIO.FALLING,
                          callback=set_zero_point, 
                          bouncetime=500)

def set_zero_point(channel):
    global zeropoint_led
    GPIO.output(zeropoint_led, 1)
    time.sleep(0.1)
    GPIO.output(zeropoint_led, 0)
    scale1.zero_point = scale1.readCount()
    print("Set new zero point")


def QRData_to_dict(QR_code):
    return {"test": "ok"}     
    
# def status_process(sensor1_status: bool, sensor2_status: bool, QR_status: bool):
#     return lambda signum, frame : handler(signum, 
#                                           frame,
#                                           sensor1_status,
#                                           sensor2_status,
#                                           QR_status)

if __name__ == "__main__":
    # test_distanSensor()
    # test_HX711()
    # test_OLED()
    # test_TCP_IP()
    # test_UART()
    # test_QRscanner()
    main()