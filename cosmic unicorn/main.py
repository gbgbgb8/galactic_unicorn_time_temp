import time
import math
import machine
import network
import ntptime
import urequests as requests
import ujson as json
from cosmic import CosmicUnicorn
from picographics import PicoGraphics, DISPLAY_COSMIC_UNICORN as DISPLAY

try:
    from secrets import WIFI_SSID, WIFI_PASSWORD, WUNDERGROUNDAPIKEY, WUNDERGROUNDSTATION
    wifi_available = True
except ImportError:
    print("Create secrets.py with your WiFi credentials to get time from NTP")
    wifi_available = False

cu = CosmicUnicorn()
graphics = PicoGraphics(DISPLAY)
rtc = machine.RTC()

width = CosmicUnicorn.WIDTH
height = CosmicUnicorn.HEIGHT

WHITE = graphics.create_pen(255, 255, 255)
BLACK = graphics.create_pen(0, 0, 0)
RED = graphics.create_pen(255, 0, 0)

last_temperature_update = 0
last_temperature = "N/A°"
utc_offset = -8

def sync_time():
    global wlan
    if not wifi_available:
        return
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        wlan.active(True)
        wlan.config(pm=0xa11140)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        max_wait = 200
        while max_wait > 0:
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            max_wait -= 1
            print('waiting for connection...')
            time.sleep(0.2)
            cu.update(graphics)
        if max_wait > 0:
            print("Connected")
            update_utc_offset_from_worldtimeapi()
            print("utc offset:", utc_offset)
        else:
            print("Connection failed")
            display_no_wifi()
            time.sleep(10)
            machine.reset()
    try:
        update_utc_offset_from_worldtimeapi()
        print("utc offset:", utc_offset)
        ntptime.settime()
        print("Time set")
    except Exception as e:
        print("Failed to set time:", str(e))

def display_no_wifi():
    graphics.set_pen(BLACK)
    graphics.clear()
    graphics.set_pen(RED)
    graphics.text("NO WIFI", 6, 12, -1, 2)
    cu.update(graphics)

up_button = machine.Pin(CosmicUnicorn.SWITCH_VOLUME_UP, machine.Pin.IN, machine.Pin.PULL_UP)
down_button = machine.Pin(CosmicUnicorn.SWITCH_VOLUME_DOWN, machine.Pin.IN, machine.Pin.PULL_UP)

def adjust_utc_offset(pin):
    global utc_offset, last_second
    if pin == up_button:
        utc_offset += 1
        last_second = None
    if pin == down_button:
        utc_offset -= 1
        last_second = None

up_button.irq(trigger=machine.Pin.IRQ_FALLING, handler=adjust_utc_offset)
down_button.irq(trigger=machine.Pin.IRQ_FALLING, handler=adjust_utc_offset)

year, month, day, wd, hour, minute, second, _ = rtc.datetime()
last_second = second

def update_utc_offset_from_worldtimeapi():
    global utc_offset
    url = "http://worldtimeapi.org/api/timezone/America/Los_Angeles"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            utc_offset_str = data['utc_offset']
            hours_offset = int(utc_offset_str.split(':')[0])
            utc_offset = hours_offset
            print("UTC Offset updated to:", utc_offset)
        else:
            print("Failed to get UTC offset, HTTP Status Code:", response.status_code)
    except Exception as e:
        print("Failed to update UTC offset:", str(e))

def get_temperature(force_update=False):
    global last_temperature_update, last_temperature
    current_time = time.time()
    if current_time - last_temperature_update >= 900 or force_update:
        api_key = WUNDERGROUNDAPIKEY
        station_id = WUNDERGROUNDSTATION
        url = f"https://api.weather.com/v2/pws/observations/current?stationId={station_id}&format=json&units=e&apiKey={api_key}"
        print("Constructed URL:", url)
        try:
            response = requests.get(url)
            weather_data = response.json()
            temp = weather_data['observations'][0]['imperial']['temp']
            last_temperature = f"{temp}°"
            last_temperature_update = current_time
            return last_temperature
        except Exception as e:
            print("Error fetching temperature:", type(e).__name__, e)
            if hasattr(e, 'errno') and e.errno is not None:
                print("Error number:", e.errno)
            if hasattr(e, 'strerror') and e.strerror is not None:
                print("Error string:", e.strerror)
            print(last_temperature)
            return last_temperature
    else:
        return last_temperature

