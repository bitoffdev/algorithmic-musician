"""
stft.py - A module for analyzing waveform audio files
Copyright EJM Software 2016

Usage: python stft.py FILENAME
"""
import sys, songsmith, fourier, waveform
import matplotlib.pyplot as plt
import numpy as np

class ProgressBar(object):
    def __init__(self, task="Working"):
        self.progress = 0 # Progress is a number from 0 to 50, for internal usage
        self.length = 50
        sys.stdout.write("==== " + task + " " + "=" * (self.length-6-len(task)) + "\n")
        sys.stdout.flush()
    def set(self, progress): # "progress" is a decimal from 0 to 1
        n = progress * self.length
        if n > self.progress:
            sys.stdout.write('.' * int(n - self.progress))
            sys.stdout.flush()
            self.progress = int(n)
    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        print ".\n==== DONE " + "="*(self.length - 10)



# ******************************************************************************
# HELPER METHODS
# ******************************************************************************

def BPM(x):
    shortest_note = min(x) # Get the duration of the shortest note
    deviations = [note % shortest_note for note in x] # Find how much each note differs from the shortest_note
    deviations = [(-shortest_note+deviation) if deviation > shortest_note/2 else deviation for deviation in deviations]
    average_deviation = sum(deviations)/len(deviations)
    average_note_time = shortest_note + average_deviation
    return 60. / average_note_time # Convert the beat time to beats per minute


def hcf(x, y, precision = 2):
    while(y>10**(-precision)):
        x, y = y, x % y
    return round(x, precision)

# ******************************************************************************
# SMOOTHING FUNCTIONS
# ******************************************************************************

def triangular_smoothing(x, n=3):
    x_padded = np.pad(x, ((n,n), (0,0)), 'constant')
    out = np.copy(x) * n
    for i in xrange(len(x)):
        for j in xrange(1,n+1):
            out[i] += x_padded[n+i-j]*(n+1-j)
            out[i] += x_padded[n+i+j]*(n+1-j)
        out[i] = out[i] / ((n+1)*(n+2)/2)
    return out

