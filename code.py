import board
import time
import busio
import lcd
import i2c_pcf8574_interface
import digitalio
import usb_hid
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from analogio import AnalogIn

# Set up Consumer Control - Control Codes can be found here: https://docs.circuitpython.org/projects/hid/en/latest/_modules/adafruit_hid/consumer_control_code.html#ConsumerControlCode
cc = ConsumerControl(usb_hid.devices)

# Set up a keyboard device. - Keycode can be found here: https://docs.circuitpython.org/projects/hid/en/latest/_modules/adafruit_hid/keycode.html#Keycode
keyboard = Keyboard(usb_hid.devices)

# Set up keyboard to write strings from macro
write_text = KeyboardLayoutUS(keyboard)


i2c = busio.I2C(scl=board.GP1, sda=board.GP0)
address = 0x3f


i2c = i2c_pcf8574_interface.I2CPCF8574Interface(i2c, address)

display = lcd.LCD(i2c, num_rows=2, num_cols=16)

display.set_backlight(True)

display.set_display_enabled(True)

display.clear()
display.set_cursor_pos(0,0)
display.print("Starting.")
time.sleep(1)
display.print(".")
time.sleep(1)
display.print(".")
time.sleep(1)

#---------------------------------------------------------------
# Run the main loop to generate a counting display.
prev = digitalio.DigitalInOut(board.GP13)
prev.switch_to_input(pull=digitalio.Pull.DOWN)

play = digitalio.DigitalInOut(board.GP14)
play.switch_to_input(pull=digitalio.Pull.DOWN)

next = digitalio.DigitalInOut(board.GP15)
next.switch_to_input(pull=digitalio.Pull.DOWN)

btn4 = digitalio.DigitalInOut(board.GP12)
btn4.switch_to_input(pull=digitalio.Pull.DOWN)
# Potentiometer related stuff

READ_TIME = 0.001

def map_function(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

potentiometer = AnalogIn(board.GP26)

# intialize the read time
last_read = time.monotonic()

# decrease volume all the way down
# this allows the volume to be set by the current value of the pot
for i in range(32):
    cc.send(ConsumerControlCode.VOLUME_DECREMENT)

# initalize volume and last position
current_volume = 0
last_position = 0

# Custom characters
volume_char = (0x02,0x09,0x05,0x15,0x15,0x05,0x09,0x02)
display.create_char(0,volume_char)

def getVolume():
    display.clear()
    display.set_cursor_pos(1,13)
    display.write(0)
    display.print(str(current_volume))
    display.home()
    
while True:

    # Keycode class defines USB HID keycodes to send using Keyboard.  
#    if btn1.value:
#        display.clear()
#        display.print("Open VLC")
#        keyboard.send(Keycode.GUI)
#        time.sleep(0.4)
#
    
    time.sleep(0.1)
    
    #Volume Control
    if time.monotonic() - last_read > READ_TIME:
        position = int(map_function(potentiometer.value, 200, 65520, 0, 100))

        if abs(position - last_position) > 1:

            last_position = position

            if current_volume < position:
                while current_volume < position:
                    # Raise volume.
                    print("Volume Up!")
                    cc.send(ConsumerControlCode.VOLUME_INCREMENT)
                    current_volume += 2
                    getVolume()
        
            elif current_volume > position:
                while current_volume > position:
                    # Lower volume.
                    print("Volume Down!")
                    cc.send(ConsumerControlCode.VOLUME_DECREMENT)
                    current_volume -= 2
                    getVolume()
                    
        # update last_read to current time
        last_read = time.monotonic()
    # handle time.monotonic() overflow
    if time.monotonic() < last_read:
        last_read = time.monotonic
        
    if play.value:
        cc.send(ConsumerControlCode.PLAY_PAUSE)
        display.clear()
        getVolume()
        display.print("Play/Pause")
        time.sleep(0.5)

    if next.value:
        cc.send(ConsumerControlCode.SCAN_NEXT_TRACK)
        display.clear()
        getVolume()
        display.print("Next")
        time.sleep(0.5)

    if prev.value:
        cc.send(ConsumerControlCode.SCAN_PREVIOUS_TRACK)
        display.clear()
        getVolume()
        display.print("Prev")
        time.sleep(0.5)
      
    if btn4.value:
        display.clear()
        getVolume()
        display.print("Open Discord")
        keyboard.send(Keycode.GUI, Keycode.FOUR)
        time.sleep(0.4)