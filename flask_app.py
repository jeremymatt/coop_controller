from flask import Flask, session, request, redirect, jsonify, render_template
import hashlib
import controller_functions as CF


app = Flask(__name__)
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
    action = request.json.get('action')
    CF.command_queue.put(action)
    while CF.response_queue.empty():
        time.sleep(0.1)
    data = CF.response_queue.get()
    print(data)
    return jsonify(data)

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/")