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
analizer.freq_plot(wav)
