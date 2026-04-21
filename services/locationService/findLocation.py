import os

import zmq
import time 
from geopy.geocoders import Nominatim
from dotenv import load_dotenv

load_dotenv()

#set zeroMQ
context = zmq.Context()
socket = context.socket(zmq.REP)
port = os.getenv("LOCATION_SERVICE_PORT", "5556")
socket.bind(f"tcp://0.0.0.0:{port}")

print(f"Location microservice is now listening on port {port}...")

while True:
    time.sleep(1)
    request = socket.recv_string()
    # calling the Nominatim tool
    loc = Nominatim(user_agent="location")

    if request[:-(len(request)-3)] == 'eng':
        place = request[4:]
        location = loc.geocode(place, language='en')
    else:
        place = request
        location = loc.geocode(place)

    print(f"Received place: {place}")
    print(f"Address obtained - {location.address}")
    print("The result was sent back to client")
    socket.send_string(location.address)

    print("Location microservice is now listening on port 5556...")