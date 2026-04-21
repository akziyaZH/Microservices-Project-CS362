import zmq 
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("WEATHERBIT_API_KEY")

#set zeroMQ
context = zmq.Context()
socket = context.socket(zmq.REP)
port = os.getenv("WEATHER_SERVICE_PORT", "5559")
socket.bind(f"tcp://0.0.0.0:{port}")

print(f"Weather microservice is now listening on port {port}...")

while True:
    # Receive city name from the Flask Hub
    city = socket.recv_string()
    print(f"Received city: {city}")

    # Call Weatherbit API via Requests
    url = f"https://api.weatherbit.io/v2.0/forecast/daily?city={city}&key={api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for errors
        json_data = response.json()

        # Process the forecast series
        formatted_data = []
        for x in json_data['data']:
            # Weatherbit daily API uses 'valid_date' or 'datetime'
            raw_date = x['valid_date']
            # Parse YYYY-MM-DD
            d = datetime.strptime(raw_date, "%Y-%m-%d")
            formatted_data.append(f"Day: {d.strftime('%d-%m-%Y')} Temp: {x['temp']}°C")

        print(f"Prepared data: {formatted_data[:3]}...")  # Print first 3 for log
        socket.send_pyobj(formatted_data)

    except Exception as e:
        print(f"Error: {e}")
        socket.send_pyobj(["Error: Could not retrieve weather data."])

    print("The weather information was sent back to client")
    print("Weather microservice is now listening on port 5559...")