import socket
import machine
import time
from colors import colors, graphics
from cosmic import CosmicUnicorn

def start_web_server(wlan, cu):
    if not wlan or not wlan.isconnected():
        print("WLAN is not connected")
        return  # Exit the function if no WLAN connection

    # Get the IP address from wlan
    ip = wlan.ifconfig()[0]
    display_ip_address(ip, cu)

    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print('Listening on', addr)

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
            print('Connection closed', e)
            cl.close()

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

def display_ip_address(ip, cu):
    ip_text = f"{str(ip)} "  # Convert ip to string and add more spaces after the IP address
    scroll_width = graphics.measure_text(ip_text, 1)
    scroll_delay = 0.1  # Delay between each scroll step (adjust as needed)

    while True:
        for i in range(scroll_width + CosmicUnicorn.WIDTH):
            graphics.set_pen(graphics.create_pen(*colors['BLACK']))
            graphics.clear()
            graphics.set_pen(graphics.create_pen(*colors['RED']))
            graphics.text(ip_text, -i, 2, -1, 1)
            cu.update(graphics)
            time.sleep(scroll_delay)

    time.sleep(1)  # Pause before repeating the scroll
