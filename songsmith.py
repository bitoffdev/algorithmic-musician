import pyaudio
from numpy import linspace,sin,int16

# Amplitude must be in the closed interval [-32768, 32768] because that is the max a 2 byte int can store
def note(freq, length=1, amp=1, rate=44100):
    TAU = 6.2831852 # tau is 2 * pi
    # Create numpy array length*rate long with the first value at 0 and the last at length
    t = linspace(0,length,length*rate)
    # Calculate the sine wave at the given frequency and multiply by amplitude
    data = sin(TAU * freq * t) * amp
    # convert the numpy array to 2 byte integers
    return data.astype(int16)

# Create a chord from multiple notes
def chord(*args):
     return sum(n//len(args) for n in args)

# Test Case
if __name__=="__main__":
    # Open a pyaudio stream
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(2),
                    channels=1,
                    rate=44100,
                    output=True)
    # create the tone
    notes = []
    notes.append(note(68,4,amp=30000))
    notes.append(note(100,4,amp=30000))
    notes.append(note(130,4,amp=30000))
    tone = chord(*notes)
    stream.write(tone)
    # close the Pyaudio stream
    stream.stop_stream()
    stream.close()
    p.terminate()
