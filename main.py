import modules
from modules.raspIO import *
from modules.data_convert import *
from modules.connection import *

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

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
#         tcp.update_queue(data)
#         data["mass"] = str(int(data.get("mass")) + 1)
#         time.sleep(0.01)

# def test_UART():
#     uart = UART()
#     data = json2dict("/home/pi/Luan-van/test/demo_data.json")
#     while True:
#         uart.update_queue(data)
#         data["mass"] = str(int(data.get("mass")) + 1)
#         time.sleep(0.2)

def main():
    sensor1 = DistanceSensor(trigger_pin=18, echo_pin=23, reference_distance=10)
    sensor2 = DistanceSensor(trigger_pin=24, echo_pin=25, reference_distance=10)
    hx = HX711(referenceUnit=-230, 
                DT=4, 
                SCK=17, 
                take_zero_point_pin=27)
    oled = OLED()
    tcp = TCP_IP()
    uart = UART()
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
            data = {
                "mass": str(loadcell_val),
                "sensor_1": sensor1_display,
                "sensor_2": sensor2_display
            }
            if switch:
                tcp.update_queue(data)
            else:
                uart.send_data(data)
            switch = not switch
            # time.sleep(0.1)
    except (KeyboardInterrupt, SystemExit):
        print("Cleaning...")
        GPIO.cleanup()
        oled.clear_display()
        sys.exit(0)        
            

if __name__ == "__main__":
    # test_distanSensor()
    # test_HX711()
    # test_OLED()
    # test_TCP_IP()
    # test_UART()
    main()