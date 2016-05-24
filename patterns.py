"""
patterns.py - A module for creating a dictionary of patterns found in music
Copyright EJM Software 2016
"""
import numpy as np

SEARCH_DEPTH = 3

class Pattern(object):
    """Represents possibilities for a note at the given frequency."""
    def __init__(self, _id, _freq):
        self.id = _id
        self.frequency = _freq
        self.subsequent_ids = [[] for i in range(SEARCH_DEPTH)]
        self.amplitudes = []
        self.durations = []

class PatternDictionary(object):
    """Class for containing Pattern objects. Use the import_stft method
    to create a PatternDictionary from the STFT class."""
    def __init__(self):
        self.patterns = []
    def find_id(self, _id):
        """Returns a Pattern object with the given id"""
        for i in xrange(len(self.patterns)):
            if self.patterns[i].id == _id:
                return i
        return -1
    def find_frequency(self, frequency):
        """Returns a Pattern object with the given frequency
        Note: Just find a frequency that is off by a factor of the twelth root of two"""
        for i in xrange(len(self.patterns)):
            # if self.patterns[i].frequency == frequency:
            #     return i
            ratio = self.patterns[i].frequency / frequency
            if ratio < 1.059463 and ratio > 0.94387:
                return i
        return -1
    def add_pattern(self, _freq):
        """Adds a new Pattern object to the dictionary"""
        self.patterns.append(Pattern(len(self.patterns), _freq))
        return len(self.patterns)-1


    def import_stft(self, stft):
        lastindices = [[0] for i in range(SEARCH_DEPTH)]
        # calculate the duration of each stft frame
        # this assumes that the wave file's frame rate was 44100 samples per second
        frame_length = stft.chunk_size*1./44100
        # create empty note
        blank_id = self.add_pattern(0)
        self.patterns[blank_id].durations.append(0)
        self.patterns[blank_id].amplitudes.append(0)
        # Iterate through the time axis
        for time in range(stft.chunk_count):
            currentindices = []
            # ranges is an array of the frequency ranges containing notes
            ranges = [[]]
            for freq in range(stft.frequency_cutoff_index):
                if stft.amplitudes[time][freq] > 5000:
                    if (freq-1) in ranges[len(ranges)-1]:
                        ranges[len(ranges)-1].append(freq)
                    else:
                        ranges.append([freq])
            # Find the max value in each chunk and interpolate it

            for i in range(len(ranges)):
                if len(ranges[i]) >= 3:
                    amp_range = stft.amplitudes[time][ranges[i][0]:ranges[i][len(ranges[i])-1]]
                    f_index = np.argmax(amp_range) + ranges[i][0]
                    f = stft.frequencies[f_index]
                    amp = stft.amplitudes[time][f_index]

                    # Get the pattern's identifier
                    pattern_id = self.find_frequency(f)
                    # Check if the pattern was played in the last frame
                    # If it was, simply increase the pattern's duration
                    if pattern_id in lastindices[-1]:
                        self.patterns[pattern_id].durations[-1] += frame_length
                    # If the pattern just started playing
                    else:
                        if pattern_id == -1:
                            pattern_id = self.add_pattern(f)
                            self.patterns[pattern_id].durations.append(frame_length)
                        else:
                            self.patterns[pattern_id].durations.append(frame_length)
                        # Add the amplitude to the note
                        self.patterns[pattern_id].amplitudes.append(amp)
                    # Add the pattern's identifier to the array of notes in the current chord
                    currentindices.append(pattern_id)
            # Update the array of last indices
            if currentindices != lastindices[-1]:
                temp = lastindices.pop(0)
                lastindices.append(currentindices)
                # Add the last indices to the subsequent_ids array for the previous note
                for i in temp:
                    for depth in range(SEARCH_DEPTH):
                        self.patterns[i].subsequent_ids[depth].extend(lastindices[depth])
