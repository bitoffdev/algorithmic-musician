"""
recorder.py - A module for recording waveform files
Copyright EJM Software 2016

Usage: python recorder.py FILENAME [LENGTH]
    FILENAME -- the path to write the new file to
    LENGTH -- the duration in seconds of the recording (default is 5)
"""
import pyaudio, waveform, sys

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024

def record(time, filename):
    # open a pyaudio stream for recording
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)
    # record the sound in frames
    print "Recording Audio..."
    frames = []
    for i in range(0, int(RATE / CHUNK * time)):
        data = stream.read(CHUNK)
        frames.append(data)
    print "Done"
    # close the pyaudio stream
    stream.stop_stream()
    stream.close()
    audio.terminate()
    # save the waveform to a file
    wav = waveform.from_string(b''.join(frames), rate=RATE, width=audio.get_sample_size(FORMAT), channels=CHANNELS)
    waveform.to_file(filename, wav)

if __name__=="__main__":
    if len(sys.argv) > 1:
        t = float(sys.argv[2]) if len(sys.argv) > 2 else 5
        record(t, sys.argv[1])
    else:
        print __doc__
