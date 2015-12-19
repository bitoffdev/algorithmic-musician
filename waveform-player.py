import waveform
from sys import argv

wav = waveform.open_wave(argv[1])

# Play the song using pyaudio
import pyaudio
# Open a pyaudio stream
p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(wav.getsamplewidth()),
                channels=wav.getchannelcount(),
                rate=wav.getsamplerate(),
                output=True)
samples = wav.getsamples()
for i in xrange(0, len(samples), 1024):
    stream.write(samples[i:i+1024])
stream.stop_stream()
stream.close()
p.terminate()
