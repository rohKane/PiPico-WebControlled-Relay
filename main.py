import machine
import network
import socket
import gc
import time

# Relay pin
relay_pin = machine.Pin(16, machine.Pin.OUT)
led = machine.Pin("LED", machine.Pin.OUT)

# Set up WiFi connection
#network.WLAN.deinit() # reset the ap
time.sleep(2)
gc.collect()
ssid = "RPI_PICO"
password = "B16plk@a"
station = network.WLAN(network.AP_IF)
print("Station status:", station.status()) # debug new
station.active(True)
station.config(essid=ssid, password=password)
print("SSID:", ssid) # debug new
#print("Password:", password) # ebug new

# Wait until connected to WiFi
while not station.isconnected():
    pass

# Create a socket and bind to a port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

# HTML webpage content
html = """
<!DOCTYPE html>
<html>
<head>
    <title>B16</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            text-align: center;
        }
        button {
            appearance: button;
                background-color: #1899D6;
                border: solid transparent;
                border-radius: 16px;
                border-width: 0 0 4px;
                box-sizing: border-box;
                color: #FFFFFF;
                cursor: pointer;
                display: inline-block;
                font-family: din-round,sans-serif;
                font-size: 18px;
                font-weight: 700;
                letter-spacing: .8px;
                line-height: 20px;
                margin: 0;
                outline: none;
                overflow: visible;
                padding: 20px 20px;
                text-align: center;
                text-transform: uppercase;
                touch-action: manipulation;
                transform: translateZ(0);
                transition: filter .2s;
                user-select: none;
                -webkit-user-select: none;
                vertical-align: middle;
                white-space: nowrap;
                width: 80%;
        }
    </style>
</head>
<body>
    <h1 style="font-size: 30px; font-family: sans-serif">Wireless Watering System</h1>
    <button onclick="toggleRelay()">Activate</button>
    <script>
        function toggleRelay() {
            var xhttp = new XMLHttpRequest();
            xhttp.open("GET", "/toggle", true);
            xhttp.send();
        }
    </script>
</body>
</html>
"""

# Function to handle the web page request 
def handle_request(client_socket):
    request = client_socket.recv(1024).decode()
    if 'GET / HTTP/1.1' in request:
        client_socket.send("HTTP/1.1 200 OK\n")
        client_socket.send("Content-type:text/html\n")
        client_socket.send("\n")
        client_socket.send(html)
    elif 'GET /toggle HTTP/1.1' in request:
        relay_pin.value(0)
        led.on()
        print("Activated")
        time.sleep(2)
        relay_pin.value(1)
        led.off()
        print("Deactivated")
        client_socket.send("HTTP/1.1 200 OK\n")
        client_socket.send("Content-type:text/html\n")
        client_socket.send("\n")
        client_socket.send(html)

# Main loop
while True:
    try:
        client, addr = s.accept()
        handle_request(client)
        client.close()
    except KeyboardInterrupt:
        break

# Disconnect from WiFi
station.disconnect()
station.active(False)


