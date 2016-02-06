---
layout: post
title:  "Determining Key from Frequencies"
date:   2016-02-03 11:56:36
---

### Task

The latest task in my project was to determine the key of a song or chord from a set of frequencies.

### Definitions
 - A **semitone** is the interval between two adjacent notes in a 12-tone (chromatic) scale.
 - The **semitone ratio** is the ratio between notes a semitone apart. It is equivalent to the twelfth root of two, which is about `1.05946309436`.
 - **NOTE_NAMES** is an array of the 12 note names starting with C.
	 - `["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]`
 - **MAJOR_SCALE** is an array of the intervals in a major scale. The array is `[0, 2, 4, 5, 7, 9, 11]`. This means that in a major scale the first note is 0 semitones above the starting note, the second note will be 2 semitones above the starting note, and so on.
 - **OCTAVE_MINIMUM** is the starting frequency of an octave that I arbitrarily chose to be 16.35 Hz.
 - **OCTAVE_MAXIMUM** is the highest frequency of the octave that I arbitrarily chose. It is twice **OCTAVE_MINIMUM**.
 - **F** is the input list of frequencies to process.

### Key Finding Algorithm
1. Adjust all the frequencies to be in the same octave. In order to do this, I arbitrarily chose the octave starting with the frequency 16.35. I could have chosen any octave, but this octave is the lowest musically recognized octave so it seemed like a good choice. For each frequency in `F`, I just divide the frequency by two until it is in the octave range. The octave range is denoted by the constants **OCTAVE_MINIMUM** and **OCTAVE_MAXIMUM**.
2. Iterate through each of the 12 possible keys. For each key:
	- Calculate the 7 notes that make up the major scale in the key. I accomplished this by transposing the **MAJOR_SCALE** intervals by the index of the key name in **NOTE_NAMES**.
	- Count the number of frequencies in **F** that are in the major scale of the current key.
	- Save the count to a list that will be checked later.
3. Chose the key that scored the most points and return its name. I do this by finding the greatest stored count from step two.

### Implementation

You can view my implementation of the algorithm on [Github](https://github.com/ejmsoftware/algorithmic-musician/blob/master/keyfinder.py).

I added several tests to the file at the bottom of the file, successfully testing several major scales. I also ran the script on "Mary Had a Little Lamb," and it returned that the key was C, which is correct.
