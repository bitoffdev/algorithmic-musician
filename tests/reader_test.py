"""
Copyright EJM Software 2015
Test of the waveform module
More tests will be added
"""
# point the module search path to the parent directory
from sys import path
path.insert(0,'..')
# import the modules to be tested
import waveform
# load a wav file
wav = waveform.open_wave('Bowed-Bass-C2.wav')
# write the data to a file
waveform.write_wave('readertest.wav', wav)
# check that the files are identical, ie. the data was read and processed properly
import filecmp
assert filecmp.cmp('Bowed-Bass-C2.wav', 'readertest.wav')
# delete the created test file
from os import remove
remove('readertest.wav')
# log that the tests were successful
print "Testing successful!"
