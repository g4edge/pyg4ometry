import json
import pickle
import time

def _write_json(obj, path):
    with open(path, "w") as f:
        json.dump(obj, f)

def _load_json(path):
    with open(path, "r") as f:
        return json.load(f)


class Timer:
    def __init__(self):
        self.time0 = time.process_time()
        self.last_time = self.time0
        self.times = {}

    def add(self, name):
        now = time.process_time()
        duration = now - self.last_time
        if name not in self.times:
            self.times[name] = [duration]
        else:
            self.times[name].append(duration)
        self.last_time = now

    def write(self, path):
        _write_json(self.times, path)

    def writeAppend(self, path, verbose=False):
        try:
            existing = _load_json(path)

            if verbose:
                print(f"Appending samples to {path}")
            new = {}
            for key, value in self.times.items():
                new[key] = value + existing[key]
            _write_json(new, path)
        except FileNotFoundError:
            self.write(path)


    def __str__(self):
        return str(self.times)
