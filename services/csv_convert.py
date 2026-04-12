import zmq
import time 
import csv
from operator import itemgetter


#set zeroMQ
context = zmq.Context()
socket = context.socket(zmq.REP)
sender = context.socket(zmq.PUB)
socket.bind("tcp://localhost:5558")

print("CSV generator microservice is now listening on port 5558...")

while True:
    time.sleep(1)
    request = socket.recv_pyobj()
    print(f"Received list: {request}")
    
    sorted_data = sorted(request, key=itemgetter('place'))

    with open('wishlist.csv', 'w', newline='') as csv_file:
        file = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
        document = file.writerow(sorted_data) 
        
    with open('wishlist.csv', 'r') as file:
        data = file.read()

    print("The CSV file was sent back to client")
    socket.send_pyobj(data)

    print("CSV generator microservice is now listening on port 5558...")