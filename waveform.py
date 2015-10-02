class WaveForm(object):
    def __init__(self, c_count, s_width, s_rate, samples):
        self._channel_count = c_count
        self._sample_width = s_width
        self._sample_rate = s_rate
        self._samples = samples
        self._sample_count = len(samples)
    def get_channel_count(self):
        return self._channel_count
    def set_channel_count(self, c):
        if self._channel_count==2 and c==1:
            new_samples = ''
            for i in range(0, len(self._samples), 2 * self._sample_width):
                new_samples += self._samples[i:i+self._sample_width]
            self._samples = new_samples
    def get_sample_width(self):
        return self._sample_width
    def set_sample_width(self, w):
        pass
    def get_sample_count(self):
        return self._get_sample_count
    def get_samples(self):
        return self._samples
    def get_params(self):
        return (self._channel_count, self._sample_width, self._sample_rate, self._sample_count, 'NONE', 'not compressed')

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
