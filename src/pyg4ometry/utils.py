import pickle
import time
import numpy as np
from copy import deepcopy

def _write_pickle(obj, path):
    with open(path, "wb") as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def _load_pickle(path):
    with open(path, "rb") as f:
        return pickle.load(f)


class Samples:
    def __init__(self, **metadata):
        self.metadata = metadata
        self.times = {}

    def add(self, name, time):
        if name not in self.times:
            self[name] = [time]
        else:
            self[name].append(time)

    def n_samples_description(self):
        return "\n".join([f"{k}: {len(v)} samples" for
                          k, v in self.times.items()])

    def sample_names(self, exclude=None):
        if exclude is None:
            exclude = []
        return [l for l in self.times.keys() if l not in exclude]

    def means(self, exclude=None):
        if exclude is None:
            exclude = []
        return {key: np.mean(val)
                for key, val in self.times.items() if key not in exclude}

    def stds(self, exclude=None):
        if exclude is None:
            exclude = []
        return {key: np.std(val, ddof=1)
                for key, val in self.times.items() if key not in exclude}

    @classmethod
    def from_existing(cls, *samples):
        """Merge two or more existing samples non-destructively to create a new
        Sample instance.

        """
        result = cls()
        result.times = deepcopy(samples[0].times)

        if len(samples) == 1:
            return result
        
        all_sample_names = set() # Get all sample names across all samples.
        for s in samples:
            all_sample_names = all_sample_names.union(s.sample_names())

        for sample in samples[1:]:  # Loop over samples and sample names.
            for sample_name in all_sample_names:
                if sample_name not in result:
                    result[sample_name] = [sample[sample_name]]
                else:
                    result[sample_name].extend(sample[sample_name])
        return result
        
    def __str__(self):
        return str(self.times)

    def write(self, path):
        _write_pickle(self, path)
    
    def writeAppend(self, path, verbose=False):
        try:
            existing = _load_pickle(path)

            if verbose:
                print(f"Appending samples to {path}")
                print(self.n_samples_description())
            new = Samples.from_existing(existing, self)

            _write_pickle(new, path)
        except FileNotFoundError:
            if verbose:
                print(f"Writing new samples to {path}")
            self.write(path)

    def __getitem__(self, key):
        return self.times[key]

    def __setitem__(self, key, value):
        self.times[key] = value

    def __contains__(self, key):
        return key in self.times
            
    

class Timer:
    """A class for recording the CPU time at specific positions within code
    with the use of a name.  Records time stamps in a Samples instance.
    To record multiple samples of a given event, simply call add with the
    same name repeatedly.

    timer = Timer()

    while True:
        ...
        timer.add("step1")
        ...
        timer.add("step2")

    mean_step1 = timer.samples.means()["step1"]
    std_step1 = timer.samples.stds()["step1"]

    """
    def __init__(self, **metadata):
        self.metadata = metadata
        self.time0 = time.process_time()
        self.last_time = self.time0
        self.samples = Samples(**metadata)

    def add(self, name):
        assert name != "total", "use updateTotal"
        now = time.process_time()
        duration = now - self.last_time
        self.samples.add(name, duration)
        self.last_time = now

    def update(self):
        """Update the last_time attribute to now."""
        self.last_time = time.process_time()

    def __str__(self):
        return str(self.samples)

    def updateTotal(self):
        now = time.process_time()
        total = now - self.time0
        self.time0 = time.process_time()
        self.samples.add("total", total)
