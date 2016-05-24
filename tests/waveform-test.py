"""
waveform-test.py - tests the waveform class
Copyright EJM Software 2016

Usage: python waveform-test.py PATH
"""
# ******************************************************************************
# Add the parent directory to Python's list of paths to search for modules
import sys
sys.path.append("../")
# ******************************************************************************
import waveform

if __name__=="__main__":
    if len(sys.argv) > 1:
        # LOAD A WAVEFORM FROM FILE
        wav = waveform.from_file(sys.argv[1])
        originalsamplewidth = wav.getsamplewidth()
        originalchannelcount = wav.getchannelcount()
        originalsize = len(wav.getsamples())

        # TEST ONE: LOADING AND WRITING
        # write the data to a file
        waveform.to_file('readertest.wav', wav)
        # check that the files are identical, ie. the data was read and processed properly
        import filecmp
        assert filecmp.cmp(sys.argv[1], 'readertest.wav')
        # delete the created test file
        from os import remove
        remove('readertest.wav')

        # TEST TWO: CHANGING THE CHANNEL COUNT
        # change the waveform sample width
        wav.setchannelcount(1)
        # check that the sample data reflects the change
        assert len(wav.getsamples()) == originalsize / originalchannelcount

        # TEST THREE: CHANGING SAMPLE WIDTH
        # change the waveform sample width
        wav.setsamplewidth(1)
        # check that the sample data reflects the change
        assert len(wav.getsamples()) == originalsize / originalchannelcount / originalsamplewidth

        print "Testing successful!"
    else:
        print __doc__
