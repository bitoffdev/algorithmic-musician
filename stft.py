"""Module for analizing waveform audio files"""
import matplotlib.pyplot as plt
import numpy as np
import fourier
import sys # For progress bar

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
    # ====================== SMALL CHUNK FFT ===================================
    # PERFORM FFT ON EACH CHUNK
    data = []
    CHUNK_SIZE = 2**10
    # Note: Frequency bucket size = frame_rate / sample_count
    CHUNK_COUNT = len(samples)//CHUNK_SIZE
    print "\n========= PARSING WAVE INPUT =====================";progress = 0 # PROGRESS BAR
    for i in range(0, CHUNK_SIZE*CHUNK_COUNT, CHUNK_SIZE):
        # perform a fast fourier transform
        amps = fourier.fft(samples[i:i+CHUNK_SIZE])
        amps = (np.array(amps) / CHUNK_SIZE).tolist()
        # freqs = fourier.freqs(len(samples), 44100)
        # use real part only
        amps = [abs(x.real) for x in amps]
        # Trim the freqs to only the range a human car hear
        # a human can hear in the range 20 Hz to 20 kHz
        # To put this in perspective, the lowest note on a piano is A0, which is 27.5 Hz
        # The highest note on a piano is C8, which is 4186.01 Hz
        start = int(20*CHUNK_SIZE//44100) + (20*CHUNK_SIZE%44100 > 0)
        freqdomain = {"start": start,
                      "end": int(5000*len(amps)/44100)
                      }
        amps = amps[freqdomain["start"]:freqdomain["end"]]
        # freqs = freqs[freqdomain["start"]:freqdomain["end"]]
        data.append(amps)

        # PROGRESS BAR
        current = i*50.0/(CHUNK_SIZE*CHUNK_COUNT)
        if current > progress:
            sys.stdout.write('.' * int(current - progress))
            sys.stdout.flush()
            progress = int(current)
    print ".\n========= DONE ===================================" # PROGRESS BAR


    # **************************************************************************
    # LARGE CHUNK FFT
    # **************************************************************************
    # PERFORM FFT ON EACH CHUNK
    LARGE_CHUNK_SIZE = 2**14
    large_chunk_count = len(samples)//LARGE_CHUNK_SIZE
    large_chunk_freq_domain = {
                    "start": int(20*LARGE_CHUNK_SIZE//44100) + (20*LARGE_CHUNK_SIZE%44100 > 0),
                    "end": int(5000*LARGE_CHUNK_SIZE/44100)
                    }
    large_chunk_freqs = fourier.freqs(LARGE_CHUNK_SIZE, 44100)[large_chunk_freq_domain["start"]:large_chunk_freq_domain["end"]]
    large_chunk_matrix = np.zeros((large_chunk_count, len(large_chunk_freqs)))
    print "\n========= PARSING WAVE INPUT (LARGE)==============";progress = 0 # PROGRESS BAR
    for i in range(0, LARGE_CHUNK_SIZE*large_chunk_count, LARGE_CHUNK_SIZE):
        _amps = fourier.fft(samples[i:i+LARGE_CHUNK_SIZE])
        _amps = [abs(x.real) for x in _amps] # use real part only
        _amps = np.array(_amps) / LARGE_CHUNK_SIZE
        _amps = _amps[large_chunk_freq_domain["start"]:large_chunk_freq_domain["end"]]
        large_chunk_matrix[i/LARGE_CHUNK_SIZE] = _amps

        # PROGRESS BAR
        current = i*50.0/(LARGE_CHUNK_SIZE*large_chunk_count)
        if current > progress:
            sys.stdout.write('.' * int(current - progress))
            sys.stdout.flush()
            progress = int(current)
    print ".\n========= DONE ===================================" # PROGRESS BAR

    # =================== ELLIOT'S SMOOTHING ALGORITHM ==========================
    # Matrix is in the form:
    # [chunk[amplitudes], chunk[amplitudes]]
    print "\n========= SMOOTHING FFT OUTPUT ===================";progress = 0 # PROGRESS BAR

    old_matrix = np.asarray(data)
    new_matrix = np.zeros(shape=old_matrix.shape)
    for chunk_index in xrange(old_matrix.shape[1]):
        #new_matrix[:,chunk_index] = triangular_smoothing(old_matrix[:,chunk_index], 20)
        #new_matrix[:,chunk_index] = moving_average(old_matrix[:,chunk_index], 20)
        #new_matrix[:,chunk_index] = remove_anomalies(moving_average(old_matrix[:,chunk_index], 20))
        new_matrix[:,chunk_index] = remove_anomalies(old_matrix[:,chunk_index])
        # PROGRESS BAR
        current = chunk_index*50.0/old_matrix.shape[1]
        if current > progress:
            sys.stdout.write('.' * int(current - progress))
            sys.stdout.flush()
            progress = int(current)

    print ".\n========= DONE ===================================" # PROGRESS BAR'''
    # ===========================================================================
    '''print "\n========= COMBINING SMALL AND LARGE ===============";progress = 0 # PROGRESS BAR
    conversion_factor = CHUNK_SIZE * 1. / LARGE_CHUNK_SIZE
    for i in xrange(len(new_matrix)):
        small_freq_index = np.argmax(new_matrix[i])
        a_index = int((small_freq_index + 0.5) / conversion_factor)
        b_index = int((small_freq_index + 0.5) / conversion_factor)
        m_amp = large_chunk_matrix[i * conversion_factor-1][a_index]
        m_i = a_index
        for j in range(a_index, b_index):
            if large_chunk_matrix[i * conversion_factor][a_index] > m_amp:
                m_amp = large_chunk_matrix[i * conversion_factor][a_index]
                m_i = j
        new_matrix[i][small_freq_index] = large_chunk_freqs[m_i]
        # PROGRESS BAR
        current = i*50.0/len(new_matrix)
        if current > progress:
            sys.stdout.write('.' * int(current - progress))
            sys.stdout.flush()
            progress = int(current)

    print ".\n========= DONE ===================================" # PROGRESS BAR'''
    # =================== GRAPH THE DATA =======================================
    start = int(20*CHUNK_SIZE//44100) + (20*CHUNK_SIZE%44100 > 0)
    freqs = fourier.freqs(CHUNK_SIZE, 44100)[start:5000*CHUNK_SIZE/44100]

    # Create a numpy matrix from data and swap the x and y axis
    a = np.swapaxes(np.matrix(new_matrix), 0, 1)
    # Create the plot of the data with the origin in the lower left hand corner.
    # The extent argument specifies that the y values range from 0 to CHUNK_COUNT
    # and the x values range from 20 Hz to 5000 Hz
    im = plt.imshow(a, origin='lower', extent=[0, CHUNK_COUNT*CHUNK_SIZE/44100, 20, 5000], interpolation='nearest')
    # Style the plot
    plt.xlabel("time (chunks)")
    plt.ylabel("frequency (hz)")
    plt.ylim(20, 5000)
    plt.axes().set_aspect('auto', 'datalim')
    # show the plot
    plt.show()

    #'''

    max_freqs = []#[freqs[np.argmax(chunk)] for chunk in new_matrix]

    conversion_factor = CHUNK_SIZE * 1. / LARGE_CHUNK_SIZE
    for i in xrange(len(new_matrix)):
        small_freq_index = np.argmax(new_matrix[i])
        # small_freq = freqs[np.argmax(chunk)]
        # Find the range of frequencies from the small chunk stft
        # a = small_freq - 44100 / CHUNK_SIZE
        # b = small_freq + 44100 / CHUNK_SIZE
        # Find the indices of frequencies from the large chunk stft
        a_index = int((small_freq_index + 0.5) / conversion_factor)
        b_index = int((small_freq_index + 0.5) / conversion_factor)
        m_amp = large_chunk_matrix[i * conversion_factor-1][a_index]
        m_i = a_index
        for j in range(a_index, b_index):
            if large_chunk_matrix[i * conversion_factor][a_index] > m_amp:
                m_amp = large_chunk_matrix[i * conversion_factor][a_index]
                m_i = j
        max_freqs.append(large_chunk_freqs[m_i])




    max_amps = [chunk[np.argmax(chunk)] for chunk in new_matrix]
    plt.plot(np.linspace(0, CHUNK_COUNT*CHUNK_SIZE/44100, len(max_freqs)), max_freqs)
    plt.show()
    #'''
    # ==========================================================================

    # Parse the data into song structure
    import songsmith
    song = songsmith.Phrase() # Container for entire song data

    # for i in range(len(max_freqs)):
    #     song.chords.append(songsmith.Chord(notes=[songsmith.Note(max_freqs[i],CHUNK_SIZE*1./44100,16000)]))


    for chunk in new_matrix:
        indices = (chunk > 1000).nonzero()[0]
        #print [freqs[index] for index in indices]
        if len(indices)==0:
            # Add empty filler note
            song.chords.append(songsmith.Chord(notes=[songsmith.Note(440, CHUNK_SIZE*1./44100, 0)]))
        else:
            # notes = [songsmith.Note(freqs[indices[0]], CHUNK_SIZE*1./44100, 16000)]
            notes = [songsmith.Note(freqs[index], CHUNK_SIZE*1./44100, chunk[index]) for index in indices]
            song.chords.append(songsmith.Chord(notes=notes))

    # ====== ====RESAMPLE THE NOTES =======================
    # new_song = songsmith.Phase()
    # for i in xrange(len(song.chords)):
    #     for j in xrange(len(song.chords[i].notes)):
    #         note_end = i
    #         for k in xrange(i+1, len(song.chords)):
    #             if abs(song.chords[i].notes[j].frequency - song.chords[i].notes[k].frequency) < 50:
    #                 note_end += 1
    #             else:
    #                 break
    #======================================================


    # Play the song using pyaudio
    import pyaudio
    #Open a pyaudio stream
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
        freq_plot(wav)
