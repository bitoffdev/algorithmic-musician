"""
songsmith-test.py - tests the songsmith class
:author: Elliot Miller

Usage: python songsmith-test.py
"""
# ******************************************************************************
# Add the parent directory to Python's list of paths to search for modules
import sys
sys.path.append("../")
# ******************************************************************************
import songsmith, player, waveform

def TEST1():
    """ Returns a 16-bit string audio waveform to test Mary Had a Little Lamb"""
    note_names = ["E4", "D4", "C4", "D4", "E4", "E4", "E4", "E4", "D4", "D4", "D4", "D4", "E4", "G4", "G4", "G4"]
    chords = [songsmith.Chord(notes=[songsmith.Note(songsmith.nametofreq(name),0.5,16000)]) for name in note_names]
    song = songsmith.Phrase(chords)
    song.addovertones(5)
    return str(song)

def TEST2():
    """ Returns a 16-bit string audio waveform to test musical chords"""
    song = songsmith.Phrase(chords=[
        songsmith.Chord(notes=[
            songsmith.Note(songsmith.nametofreq("C4"), 0.5, 8000)
        ]),
        songsmith.Chord(notes=[
            songsmith.Note(songsmith.nametofreq("C4"), 0.5, 8000),
            songsmith.Note(songsmith.nametofreq("E4"), 0.5, 8000)
        ]),
        songsmith.Chord(notes=[
            songsmith.Note(songsmith.nametofreq("C4"), 0.5, 8000),
            songsmith.Note(songsmith.nametofreq("E4"), 0.5, 8000),
            songsmith.Note(songsmith.nametofreq("G4"), 0.5, 8000)
        ]),
        songsmith.Chord(notes=[
            songsmith.Note(songsmith.nametofreq("C4"), 1.5, 8000),
            songsmith.Note(songsmith.nametofreq("E4"), 1.5, 8000),
            songsmith.Note(songsmith.nametofreq("G4"), 1.5, 8000),
            songsmith.Note(songsmith.nametofreq("C5"), 1.5, 8000)
        ])
    ])
    song.addovertones(5)
    return str(song)

def TEST3():
    """ Returns a 16-bit string audio waveform to test musical beats"""
    return str(songsmith.Phrase(chords=[
        songsmith.Chord(notes=[
            songsmith.Note(220, 20.0, 16000),
            songsmith.Note(220.2, 20.0, 16000)
        ])
    ]))

if __name__=="__main__":
    player.play(waveform.from_string(TEST1()))
    player.play(waveform.from_string(TEST2()))
    player.play(waveform.from_string(TEST3()))
