import subprocess
import time

class test_counter:
    def __init__(self):
        self.counter = 0
    def run(self):
        while True:
            self.counter += 1
            time.sleep(0.5)

tc = test_counter()

process = subprocess.Popen(tc.run(), stdout=subprocess.PIPE)

prev_counter = -1
while True:
