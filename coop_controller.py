#!/user/bin/env python

"""
Created on Fri Dec 10 11:34:53 2021

@author: jmatt
"""

import coop_functions as CF
import traceback
from flask import Flask, jsonify, request
from multiprocessing import Process
import time

app = Flask(__name__)
   
try:
    process = Process(target=CF.run_coop_controller, args=(CF.command_queue, CF.response_queue))
    process.start()
except Exception as e:
    err_msg = str(e)
    
    with open(CF.logfile_name, 'a') as file:
        file.write('\nCONTROLLER CRASH TRACEBACK\n')
        traceback.print_exc(limit=None, file=file, chain=True)
    
    CF.send_crash_notification(CF.logfile_name)
        
    CF.restart()

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
    app.run(host='0.0.0.0', port=8000)
    
