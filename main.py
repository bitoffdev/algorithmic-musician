# ******************************************************************************
# Copyright EJM Software 2016
# http://ejmsoftware.com
# ******************************************************************************
import waveform
import keyfinder
import stft
import random
import songsmith # Used in generate()

class NotePattern(object):
    def __init__(self):
        self.name
        self.frequency
        self.durations = []
        self.duration = []


class MusicGen(object):
    def __init__(self):
        self.patterns = []
    def add_template(self, filename):
        """Adds a song to the music generator's knowledge base"""
        # Read the waveform music file at the given path
        wave = waveform.from_file(filename)
        print "Setting channel count"
        wave.setchannelcount(1)
        print "Making samples"
        samples = stft.np.fromstring(wave.getsamples(), dtype='Int16').tolist()
        print "Done"
        # Create an STFT from the sample data in the waveform file
        matrix = stft.STFT_Matrix(samples, c_size=2**10)
        matrix.amplitudes = stft.triangular_smoothing(matrix.amplitudes, 10)
        matrix.smooth_amps_2()
        matrix.filter(25000)
        matrix.spectrogram()
        # Parse the data into songsmith format
        # Then, place each note into the patterns dictionary
        song = matrix.to_song()
        # Method 2
        self.patterns.append({"name":"", "frequency":"", "durations":[0], "nexts":[], "next2":[], "chords":[]}) 
        last1indices = [0]
        last2indices = [0]
            
        for chord in song.chords:
            indices = []
            for note in chord.notes:
                name = songsmith.freqtoname(note.frequency)[:-1]
                index = next((i for i,v in enumerate(self.patterns) if v["name"]==name), None)
                if index==None:
                    index = len(self.patterns)
                    self.patterns.append({"name":name, "frequency":note.frequency, "durations":[], "nexts":[], "next2":[], "chords":[]})
                self.patterns[index]["durations"].append(note.duration)
                for last1index in last1indices:
                    self.patterns[last1index]["nexts"].append(index)
                for last2index in last2indices:
                    self.patterns[last2index]["next2"].append(index)
                indices.append(index)
            last2indices = last1indices
            last1indices = indices 
                


    def generate(self, length=100):
        notelength = 0.75
        
        song = songsmith.Phrase()
        lastnoteindex = 0
        lastlastnote = 0
        for i in range(length):
            # Pick the next note
            next = 0
            if len(self.patterns[lastnoteindex]["nexts"]) > 0:
                next = random.choice(self.patterns[lastnoteindex]["nexts"])
                if len(self.patterns[lastlastnote]["next2"]) > 0:
                    possibilities = list(set(self.patterns[lastlastnote]["next2"]) & set(self.patterns[lastnoteindex]["nexts"]))
                    if len(possibilities) > 0:
                        next = random.choice(possibilities)
            # Generate the note
            if self.patterns[next]["name"] == "":
                c = songsmith.Chord(
                    notes=[songsmith.Note(0,0.5,0)]
                )
            else:
                freq = songsmith.nametofreq(self.patterns[next]["name"] + "4")
                duration = notelength#random.choice(self.patterns[next]["durations"])
                c = songsmith.Chord(
                    notes=[
                        songsmith.Note(freq,duration,16000)
                    ]
                )
                c.addovertones(3)
            lastlastnote = lastnoteindex
            lastnoteindex = next
            song.chords.append(c)
        return song


if __name__ == "__main__":
    from sys import argv
    if len(argv)>1:
        gen = MusicGen()
        for i in range(1, len(argv)):
            gen.add_template(argv[i])
        print gen.patterns
        song = gen.generate(200)
        samples = stft.np.fromstring(str(song), dtype='Int16').tolist()
        matrix = stft.STFT_Matrix(samples, c_size=2**11)
        matrix.spectrogram()
        song.play()
