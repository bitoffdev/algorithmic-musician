"""Module for analizing waveform audio files"""
import matplotlib.pyplot as plt
import numpy as np

def time_plot(wav):
    """Graphs amplitude as a function of time

    Args:
        wav: The waveform.WaveForm object to graph.
    """
    # make sure the channel count is 1
    wav.set_channel_count(1)
    # get the samples, dtype is signed integer for samples of width 2
    # See http://stackoverflow.com/a/2226907
    samples = np.fromstring(wav.get_samples(), dtype='Int16')
    # plot the waveform using matplotlib
    plt.figure(1)
    plt.plot(samples)
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    plt.show()
def freq_plot(wav):
    """Graphs amplitude as a function of frequency

    Args:
        wav: The waveform.WaveForm object to graph.
    """
    # make sure the channel count is 1
    wav.setchannelcount(1)
    # get the samples, dtype is signed integer for samples of width 2
    # See http://stackoverflow.com/a/2226907
    samples = np.fromstring(wav.getsamples(), dtype='Int16')
    # perform a fast fourier transform
    import fourier
    amps = fourier.fft(samples.tolist())
    amps = (np.array(amps) / wav.getsamplecount()).tolist()
    freqs = fourier.freqs(len(samples), 44100)
    # use real part only
    amps = [abs(x.real) for x in amps]
    # Trim the freqs to only the range a human car hear
    # a human can hear in the range 20 Hz to 20 kHz
    # To put this in perspective, the lowest note on a piano is A0, which is 27.5 Hz
    # The highest note on a piano is C8, which is 4186.01 Hz
    freqdomain = {"start": int(20*len(amps)/44100),
                  "end": int(5000*len(amps)/44100)
                  }
    amps = amps[freqdomain["start"]:freqdomain["end"]]
    freqs = freqs[freqdomain["start"]:freqdomain["end"]]
    # use only the positive frequencies (negative frequncies are just a mirror reflection)
    # amps = amps[:(len(amps)-1)//2 + 1]
    # freqs = freqs[:(len(freqs)-1)//2 + 1]
    # plot the frequencies using matplotlib
    plt.plot(freqs, amps)
    plt.xlabel('Frequency (Hz)')
    plt.xlim(0, 5000)
    plt.ylabel('Amplitude')
    plt.show()

def loudest_freqs(wav, start=0, stop=1024):
    # make sure the channel count is 1
    wav.setchannelcount(1)
    # get the samples, dtype is signed integer for samples of width 2
    # See http://stackoverflow.com/a/2226907
    samples = np.fromstring(wav.getsamples()[start:stop], dtype='Int16')
    # perform a fast fourier transform
    import fourier
    amps = fourier.fft(samples.tolist())
    freqs = fourier.freqs(len(samples), 44100)
    # use real part only
    amps = [abs(x.real) for x in amps]
    # Trim the freqs to only the range a human car hear
    # a human can hear in the range 20 Hz to 20 kHz
    # To put this in perspective, the lowest note on a piano is A0, which is 27.5 Hz
    # The highest note on a piano is C8, which is 4186.01 Hz
    freqdomain = {"start": int(20*len(amps)/44100),
                  "end": int(5000*len(amps)/44100)
                  }
    amps = amps[freqdomain["start"]:freqdomain["end"]]
    freqs = freqs[freqdomain["start"]:freqdomain["end"]]
    # use only the positive frequencies (negative frequncies are just a mirror reflection)
    # amps = amps[:(len(amps)-1)//2 + 1]
    # freqs = freqs[:(len(freqs)-1)//2 + 1]
    # get the indices of the frequencies sorted by amplitude
    indices = sorted(range(len(amps)), key=lambda x:amps[x])
    # convert indices to notes
    import tuner
    tuned_indices = []
    for i in indices[::-1]:
        new = tuner.tune(freqs[i])
        if not (new in tuned_indices):
            tuned_indices.append(new)
    #indices = map(tuner.tune, indices)
    #return amps[:5]
    return [x for x in tuned_indices[:15]]

def loudest(samplestring):
    samples = np.fromstring(samplestring)
    # perform a fast fourier transform
    import fourier
    amps = fourier.fft(samples.tolist())
    freqs = fourier.freqs(len(samples), 44100)
    # use real part only
    amps = [abs(x.real) for x in amps]
    # use only the positive frequencies (negative frequncies are just a mirror reflection)
    amps = amps[:(len(amps)-1)//2 + 1]
    freqs = freqs[:(len(freqs)-1)//2 + 1]
    # get the indices of the frequencies sorted by amplitude
    indices = sorted(range(len(amps)), key=lambda x:amps[x])
    #return amps[:5]
    return [freqs[x] for x in indices[-15:][::-1]]
    
# If we are running the script, analize the wav file that was passed in
if __name__ == "__main__":
    from sys import argv
    if len(argv)>1:
        import waveform
        wav = waveform.open_wave(argv[1])
        print loudest_freqs(wav, stop=wav.getsamplecount())
        freq_plot(wav)
