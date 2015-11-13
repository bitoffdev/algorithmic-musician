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
stream.write(wav.getsamples())
stream.stop_stream()
stream.close()
p.terminate()
