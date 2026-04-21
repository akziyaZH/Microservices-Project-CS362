# Developed by Ashton Haviland for CS361 Team Project
# GitHub link: https://github.com/Ashton-Haviland/CS361-Microservice-A
import os

import zmq
import wikipedia
import time
from dotenv import load_dotenv

load_dotenv()

# Set up ZeroMQ context and socket
context = zmq.Context()
socket = context.socket(zmq.REP)
port = os.getenv("WIKI_SERVICE_PORT", "5555")
socket.bind(f"tcp://0.0.0.0:{port}")

print(f"Wikipedia microservice listening on port {port}")

while True:
    time.sleep(1)
    # Receive request from client
    request = socket.recv_string()
    print(f"Received request: {request}")

    # Query Wikipedia API for page type, if no page found, return not found
    search = wikipedia.suggest(request)
    if search == "None":
        socket.send_string("not found")
        continue

    # Send "what type?" response
    socket.send_string("what type?")

    # Receive second request from client
    type = socket.recv_string()
    print(f"Received second request: {type}")

    # Query Wikipedia API for summary or image
    if type == "summary":
        # if receive request for summary, return summary up to 10 sentences.
        socket.send_string(wikipedia.summary(request))
        continue
    elif type == "photo":
        page = wikipedia.page(title=request)
        photos = (wikipedia.page(request).images[0])
        if len(photos) >= 1:
            socket.send_string(wikipedia.page(request).images[0])
            continue
    else:
        socket.send_string("Invalid request")
        continue
