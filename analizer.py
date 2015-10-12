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
    samples = np.fromstring(wav.get_samples()[:1024], dtype='Int16')
    # perform a fast fourier transform
    import fourier
    w = fourier.dft(samples.tolist())
    freqs = fourier.freqs(len(samples), 44100)
    # plot the frequencies using matplotlib
    plt.plot(freqs, w)
    plt.xlabel('Frequency (Hz)')
    plt.xlim(0, 5000)
    plt.ylabel('Amplitude')
    plt.show()
