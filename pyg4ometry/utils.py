import pickle
import time


class Timer:
    def __init__(self):
        self.time0 = time.process_time()
        self.last_time = self.time0
        self.times = {}

    def add(self, name):
        now = time.process_time()
        duration = now - self.last_time
        self.times[name] = duration
        self.last_time = now

    def write(self, name):
        with open(f"{name}-timings.pickle", "wb") as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    def __str__(self):
        return str(self.times)
