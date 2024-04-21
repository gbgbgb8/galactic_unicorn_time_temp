# Cosmic Unicorn Weather Clock

This project is a fun and interactive weather clock designed for the Pimoroni Cosmic Unicorn Pico Pi W 32x32 LED display. It displays the current time, temperature, and a colorful twinkle effect. The clock synchronizes time using NTP and fetches temperature data from the Weather Underground API. It also allows you to adjust the UTC offset and update settings through a web server.

## Features

- Displays the current time with a moving clock animation
- Shows the temperature in Fahrenheit with a sliding animation
- Colorful twinkle effect with randomly changing pixels
- Web server for updating settings, Wi-Fi credentials, and timezone offset URL
- Adjustable brightness using the volume up/down buttons
- UTC offset adjustment using the volume up/down buttons or through the web server
- Automatic timezone offset update from the World Time API

## Requirements

- Pimoroni Cosmic Unicorn Pico Pi W 32x32 LED display
- MicroPython firmware installed on the Pico Pi W
- Wi-Fi connection
- Weather Underground API key and station ID

## Installation

1. Install the required MicroPython libraries on your Pico Pi W:
   - `picographics`
   - `cosmic`
   - `urequests`
   - `ujson`

2. Download the project files and copy them to your Pico Pi W:
   - `main.py`
   - `webserver.py`
   - `twinkle.py`
   - `colors.py`

3. Create a `secrets.py` file in the same directory with the following content:

   ```python
   WIFI_SSID = 'your_wifi_ssid'
   WIFI_PASSWORD = 'your_wifi_password'
   WUNDERGROUNDAPIKEY = 'your_api_key'
   WUNDERGROUNDSTATION = 'your_station_id'
   TIMEZONEOFFSET = 'http://worldtimeapi.org/api/ip'
   #Or use something like http://worldtimeapi.org/api/timezone/America/Los_Angeles
   ```

   Replace `your_wifi_ssid`, `your_wifi_password`, `your_api_key`, and `your_station_id` with your actual Wi-Fi credentials and Weather Underground API information. The `TIMEZONEOFFSET` variable should contain the URL for retrieving the timezone offset.

4. Run the `main.py` script using Thonny or your preferred MicroPython IDE.

## Usage

- The clock will automatically synchronize time using NTP and display the current time on the LED display.
- The temperature will be fetched from the Weather Underground API and displayed below the time.
- Press the volume up/down buttons to adjust the display brightness.
- Press and hold the volume up/down buttons to adjust the UTC offset.
- Press button A to start the web server for updating settings.
- Press button B to force an immediate temperature update.
- Press button C to toggle the twinkle effect on/off.

## Web Server

The project includes a web server that allows you to update the Wi-Fi credentials, Weather Underground API settings, and timezone offset without modifying the code.

1. Press button A to start the web server.
2. The IP address of the Pico Pi W will be displayed on the LED matrix.
3. Open a web browser on a device connected to the same Wi-Fi network and navigate to the displayed IP address.
4. You will see a form where you can enter the updated Wi-Fi SSID, password, Weather Underground API key, station ID, and timezone offset URL.
5. Click the "Update and Reboot" button to save the changes. The device will restart with the new settings.
6. You can also download the current `secrets.py` file by clicking the "Download secrets.py" link.
7. To cancel the changes and reboot the device without updating the settings, click the "Cancel and Reboot" button.

## License

This project is open-source and available under the [MIT License](LICENSE).

Enjoy your Cosmic Unicorn Weather Clock!