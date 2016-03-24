# algorithmic-musician

---

Example usage:

    import waveform, analizer
    wav = waveform.open_wave('Bowed-Bass-C2.wav')
    analizer.time_plot(wav)

To Do:

- Quadratic interpolation of spectral peaks
- Speed up waveform class, specifically setchannelcount
