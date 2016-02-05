# ******************************************************************************
# Copyright EJM Software 2016
# http://ejmsoftware.com
# ******************************************************************************
from math import log

# ******************************************************************************
# CONSTANTS
# ******************************************************************************
# list containing the names of all the possible key tonic notes
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
# represents the intervals in a major scale
MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
# Starting note in the octave we will use to tune the notes
OCTAVE_MINIMUM = 16.35
# Highest note in the octave we will use to tune the notes
OCTAVE_MAXIMUM = OCTAVE_MINIMUM*2.

# ******************************************************************************
# METHODS
# ******************************************************************************
def key(F):
    # STEP ONE - adjust all the frequecies to be in the octave we chose for tuning
    for n in range(0, len(F)):
        while F[n] >= OCTAVE_MAXIMUM:
            F[n] *= 0.5
        while F[n] < OCTAVE_MINIMUM:
            F[n] *= 2.

    # STEP TWO
    scores = []
    for i in range(12): # Iterate through the twelve notes
        current_intervals = map(lambda x: i+x-12, filter(lambda x: i+x>=12, MAJOR_SCALE)) + map(lambda x: i + x, filter(lambda x: i+x<12, MAJOR_SCALE))
        score = 0
        for freq in F:
            interval = int(round(log(freq/OCTAVE_MINIMUM, 2) * 12.))
            if interval in current_intervals:
                score += 1
        scores.append(score)

    # STEP THREE
    return NOTE_NAMES[scores.index(max(scores))]

# ******************************************************************************
# TEST CASE
# ******************************************************************************
if __name__=="__main__":
    assert(key([261.6, 293.7, 329.6, 349.2, 392.0, 440.0, 493.9])=="C")
    assert(key([277.2, 311.1, 349.2, 370.0, 415.3, 466.2, 523.3, 554.4])=="C#")
    assert(key([293.7, 329.6, 370.0, 392.0, 440.0, 493.9, 554.4, 587.3])=="D")
    print "Tests succeded!"
