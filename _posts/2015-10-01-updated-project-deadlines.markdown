---
layout: post
title:  "Updated Project Deadlines"
date:   2015-10-01 11:56:43
---

The deadlines for the project have changed and are now as follows:

### Waveform Reader Tests

- Due 2015-11-02
- I have begun to write some of the tests for the waveform reader. As of right now, I will be putting all the tests in the "tests" directory of the project repository.

### Waveform Reader

- Due 2015-11-13

### Fourier Transform and Tests

- Due 2015-11-30
- This deadline will use the Fourier Transform to convert the amplitude-time data stored in a waveform file to amplitude-frequency data. I will also try to isolate which frequencies are most important in the music.

### Full Tone Recognition and Tests

- Due 2015-12-18
- This deadline is majorly about creating the structure with which to store all the musical data. It will almost certainly have to include at the very least a rudimentary beat identifier, because most likely the frequencies will be stored based on the beat. For example, each note of the song can be represented with the properties frequency (pitch), amplitude (loudness), beat number, and duration. To assign a beat number (the index of the beat at which a note is played), the beat must be determined, which is why I say that this deadline will most likely have to include at least a rudimentary beat identifier.

### Pattern Recognition and Tests

- Due 2016-01-15
- This is when the beat recognition will have to be finished. The program will also begin to look for patterns in the music. Likely, I will program some type of data structure which contains the notes most likely to follow another note, or form a chord with a certain note.

### Key Recognition and Tests

- Due 2016-02-05
- This deadline will determine the key of the music and should be able to transpose different pieces to match keys as best as possible. Of course, it would also be fun to test the program without transposition to find what the program creates. It would likely have a lot of key changes!

### Music Generation and Tests

- Due 2016-03-24
- Build new, unique audio from the patterns found in the waveform audio files.

### Interface

- Due 2016-05-20
- Build a user-friendly interface for the music generator or a different use for it - this deadline will develop more alongside the project