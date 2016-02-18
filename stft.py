"""Module for analizing waveform audio files"""
import songsmith
import matplotlib.pyplot as plt
import numpy as np
import fourier
import sys # For progress bar

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
    out = np.copy(x) * n
    for i in xrange(len(x)):
        if i>n-1 and i<len(x)-n:
            for j in xrange(1,n+1):
                out[i] += x[i-j]*(n+1-j)
                out[i] += x[i+j]*(n+1-j)
            out[i] = out[i] / ((n+1)*(n+2)/2)
        else:
            out[i] = out[i] / n
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
        # Time axis
        self.chunk_size = c_size # Chunk size == frequency count
        self.chunk_count = len(samples) // self.chunk_size
        # Frequency axis
        self.frequency_precision = sample_rate / self.chunk_size # The accuracy of the frequencies (e.g. How many Hz off are the freqs?)
        self.frequency_cutoff = 5000 # Frequencies above this Hertz will be discarded
        self.frequency_cutoff_index = int(self.frequency_cutoff*self.chunk_size/sample_rate)
        self.frequencies = fourier.freqs(self.chunk_size, sample_rate)[:self.frequency_cutoff_index]
        # Amplitude axis
        self.amplitudes = np.zeros((self.chunk_count, len(self.frequencies))) # 2D array containing amp in terms of frequency at a time
        print "\n========= PERFORMING STFT =========================";progress = 0 # PROGRESS BAR
        for i in range(0, self.chunk_size*self.chunk_count, self.chunk_size):
            amps = fourier.fft(samples[i:i+self.chunk_size])
            amps = (np.array(amps) / self.chunk_size).tolist()
            amps = [abs(x.real) for x in amps] # use real part only
            amps = amps[:self.frequency_cutoff_index]
            self.amplitudes[i/self.chunk_size] = amps
            # PROGRESS BAR
            current = i*50.0/(self.chunk_size*self.chunk_count)
            if current > progress:
                sys.stdout.write('.' * int(current - progress))
                sys.stdout.flush()
                progress = int(current)
        print ".\n========= DONE ===================================" # PROGRESS BAR
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
        for time in range(self.chunk_count):
            frame_max = max(self.amplitudes[time])
            if frame_max!=0:
                for freq in range(self.frequency_cutoff_index):
                    self.amplitudes[time][freq] *= 2**15 / frame_max
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
        max_freqs = [self.frequencies[np.argmax(chunk)] for chunk in self.amplitudes]
        # Container for entire song data
        song = songsmith.Phrase()

        for i in range(len(max_freqs)):
            c = songsmith.Chord(
                notes=[songsmith.Note(max_freqs[i],self.chunk_size*1./44100,16000)]
            )
            if i==0 or not c==song.chords[len(song.chords)-1]:
                song.chords.append(c)
            else:
                num = len(song.chords)-1
                for n in range(len(song.chords[num].notes)):
                    song.chords[num].notes[n].duration += self.chunk_size*1./44100
        return song


class STFT(object):
    def __init__(self, _waveform):
        self.waveform = _waveform
        # make sure the channel count is 1
        self.waveform.setchannelcount(1)
        # get the samples, dtype is signed integer for samples of width 2
        # See http://stackoverflow.com/a/2226907
        self.samples = np.fromstring(wav.getsamples(), dtype='Int16').tolist()
    # def transform(self, chunk_size):
    #     '''
    #     chunk_size is the number of time frames per chunk.
    #     '''
    #     sample_rate = 44100.0
    #
    #     matrix = STFT_Matrix()
    #     # Time axis
    #     matrix.chunk_size = chunk_size
    #     matrix.chunk_count = len(self.samples) // small_sample_size # Number of time chunks
    #     # Frequency axis
    #     matrix.frequency_precision = sample_rate / chunk_size # The accuracy of the frequencies (e.g. How many Hz off are the freqs?)
    #     matrix.frequency_cutoff = 5000 # Frequencies above this Hertz will be discarded
    #     matrix.frequency_cutoff_index = int(frequency_cutoff*chunk_size/sample_rate)
    #     frequencies = fourier.freqs(chunk_size, sample_rate)[:frequency_cutoff_index]
    #     matrix = np.zeros((count, len(frequencies)))
    #     print "\n========= PARSING WAVE INPUT (SMALL)==============";progress = 0 # PROGRESS BAR
    #     for i in range(0, chunk_size*chunk_count, chunk_size):
    #         amps = fourier.fft(self.samples[i:i+chunk_size])
    #         amps = (np.array(amps) / size).tolist()
    #         amps = [abs(x.real) for x in amps] # use real part only
    #         amps = amps[:frequency_cutoff_index]
    #         small_sample_matrix[i/small_sample_size] = amps
    #         # PROGRESS BAR
    #         current = i*50.0/(small_sample_size*small_sample_count)
    #         if current > progress:
    #             sys.stdout.write('.' * int(current - progress))
    #             sys.stdout.flush()
    #             progress = int(current)
    #     print ".\n========= DONE ===================================" # PROGRESS BAR



