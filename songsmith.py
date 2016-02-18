"""
This module is used to compose songs as sample strings for use in a wave file.
Copyright EJM Software 2016
"""
from numpy import linspace,sin,int16,concatenate
import math # Used in tune function

# ********************************************************************
# HELPER FUNCTIONS
# ********************************************************************
def freqtoname(f):
    # return empty string if input is not valid
    if f <= 0:
        #print "F = ", f
        return ""
    # constant frequency of lowest C
    # based off an instrument tuned to A4 == 440 Hz
    C0 = 16.3515978313
    # each scale starts with a C
    NOTE_NAMES = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
    # calculate and return the note and octave
    n = math.log(f/C0, 2)
    note = int(round(n%1*12, 0))
    octave = int(n)
    # If the frequency is rounded to the next octave
    if note == 12:
        octave += 1
        note = 0
    # return the tuned note
    return NOTE_NAMES[note] + str(octave)

def nametofreq(name):
    # if no name, return frequency of 0
    if name=="":
        return 0
    # constant frequency of lowest C
    # based off an instrument tuned to A4 == 440 Hz
    C0 = 16.3515978313
    # each scale starts with a C
    NOTE_NAMES = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
    # calculate the frequency
    return C0 * 2 ** (float(name[-1]) + NOTE_NAMES.index(name[:-1])/12.0)


# ********************************************************************
# SONG STRUCTURE
# ********************************************************************
# Amplitude must be in the closed interval [-32768, 32768] because that is the max a 2 byte int can store
class Note (object):
    def __init__(self, _freq, _time, _amp, _rate=44100):
        self.frequency = _freq
        self.duration = _time
        self.amplitude = _amp
        self.rate = _rate
        self.phase = 0 # Used by phrase to align notes, should be between 0 and 1
    def asarray(self):
        """returns numpy array"""
        TAU = 6.2831852 # tau is 2 * pi
        # Create numpy array length*rate long with the first value at 0 and the last at length
        t = linspace(0, self.duration, self.duration*self.rate)
        # Calculate the sine wave at the given frequency and multiply by amplitude
        data = sin(TAU * (self.frequency * t + self.phase)) * self.amplitude
        # convert the numpy array to 2 byte integers
        return data.astype(int16)
    def __eq__(self, other):
        # Check if the notes are closer that half to the next note
        # Basically, check if the other note is less than
        # This note's frequency * (2^(1/12) + 1) / 2
        # and greater than This note's frequency / (2^(1/12) + 1) / 2
        ratio = 1.02973154718 # Ratio = (2^(1/12) + 1) / 2
        return (other.frequency < self.frequency * ratio and other.frequency > self.frequency / ratio)
    def __str__(self):
        """returns string"""
        return self.asarray().tostring()

# Create a chord from multiple notes
class Chord (object):
    def __init__(self, notes=None):
        self.notes = notes
    def asarray(self):
        return sum(n.asarray() for n in self.notes)
        #return sum(n.asarray()//len(self.notes) for n in self.notes)
    def __eq__(self, other):
        return all(b==a for a in self.notes for b in other.notes)
    def __str__(self):
        return self.asarray().tostring()

class Phrase (object):
    def __init__(self, chords=None):
        self.chords = chords or []
    def asarray(self):
        currentphase = 0.34
        for chord in self.chords:
            for note in chord.notes:
                note.phase = currentphase
            currentphase += chord.notes[0].frequency * chord.notes[0].duration

        return concatenate([n.asarray() for n in self.chords])
    def play(self):
        import pyaudio
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(2),
                        channels=1,
                        rate=44100,
                        output=True)
        song = self.__str__()
        for i in xrange(0, len(song), 1024):
            stream.write(song[i:i+1024])
        stream.stop_stream()
        stream.close()
        p.terminate()
    def __str__(self):
        return self.asarray().tostring()


# ********************************************************************
# TEST CASE
# ********************************************************************
if __name__=="__main__":
    print "Running test..."
    import pyaudio
    # Open a pyaudio stream
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(2),
                    channels=1,
                    rate=44100,
                    output=True)
    # create the tone of a C2 bowed bass
    chord = Chord(Note(68,1,32000), Note(100,1,32000), Note(130,1,6000))
    #song = phrase(chord(*notes))
    stream.write(str(chord))
    # close the Pyaudio stream
    stream.stop_stream()
    stream.close()
    p.terminate()
