import math

def tune(raw):
    # constant frequency of lowest C
    # based off an instrument tuned to A4 == 440 Hz
    C0 = 16.35
    # each scale starts with a C
    NOTE_NAMES = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
    # calculate and return the note and octave
    n = math.log(raw/C0, 2)
    note=int(n%1*12)
    octave=int(n)
    return NOTE_NAMES[note] + str(octave)

if __name__=="__main__":
    # test the tuning function
    assert tune(27.50) == "A0"
    assert tune(440) == "A4"
    assert tune(2489.5) == "D#7"
    print("tuner tested successfully")
