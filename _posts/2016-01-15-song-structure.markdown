---
layout: post
title:  "Song Structure"
date:   2016-01-15 23:23:52
---

This post describes the work I have done to complete the second quarter deadline. The most recent changes can be seen in commit [3291d00](https://github.com/ejmsoftware/algorithmic-musician/commit/20c71ceb1478224a1f2b36c237a577f771f1de67). The two big pieces of this latest commit are improved song structure and approximate bpm calculation.

## 1. Approximate BPM Calculation

Obviously, the beats per minute fluctuates throughout a piece of music, but I wrote a simple algorithm to find an average bpm:

{% highlight python %}
def BPM(x):
    shortest_note = min(x) # Get the duration of the shortest note
    deviations = [note % shortest_note for note in x] # Find how much each note differs from the shortest_note
    deviations = [(-shortest_note+deviation) if deviation > shortest_note/2 else deviation for deviation in deviations]
    average_deviation = sum(deviations)/len(deviations)
    average_note_time = shortest_note + average_deviation
    return 60. / average_note_time # Convert the beat time to beats per minute
{% endhighlight %}

`x` is a python array of note lengths. The algorithm first finds the shortest note. Then, the algorithm finds the average deviation of each note's length from the duration of the shortest note. The algorithm simply adds the average deviation to the shortest note to get the average note length. Finally, the algorithm simply converts that to beats per minute. [Better explanation to come]

Here is an example:

    >>> BPM([0.75, 1.5, 2.25, 3.0])
    80.0

The `BPM` function obviously calculated that the average beat length is 0.75, meaning that there are 80 beats in a minute. Therefore, the function correctly returned 80 bpms.

## 2. Improved song structure

In this latest commit, I added a piece of code to convert 43 FFT samples per second to 1 sample per note. For example, before I implemented my new algorithm, the stft file generated several hundred notes for the song, "Mary Had a Little Lamb." Obviously, this was extreme overkill. The issue was that the program created multiple copies of the same note in a row with a very short duration each instead of combining the notes into one with a longer duration. The new algorithm looks like this:

{% highlight python %}
import songsmith
song = songsmith.Phrase() # Container for entire song data

for i in range(len(max_freqs)):
    c = songsmith.Chord(
        notes=[songsmith.Note(max_freqs[i],small_sample_size*1./44100,16000)]
    )
    if i==0 or not c==song.chords[len(song.chords)-1]:
        song.chords.append(c)
    else:
        num = len(song.chords)-1
        for n in range(len(song.chords[num].notes)):
            song.chords[num].notes[n].duration += small_sample_size*1./44100
{% endhighlight %}

`songsmith` is the module I created that contains all the notes. `maxfreqs` is an array of the greatest frequency at time intervals for the song. The algorithm only adds a new note if the frequency has changed since the last note. If the frequency has not changed, the algorithm simply lengthens the duration of the last note.

The new algorithm structures the data like this:

    [{'duration': 0.626938775510204, 'phase': 0, 'rate': 44100, 'frequency': 344, 'amplitude': 16000}] "Mar"
    [{'duration': 0.5572789115646257, 'phase': 0, 'rate': 44100, 'frequency': 301, 'amplitude': 16000}] "-y"
    [{'duration': 0.5572789115646257, 'phase': 0, 'rate': 44100, 'frequency': 258, 'amplitude': 16000}] "had"
    [{'duration': 0.5572789115646257, 'phase': 0, 'rate': 44100, 'frequency': 301, 'amplitude': 16000}] "a"
    [{'duration': 1.8575963718820878, 'phase': 0, 'rate': 44100, 'frequency': 344, 'amplitude': 16000}] "little lamb"
    [{'duration': 2.1594557823129272, 'phase': 0, 'rate': 44100, 'frequency': 301, 'amplitude': 16000}] "little lamb"
    [{'duration': 0.3482993197278911, 'phase': 0, 'rate': 44100, 'frequency': 344, 'amplitude': 16000}] "lit"
    [{'duration': 0.9520181405895696, 'phase': 0, 'rate': 44100, 'frequency': 387, 'amplitude': 16000}] "-tle lamb"

I added the lyrics after the notes to assist your understanding of the data. You can clearly see the note durations and frequencies accurately reflect the song, "Mary Had a Little Lamb."
