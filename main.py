# ******************************************************************************
# Copyright EJM Software 2016
# http://ejmsoftware.com
# ******************************************************************************
import waveform
import keyfinder
import stft
import random
import songsmith # Used in generate()

class MusicGen(object):
    def __init__(self):
        self.patterns = {}
        for name in keyfinder.NOTE_NAMES:
            self.patterns[name] = []
    def add_template(self, filename):
        """Adds a song to the music generator's knowledge base"""
        # Read the waveform music file at the given path
        wave = waveform.open_wave(filename)
        wave.setchannelcount(1)
        samples = stft.np.fromstring(wave.getsamples(), dtype='Int16').tolist()
        # Create an STFT from the sample data in the waveform file
        matrix = stft.STFT_Matrix(samples, c_size=2**10)
        matrix.amplitudes = stft.triangular_smoothing(matrix.amplitudes)
        matrix.smooth_amps_2()
        # Parse the data into songsmith format
        # Then, place each note into the patterns dictionary
        song = matrix.to_song()
        lastnote = ""
        for chord in song.chords:
            if lastnote=="":
                lastnote = songsmith.freqtoname(chord.notes[0].frequency)[:-1]
            else:
                for note in chord.notes:
                    notename = songsmith.freqtoname(note.frequency)[:-1]
                    self.patterns[lastnote].append(notename)
                    lastnote = notename        
        
    def generate(self, length=60):
        song = songsmith.Phrase()
        n = "C"
        for i in range(length):
            if len(self.patterns[n]) > 0:
                n = self.patterns[n][random.randint(0, len(self.patterns[n])-1)]
            else:
                n = "C"
            if n=="":
                c = songsmith.Chord(
                    notes=[songsmith.Note(0,0.25,0)]
                )
                n = "C"
            else:
                c = songsmith.Chord(
                    notes=[songsmith.Note(songsmith.nametofreq(n + "4"),0.25,16000)]
                )
            song.chords.append(c)
            
        song.play()
        


if __name__ == "__main__":
    from sys import argv
    if len(argv)>1:
        gen = MusicGen()
        for i in range(1, len(argv)):
            gen.add_template(argv[i])
        print gen.patterns
        gen.generate()