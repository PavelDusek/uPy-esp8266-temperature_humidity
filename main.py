import time
import machine
import dht
import network
import socket
import ussl

url_base, name, token = "https://www.example.com", "<name>", "<token>"
ssid, key = "<SSID>", "<KEY>"

def do_connect(ssid, key):
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(ssid, key)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

def https_get(url):
    _, _, host, path = url.split('/', 3)
    sock = socket.socket()
    addr = socket.getaddrinfo(host, 443)
    sock.connect(addr[0][4])
    sock = ussl.wrap_socket(sock)

    def send_header(header, *args):
        sock.write(header % args + '\r\n')

    send_header(bytes('GET /' + path + ' HTTP/1.1', 'utf8'))
    send_header(bytes('Host: ' + host + ':443', 'utf8'))
    send_header(b'')
    data = sock.readline()
    response = data
    while data:
        print(data)
        data = sock.readline()
        response += data
    sock.close()
    return response

def measure():
    sensor  = dht.DHT11(machine.Pin(5))
    time.sleep_ms(500)
    sensor.measure()
    tem = sensor.temperature()
    hum = sensor.humidity()
    return tem, hum

def deep_sleep(msecs):
    # D0 and RST must be connected
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    rtc.alarm(rtc.ALARM0, msecs)
    machine.deepsleep()

########
# BODY #
########

led_pin = machine.Pin(2, machine.Pin.OUT)
led = machine.Signal(led_pin, invert=True)
led.on()

do_connect(ssid, key)
tem, hum = measure()
print(tem, hum)
url = url_base + "/input/temperature/" + name + "/" + token + "?value=" + str(tem)
https_get(url)
url = url_base + "/input/humidity/"    + name + "/" + token + "?value=" + str(hum)
https_get(url)
time.sleep_ms(5 * 1000)
led.off()
deep_sleep(60 * 60 * 1000) #sleep for 1 hour
