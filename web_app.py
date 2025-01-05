from flask import Flask, session, request, redirect, jsonify, render_template
import hashlib
import coop_functions as CF
import time
import os
import settings
from dotenv import load_dotenv

# Load environment variables from the credentials file
load_dotenv(os.path.join(settings.path_to_repo, "flask_credentials.env"))

app = Flask(__name__)

# Get the secret key from the credentials file
app.secret_key = os.getenv("FLASK_SECRET_KEY")

if app.secret_key is None:
    raise ValueError("No secret key found. Please ensure the credentials file is correctly set up.")


# Load credentials
with open(os.path.join(settings.path_to_repo,'credentials.config'), 'r') as file:
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
        action = request.json.get('command')
        print('received post request with action of: {}'.format(action))
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
                        <h1> HELLO WORLD </h1>
                    </head>
                    <body>
                        here be chickens
                    </body>
                </html>'''


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/")