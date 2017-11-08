import sensor, image, time
from pyb import UART,Pin,Timer
import pyb
import utime

# For color tracking to work really well you should ideally be in a very, very,
# very, controlled enviroment where the lighting is constant...
pingpang =(70,90,10,35,10,50)
pingpang_night = (65,80,0,45,0,60)
tennis   = ( 60, 75, -30, -15, 30  , 50)
black=(15,75,-5,5,-5,20)
# You may need to tweak the above settings for tracking green things...
# Select an area in the Framebuffer to copy the color settings.

sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # use RGB565.
sensor.set_framesize(sensor.QQVGA) # use QQVGA for speed.
sensor.skip_frames(10) # Let new settings take affect.
sensor.set_auto_whitebal(False) # turn this off.
clock = time.clock() # Tracks FPS.
uart=UART(3,115200)
flag=0
timeNumber = 0
x=0
y=0

Kp_x=0.08
Td_x=0.02
Kp_y=0.08
Td_y=0.02
'''
Kp_x=0.09
Td_x=0.02
Kp_y=0.09
Td_y=0.02
'''
lasterr_x=0
lasterr_y=0

err_x=0
err_y=0

duty_x=15
duty_y=12

pos_set=(80,56)
x_set=(52,82,112)
y_set=(26,56,86)

p_x=Pin('P7')
p_y=Pin('P8')
tim=Timer(4,freq=100)

x_steer=tim.channel(1,Timer.PWM,pin=p_x)
y_steer=tim.channel(2,Timer.PWM,pin=p_y)
x_steer.pulse_width_percent(20)
y_steer.pulse_width_percent(15  )


def set_pos(n):
        global pos_set
        d={1:(x_set[0],y_set[0]),
        2:(x_set[0],y_set[1]),
        3:(x_set[0],y_set[2]),
        4:(x_set[1],y_set[0]),
        5:(x_set[1],y_set[1]),
        6:(x_set[1],y_set[2]),
        7:(x_set[2],y_set[0]),
        8:(x_set[2],y_set[1]),
        9:(x_set[2],y_set[2]),}
        pos_set=(d[n][0],d[n][1])
        print("target position has been set as",pos_set)
        return pos_set

def pid():
        global pos_set
        global lasterr_x
        global lasterr_y
        global err_x
        global err_y
        global x,y
        global duty_x,duty_y
        err_x=pos_set[0]-x
        err_y=pos_set[1]-y
        print("x_err:",err_x,"     y_err:",err_y)

        if (abs(err_x)<=2):
            err_x=0
        if (abs(err_y)<=2):
            err_y=0
        duty_x=15-Kp_x*err_x+Td_x*lasterr_x
        duty_y=15+Kp_y*err_y+Td_y*lasterr_y
        lasterr_x=err_x
        lasterr_y=err_y

        if duty_x>=20:
            duty_x=20
        elif duty_x<=5:
            duty_x=5
        if duty_y>=20:
            duty_y=20
        elif duty_y<=5:
            duty_y=5
        x_steer.pulse_width_percent(duty_x)
        y_steer.pulse_width_percent(duty_y)
        print("x_duty:",duty_x," y_duty:",duty_y)

tim2=Timer(2,freq=20)#10MS一次打角
#tim2.freq(100)
def f(t):
    global flag
    global timeNumber
    pyb.LED(3).toggle()
    flag=1

tim2.callback(f)

while(True):
    t1=utime.ticks_us()
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot().lens_corr(1.8) # Take a picture and return the image.
   # blobs = img.find_blobs([black])

    blobs = img.find_blobs([pingpang])
    if len(blobs) == 1:
        # Draw a rect around the blob.
        b = blobs[0]
        # img.draw_rectangle(b[0:4],color = (255, 0, 0)) # rect
        img.draw_cross(b[5], b[6],color = (255, 0, 0)) # cx, cy
        print(b[5],b[6])

        x=b[5]
        y=b[6]

        if (flag==1):
            set_pos(5)
            pid()
            flag=0
        t2=utime.ticks_us()
        print("handle cost:",t2-t1,"us")
        uart_buf='x:'+str(x)+' y:'+str(y)

        uart.write(uart_buf)
    # print(clock.fps()) # Note: Your OpenMV Cam runs about half as fast while
    # connected to your computer. The FPS should increase once disconnected.

