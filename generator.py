"""
server.py - The main program for running a web interface in this project
:author: Elliot Miller

Usage: python generator.py [FILE 1] [FILE 2] ... [FILE N]
"""
import patterns, waveform, numpy as np, stft, songsmith, random

class Generator(object):
    def __init__(self):
        self.pattern_dictionary = patterns.PatternDictionary()
    def add_wave(self, path):
        """Reads a wave file at `path` and imports its structure into a pattern
        dictionary."""
        # **********************************************************************
        # STEP 1: Open waveform from argv and get mono audio samples
        wav = waveform.from_file(path)
        wav.setchannelcount(1)
        samples = np.fromstring(wav.getsamples(), dtype='Int16').tolist()

        # **********************************************************************
        # STEP 2: Run STFT on samples
        matrix = stft.STFT_Matrix(samples, c_size=2**10)
        matrix.amplitudes = stft.triangular_smoothing(matrix.amplitudes, 3)
        matrix.smooth_amps_2()
        matrix.blip_filter_2()
        #matrix.spectrogram()

        # **********************************************************************
        # STEP 3: Convert the STFT to PatternDictionary
        self.pattern_dictionary.import_stft(matrix)

    def run(self):
        """Generate a song using the PatternDictionary"""
        song = songsmith.Phrase()
        # Check to be sure that there are patterns
        if len(self.pattern_dictionary.patterns) == 0:
            print "Error: There are no patterns to generate the music with!"
            return song
        # Add blank note to start
        song.chords.append(songsmith.Chord(notes=[songsmith.Note(0, 0, 0)]))
        pattern_choices = [0]
        for t in range(1, 200):
            # Determine all the possible next notes
            possibilities = []
            for depth in range(min(len(pattern_choices), patterns.SEARCH_DEPTH)):
                possibilities.append(self.pattern_dictionary.patterns[pattern_choices[t-1-depth]].subsequent_ids[depth])
            # choices = filter(lambda x: all((x in l) for l in possibilities), range(len(self.pattern_dictionary.patterns)))
            choices = filter(lambda x: all((x in l) for l in possibilities), possibilities[0])
            if len(choices)==0:
                choices = [0]
            # Randomly pick a note from the next possible notes
            next_id = 0 if len(choices)==0 else random.choice(choices)
            next_freq = self.pattern_dictionary.patterns[next_id].frequency
            next_dur = random.choice(self.pattern_dictionary.patterns[next_id].durations)
            if next_dur < 0.08: next_dur = 0 # Ignore the really short notes
            next_amp = random.choice(self.pattern_dictionary.patterns[next_id].amplitudes)
            # Add the new note to the songsmith class
            song.chords.append(songsmith.Chord(notes=[songsmith.Note(next_freq, next_dur, 16000)]))
            # Add the new note to the array of all the generated notes
            pattern_choices.append(next_id)
        # add overtones to the music
        song.addovertones(2)
        # return the generated song
        return song

if __name__=="__main__":
    import sys
    if len(sys.argv)>1:
        g = Generator()
        for i in range(1, len(sys.argv)):
            g.add_wave(sys.argv[i])
        g.run().play()
    else:
        print __doc__
