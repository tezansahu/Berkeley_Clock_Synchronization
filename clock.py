import datetime
import time
import threading

class Clock:

    # Initialize the clock with the system time
    def __init__(self, sys_time = datetime.datetime.now(), drift_rate = 1):
        self.local_time = sys_time
        self.t = threading.Thread(target = self.tick, args = (drift_rate, ))
        self.t.start()
    # Keep the clock ticking at every millisecond with a specified drift rate [for simulation purposes]
    def tick(self, drift_rate = 1):
        while True:
            time.sleep(0.001)
            self.local_time = self.local_time + datetime.timedelta(seconds = drift_rate * 0.001)

    # Set the local clock time [To be used for synchronization]
    def setTime(self, time_dif):
        self.local_time = self.local_time + datetime.timedelta(seconds = time_dif)

    # Obtain the local clock time
    def getTime(self):
        return self.local_time