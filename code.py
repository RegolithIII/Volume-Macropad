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

# ---------------------------------------------------------------
# Set up Consumer Control - Control Codes can be found here: https://docs.circuitpython.org/projects/hid/en/latest/_modules/adafruit_hid/consumer_control_code.html#ConsumerControlCode
cc = ConsumerControl(usb_hid.devices)

# Set up a keyboard device. - Keycode can be found here: https://docs.circuitpython.org/projects/hid/en/latest/_modules/adafruit_hid/keycode.html#Keycode
keyboard = Keyboard(usb_hid.devices)

# Set up keyboard to write strings from macro
write_text = KeyboardLayoutUS(keyboard)

# ---------------------------------------------------------------
# LCD declarations
i2c = busio.I2C(scl=board.GP1, sda=board.GP0)

address = 0x3f # Put the address given by ic2_scan here

i2c = i2c_pcf8574_interface.I2CPCF8574Interface(i2c, address)
display = lcd.LCD(i2c, num_rows=2, num_cols=16)
display.set_backlight(True)
display.set_display_enabled(True)

# Starting animation here, purely aesthetics
display.clear()
display.set_cursor_pos(0,0)
display.print("Starting.")
time.sleep(1)
display.print(".")
time.sleep(1)
display.print(".")
time.sleep(1)

# ---------------------------------------------------------------
# Buttons declarations
btn1 = digitalio.DigitalInOut(board.GP15)
btn1.switch_to_input(pull=digitalio.Pull.DOWN)

btn2 = digitalio.DigitalInOut(board.GP14)
btn2.switch_to_input(pull=digitalio.Pull.DOWN)

btn3 = digitalio.DigitalInOut(board.GP13)
btn3.switch_to_input(pull=digitalio.Pull.DOWN)

btn4 = digitalio.DigitalInOut(board.GP12)
btn4.switch_to_input(pull=digitalio.Pull.DOWN)

# What buttons do :
# Keycode class defines USB HID keycodes to send using Keyboard.  
def btn1Action():
    cc.send(ConsumerControlCode.PLAY_PAUSE)
    display.clear()
    getVolume()
    display.set_cursor_pos(1,0)
    display.print("Play/Pause")
    time.sleep(0.5)
    
def btn2Action():
    cc.send(ConsumerControlCode.SCAN_NEXT_TRACK)
    display.clear()
    getVolume()
    display.set_cursor_pos(1,0)
    display.print("Next")
    time.sleep(0.5)
    
def btn3Action():
    display.clear()
    getVolume()
    display.set_cursor_pos(1,0)
    display.print("Open Brave")
    keyboard.send(Keycode.GUI, Keycode.TWO)
    time.sleep(0.4)
    
def btn4Action():
    display.clear()
    getVolume()
    display.set_cursor_pos(1,0)
    display.print("Open Discord")
    keyboard.send(Keycode.GUI, Keycode.FOUR)
    time.sleep(0.4)

# ---------------------------------------------------------------    
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

# ---------------------------------------------------------------
# Custom characters
# Creator : https://educ8s.tv/tools/lcd-character-creator/
volume_char = (0x02,0x09,0x05,0x15,0x15,0x05,0x09,0x02)
display.create_char(0,volume_char)

discord1_char = (0x00,0x0C,0x1E,0x1F,0x17,0x1F,0x1F,0x06)
display.create_char(1,discord1_char)
discord2_char = (0x00,0x06,0x0F,0x1F,0x1D,0x1F,0x1F,0x0C)
display.create_char(2,discord2_char)

brave1_char = (0x03,0x04,0x0B,0x09,0x09,0x04,0x04,0x03)
display.create_char(3,brave1_char)
brave2_char = (0x10,0x08,0x14,0x04,0x04,0x08,0x08,0x10)
display.create_char(4,brave2_char)

play_char = (0x10,0x18,0x1C,0x1E,0x1E,0x1C,0x18,0x10)
display.create_char(5,play_char)
pause_char = (0x1B,0x1B,0x1B,0x1B,0x1B,0x1B,0x1B,0x1B)
display.create_char(6,pause_char)

def DiscordLogo():
    display.set_cursor_pos(0,14)
    display.write(2)
    display.set_cursor_pos(0,15)
    display.write(1)
    display.home()

def BraveLogo():
    display.set_cursor_pos(0,10)
    display.write(3)
    display.set_cursor_pos(0,11)
    display.write(4)
    display.home()
    
def playPause():
    display.set_cursor_pos(0,0)
    display.write(5)
    display.set_cursor_pos(0,1)
    display.write(6)
    display.home()
    
def nextTrack():
    display.set_cursor_pos(0,4)
    display.write(5)
    display.set_cursor_pos(0,5)
    display.write(5)
    display.home()
    

def getVolume():
    display.clear()
    display.set_cursor_pos(1,13)
    display.write(0)
    display.print(str(current_volume))
    display.home()
    DiscordLogo()
    BraveLogo()
    playPause()
    nextTrack()
    
# ---------------------------------------------------------------
# Loop
while True:
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

# ---------------------------------------------------------------
# Button press listening
    if btn1.value:
        btn1Action()

    if btn2.value:
        btn2Action()

    if btn3.value:
        btn3Action()
      
    if btn4.value:
        btn4Action()
