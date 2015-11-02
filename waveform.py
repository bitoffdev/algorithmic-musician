class WaveForm(object):
    def __init__(self, c_count, s_width, s_rate, samples):
        self._channel_count = c_count
        self._sample_width = s_width
        self._sample_rate = s_rate
        self._samples = samples
        self._sample_count = len(samples)
    def getchannelcount(self):
        return self._channel_count
    def setchannelcount(self, c):
        if self._channel_count==2 and c==1:
            new_samples = ''
            for i in range(0, len(self._samples), 2 * self._sample_width):
                new_samples += self._samples[i+2:i+self._sample_width+2]
            self._samples = new_samples
            self._channel_count = 1
    def getsamplewidth(self):
        return self._sample_width
    def setsamplewidth(self, w):
        pass
    def getsamplecount(self):
        return self._sample_count
    def getsamples(self):
        return self._samples
    def getparams(self):
        return (self._channel_count, self._sample_width, self._sample_rate, self._sample_count, 'NONE', 'not compressed')

# OLD API, will be removed

def open_wave(filename):
    import wave
    spf = wave.open(filename, 'rb')
    wave_obj = WaveForm(spf.getnchannels(), spf.getsampwidth(), spf.getframerate(), spf.readframes(-1))
    return wave_obj
    
def write_wave(filename, wav):
    import wave
    fh = wave.open(filename, 'wb')
    fh.setparams((wav.get_params()))
    fh.writeframes(wav.get_samples())
    
# NEW API
    
def from_string(samplestring, rate=44100, width=2, channels=1):
    waveobj = WaveForm(channels, width, rate, samplestring)
    return waveobj

def from_file(filename):
    import wave
    fh = wave.open(filename, 'rb')
    waveobj = WaveForm(fh.getnchannels(), fh.getsampwidth(), fh.getframerate(), fh.readframes(-1))
    return waveobj

def to_file(filename, waveobj):
    import wave
    fh = wave.open(filename, 'wb')
    fh.setparams((waveobj.getparams()))
    fh.writeframes(waveobj.getsamples())