from flask import Flask, session, request, redirect, jsonify, render_template
import hashlib
import coop_functions as CF
import time
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # Allow CORS for all routes
app.secret_key = 'your_secret_key_here'  # Replace with a strong secret key

# Load credentials
with open('credentials.config', 'r') as file:
    credentials = file.read().splitlines()
    USERNAME_HASH = credentials[0].strip()
    PASSWORD_HASH = credentials[1].strip()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if (hashlib.md5(username.encode()).hexdigest() == USERNAME_HASH and
                hashlib.md5(password.encode()).hexdigest() == PASSWORD_HASH):
            session["authenticated"] = True
            return redirect("/")

    if session.get("authenticated"):
        return render_template("template.html")
    else:
        return render_template('login.html')    
        
@app.route('/update', methods=['GET','POST'])
def update():
    if request.method == "POST":
        print('received post request')
        action = request.json.get('action')
        CF.command_queue.put(action)
        while CF.response_queue.empty():
            time.sleep(0.1)
        data = CF.response_queue.get()
        print(data)
        return jsonify(data)
    elif request.method == "GET":
        print('received get request')
        return  '''
                <!DOCTYPE html>
                <html>
                    <head>
                        <!-- head definitions go here -->
                    </head>
                    <body>
                        <!-- the content goes here -->
                    </body>
                </html>'''


# @app.route('/update', methods=['POST'])
# def update():
#     data = request.json  # Get JSON data from the request
#     command = data.get('command')  # Extract the command from the JSON payload
#     print(f"Received command: {command}")  # Debugging log

#     # Mock response for testing
#     return jsonify({"status": "success", "command": command})


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/")