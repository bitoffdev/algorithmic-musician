# Create the song Mary Had a Little Lamb
from songsmith import *

note_names = ["E4", "D4", "C4", "D4", "E4", "E4", "E4", "E4", "D4", "D4", "D4", "D4", "E4", "G4", "G4", "G4"]

notes = []
for name in note_names:
    notes.append(note(nametofreq(name),0.5,amp=16000))
    
song = phrase(notes).tostring()

"""
# Play the song using pyaudio
import pyaudio
# Open a pyaudio stream
p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(2),
                channels=1,
                rate=44100,
                output=True)
stream.write(song)
stream.stop_stream()
stream.close()
p.terminate()"""


# Save to wave file
import waveform
wav = waveform.from_string(song)
waveform.to_file("mary.wav", wav)