import network
import socket
import time



def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('SmartLab-206', 'smartlab602')
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())

	
def UDP_shakehands():
	import socket
	port = 10086
	s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(('192.168.199.112',port))  #绑定端口
	print('link success waiting for data ...')
	while True:         #接收数据
		data,addr=s.recvfrom(1024)
		s.sendto(data,addr)
		print('received:',data,'from',addr)
if __name__ == '__main__':
	do_connect()
	do_UDP_receive()