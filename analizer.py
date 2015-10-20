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
    wav.set_channel_count(1)
    # get the samples, dtype is signed integer for samples of width 2
    # See http://stackoverflow.com/a/2226907
    samples = np.fromstring(wav.get_samples()[:2048], dtype='Int16')
    # perform a fast fourier transform
    import fourier
    amps = fourier.dft(samples.tolist())
    freqs = fourier.freqs(len(samples), 44100)
    # use real part only
    amps = [abs(x.real) for x in amps]
    # use only the positive frequencies (negative frequncies are just a mirror reflection)
    amps = amps[:(len(amps)-1)//2 + 1]
    freqs = freqs[:(len(freqs)-1)//2 + 1]
    # plot the frequencies using matplotlib
    plt.plot(freqs, amps)
    plt.xlabel('Frequency (Hz)')
    plt.xlim(0, 5000)
    plt.ylabel('Amplitude')
    plt.show()

def loudest_freqs(wav, start=0, stop=1024):
    # make sure the channel count is 1
    wav.set_channel_count(1)
    # get the samples, dtype is signed integer for samples of width 2
    # See http://stackoverflow.com/a/2226907
    samples = np.fromstring(wav.get_samples()[start:stop], dtype='Int16')
    # perform a fast fourier transform
    import fourier
    amps = fourier.dft(samples.tolist())
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
