from flask import Flask, render_template, redirect, request, url_for, send_file
import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
import zmq
import time

load_dotenv()

uri = os.getenv("MONGO_URI")
print(f"DEBUG: My URI is: {uri}")
app = Flask(__name__)
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client['cs361']
collection = db['travel_hub']
collection2 = db['travel_dates']


@app.route('/')
def root():
    return render_template('base.html')


@app.route('/base')
def home():
    return render_template('base.html')


@app.route('/todo', methods=('GET', 'POST'))
def todo():
    # place = request.args.get('place', None)
    # info = request.args.get('info', None)
    data = collection.find()
    return render_template("todo.html", data=data)


@app.route('/todo-add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        if request.form.get('Add_Place'):
            place = request.form['place']
            info = request.form['info']
            collection.insert_one({'place': place, 'info': info})
            print("Data added to database")
            data = collection.find()
            return redirect(url_for('todo', data=data))
    return render_template("todo-add.html")


@app.route('/update/<string:id>', methods=('GET', 'POST'))
def update(id):
    data = collection.find_one({"_id": ObjectId(id)})
    print(f"first data is {data}")
    if request.method == 'POST':
        place = request.values.get("place")
        info = request.values.get("info")
        collection.update_one({"_id": ObjectId(id)}, {"$set": {"place": place, "info": info}})
        data2 = collection.find_one({"_id": ObjectId(id)})
        print(f"updated data is {data2}")
        return redirect(url_for('todo'))
    return render_template('update.html')


@app.post('/<id>/delete/')
def delete(id):
    collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('todo'))


@app.post('/delete_all')
def delete_all():
    collection.drop()
    print("the list was deleted")
    return redirect(url_for('todo'))


@app.route('/calendar', methods=('GET', 'POST'))
def calendar():
    return render_template("calendar.html")


@app.route('/calendar2', methods=('GET', 'POST'))
def calendar_list():
    return render_template("calendar2.html")


@app.route('/contact')
def help():
    return render_template("help.html")


@app.route('/wiki-place/<string:id>', methods=('GET', 'POST'))
def get_info(id):
    # set up zeroMQ
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    data = collection.find_one({"_id": ObjectId(id)})
    print(f"find the data - {data}")
    print(f"this is the place - {data['place']}")

    # obtain summery from Wiki
    socket.send_string(data['place'])
    time.sleep(1)
    response = socket.recv_string()
    if response == 'what type?':
        socket.send_string('summary')
        result = socket.recv_string()
        data1 = result
        print(f"this is summary - {data1}")
    elif response == 'not found':
        result = 'No information from Wikipedia'
        data1 = result

    # obtain photo from Wiki
    socket.send_string(data['place'])
    time.sleep(1)
    response = socket.recv_string()
    if response == 'what type?':
        socket.send_string('photo')
        photo_result = socket.recv_string()
    elif response == 'not found':
        photo_result = 'No information from Wikipedia'
    data2 = photo_result
    print(f"this is photo URL - {photo_result}")
    return render_template('wiki-place.html', infos=data1, photos=data2)


@app.route('/information')
def info():
    place = "Please enter a place to find the address"
    weather = "Please enter a city to get weather information"
    return render_template("information.html", addresses=place, weathers=weather)


@app.route('/weather', methods=('GET', 'POST'))
def get_weather():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5559")
    if request.method == 'POST':
        city = request.form['weather']
        place = "Please enter a place to find the address"
        if request.form.get('Get_Weather_Forecast'):
            print(f"Obtained city is {city} to get weather information")
            socket.send_string(city)
            print("The request was sent to server")
            time.sleep(1)
            weather = socket.recv_pyobj()

            weather_info = city + "\n"
            for i in weather:
                weather_info += i + '\n'
            print(f"The following weather information was received - {weather_info}")
    return render_template('information.html', weathers=weather_info, addresses=place)


@app.route('/location', methods=('GET', 'POST'))
def location():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5556")
    if request.method == 'POST':
        place = request.form['address']
        weather = "Please enter a city to get weather information"
        if request.form.get('Get_Address_Eng'):
            # place = request.form['address']
            print(f"Get address of {place}")
            socket.send_string("eng " + place)
            time.sleep(1)
            address = socket.recv_string()
            print(f"The address received - {address}")

        if request.form.get('Get_Address_Local'):
            # place = request.form['address']
            print(f"Get address if {place} in local language")
            socket.send_string(place)
            time.sleep(1)
            address = socket.recv_string()
            print(f"The address received - {address}")
    return render_template('information.html', addresses=address, weathers=weather)


@app.route('/generate_csv', methods=('GET', 'POST'))
def generate_csv():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5558")

    data = []
    for file in collection.find({}):
        data.append(file)
    socket.send_pyobj(data)

    info = socket.recv_pyobj()
    with open('wishlist.csv', 'w') as csv_file:
        # csv_file.write(info)
        for l in info:
            csv_file.write(l)
            if l == "}":
                csv_file.write('\n')

    print(f"The file was received - {info}")
    return send_file('wishlist.csv', as_attachment=True, download_name="wishlist.csv")


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 45678))
    app.run(port=port, debug=True)
