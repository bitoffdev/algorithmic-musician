---
layout: post
title:  "Initial Project Proposal"
date:   2015-09-17 12:25:56
---

My senior project will be to generate completely *original* audio files. It will generate new music through the algorithmic analysis of other music. The new audio file will represent the genre of WAVE files that are inputed. If beautiful piano WAVE files are submitted to the program, the program should spit out beautiful piano music!

### Here is the unpolished algorithm the program will use to generate music.

1. The user inputs 10-20 WAVE files.
2. The program will parse all of the WAVE files.
  * The wave file consists of a 32 bit header followed by the audio data.
  * The audio data consists of an array of bytes representing amplitudes.
  * Most files contain 44100 amplitude samples per second.
  * From the array of amplitudes, the program can reconstruct the wave that make up the fie.
3. Using a Fourier transform, the program will separate the complex wave into its individual sinusoid waves.
  * The magnitude of the sinusoid waves will be extracted as the pitch's frequency.
4. The program will build patterns in pitches that go together, and pitches that follow other pitches.
5. The program will quasi-randomly generate new music using patterns found in its analyzed wave files.
6. The new audio will be exported to a new WAVE file.

### The tools to be used:

I have not yet definitively selected which tools will be used for this project. As the old proverb goes, "It's a poor craftsman who blames his tools." I am worried about the theory first and the tools second.

That being said, I have run several initial tests in Python to confirm my understanding of WAVE files. Using the pyaudio module, I was able to play music from a WAVE file. The code is as follows:

{% highlight python %}
import pyaudio
import wave
import sys

CHUNK = 1024

def PlayWave(path):
    wf = wave.open(path, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(CHUNK)
    while data != '':
        stream.write(data)
        data = wf.readframes(CHUNK)
    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
        sys.exit(-1)
    PlayWave(sys.argv[1])
{{% endhighlight %}}

I also wrote a test function to convert the audio from Stero to Mono. This will make it easier to process the sounds.

{% highlight python %}
def SteroToMono(data, samplewidth):
    new_data = ''
    for i in range(0, len(data), 2 * samplewidth):
        new_data += data[i:i+samplewidth]
    return new_data
{{% endhighlight %}}
