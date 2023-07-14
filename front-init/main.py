from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import json
import socket
import threading

app = Flask(__name__)

# HTTP routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        username = request.form.get('username')
        message = request.form.get('message')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

        # Send data to socket server
        send_to_socket_server(username, message)

        # Save data to JSON file
        save_to_json(timestamp, username, message)

        return redirect(url_for('index'))
    else:
        return render_template('message.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html'), 404

# Socket server
def socket_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('localhost', 5000))
    print('Socket server started.')

    while True:
        data, addr = server_socket.recvfrom(1024)
        data_dict = json.loads(data.decode('utf-8'))
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

        # Save data to JSON file
        save_to_json(timestamp, data_dict['username'], data_dict['message'])

def send_to_socket_server(username, message):
    data_dict = {
        'username': username,
        'message': message
    }
    data = json.dumps(data_dict).encode('utf-8')
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(data, ('localhost', 5000))

def save_to_json(timestamp, username, message):
    data_dict = {
        timestamp: {
            'username': username,
            'message': message
        }
    }
    with open('storage/data.json', 'a') as file:
        json.dump(data_dict, file)
        file.write('\n')

if __name__ == '__main__':
    # Start socket server in a separate thread
    socket_thread = threading.Thread(target=socket_server)
    socket_thread.start()

    # Start Flask HTTP server
    app.run(port=3000)

