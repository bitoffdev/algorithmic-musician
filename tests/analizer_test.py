"""
Copyright EJM Software 2015
Test of the waveform module
More tests will be added
"""
# point the module search path to the parent directory
from sys import path
path.insert(0,'..')
# import the modules to be tested
import waveform, analizer
# load a wav file
wav = waveform.open_wave('Bowed-Bass-C2.wav')
# graph the data
CHUNK = 4096
for i in range(0, 3):
    print analizer.loudest_freqs(wav, CHUNK * i, CHUNK * i + CHUNK)
# raw_input()
# analizer.freq_plot(wav)
