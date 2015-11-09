---
layout: post
title:  "Calculating C0"
date:   2015-11-09 12:06:46
---

If you read my original post on tuning frequencies, you will see this portion of my code:

{% highlight python %}
# based off an instrument tuned to A4 == 440 Hz
C0 = 16.35
{% endhighlight %}

I originally set the frequency of the lowest octave C to 16.35 based on a chart online. Recently, I decided to make sure this constant was precise as possible. I decided to calculate it my self. Based on A4 having a frequency of 440 Hz, I created the following equation:

![]({{ site.baseurl }}/images/c0-calculation.png)

From this, I used Wolfram Alpha to calculate C0.

> C0 = 16.351597831287414667365624595