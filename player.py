"""
player.py - A module for playing a waveform using PyAudio
:author: Elliot Miller

Usage: python waveform-player.py FILENAME [START] [END] [SPEED]
"""
import pyaudio, waveform
from sys import argv

def play(wav, _start=None, _end=None, _speed=None):
    # Get the samples from the waveform object
    samples = wav.getsamples()
    # Check the input
    bytespersecond = float(wav.getsamplerate()) * float(wav.getsamplewidth()) * float(wav.getchannelcount())
    start = int(float(_start) * bytespersecond) if _start else 0
    end = int(float(_end) * bytespersecond) if _end else len(samples)
    speed = float(_speed) if _speed else 1
    # Play the song using a pyaudio stream
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wav.getsamplewidth()),
                    channels=wav.getchannelcount(),
                    rate=int(wav.getsamplerate() * speed),
                    output=True)
    for i in xrange(start, end, 1024):
        stream.write(samples[i:i+1024])
    stream.write(samples[i:end]) # Write the extra samples
    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__=="__main__":
    if len(argv) > 1:
        wav = waveform.open_wave(argv[1])
        play(wav, argv[2] if len(argv)>2 else None, argv[3] if len(argv)>3 else None, argv[4] if len(argv)>4 else None)
    else:
        print __doc__
