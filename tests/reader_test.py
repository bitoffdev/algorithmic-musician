"""
Copyright EJM Software 2015
Test of the waveform module
"""
# point the module search path to the parent directory
from sys import path
path.insert(0,'..')
# import the modules to be tested
import waveform


# LOAD A WAVEFORM FROM FILE
wav = waveform.from_file('Bowed-Bass-C2.wav')
originalsamplewidth = wav.getsamplewidth()
originalchannelcount = wav.getchannelcount()
originalsize = len(wav.getsamples())


# TEST ONE: LOADING AND WRITING
# write the data to a file
waveform.to_file('readertest.wav', wav)
# check that the files are identical, ie. the data was read and processed properly
import filecmp
assert filecmp.cmp('Bowed-Bass-C2.wav', 'readertest.wav')
# delete the created test file
from os import remove
remove('readertest.wav')


# TEST TWO: CHANGING THE CHANNEL COUNT
# change the waveform sample width
wav.setchannelcount(1)
# check that the sample data reflects the change
assert len(wav.getsamples()) == originalsize / originalchannelcount


# TEST TWO: CHANGING SAMPLE WIDTH
# change the waveform sample width
wav.setsamplewidth(1)
# check that the sample data reflects the change
assert len(wav.getsamples()) == originalsize / originalchannelcount / originalsamplewidth


# log that the tests were successful
print "Testing successful!"
