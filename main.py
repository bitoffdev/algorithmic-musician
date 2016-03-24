# ******************************************************************************
# Copyright EJM Software 2016
# http://ejmsoftware.com
# ******************************************************************************
import waveform, stft, random, songsmith

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
        matrix.filter(28000)
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
                for other in indices:
                    if other != note:
                        self.patterns[index]["chords"].append(other)
                for last1index in last1indices:
                    self.patterns[last1index]["nexts"].append(index)
                for last2index in last2indices:
                    self.patterns[last2index]["next2"].append(index)
                indices.append(index)
            last2indices = last1indices
            last1indices = indices



    def generate(self, length=100):
        notelength = 0.15 # Minimum note length

        song = songsmith.Phrase()
        last1indices = [0]
        last2indices = [0]
        for i in range(length):
            indices = []
            # Pick the next note
            choices = []
            for last1index in last1indices:
                choices.extend(self.patterns[last1index]["nexts"])
            indices.append(random.choice(choices))
            if len(self.patterns[last1index]["chords"]) > 0:
                indices.append(random.choice(self.patterns[last1index]["chords"]))
            # Generate the next chord
            c = songsmith.Chord(notes=[])
            duration = max(random.choice(self.patterns[indices[0]]["durations"]), notelength)
            for index in indices:
                freq = 0 if self.patterns[index]["name"] == "" else songsmith.nametofreq(self.patterns[index]["name"] + "4")
                amplitude = 0 if self.patterns[index]["name"] == "" else 16000
                c.notes.append(songsmith.Note(freq,duration,amplitude))
            c.addovertones(5)
            last2indices = last1indices
            last1indices = indices
            song.chords.append(c)
        return song


if __name__ == "__main__":
    from sys import argv
    if len(argv)>1:
        gen = MusicGen()
        for i in range(1, len(argv)):
            gen.add_template(argv[i])
        song = gen.generate(100)
        samples = stft.np.fromstring(str(song), dtype='Int16').tolist()

        #song.play()
        wav = waveform.from_string(str(song), rate=44100, width=2, channels=1)
        waveform.to_file("demo.wav", wav)