def freq_plot(wav):
    """Graphs amplitude as a function of frequency

    Args:
        wav: The waveform.WaveForm object to graph.
    """
    # make sure the channel count is 1
    wav.setchannelcount(1)
    # get the samples, dtype is signed integer for samples of width 2
    # See http://stackoverflow.com/a/2226907
    samples = np.fromstring(wav.getsamples(), dtype='Int16').tolist()
    # **************************************************************************
    # SMALL SAMPLES FFT
    # **************************************************************************
    # PERFORM FFT ON EACH CHUNK
    small_sample_size = 2**10
    small_sample_count = len(samples)//small_sample_size
    small_freq_precision = 44100.0 / small_sample_size # frequency precision = sample rate / sample count
    small_sample_freq_domain = {
                    "start": 0,#int(20*small_sample_size//44100) + (20*small_sample_size%44100 > 0),
                    "end": int(5000*small_sample_size/44100)
                    }
    small_sample_freqs = fourier.freqs(small_sample_size, 44100)[small_sample_freq_domain["start"]:small_sample_freq_domain["end"]]
    small_sample_matrix = np.zeros((small_sample_count, len(small_sample_freqs)))
    print "\n========= PARSING WAVE INPUT (SMALL)==============";progress = 0 # PROGRESS BAR
    for i in range(0, small_sample_size*small_sample_count, small_sample_size):
        amps = fourier.fft(samples[i:i+small_sample_size])
        amps = (np.array(amps) / small_sample_size).tolist()
        amps = [abs(x.real) for x in amps] # use real part only
        amps = amps[small_sample_freq_domain["start"]:small_sample_freq_domain["end"]]
        small_sample_matrix[i/small_sample_size] = amps
        # PROGRESS BAR
        current = i*50.0/(small_sample_size*small_sample_count)
        if current > progress:
            sys.stdout.write('.' * int(current - progress))
            sys.stdout.flush()
            progress = int(current)
    print ".\n========= DONE ===================================" # PROGRESS BAR


    # **************************************************************************
    # LARGE SAMPLES FFT
    # **************************************************************************
    # PERFORM FFT ON EACH CHUNK
    large_sample_size = 2**14
    large_sample_count = len(samples)//large_sample_size
    large_freq_precision = 44100.0 / large_sample_size # frequency precision = sample rate / sample count
    large_sample_freq_domain = {
                    "start": 0,#int(20*large_sample_size//44100) + (20*large_sample_size%44100 > 0),
                    "end": int(5000*large_sample_size/44100)
                    }
    large_sample_freqs = fourier.freqs(large_sample_size, 44100)[large_sample_freq_domain["start"]:large_sample_freq_domain["end"]]
    large_sample_matrix = np.zeros((large_sample_count, len(large_sample_freqs)))
    print "\n========= PARSING WAVE INPUT (LARGE)==============";progress = 0 # PROGRESS BAR
    for i in range(0, large_sample_size*large_sample_count, large_sample_size):
        _amps = fourier.fft(samples[i:i+large_sample_size])
        _amps = [abs(x.real) for x in _amps] # use real part only
        _amps = np.array(_amps) / large_sample_size
        _amps = _amps[large_sample_freq_domain["start"]:large_sample_freq_domain["end"]]
        large_sample_matrix[i/large_sample_size] = _amps
        # PROGRESS BAR
        current = i*50.0/(large_sample_size*large_sample_count)
        if current > progress:
            sys.stdout.write('.' * int(current - progress))
            sys.stdout.flush()
            progress = int(current)
    print ".\n========= DONE ===================================" # PROGRESS BAR




    print "Small Freq Range:",
    print small_sample_freqs[0],
    print small_sample_freqs[len(small_sample_freqs)-1]
    print "Large Freq Range:",
    print large_sample_freqs[0],
    print large_sample_freqs[len(large_sample_freqs)-1]



    # **************************************************************************
    # ELLIOT'S SMOOTHING ALGORITHM
    # **************************************************************************
    # Matrix is in the form: Matrix[sample index][frequency index] = amplitude
    print "\n========= SMOOTHING FFT OUTPUT ===================";progress = 0 # PROGRESS BAR

    old_matrix = small_sample_matrix
    new_matrix = np.zeros(shape=old_matrix.shape)
    for chunk_index in xrange(old_matrix.shape[1]):
        #new_matrix[:,chunk_index] = triangular_smoothing(old_matrix[:,chunk_index], 20)
        new_matrix[:,chunk_index] = moving_average(old_matrix[:,chunk_index], 20)
        #new_matrix[:,chunk_index] = remove_anomalies(moving_average(old_matrix[:,chunk_index], 20))
        #new_matrix[:,chunk_index] = remove_anomalies(old_matrix[:,chunk_index])
        # PROGRESS BAR
        current = chunk_index*50.0/old_matrix.shape[1]
        if current > progress:
            sys.stdout.write('.' * int(current - progress))
            sys.stdout.flush()
            progress = int(current)

    print ".\n========= DONE ===================================" # PROGRESS BAR'''


    # **************************************************************************
    # USE THE DATA FROM THE LARGE SAMPLES TO MAKE THE SMALL SAMPLES MORE ACCURATE
    # **************************************************************************
    lower_bound = []
    upper_bound = []
    middle_bound = []
    max_freqs = []#[freqs[np.argmax(chunk)] for chunk in new_matrix]
    # factor * small_chunk_index = large_chunk_index
    # factor * large_chunk_freq = small_chunk_freq
    conversion_factor = small_sample_size * 1. / large_sample_size
    # Iterate through the time chunks
    for i in xrange(small_sample_count-16):
        small_sample_index = i
        large_sample_index = i * conversion_factor
        # Find the index of the frequency in the stft matrix with small samples
        small_freq_index = np.argmax(new_matrix[i])
        large_freq_index = int(small_freq_index * 1. / conversion_factor)
        large_freq_range_start = int((small_freq_index-1.) / conversion_factor)
        large_freq_range_end = int((small_freq_index+1.) / conversion_factor)
        lower_bound.append(large_sample_freqs[large_freq_range_start])
        upper_bound.append(large_sample_freqs[large_freq_range_end])
        middle_bound.append(small_sample_freqs[small_freq_index])
        # Find the indices of frequencies in the stft matrix with large samples
        a_index = int((small_freq_index - 0.5) / conversion_factor)
        if a_index < 0: a_index = 0
        b_index = int((small_freq_index + 0.5) / conversion_factor)
        # Iterate through the possible frequencies of the large sampled matrix
        m_amp = large_sample_matrix[large_sample_index][a_index]
        m_i = a_index
        #print "Time: %.2f"%(large_sample_index*large_sample_size/44100)
        for j in range(a_index, b_index):
            #print "(", large_sample_freqs[j], ",", large_sample_matrix[large_sample_index][j], ")",
            if large_sample_matrix[large_sample_index][j] > m_amp:
                m_amp = large_sample_matrix[large_sample_index][j]
                m_i = j
        #print "\n%s\n"%(large_sample_freqs[m_i])
        # Add the new values to the plot arrays
        max_freqs.append(small_sample_freqs[small_freq_index])
        #max_freqs.append(large_sample_freqs[large_freq_index])
        #max_freqs.append(large_sample_freqs[m_i])
        #max_freqs.append(large_sample_freqs[np.argmax(large_sample_matrix[i * conversion_factor-1])])

    # **************************************************************************
    # GRAPH THE DATA AS A SPECTROGRAM
    # **************************************************************************

    #a = np.swapaxes(np.matrix(new_matrix), 0, 1) # Create a numpy matrix from data and swap the x and y axis
    # Create the plot of the data with the origin in the lower left hand corner.
    # The extent argument specifies that the y values range from 0 to small_sample_count
    # and the x values range from 20 Hz to 5000 Hz
    #im = plt.imshow(a, origin='lower', extent=[0, small_sample_count*small_sample_size/44100, 20, 5000], interpolation='nearest')

    a = np.swapaxes(large_sample_matrix, 0, 1) # Create a numpy matrix from data and swap the x and y axis
    im = plt.imshow(a, origin='lower', extent=[0, large_sample_count*large_sample_size/44100, 0, 5000], interpolation='nearest')
    # Style the plot
    plt.xlabel("time (chunks)")
    plt.ylabel("frequency (hz)")
    plt.ylim(20, 5000)
    plt.axes().set_aspect('auto', 'datalim')

    #max_amps = [chunk[np.argmax(chunk)] for chunk in new_matrix]
    #max_freqs = [large_sample_freqs[np.argmax(chunk)] for chunk in large_sample_matrix]
    plt.plot(np.linspace(0, small_sample_count*small_sample_size/44100, len(max_freqs)), max_freqs, "r")
    plt.plot(np.linspace(0, small_sample_count*small_sample_size/44100, len(max_freqs)), lower_bound, "y")
    plt.plot(np.linspace(0, small_sample_count*small_sample_size/44100, len(max_freqs)), upper_bound, "y")
    plt.plot(np.linspace(0, small_sample_count*small_sample_size/44100, len(max_freqs)), middle_bound, "g")
    plt.show()
    # **************************************************************************
    # RECREATE THE SONG FROM THE PARSED DATA
    # **************************************************************************
    # Parse the data into song structure and
    # merge sequential chords that contain the same notes
    import songsmith
    song = songsmith.Phrase() # Container for entire song data

    for i in range(len(max_freqs)):
        c = songsmith.Chord(
            notes=[songsmith.Note(max_freqs[i],small_sample_size*1./44100,16000)]
        )
        if i==0 or not c==song.chords[len(song.chords)-1]:
            song.chords.append(c)
        else:
            num = len(song.chords)-1
            for n in range(len(song.chords[num].notes)):
                song.chords[num].notes[n].duration += small_sample_size*1./44100
    for chord in song.chords:
        print [vars(note) for note in chord.notes]
    print "BPMs:", BPM([chord.notes[0].duration for chord in song.chords])


    # ****************************IN DEVELOPMENT
    note_names = []
    for chord in song.chords:
        for note in chord.notes:
            note_names.append(note.frequency)
    import keyfinder
    print keyfinder.key(note_names)


    # **************************************************************************
    # PLAY THE RECREATED SONG
    # **************************************************************************
    import pyaudio
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(2),
                    channels=1,
                    rate=44100,
                    output=True)
    song = str(song)
    for i in xrange(0, len(song), 1024):
        stream.write(song[i:i+1024])
    stream.stop_stream()
    stream.close()
    p.terminate()



# If we are running the script, analize the wav file that was passed in
if __name__ == "__main__":
    from sys import argv
    if len(argv)>1:
        import waveform
        wav = waveform.open_wave(argv[1])
        #freq_plot(wav)


        wav.setchannelcount(1)
        samples = np.fromstring(wav.getsamples(), dtype='Int16').tolist()
        matrix = STFT_Matrix(samples, c_size=2**10)
        matrix.amplitudes = triangular_smoothing(matrix.amplitudes)
        matrix.smooth_amps_2()
        print [amp for amp in matrix.amplitudes[5]]
        print sum(matrix.amplitudes[5])
        #matrix.amp_graph()
        matrix.collapse_overtones()
        #matrix.smooth_amps()
        matrix.spectrogram()