def moving_average(a, n=3) :
    ret = np.cumsum(np.pad(a, (n-1,0), 'constant', constant_values=(0, 0)), dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

def remove_anomalies(x):
    for i in xrange(2, len(x)-2):
        ave = (x[i-2]+x[i-1]+x[i+1]+x[i+2])*0.25
        if abs(ave - x[i]) > 20:
            x[i] = ave
    return x

# ******************************************************************************
# STFT CLASS
# ******************************************************************************

class STFT_Matrix(object):
    def __init__(self, samples, sample_rate=44100.0, c_size=1024):
        # NEW TEST VARIABLES
        input_chunk_size = c_size # Number of samples to take from "samples" per fft
        input_chunk_count = len(samples) // input_chunk_size
        input_padding = 8192 # Number of zeros to pad each chunk with (multiple of 2)
        padded_chunk_size = input_chunk_size + input_padding # Number of frequency bins in the fft output


        # Calculate the frequency information
        frequency_bins = int(5000*padded_chunk_size/sample_rate)
        # frequency_bins = padded_chunk_size // 2 # The number of frequency bins (trim off the top half)
        frequency_bin_size = sample_rate / padded_chunk_size # The difference in max and min Hz per frequency bin
        frequencies = fourier.freqs(padded_chunk_size, sample_rate)[:frequency_bins]

        # output matrix
        self.amplitudes = np.zeros((input_chunk_count, len(frequencies))) # 2D array containing amp in terms of frequency at a time

        window = np.hamming(input_chunk_size)
        with ProgressBar("Performing STFT") as bar:
            for i in range(0, input_chunk_count*input_chunk_size, input_chunk_size):
                amps = fourier.fft(np.pad(window*samples[i:i+input_chunk_size], (input_padding/2, input_padding/2), 'constant'))
                amps = (np.array(amps) / padded_chunk_size).tolist()
                amps = [abs(x.real) for x in amps] # use real part only
                amps = amps[:frequency_bins]
                self.amplitudes[i/input_chunk_size] = amps
                bar.set(i*1./(input_chunk_count*input_chunk_size))

        # Set old variables
        self.chunk_size = input_chunk_size
        self.chunk_count = input_chunk_count
        self.frequency_precision = frequency_bin_size
        self.frequencies = frequencies
        self.frequency_cutoff_index = frequency_bins-1
        self.frequency_cutoff = frequencies[frequency_bins-1]

        print len(self.frequencies), frequency_bin_size


    def filter_blips(self, threshold=None, surrounding=2):
        if threshold==None: threshold = 5000 / (self.chunk_count/100)
        """Removes notes that are shorter than 0.05 seconds (1200 beats per minutes, 20 beats per second)"""
        for freq in range(self.frequency_cutoff_index):
            for time in range(self.chunk_count):
                sumation = 0
                for i in range(max(time-surrounding, 0), min(self.chunk_count, time+surrounding+1)):
                    sumation += self.amplitudes[i][freq]
                if sumation < threshold:
                    self.amplitudes[time][freq] = 0
        return
    def smooth_amps(self):
        for time in range(self.chunk_count):
            for freq in range(self.frequency_cutoff_index):
                if self.amplitudes[time][freq] < 20:
                    self.amplitudes[time][freq] = 0
            frame_amp = sum(self.amplitudes[time])
            if frame_amp!=0:
                for freq in range(self.frequency_cutoff_index):
                    self.amplitudes[time][freq] *= 2**15 / frame_amp / 2
    def smooth_amps_2(self):
        with ProgressBar("Smoothing STFT Amplitudes") as bar:
            for time in range(self.chunk_count):
                frame_max = max(self.amplitudes[time])
                if frame_max!=0:
                    for freq in range(self.frequency_cutoff_index):
                        self.amplitudes[time][freq] *= 2**15 / frame_max
                bar.set(time*1./self.chunk_count)
    def collapse_overtones(self):
        for time in range(self.chunk_count):
            for freq in range(self.frequency_cutoff_index):
                if self.amplitudes[time][freq] > 40:
                    for harmonic in range(2, 10):
                        # Note that multiplying a freq index by x will also
                        # multiply the frequency by x
                        if len(self.amplitudes[time]) > freq*harmonic:
                            value = min(self.amplitudes[time][freq*harmonic], self.amplitudes[time][freq] / harmonic)
                            #value = self.amplitudes[time][freq*harmonic]
                            self.amplitudes[time][freq*harmonic] -= value
                            self.amplitudes[time][freq] += value
    def filter(self, min, max=32000):
        for time in range(self.chunk_count):
            for freq in range(self.frequency_cutoff_index):
                if self.amplitudes[time][freq] < min:
                    self.amplitudes[time][freq] = 0
                elif self.amplitudes[time][freq] > max:
                    self.amplitudes[time][freq] = max

    def blip_filter_2(self):
        """Use this method!!! This is my most recent filter function and one of
        the best I have written. It works by removing all notes that are shorter
        than `min_frames`."""
        min_frames = 15
        # iterate through the the times for each frequency and remove notes that are shorter than "min_frames"
        note_start = -1
        for freq in range(self.frequency_cutoff_index):
            for time in range(self.chunk_count):
                if note_start > -1:
                    if self.amplitudes[time][freq] <= 7500:
                        # THE note just ended
                        # get sum of all the frames in the note
                        if time - note_start < min_frames:
                            for i in range(note_start, time+1):
                                self.amplitudes[i][freq] = 0
                        # Reset the note start index
                        note_start = -1
                elif self.amplitudes[time][freq] > 7500:
                    # The note just started
                    note_start = time
                else:
                    self.amplitudes[time][freq] = 0


    def spectrogram(self):
        a = np.swapaxes(self.amplitudes, 0, 1) # Create a numpy matrix from data and swap the x and y axis
        im = plt.imshow(a, origin='lower', extent=[0, self.chunk_count*self.chunk_size/44100.0, 0, self.frequency_cutoff], interpolation='nearest')
        # Style the plot
        plt.xlabel("time (seconds)")
        plt.ylabel("frequency (hz)")
        #plt.ylim(0, self.frequency_cutoff)
        plt.axes().set_aspect('auto', 'datalim')
        # Show the plot
        plt.show()
    def amp_graph(self):
        amplitudes = [max(self.amplitudes[t]) for t in range(self.chunk_count)]
        plt.plot(np.linspace(0, self.chunk_count*self.chunk_size/44100, len(amplitudes)), amplitudes, "r")
        plt.xlabel("time (seconds)")
        plt.ylabel("amplitude")
        #plt.ylim(0, self.frequency_cutoff)
        plt.show()
    def to_song(self):
        # max_freqs = [self.frequencies[np.argmax(chunk)] for chunk in self.amplitudes]
        # # Container for entire song data
        song = songsmith.Phrase()
        #
        # for i in range(len(max_freqs)):
        #     c = songsmith.Chord(
        #         notes=[songsmith.Note(max_freqs[i],self.chunk_size*1./44100,16000)]
        #     )
        #     if i==0 or not c==song.chords[len(song.chords)-1]:
        #         song.chords.append(c)
        #     else:
        #         num = len(song.chords)-1
        #         for n in range(len(song.chords[num].notes)):
        #             song.chords[num].notes[n].duration += self.chunk_size*1./44100
        # return song

        for t in range(len(self.amplitudes)):
            # Create chord
            c = songsmith.Chord(notes=[])
            # Add rest if there are no notes
            if sum(self.amplitudes[t]) == 0:
                c.notes = [songsmith.Note(0,self.chunk_size*1./44100,0)]
            # Add notes if there are notes
            else:
                for f in range(len(self.frequencies)):
                    if self.amplitudes[t][f] != 0:
                        c.notes.append(songsmith.Note(self.frequencies[f],self.chunk_size*1./44100,16000))
            # Add the newly created chord to the song
            if t==0 or not c==song.chords[len(song.chords)-1]:
                song.chords.append(c)
            else:
                num = len(song.chords)-1
                for n in range(len(song.chords[num].notes)):
                    song.chords[num].notes[n].duration += self.chunk_size*1./44100
        return song

    def to_song2(self):
        song = songsmith.Phrase()
        # Iterate through each of the time chunks
        for time in range(10):#range(self.chunk_count):
            # Indices is an array of the frequency ranges containing notes
            indices = [[]]
            for freq in range(self.frequency_cutoff_index):
                if self.amplitudes[time][freq] > 5000:
                    if (freq-1) in indices[len(indices)-1]:
                        indices[len(indices)-1].append(freq)
                    else:
                        indices.append([freq])
            # Create a container for the new chord
            # Find the max value in each chunk and interpolate it
            for i in range(len(indices)):
                if len(indices[i]) >= 3:
                    amp_range = self.amplitudes[time][indices[i][0]:indices[i][len(indices[i])-1]]
                    f_index = np.argmax(amp_range) + indices[i][0]
                    # CONSIDER ADDING QUADRATIC PEAK INTERPOLATION
                    #print self.frequencies[f_index], f_index, indices[i]


            print
        return


# If we are running the script, analize the wav file that was passed in
if __name__ == "__main__":
    if len(sys.argv)>1:
        # STEP 1: Open waveform from argv and get mono audio samples
        wav = waveform.open_wave(sys.argv[1])
        wav.setchannelcount(1)
        samples = np.fromstring(wav.getsamples(), dtype='Int16').tolist()

        # STEP 2: Run STFT on samples
        matrix = STFT_Matrix(samples, c_size=2**10)
        matrix.amplitudes = triangular_smoothing(matrix.amplitudes, 3)
        matrix.smooth_amps_2()
        matrix.blip_filter_2()
        matrix.spectrogram()
    else:
        print __doc__
