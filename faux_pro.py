import RPi.GPIO as GPIO
import time, picamera
import datetime as dt
from gps import *
from picamera import Color

# Based on using U-blox7 USB GPS dongle
# Need to install libraries : sudo apt-get install gpsd gpsd-clients python-gps
# gpsd can also be run as a standalone service from terminal with sudo gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock
# Once running as a service, view live data with cgps -s 

# Switch for start / stop recording on GPIO 26
# LED on GPIO 14

running = True

gpsd = gps(mode=WATCH_ENABLE|WATCH_NEWSTYLE)


GPIO.setmode(GPIO.BCM)

GPIO.setup(26, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(14, GPIO.OUT)

pressed = False

for each in range(0,6):
    GPIO.output(14, True)
    time.sleep(0.1)
    GPIO.output(14, False)
    time.sleep(0.1)

latitude = 0
longitude = 0
speed = 0
alt = 0

cam = picamera.PiCamera()
cam.resolution = (1360, 768)
cam.framerate = 30
cam.rotation = 270 # This is because my camera mounted sideways in case - comment out if not needed. Setting can be 90, 180 or 270
cam.annotate_background = Color('black')
cam.annotate_foreground = Color('white')
cam.exposure_mode = 'antishake'

def getPositionData(gps):
    global latitude, longitude, speed, alt
    nx = gpsd.next()
    # For a list of all supported classes and fields refer to:
    # https://gpsd.gitlab.io/gpsd/gpsd_json.html
    if nx['class'] == 'TPV':
        latitude = getattr(nx,'lat', "0")
        longitude = getattr(nx,'lon', "0")
        speed = getattr(nx, 'speed', '0.0')
        alt = getattr(nx, 'alt', '0')
        speed = float(speed)
        speed = 3.6 * speed
        #print speed, alt, latitude, longitude

while True:
    if GPIO.input(26) == GPIO.HIGH and not pressed:
        print 'Recording....'
        pressed = True
        getPositionData(gpsd)
        GPIO.output(14, True)
        time.sleep(0.5)

        filename = dt.datetime.now().strftime('%d-%m-%y_%H:%M:%S.mjpeg')
        cam.start_recording(filename, format='mjpeg')
        #cam.start_preview()
    if GPIO.input(26) == GPIO.HIGH and pressed:
        GPIO.output(14, False)
        pressed = False
        print 'Stopped.'
        cam.stop_recording()
        
        time.sleep(1)

    if pressed:
            getPositionData(gpsd)
            alt = str(alt)[0:5]
            speed = str(speed)[0:4]
            latitude = str(latitude)[0:7]
            longitude = str(longitude)[0:7]
            data = ' Lat:'+latitude +' Long:'+longitude + ' Alt:' + alt + 'm Speed:' + speed + 'kph ' 
            cam.annotate_text = data
        
            
            

        
