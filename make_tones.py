from harmonic import ordered_harmonics, harmonics, ordered_harmonics_440, harmonics_440, series, ordered_series
from sound import Tone

tones = {k: Tone(v) for k,v in ordered_harmonics.items()}

class Scale(object):
    def __init__(self, series_hz, base_freq=440, delay=250):
        self.series_hz = series_hz
        self.base_freq = base_freq
        self.delay = delay
    
    def make_scale_tones(self):
        self.tones = [Tone(freq) for freq in self.series_hz]
    
    def play(self, delay=None):
        delay = delay or self.delay
        [t.play(delay) for t in self.tones]