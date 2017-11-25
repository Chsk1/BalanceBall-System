import sensor, image, time
from pyb import UART, Pin, Timer
import pyb
import utime

r_b = (45, 80, 40, 75, -50, -25)
y_b = (60, 80, 0, 40, 55, 85)

##### 相机初始化 #####
sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # use RGB565.
sensor.set_framesize(sensor.QVGA) # use QQVGA for speed.
sensor.skip_frames(10) # Let new settings take affect.
sensor.set_auto_whitebal(False) # turn this off.
clock = time.clock() # Tracks FPS.

##### 变量初始化 #####
uart = UART(3, 115200)
x = 0
y = 0
last_x = 0
last_y = 0
#########################
Kp_x = 0.130 #############
I_x = 0.018 #############
Td_x = 0.08 ###############
Kp_y = 0.135 ###############
I_y = 0.018 #############
Td_y = 0.10 #############
#########################
#########################
Kp_speed_x = 0.15 #############
Td_speed_x = 0.05 ###############
Kp_speed_y = 0.12 ###############
Td_speed_y = 0.05 #############
#########################

pos_I_x_inc = 0
pos_I_y_inc = 0
speed_x = 0
speed_y = 0
lastspeed_x = 0
lastspeed_y = 0
lasterr_x = 0
lasterr_y = 0
err_x = 0
err_y = 0
duty_x = 16.3
duty_y = 15.7
pos_set = [160, 120]
##### 舵机初始化 #####
p_x = Pin('P7')
p_y = Pin('P8')
tim = Timer(4,freq = 100)
x_steer = tim.channel(1,Timer.PWM,pin = p_x)
y_steer = tim.channel(2,Timer.PWM,pin = p_y)
x_steer.pulse_width_percent(15)
y_steer.pulse_width_percent(15)


##### 目标点设定函数 #####
def set_pos(a,b):
    global pos_set
    pos_set=(a,b)
    print("target position has been set as", pos_set)
    return pos_set

def cascade_pid():
    global lasterr_x, lasterr_y
    global err_x, err_y
    global duty_x, duty_y
    global pos_I_x_inc
    global pos_I_y_inc
    pos_set[0] = x_set
    pos_set[1] = y_set
    err_x = pos_set[0] - x
    err_y = pos_set[1] - y
    if (abs(err_x) <= 2):
        err_x = 0
    if (abs(err_y) <= 2):
        err_y = 0
    # 积分
    pos_I_x_inc = pos_I_x_inc + I_x * err_x
    pos_I_y_inc = pos_I_y_inc + I_y * err_y
    limit_x = 2
    limit_y = 2
    if pos_I_x_inc > limit_x:
        pos_I_x_inc = limit_x
    elif pos_I_x_inc < -limit_x:
        pos_I_x_inc = -limit_x
    if pos_I_y_inc > limit_y:
        pos_I_y_inc = limit_y
    elif pos_I_y_inc < -limit_y:
        pos_I_y_inc = -limit_y
    duty_pos_x = Kp_x*err_x + pos_I_x_inc + Td_x * (err_x - lasterr_x)
    duty_pos_y = Kp_y*err_y + pos_I_y_inc + Td_y * (err_y - lasterr_y)
    # 速度环_x
    global speed_x, speed_y, lastspeed_x, lastspeed_y
    speed_x = float(err_x - lasterr_x)
    # speed_x_err = (-0- speed_x)
    speed_x_err = (-duty_pos_x - speed_x)
    duty_speed_x = Kp_speed_x * speed_x_err + Td_speed_x * (speed_x - lastspeed_x)
    # print(speed_x_err)
    # 速度环_y
    speed_y = float(err_y - lasterr_y)
    speed_y_err = (-duty_pos_y - speed_y)
   # speed_y_err = (- 0 - speed_y)
    duty_speed_y = Kp_speed_y * speed_y_err + Td_speed_y * (speed_y - lastspeed_y)
    # ---
    lastspeed_x = speed_x
    lastspeed_y = speed_y
    lasterr_x = err_x
    lasterr_y = err_y

    duty_x = 16.3 + duty_speed_x
    duty_y = 15.7 + duty_speed_y
    if duty_x >=25:
        duty_x = 25
    elif duty_x <= 5:
        duty_x = 5
    if duty_y >= 25:
        duty_y = 25
    elif duty_y <= 5:
        duty_y = 5

    x_steer.pulse_width_percent(duty_x)
    y_steer.pulse_width_percent(duty_y)
    print("x_duty:", duty_x, " y_duty:", duty_y)


##### 定时器中断 #####
'''
tim2 = Timer(2, freq = 0.2)#50MS一次打角
def f(t):
    global flag
    pyb.LED(3).toggle()
    flag = flag + 1
    if (flag>3):
        flag=0

tim2.callback(f)
'''

##### 循环主体 #####
while(True):
    t1 = utime.ticks_us()# 滴答计时器
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot().lens_corr(1.8) # Take a picture and return the image.
    # x_steer.pulse_width_percent(16.3)
    # y_steer.pulse_width_percent(15.7) # 舵机测试 注释掉下边部分
    blobs = img.find_blobs([y_b])# 寻找色块 蓝色背景黄色球
    blobs_red = img.find_blobs([red])
    if len(blobs_red) == 1:
        b_r = blobs_red[0]
        img.draw_cross(b_r[5], b_r[6], color = (0, 255, 0)) # cx, cy画十字
        #print(b_r[5], b_r[6])
        pos_set = set_pos(b_r[5],b_r[6])


    if len(blobs) == 1:
        b = blobs[0]
        img.draw_cross(b[5], b[6], color = (255, 0, 0)) # cx, cy画十字
        print(b[5], b[6])
        t2 = utime.ticks_us()
        x = b[5]
        y = b[6]
        cascade_pid()
        last_x = x
        last_y = y
    else:
        x = last_x
        y = last_y
        cascade_pid()
        # uart_buf = 'x:' + str(x) + ' y:' + str(y)
        # uart.write(uart_buf) # 串口发送坐标

