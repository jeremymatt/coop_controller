#!/user/bin/env python

"""
Created on Fri Dec 10 11:34:53 2021

@author: jmatt
"""

import coop_functions as CF
import traceback
from flask import Flask, session, request, jsonify, render_template
from multiprocessing import Process
import time
import subprocess
import signal
import sys

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a strong secret key

def start_ngrok(port, static_ngrok_url):
    """Start Ngrok with the specified static URL."""
    try:
        ngrok_process = subprocess.Popen(
            ["ngrok", "http", str(port), "--url", static_ngrok_url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"Ngrok started with static URL: {static_ngrok_url}")
        # Optionally, print output for debugging
        time.sleep(5)  # Wait for Ngrok to initialize
        return ngrok_process
    except Exception as e:
        print(f"Failed to start Ngrok: {e}")
        return None
   
def cleanup(ngrok_process,controller_process):
    print("\nCleaning up...")
    if ngrok_process:
        ngrok_process.terminate()
        print("ngrok process terminated.")
    if controller_process:
        controller_process.terminate()
        print("Coop controller process terminated.")
    sys.exit(0)

# Signal handler
def signal_handler(sig, frame):
    cleanup()


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
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login</title>
        </head>
        <body>
            <h1>Login</h1>
            <form method="post">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username"><br><br>
                <label for="password">Password:</label>
                <input type="password" id="password" name="password"><br><br>
                <button type="submit">Login</button>
            </form>
        </body>
        </html>
        '''     
        
@app.route('/update', methods=['GET'])
def update():
    action = request.json.get('action')
    CF.command_queue.put(action)
    while CF.response_queue.empty():
        time.sleep(0.1)
    data = CF.response_queue.get()
    return jsonify(data)




if __name__ == '__main__':
    port = 8000
    ngrok_static_url = 'chickencoop.fun'

    # Start Ngrok
    ngrok_process = start_ngrok(port, ngrok_static_url)
    if not ngrok_process:
        print("Ngrok failed to start. Exiting.")
        exit(1)

        
    controller_process = Process(target=CF.run_coop_controller, args=(CF.command_queue, CF.response_queue))
    controller_process.start()


    # Start Flask app
    try:
        app.run(host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        cleanup()

    # Start Flask app
    try:
        print(f"Starting Flask app on port {port}...")
        app.run(port=port, debug=True)
    except Exception as e:
        print(f"Failed to start Flask app: {e}")
    finally:
        cleanup(ngrok_process,controller_process)
    
