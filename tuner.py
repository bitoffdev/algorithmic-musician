import math

def tune(f):
    # return empty string if input is not valid
    if f <= 0:
        return ""
    # constant frequency of lowest C
    # based off an instrument tuned to A4 == 440 Hz
    C0 = 16.35
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

if __name__ == "__main__":
    # test the tuning function
    assert tune(27.50) == "A0"
    assert tune(45) == "F#1"
    assert tune(440) == "A4"
    assert tune(2489.5) == "D#7"
    print("tuner tested successfully")
