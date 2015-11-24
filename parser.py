import waveform, analizer, songsmith, sys

# **********************
# LOAD A WAVEFORM FILE INTO THE SONGSMITH STRUCTURE

CHUNK = 16000#8192
wav = waveform.open_wave(sys.argv[1])
song = songsmith.Phrase() # Container for entire song data

print "\n========= PARSING WAVE INPUT ====================="
progress = 0

for i in range(0, wav.getsamplecount(), CHUNK):
    names = analizer.loudest_freqs(wav, start=i, stop=i+CHUNK)
    chord = songsmith.Chord(
        songsmith.Note(songsmith.nametofreq(names[0]), CHUNK*1.0/wav.getsamplerate(), analizer.getampforfreq(wav, i, i+CHUNK, songsmith.nametofreq(names[0]))),
        songsmith.Note(songsmith.nametofreq(names[1]), CHUNK*1.0/wav.getsamplerate(), analizer.getampforfreq(wav, i, i+CHUNK, songsmith.nametofreq(names[1])))
        )
    song.notes.append(chord)
    
    current = i*50.0/wav.getsamplecount()
    if current > progress:
        sys.stdout.write('.' * int(current - progress))
        sys.stdout.flush()
        progress = int(current)

print ".\n========= DONE ==================================="

# **********************
# REBUILD THE WAVEFORM FROM THE PARSED DATA

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
