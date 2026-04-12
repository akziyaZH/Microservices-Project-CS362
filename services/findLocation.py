import zmq
import time 
from geopy.geocoders import Nominatim

#set zeroMQ
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://localhost:5556")

print("Location microservice is now listening on port 5556...")

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