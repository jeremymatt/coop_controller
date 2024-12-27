from flask import Flask, request, jsonify, render_template_string, session, redirect
import hashlib
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a strong secret key

# Load credentials
with open('credentials.config', 'r') as file:
    credentials = file.read().splitlines()
    USERNAME_HASH = credentials[0].strip()
    PASSWORD_HASH = credentials[1].strip()

# System state (mock data for demonstration purposes)
state = {
    "light_status": "Off",
    "door_status": "Closed",
    "timer_seconds": 0,
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print('{}'.format(hashlib.md5(username.encode()).hexdigest()))
        print('{}'.format(hashlib.md5(password.encode()).hexdigest()))

        if (hashlib.md5(username.encode()).hexdigest() == USERNAME_HASH and
                hashlib.md5(password.encode()).hexdigest() == PASSWORD_HASH):
            session['authenticated'] = True
            return redirect('/')

    if session.get('authenticated'):
        template = '''
        <!DOCTYPE html>
        <html>
        <head>
            <script src="/static/test_script.js"></script>
        </head>
        <body>
            <h1>Chicken Coop Controller</h1>

            <p>Light Status:</p>
            <button id="light-button" style="background-color: {{ 'green' if light_status == 'On' else 'red' }};" 
                    onclick="toggleLight()">{{ light_status }}</button>

            <p>Door Status:</p>
            <input type="text" id="new-door-status" placeholder="New door status">
            <button id="door-button" onclick="toggleDoor()">{{ door_button_label }}</button>

            <p>System Time: <span id="system-time">{{ system_time }}</span></p>
            <p>{{ light_next_action }}</p>
            <p>{{ door_next_action }}</p>

            <form method="post" action="/logout">
                <button type="submit">Logout</button>
            </form>

            <script>
                setInterval(() => {
                    fetch('/update')
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('system-time').innerText = data.system_time;
                        })
                        .catch(error => console.error('Error fetching system time:', error));
                }, 1000);
            </script>
        </body>
        </html>
        '''

        light_next_action = "Light: turning on" if state['light_status'] == "Off" else "Light: turning off"
        door_next_action = "Door: opening" if state['door_status'] == "Closed" else (
            "Door: closing" if state['door_status'] == "Open" else "Door action: N/A")

        return render_template_string(template,
                                      light_status=state['light_status'],
                                      door_button_label=get_door_button_label(),
                                      system_time=datetime.now().strftime('%Y:%m:%d %H:%M:%S'),
                                      light_next_action=light_next_action,
                                      door_next_action=door_next_action)
    else:
        return '''
        <!DOCTYPE html>
        <html>
        <body>
            <form method="post">
                Username: <input type="text" name="username"><br>
                Password: <input type="password" name="password"><br>
                <button type="submit">Login</button>
            </form>
        </body>
        </html>
        '''

@app.route('/update', methods=['GET'])
def update():
    system_time = datetime.now().strftime('%Y:%m:%d %H:%M:%S')
    light_next_action = "Light: turning on" if state['light_status'] == "Off" else "Light: turning off"
    door_next_action = "Door: opening" if state['door_status'] == "Closed" else (
        "Door: closing" if state['door_status'] == "Open" else "Door action: N/A")

    return jsonify({
        "light_status": state['light_status'],
        "door_status": state['door_status'],
        "system_time": system_time,
        "light_next_action": light_next_action,
        "door_next_action": door_next_action,
        "timer_seconds": state['timer_seconds']
    })

@app.route('/set_light', methods=['POST'])
def set_light():
    if not session.get('authenticated'):
        return "Unauthorized", 401

    state['light_status'] = "On" if state['light_status'] == "Off" else "Off"
    return "OK"

@app.route('/set_door', methods=['POST'])
def set_door():
    if not session.get('authenticated'):
        return "Unauthorized", 401

    new_status = request.json.get('new_status', 'Override')
    state['door_status'] = new_status
    state['timer_seconds'] = 10
    return "OK"

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect('/')

def get_door_button_label():
    if state['door_status'] == "Closed":
        return "Closed"
    elif state['door_status'] == "Open":
        return "Open"
    elif state['door_status'] in ["Closing", "Opening"]:
        return f"{state['door_status']} (time remaining: {state['timer_seconds']} sec)"
    elif state['door_status'] == "Override":
        return "Override"
    elif state['door_status'] == "Failed to open":
        return "Failed to open"
    elif state['door_status'] == "Failed to close":
        return "Failed to close"
    return "Unknown"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