def redraw_display_if_reqd():
    global year, month, day, wd, hour, minute, second, last_second, last_temperature_update, clock_x, clock_direction, last_minute, temp_y, temp_direction

    year, month, day, wd, hour, minute, second, _ = rtc.datetime()
    if second != last_second:
        hour = (hour + utc_offset) % 24
        is_pm = hour >= 12
        if hour == 0:
            hour = 12
        elif hour > 12:
            hour -= 12

        graphics.set_pen(BLACK)
        graphics.clear()

        clock = f"{hour}:{minute:02}"
        graphics.set_pen(RED)
        x = clock_x
        y = 0
        graphics.text(clock, x, y, -1, 1)

        temperature = get_temperature()
        graphics.set_pen(WHITE)
        temp_x = 1
        graphics.text(temperature, temp_x, temp_y, -1, 2)

        last_second = second

        if minute != last_minute:
            if clock_direction == "left":
                clock_x -= 1
                if clock_x <= 6:
                    clock_direction = "right"
            else:
                clock_x += 1
                if clock_x >= 16:
                    clock_direction = "left"
            
            if temp_direction == "up":
                temp_y -= 1
                if temp_y <= 8:
                    temp_direction = "down"
            else:
                temp_y += 1
                if temp_y >= 18:
                    temp_direction = "up"
            
            last_minute = minute

# Initialize clock position, direction, and last minute
clock_x = 16
clock_direction = "left"
temp_y = 8
temp_direction = "up"
_, _, _, _, _, last_minute, _, _ = rtc.datetime()

# Rest of the code remains the same

def start_web_server():
    global wlan
    import socket
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print('Listening on', addr)
    ip = wlan.ifconfig()[0]
    display_ip_address(ip)

    while True:
        try:
            cl, addr = s.accept()
            print('Client connected from', addr)
            request = cl.recv(1024)
            print(request)

            if b'GET /secrets.py' in request:
                with open('secrets.py', 'r') as f:
                    secrets_content = f.read()
                response = 'HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Disposition: attachment; filename=secrets.py\r\n\r\n'
                response += secrets_content
                cl.send(response)
                cl.close()
            elif b'POST' in request:
                content_length = int(request.split(b'Content-Length: ')[1].split(b'\r\n')[0])
                data = request.split(b'\r\n\r\n')[1][:content_length].decode('utf-8')
                print("Received data:", data)
                update_secrets(data)
                response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n'
                response += 'Settings updated successfully. Restarting device...'
                cl.send(response)
                cl.close()
                s.close()
                machine.reset()
            else:
                response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n'
                response += '<html><body>'
                response += '<form method="post">'
                response += 'WIFI_SSID: <input type="text" name="wifi_ssid"><br>'
                response += 'WIFI_PASSWORD: <input type="password" name="wifi_password"><br>'
                response += 'WUNDERGROUNDAPIKEY: <input type="text" name="api_key"><br>'
                response += 'WUNDERGROUNDSTATION: <input type="text" name="station_id"><br>'
                response += '<input type="submit" value="Update">'
                response += '</form>'
                response += '<br><a href="/secrets.py">Download secrets.py</a>'
                response += '</body></html>'
                cl.send(response)
                cl.close()
        except OSError as e:
            cl.close()
            print('Connection closed')

def update_secrets(data):
    params = {}
    for param in data.split('&'):
        key, value = param.split('=')
        params[key] = value

    with open('secrets.py', 'w') as f:
        f.write(f"WIFI_SSID = '{params['wifi_ssid']}'\n")
        f.write(f"WIFI_PASSWORD = '{params['wifi_password']}'\n")
        f.write(f"WUNDERGROUNDAPIKEY = '{params['api_key']}'\n")
        f.write(f"WUNDERGROUNDSTATION = '{params['station_id']}'\n")

def display_ip_address(ip):
    graphics.set_pen(BLACK)
    graphics.clear()
    graphics.set_pen(RED)
    graphics.text(f"{ip}", 0, 2, -1, 1)
    cu.update(graphics)

graphics.set_font("bitmap8")
cu.set_brightness(1.0)

sync_time()

while True:
    if cu.is_pressed(CosmicUnicorn.SWITCH_BRIGHTNESS_UP):
        cu.adjust_brightness(+0.01)
        last_second = None

    if cu.is_pressed(CosmicUnicorn.SWITCH_BRIGHTNESS_DOWN):
        cu.adjust_brightness(-0.01)
        last_second = None

    if cu.is_pressed(CosmicUnicorn.SWITCH_A):
        start_web_server()

    if cu.is_pressed(CosmicUnicorn.SWITCH_B):
        get_temperature(force_update=True)
        last_second = None

    redraw_display_if_reqd()
    cu.update(graphics)
    time.sleep(0.01)
