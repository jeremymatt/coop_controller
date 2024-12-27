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


if __name__ == '__main__':
    port = 8000
    ngrok_static_url = 'chickencoop.fun'

    # Start Ngrok
    ngrok_process = start_ngrok(port, ngrok_static_url)
    if not ngrok_process:
        print("Ngrok failed to start. Exiting.")
        exit(1)

    print('\nINIT CONTROLLER PROCESS\n')
    controller_process = Process(target=CF.run_coop_controller, args=(CF.command_queue, CF.response_queue))
    print('\nSTART CONTROLLER PROCESS\n')
    controller_process.start()

    # Start Flask app
    try:
        print(f"Starting Flask app on port {port}...")
        WA.app.run(port=port, debug=True)
    except Exception as e:
        print(f"Failed to start Flask app: {e}")
    finally:
        cleanup(ngrok_process,controller_process)
    
