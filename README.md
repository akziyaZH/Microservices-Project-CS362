# Travel Hub 

**Everything you need to stay prepared for your next trip!** Save your travel dates and create a list of places to visit.

---

##  Project Overview
Travel Hub is a full-stack application that helps users organize their travel wishlists. It is built using a **decoupled microservices architecture**, meaning the main application communicates with independent "worker" services to fetch weather, location, and historical data.

##  Tech Stack
* **Framework:** Flask (Python)
* **Database:** MongoDB Atlas (NoSQL)
* **Messaging:** ZeroMQ (REQ/REP Pattern)
* **APIs:** Weatherbit, Wikipedia, GeoPy (Nominatim)

##  Microservices Architecture
The system is divided into a **Hub** and several **Spokes** to ensure scalability:

* **Flask App (The Hub):** Manages the UI and MongoDB data.
* **Weather Service (getWeather.py):** Listens on port `5559` for city-specific forecasts.
* **Location Service (findLocation.py):** Listens on port 5557 to provide address details via Geopy.
* **CSV Service (csv_convert.py):** Handles the logic for exporting the wishlist to downloadable files.
* **Wiki Service (informationLink.py):** Connects to the Wikipedia API to provide background on travel destinations.



## Features
* **Wishlist:** Full CRUD functionality (Create, Read, Update, Delete) for travel spots. Data is securely stored and retrieved using MongoDB Atlas, ensuring persistence across sessions.
* **Live Weather:** Provides real-time, 7-day forecasts for any city entered by the user. This feature leverages the Weatherbit API via a dedicated ZMQ microservice to keep the main application lightweight.
* **Smart Search:** Automatically fetches historical and cultural summaries for added places. This is powered by the Wikipedia API, allowing users to learn more about their destinations instantly.
* **Export:** Allows users to download their entire wishlist as a .csv file. This is handled by a separate ZMQ worker to demonstrate background data processing

## Installation

1. **Clone the repo:**
   ```bash
   git clone [your-link]
   ```
2. **Install dependencies:**
    ```
    pip install -r requirements.txt
    ```
3. **Configure Environment:**
    
    Create a .env file with your MONGO_URI and WEATHERBIT_API_KEY

## How to Run

To run the full system, start the services first, then the app:

```
# Start all microservices
python services/getWeather.py
python services/csv_convert.py
python services/findLocation.py
python services/informationLink.py

# Start the main application
python app.py
```

## Project Gallery
|         Main Dashboard          |      Information & Weather       |
|:-------------------------------:|:--------------------------------:|
|   ![Dashboard](img/home.jpeg)   | ![Weather](img/information.jpeg) |

 Wishlist            
 ![Dashboard](img/wishlist.jpeg) 