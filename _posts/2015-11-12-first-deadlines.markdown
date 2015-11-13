---
layout: post
title:  "First Deadlines"
date:   2015-11-12 11:52:49
---

The first two deadlines for my project went hand-in-hand. The first major deadline was to write a class that would open waveform files, convert 2 channels to 1 channel, convert 16 bit samples to 8 bit samples, and save .wav files. The first minor deadline was to create a testing script for the waveform reader.

### Waveform Reader Test

This was due on November 2nd. You can see the waveform reader test I commited on November 2nd [here](https://github.com/ejmsoftware/algorithmic-musician/commit/51c256cb0cfc703bc9469f0d82897fdc41a24818). However, I have since moved the test from the "tests" directory I had it in to the main directory. You can find the latest testing script on [this commit](https://github.com/ejmsoftware/algorithmic-musician/commit/0a14712dd52eae058584654b355e9c9919566540).

There are three tests it runs:

1. Load data from wave files and write wave files
2. Changing the channel count
3. Changing the sample width

### Waveform Reader

This is due tomorrow, November 13. The waveform reader must pass the tests set forth by the last deadline. I created a module to accomplish this task. The module has a class inside it called "WaveForm" to represent all the data of a waveform.

*Solving the problem of changing the channel count*

This problem was not terribly hard to solve. To go from two channels to one channel I just got rid of one of the channels.

{% highlight python %}
new_samples = ''
for i in range(0, len(self._samples), 2 * self._sample_width):
    new_samples += self._samples[i+2:i+self._sample_width+2]
{% endhighlight %}


*Solving the problem of changing the sample width*

This was a little harder then the previous problem. I did a little research and found out that in the wav file format, 16 bit samples are signed, while 8 bit samples are unsigned. A little weird, right? So, to convert one sample from 16 bits to 8 bits, I do the following:

{% highlight python %}
struct.pack("B", struct.unpack("h", self._samples[i:i+2])[0]/256 + 128)
{% endhighlight %}

I unpack the 16 bit sample using python's struct module (The "h" stands for a signed short). I then divide by 256 to convert the 16 bit size to an 8 bit size. Then, because the 8 bit format should not be signed, I add 128. This pushes the entire sinusoid range into the positives. Finally, I use struct again to pack the altered sample into an 8 bit unsigned integer (The "B" stands for an unsigned char).

To convert 8 bit samples to 16 bits we do the opposite:

{% highlight python %}
new_samples += struct.pack("h", (struct.unpack("B", self._samples[i])[0] - 128) * 256)
{% endhighlight %}

### Putting it all together

Once I completed both of these deadlines, I ran the test:

    Elliots-MacBook-Pro:musician-project elliot$ python waveform-test.py mary.wav
    Testing successful!

There you have it! The waveform reader works!
