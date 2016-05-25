"""
songsmith.py - A module for constucting a 16-bit audio waveform from an
intuitive musical structue.
Copyright EJM Software 2016
"""
from numpy import linspace,sin,int16,concatenate, fromfunction
import sys, math

# ********************************************************************
# HELPER FUNCTIONS
# ********************************************************************
def freqtoname(f):
    """ Returns the letter name of the note followed by its octave number
    If the input is not valid, an empty string is returned

    f -- a float representing the frequency of the note
    """
    # return empty string if input is not valid
    if f <= 0:
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
    """Returns a float representing the frequency of a given note name

    name -- a string representation of a note starting with the letter of the
    note followed by the octave number
    """
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

def overtone(fundamental, n, B=0.00075145):
    """ Returns the nth partial of the fundamental frequency
    When n==1, the function returns the fundamental frequency
    See: http://daffy.uah.edu/piano/page4/page8/index.html

    fundamental -- a float that represents the fundamental frequency
    n -- which partial to return
    """
    return n * fundamental * (1 + 0.5 * (n*n-1) * B)

def linear_adsr(frame_count):
    """ Returns a numpy array decay function for a note
    Affects the timbre of a note

    frame_count -- the length of the returned decay array
    """
    peak = 0.75
    rate = 44100
    a_count = int(frame_count*0.1)
    d_count = int(frame_count*0.1)
    r_count = int(frame_count*0.2)
    s_count = frame_count - a_count - d_count - r_count
    a = linspace(0, peak, a_count)
    d = linspace(peak, peak*0.5, d_count)
    s = linspace(peak*0.5, peak*0.4, s_count)
    r = linspace(peak*0.4, 0, r_count)
    return concatenate((a,d,s,r))

def compare_freqs(f1, f2):
    """compares 2 frequencies to see if they are within the same note name"""
    ratio = 1.02930223664 # Ratio = 2^(1/24)
    return (f2 < f1 * ratio and f2 > f1 / ratio)




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

        # DECAY
        COUNT = self.duration * self.rate
        #decay = linspace(0.6, 0.1, self.duration*self.rate)
        decay = 1 - linspace(0,COUNT-1, COUNT) / COUNT

        decay = linear_adsr(COUNT)


        #indices = linspace(0,COUNT-1, COUNT)
        #decay = -1*((indices/COUNT-1)**4 + indices/COUNT - 1)

        # Calculate the sine wave at the given frequency and multiply by amplitude
        data = sin(TAU * (self.frequency * t + self.phase)) * self.amplitude * decay

        #print data.shape
        # convert the numpy array to 2 byte integers
        return data.astype(int16)
    def __eq__(self, other):
        # Check if the notes are closer that half to the next note
        # Basically, check if the other note is less than
        # This note's frequency * (2^(1/12) + 1) / 2
        # and greater than This note's frequency / (2^(1/12) + 1) / 2
        ratio = 1.02973154718 # Ratio = (2^(1/12) + 1) / 2
        return (other.frequency <= self.frequency * ratio and other.frequency >= self.frequency / ratio)
    def __str__(self):
        """returns string"""
        return self.asarray().tostring()

# Create a chord from multiple notes
class Chord (object):
    def __init__(self, notes=None):
        self.notes = notes
    def addovertones(self, count):
        overtones = []
        for note in self.notes:
            for i in range(count):
                overtones.append(Note(overtone(note.frequency, i + 2), note.duration, note.amplitude/(i+2)))
        self.notes.extend(overtones)
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
    def addovertones(self, count):
        for i in range(len(self.chords)):
            self.chords[i].addovertones(count)
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
    def debug(self):
        for chord in self.chords:
            print [vars(note) for note in chord.notes]
    def __str__(self):
        return self.asarray().tostring()
