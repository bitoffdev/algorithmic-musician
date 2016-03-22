import songsmith, player, waveform

# ====================== MARY HAD A LITTLE LAMB TEST ===========================
# note_names = ["E4", "D4", "C4", "D4", "E4", "E4", "E4", "E4", "D4", "D4", "D4", "D4", "E4", "G4", "G4", "G4"]
# chords = [songsmith.Chord(notes=[songsmith.Note(songsmith.nametofreq(name),0.5,16000)]) for name in note_names]
# music = str(songsmith.Phrase(chords))

# ========================== BROKEN CHORD TEST =================================
music = songsmith.Phrase(chords=[
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


# =========================== BEAT TEST ========================================
# music = str(songsmith.Phrase(chords=[
#     songsmith.Chord(notes=[
#         songsmith.Note(220, 20.0, 8000),
#         songsmith.Note(220.1, 20.0, 8000)
#     ])
# ]))

# =========================== Add Overtones ====================================
for i in range(len(music.chords)):
    music.chords[i].addovertones(10)

# =========================== Play the Song ====================================
player.play(waveform.from_string(str(music)))

# =========================== Save the Wave ====================================
# wav = waveform.from_string(music)
# waveform.to_file("mary.wav", wav)
