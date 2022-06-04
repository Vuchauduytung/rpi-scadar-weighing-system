import time
import sys

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
import RPi.GPIO as GPIO

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess


class DistanceSensor:
    def __init__(self, trigger_pin: int, echo_pin: int, reference_distance: float):
        self.TRIGGER = trigger_pin
        self.ECHO = echo_pin
        self.rf_dist = reference_distance
        GPIO.setup(self.TRIGGER, GPIO.OUT)
        GPIO.setup(self.ECHO, GPIO.IN)

    def distance(self):
        # set Trigger to HIGH
        GPIO.output(self.TRIGGER, True)
        # set Trigger after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(self.TRIGGER, False)
        StartTime = time.time()
        StopTime = time.time()
        # save StartTime
        while GPIO.input(self.ECHO) == 0:
            StartTime = time.time()
        # save time of arrival
        while GPIO.input(self.ECHO) == 1:
            StopTime = time.time()
        # time difference between start and arrival
        TimeElapsed = StopTime - StartTime
        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        dist = (TimeElapsed * 34300) / 2
        return dist

    def get_status(self):
        if self.distance() <= self.rf_dist:
            return True
        else:
            return False


class HX711:
    def __init__(self, referenceUnit: float, DT: int, SCK: int):
        self.DT = DT
        self.SCK = SCK
        self.referenceUnit = referenceUnit
        self.zero_point = 0
        self.pins_setup()

    def pins_setup(self):
        GPIO.setup(self.DT, GPIO.OUT)
        GPIO.setup(self.SCK, GPIO.OUT)

    def readCount(self):
        GPIO.setup(self.DT, GPIO.OUT)
        GPIO.output(self.DT, 1)
        GPIO.output(self.SCK, 0)
        GPIO.setup(self.DT, GPIO.IN)
        i = 0
        Count = 0
        while GPIO.input(self.DT) == 1:
            i = 0
        for i in range(24):
            GPIO.output(self.SCK, 1)
            Count = Count << 1
            GPIO.output(self.SCK, 0)
            # time.sleep(0.001)
            if GPIO.input(self.DT) == 0:
                Count = Count+1
                # print Count
        GPIO.output(self.SCK, 1)
        Count = Count ^ 0x800000
        # time.sleep(0.001)
        GPIO.output(self.SCK, 0)
        return Count

    def update_zero_point(self, value: float):
        self.zero_point = value

    def read_value(self):
        count = self.readCount()
        value = (count-self.zero_point)/self.referenceUnit
        return value


class OLED:
    def __init__(self):
        # Raspberry Pi pin configuration:
        RST = None     # on the PiOLED this pin isnt used
        # Note the following are only used with SPI:
        DC = 23
        SPI_PORT = 0
        SPI_DEVICE = 0
        self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)
        self.screen_init()

    class SCREEN:
        def __init__(self, width, height, padding=-2, font=ImageFont.load_default(), column_pointer=0):
            self.width = width
            self.height = height
            self.image = Image.new('1', (width, height))
            # Get drawing object to draw on image.
            self.draw = ImageDraw.Draw(self.image)
            # Draw a black filled box to clear the image.
            self.draw.rectangle((0, 0, width, height), outline=0, fill=0)
            # Draw some shapes.
            # First define some constants to allow easy resizing of shapes.
            self.padding = padding
            self.top = padding
            self.bottom = height-padding
            # Move left to right keeping track of the current position for drawing shapes.
            self.column_pointer = column_pointer
            self.font = font

        def set_text(self, text):
            # Draw a black filled box to clear the image.
            self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
            # Write two lines of text.
            self.draw.multiline_text(
                (self.column_pointer, self.top), text, spacing=0, font=self.font, fill=255)

    def screen_init(self):
        screen_width = self.disp.width
        screen_height = self.disp.height
        self.screen: SCREEN = self.SCREEN(width=screen_width,
                                        height=screen_height)
        self.disp.begin()                               
        image = self.screen.image
        # display image.
        self.disp.image(image)
        self.disp.display()

    def print_text(self, text):
        self.screen.set_text(text)
        image = self.screen.image
        self.disp.image(image)
        self.disp.display()

    def clear_display(self):
        # Clear display.
        self.disp.clear()
        self.disp.display() 
