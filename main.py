"""
main.py - a file for generating new music
Copyright EJM Software 2016

This file has been deprecated. Use generator.py instead.
"""
import waveform, stft, random, songsmith

class MusicGen(object):
    def __init__(self):
        self.patterns = []
        self.search_depth = 4
    def add_template(self, filename):
        """Adds a song to the music generator's knowledge base"""
        # STEP 1: Read the waveform music file at the given path
        wave = waveform.from_file(filename)
        print "Setting channel count"
        wave.setchannelcount(1)
        print "Making samples"
        samples = stft.np.fromstring(wave.getsamples(), dtype='Int16').tolist()
        print "Done"

        # STEP 2: Parse the waveform music into a music note format using STFT
        matrix = stft.STFT_Matrix(samples, c_size=2**10)
        matrix.amplitudes = stft.triangular_smoothing(matrix.amplitudes, 5)
        matrix.smooth_amps_2()
        matrix.filter(31000)
        matrix.spectrogram()

        # STEP 3: Create an array with all the patterns found in the music
        # Notes about the self.patterns dictionary:
        #     "Next" - an array
        # Parse the data into songsmith format
        # Then, place each note into the patterns dictionary
        song = matrix.to_song()
        #print len(song.chords)
        song.debug()
        # Note: In "next" array, the 0 index is the newest
        self.patterns.append({"name":"", "frequency":"", "durations":[0], "next":[[] for i in range(self.search_depth)], "chords":[]})
        lastindices = [[0] for i in range(self.search_depth)]

        for chord in song.chords:
            currentindices = []
            # Skip notes shorter than 25 bps, its probably trash data
            if chord.notes[0].duration < 0.04:
                continue
            # Add the notes from the chord
            for note in chord.notes:
                name = songsmith.freqtoname(note.frequency)[:-1]
                currentindex = next((i for i,v in enumerate(self.patterns) if v["name"]==name), None)
                if currentindex==None:
                    currentindex = len(self.patterns)
                    self.patterns.append({"name":name, "frequency":note.frequency, "durations":[], "next":[[] for i in range(self.search_depth)], "chords":[]})
                self.patterns[currentindex]["durations"].append(note.duration)
                for other in currentindices:
                    if other != note:
                        self.patterns[currentindex]["chords"].append(other)
                # Pack the next note data into the patterns dictionary
                for depth, indices in enumerate(lastindices):
                    for index in indices:
                        self.patterns[index]["next"][depth].append(currentindex)
                currentindices.append(currentindex)
            # Update the lastindices for the next loop
            lastindices.pop()
            lastindices.insert(0, currentindices)
            # last2indices = last1indices
            # last1indices = currentindices
        # Add the blank notes to the end of the song
        # for last1index in last1indices:
        #     self.patterns[last1index]["nexts"].append(0)
        # for last2index in last2indices:
        #     self.patterns[last2index]["next2"].append(0)
        # Add as many empty notes to the end of the patterns as the search_depth
        for depth, indices in enumerate(lastindices):
            for index in indices:
                for i in range(depth, self.search_depth):
                    self.patterns[index]["next"][i].append(0)



    def generate(self, length=100):
        song = songsmith.Phrase()
        lastindices = [[0] for i in range(self.search_depth)]
        for i in range(length):
            currentindices = []
            # Pick the next note
            choices = []
            for depth, indices in enumerate(lastindices):
                for index in indices:
                    choices.extend(self.patterns[index]["next"][depth])
            currentindices.append(random.choice(choices))
            # Generate the next chord
            c = songsmith.Chord(notes=[])
            duration = random.choice(self.patterns[currentindices[0]]["durations"])
            for index in currentindices:
                freq = 0 if self.patterns[index]["name"] == "" else songsmith.nametofreq(self.patterns[index]["name"] + "4")
                amplitude = 0 if self.patterns[index]["name"] == "" else 16000
                c.notes.append(songsmith.Note(freq,duration,amplitude))
            c.addovertones(5)
            # Update the lastindices for the next loop
            lastindices.pop()
            lastindices.insert(0, currentindices)
            song.chords.append(c)
        return song


if __name__ == "__main__":
    from sys import argv
    if len(argv)>1:
        gen = MusicGen()
        for i in range(1, len(argv)):
            gen.add_template(argv[i])
        #print gen.patterns
        song = gen.generate(100)
        #samples = stft.np.fromstring(str(song), dtype='Int16').tolist()

        # print "\n\n"
        #
        # for chord in song.chords:
        #     print [vars(note) for note in chord.notes]

        matrix = stft.STFT_Matrix(song.asarray(), c_size=2**10)
        #matrix.amplitudes = stft.triangular_smoothing(matrix.amplitudes, 10)
        #matrix.smooth_amps_2()
        #matrix.filter(31000)
        matrix.spectrogram()

        song.play()
        #wav = waveform.from_string(str(song), rate=44100, width=2, channels=1)
        #waveform.to_file("demo.wav", wav)
