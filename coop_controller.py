#!/user/bin/env python

"""
Created on Fri Dec 10 11:34:53 2021

@author: jmatt
"""

import coop_functions as CF
import traceback
from flask import Flask, session, request, redirect, jsonify, render_template
from multiprocessing import Process, Queue
import time
import subprocess
import signal
import sys
import hashlib
import web_app as WA

# app = Flask(__name__)
# app.secret_key = 'your_secret_key_here'  # Replace with a strong secret key

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



# def run_coop_controller(command_queue, response_queue):
#     controller = CF.coop_controller()
#     while True:
#         # Simulate running the controller
#         controller.update()
#         with open('/home/circuit/github/coop_controller/test.log','a') as f:
#             f.write('test\n')
#         # Check for commands from the main process
#         if not command_queue.empty():
#             command = command_queue.get()
#             allowable_commands = [
#                 'update',
#                 'raise_door',
#                 'lower_door',
#                 'stop_door',
#                 'cancel_override_door',
#                 'light_on',
#                 'light_off',
#                 'cancel_override_light',
#                 'clear_errors'
#             ]
#             if command in allowable_commands:
#                 if command == "raise_door":
#                     controller.override_door_raise()
#                 elif command == "lower_door":
#                     controller.override_door_lower()
#                 elif command == "stop_door":
#                     controller.door_stop()
#                 elif command == "cancel_override_door":
#                     controller.cancel_door_override()
#                 elif command == "light_on":
#                     controller.override_light_on()
#                 elif command == "light_off":
#                     controller.override_light_off()
#                 elif command == "cancel_override_light":
#                     controller.cancel_light_override()
#                 elif command == "clear_errors":
#                     controller.cancel_error()
#                 response_queue.put(controller.return_current_state())

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
        print(f"Starting Flask app on port {port}...")
        WA.app.run(port=port, debug=True)
    except Exception as e:
        print(f"Failed to start Flask app: {e}")
    finally:
        cleanup(ngrok_process,controller_process)
    
