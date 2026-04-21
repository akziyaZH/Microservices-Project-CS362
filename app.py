from flask import Flask, render_template, redirect, request, url_for, send_file
import os
from dotenv import load_dotenv
from database import get_all_items, add_item, delete_item, delete_collection, update_item, get_item_by_id
import zmq
import time

app = Flask(__name__)

load_dotenv()


@app.route('/')
def root():
    return render_template('base.html')


@app.route('/base')
def home():
    return render_template('base.html')


@app.route('/todo', methods=('GET', 'POST'))
def todo():
    data = get_all_items()
    return render_template("todo.html", data=data)


@app.route('/todo-add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        if request.form.get('Add_Place'):
            place = request.form['place']
            info = request.form['info']
            add_item(place, info)

            data = get_all_items()

            return redirect(url_for('todo', data=data))
    return render_template("todo-add.html")


@app.route('/update/<string:id>', methods=('GET', 'POST'))
def update(id):
    data = get_item_by_id(id)
    print(f"first data is {data}")
    if request.method == 'POST':
        place = request.values.get("place")
        info = request.values.get("info")

        update_item(id, place, info)

        data2 = get_item_by_id(id)
        print(f"updated data is {data2}")
        return redirect(url_for('todo'))
    return render_template('update.html', item=data)


@app.post('/<id>/delete/')
def delete(id):
    delete_item(id)
    return redirect(url_for('todo'))


@app.post('/delete_all')
def delete_all():
    # collection.drop()
    delete_collection()
    print("The list was deleted by the user")
    return redirect(url_for('todo'))


@app.route('/contact')
def help():
    return render_template("help.html")


@app.route('/wiki-place/<string:id>', methods=('GET', 'POST'))
def get_info(id):
    # set up zeroMQ
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://wiki-service:{os.getenv('WIKI_SERVICE_PORT')}")

    data = get_item_by_id(id)
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
    socket.connect(f"tcp://weather-service:{os.getenv('WEATHER_SERVICE_PORT')}")
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
    socket.connect(f"tcp://location-service:{os.getenv('LOCATION_SERVICE_PORT')}")
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
    socket.connect(f"tcp://csv-service:{os.getenv('CSV_SERVICE_PORT')}")

    data = get_all_items()

    socket.send_pyobj(data)
    info = socket.recv_pyobj()

    with open('wishlist.csv', 'w') as csv_file:
        # csv_file.write(info)
        for line in info:
            csv_file.write(line)
            if line == "}":
                csv_file.write('\n')

    print(f"The file was received - {info}")
    return send_file('wishlist.csv', as_attachment=True, download_name="wishlist.csv")


if __name__ == "__main__":
    port = int(os.environ.get('PORT', os.getenv("APP_PORT")))
    app.run(host='0.0.0.0', port=port, debug=True)
