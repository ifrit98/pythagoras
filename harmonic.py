import numpy as np
from numpy import pi, sin, array, c_, int16
from pprint import pprint as pp
from pprint import pformat
from collections import OrderedDict
import pygame


"""
GOLD IS TO BE FOUND ASSOCIATING ANGLES IN PLATONIC SOLIDS WITH PYTHAGOREAN HARMONICS
"""

ORDERED_NAMES = [
    'base',
    'minor second', 'major second', 'minor third', 'major third',
    'fourth', 'tritone', 'fifth', 'minor sixth', 
    'major sixth', 'minor seventh', 'major seventh', 'octave'
]

ORDERED_SERIES = [
    1,
    16/15, 9/8, 6/5, 5/4, 
    4/3, 45/32, 3/2, 8/5, 
    5/3, 9/5, 15/8, 2/1
]

NAMES = [
    'base',
    'octave', 'fifth', 'fourth', 'major sixth', 
    'major third', 'minor third', 'minor sixth', 'minor seventh', 
    'major second', 'major seventh', 'minor second', 'tritone'
]

SERIES = [
    1, 
    2/1, 3/2, 4/3, 5/3, 
    5/4, 6/5, 8/5, 9/5, 
    9/8, 15/8, 16/15, 45/32
]

# SHOW AS PAIRS OF POLYGONS: pair(n-sided-polygon(5), b-sided-polygon(4))
base_freq = 440 # 128 # Hz

harmonics = OrderedDict(zip(NAMES, SERIES))
print("Harmonics:")
pp(harmonics)

ordered_harmonics = OrderedDict(zip(ORDERED_NAMES, ORDERED_SERIES))
print("\nOrdered Harmonics")
pp(ordered_harmonics)

class Tone(object):
    """

    # sampling frequency, size, channels, buffer

    # Sampling frequency
    # Analog audio is recorded by sampling it 44,100 times per second, 
    # and then these samples are used to reconstruct the audio signal 
    # when playing it back.

    # size
    # The size argument represents how many bits are used for each 
    # audio sample. If the value is negative then signed sample 
    # values will be used.

    # channels
    # 1 = mono, 2 = stereo

    # buffer
    # The buffer argument controls the number of internal samples 
    # used in the sound mixer. It can be lowered to reduce latency, 
    # but sound dropout may occur. It can be raised to larger values
    # to ensure playback never skips, but it will impose latency on sound playback. 

    """
    def __init__(self, freq=440, sampleRate=44100):
        pygame.mixer.init(sampleRate, -16, 2, 512)
        self.freq = freq # Hz
        self.sampleRate = sampleRate
        self.array = None
        self.sound = self.make_sound()

    def make_sound_arr(self):
        return array(
            [4096 * sin(2.0 * pi * self.freq * x / self.sampleRate) \
                for x in range(0, self.sampleRate)]).astype(int16)
    
    def make_sound(self):
        self.arr = self.make_sound_arr()
        return pygame.sndarray.make_sound(c_[self.arr, self.arr])

    def play(self, delay=1000):
        self.sound.play(-1)
        pygame.time.delay(delay)
        self.sound.stop()


class HarmonicStack(object):
    # TODO: Why aren't certain tones being emphasized? Need to adjust amplitude based on # partial?
    def __init__(self, freqs, sampleRate=44100):
        assert hasattr(freqs, '__len__')
        pygame.mixer.init(sampleRate, -16, 2, 512)
        self.freqs = freqs # Hz
        self.sampleRate = sampleRate
        self.sound = self.make_sound_stack()

    def make_sound_arr(self, freq):
        return array(
            [4096 * sin(2.0 * pi * freq * x / self.sampleRate) \
                for x in range(0, self.sampleRate)]).astype(int16)

    def make_sound_stack(self):
        freq_arr = []
        for hz in self.freqs:
            freq_arr.append(self.make_sound_arr(hz))
        self.freq_array = (np.sum(np.asarray(freq_arr), axis=0) / len(freq_arr)).astype(int16)
        self.sound = pygame.sndarray.make_sound(c_[self.freq_array, self.freq_array])
        return self.sound

    def play_stack(self, delay=5000):
        self.sound.play(-1)
        pygame.time.delay(delay)
        self.sound.stop()
    

class Scale(object):
    def __init__(self, series_hz, delay=1000):
        self.series_hz = series_hz
        self.delay = delay
        self.tones = self.make_scale_tones()
    
    def make_scale_tones(self):
        return [Tone(freq) for freq in self.series_hz]
    
    def play(self, delay=None):
        delay = delay or self.delay
        [t.play(delay) for t in self.tones]


from toolz import interpose
class Stutter(object):
    """
    Interpose freq array with first element of sequence (base freq).
    e.g. 
        freq_arr = [256, 512, 768, 1024]
        interposed = [256, 512, 256, 768, 256, 1024]

    """
    def __init__(self, freqs):
        self.freqs = freqs
        self.interposed_freqs = np.asarray(list(interpose(freqs[0], freqs)))[1:]
        self.tones = self.make_tones()
    
    def make_tones(self):
        return [Tone(freq) for freq in self.interposed_freqs]

    def play(self, delay=2000):
        [t.play(delay) for t in self.tones]


class Harmonic(object):
    def __init__(self, base_freq=440):
        self.base_freq = base_freq
        self.series = [
            1, 
            2/1, 3/2, 4/3, 5/3, 
            5/4, 6/5, 8/5, 9/5, 
            9/8, 15/8, 16/15, 45/32
        ]
        self.names = [
            'base',
            'octave', 'fifth', 'fourth', 'major sixth', 
            'major third', 'minor third', 'minor sixth', 'minor seventh', 
            'major second', 'major seventh', 'minor second', 'tritone'
        ]
        self.harmonics = self.make_harmonic()
        self.scale = np.asarray(list(self.harmonics.values()))

    def __str__(self):
        return pformat(self.harmonics)

    def make_harmonic(self):
        return OrderedDict(
            zip(self.names, np.asarray(self.series) * self.base_freq)
        )


class OrderedHarmonic(object):
    def __init__(self, base_freq=440):
        self.base_freq = base_freq
        self.series = ORDERED_SERIES
        self.names = ORDERED_NAMES

        self.harmonics = self.make_harmonic()
        self.scale = np.asarray(list(self.harmonics.values()))

    def __str__(self):
        return pformat(self.harmonics)

    def make_harmonic(self):
        return OrderedDict(
            zip(self.names, np.asarray(self.series) * self.base_freq)
        )



if False:
    h = Harmonic(256)
    oh = OrderedHarmonic(256)
    stuttered_harmonic_scale = lambda base_freq: Stutter(OrderedHarmonic(base_freq).scale)
    harmonic_scale = lambda base_freq: Stutter(Harmonic(base_freq).scale)

    h = harmonic_scale(256)
    h.play()