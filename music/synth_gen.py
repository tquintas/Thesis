import wave as _w
import random2 as _r
import numpy as np
from pathlib import Path as _p
import time as _t

bitSamples = "/Users/tiagoquintas/Documents/bitSamples"

def noteToFreq(note):
    a = 440
    return (a / 32) * (2 ** ((note - 9) / 12))

def LP(buffer, cutoff_freq=1000, Q=0.707, envelope=None, fs=44100):
    filtered_buffer = np.zeros_like(buffer)
    nyquist = fs / 4
    q = 0.2
    if envelope is None:
        envelope = np.linspace(1.0,1.0,len(buffer))
    for i in range(len(buffer)):
        dynamic_cutoff = cutoff_freq + nyquist ** ((1.0 - envelope[i])**q) - 1
        w = 2 * np.pi * dynamic_cutoff / fs
        alpha = np.sin(w) / (2 * Q)
        coeff_b0 = (1 - np.cos(w)) / 2
        coeff_b1 = 1 - np.cos(w)
        coeff_b2 = (1 - np.cos(w)) / 2
        coeff_a0 = 1 + alpha
        coeff_a1 = -2 * np.cos(w)
        coeff_a2 = 1 - alpha
        b = np.array([coeff_b0 / coeff_a0, coeff_b1 / coeff_a0, coeff_b2 / coeff_a0])
        a = np.array([1, coeff_a1 / coeff_a0, coeff_a2 / coeff_a0])
        if i > 2:
            filtered_buffer[i] = b[0] * buffer[i] + b[1] * buffer[i - 1] + b[2] * buffer[i - 2] - a[1] * filtered_buffer[i - 1] - a[2] * filtered_buffer[i - 2]
        else:
            filtered_buffer[i] = buffer[i]
    return filtered_buffer

class Wave:
    def __init__(self, shape=0.5, sample_rate=44100):
        self.period = 1
        self.f = np.vectorize(lambda x: 0)
        self.sample_rate = sample_rate
        self.set_adsr()
        self.shape = shape
    def set_adsr(self,a=20,d=5,s=0.8,r=750):
        self.A = a
        self.D = d
        self.S = s
        self.R = r
    def get_adsr_buffer(self, dur=1.0):
        attack = np.linspace(0, 1, int(self.sample_rate * self.A/1000), False)
        decay = np.linspace(1, self.S, int(self.sample_rate * self.D/1000), False)
        sustain = np.linspace(self.S, self.S, int(self.sample_rate * (dur - (self.A+self.D+self.R)/1000)), False)
        release = np.linspace(self.S, 0, int(self.sample_rate * self.R/1000), False)
        arr = np.concatenate((attack, decay, sustain, release))
        return np.pad(arr, (0, int(self.sample_rate * dur) - len(arr)), mode='constant')
    def __call__(self, midi=60, vel=98, dur=1.0):
        freq = noteToFreq(midi)
        amp = vel / 128
        time_array = np.linspace(0, dur, int(self.sample_rate * dur), False)
        envelope_array = self.get_adsr_buffer(dur)
        return np.clip(amp * np.multiply(envelope_array, self.f(self.period * freq * time_array)), -1.0, 1.0)
    def AM(self, midi=60, vel=98, dur=1.0, am=None, am_midi=48, am_vel=98, am_rad=0.25):
        if am is None:
            am = Sine(self.sample_rate)
            am.set_adsr(0,0,1.0,0)
        freq = noteToFreq(midi)
        amp = vel / 128
        amp_ring = am_rad * am(am_midi, am_vel, dur)
        time_array = np.linspace(0, dur, int(self.sample_rate * dur), False)
        envelope_array = self.get_adsr_buffer(dur)
        return np.clip((amp + amp_ring) * np.multiply(envelope_array, self.f(self.period * freq * time_array)), -1.0, 1.0)
    def AM_from_buffer(self, midi=60, vel=98, dur=1.0, am_buffer=None, am_rad=0.25):
        if am_buffer is None:
            am = Sine(self.sample_rate)
            am.set_adsr(0,0,1.0,0)
            am_buffer = am(48, 98, dur)
        am_buffer = am_rad * am_buffer
        freq = noteToFreq(midi)
        amp = vel / 128
        time_array = np.linspace(0, dur, int(self.sample_rate * dur), False)
        envelope_array = self.get_adsr_buffer(dur)
        return np.clip((amp + am_buffer) * np.multiply(envelope_array, self.f(self.period * freq * time_array)), -1.0, 1.0)
    def FM(self, midi=60, vel=98, dur=1.0, fm=None, fm_midi=36, fm_vel=98, fm_rad=2):
        if fm is None:
            fm = Sine(self.sample_rate)
            fm.set_adsr(0,0,1.0,0)
        freq = noteToFreq(midi)
        amp = vel / 128
        fm_ring = fm_rad * fm(fm_midi, fm_vel, dur)
        time_array = np.linspace(0, dur, int(self.sample_rate * dur), False)
        envelope_array = self.get_adsr_buffer(dur)
        return np.clip(amp * np.multiply(envelope_array, self.f(self.period * freq * time_array + fm_ring)), -1.0, 1.0)
    def FM_from_buffer(self, midi=60, vel=98, dur=1.0, fm_buffer=None, fm_rad=2):
        if fm_buffer is None:
            fm = Sine(self.sample_rate)
            fm.set_adsr(0,0,1.0,0)
            fm_buffer = fm(48, 98, dur)
        fm_buffer = fm_rad * fm_buffer
        freq = noteToFreq(midi)
        amp = vel / 128
        time_array = np.linspace(0, dur, int(self.sample_rate * dur), False)
        envelope_array = self.get_adsr_buffer(dur)
        return np.clip(amp * np.multiply(envelope_array, self.f(self.period * freq * time_array + fm_buffer)), -1.0, 1.0)

    @staticmethod
    def save(buffer, name="./wave", sample_rate=44100):
        buffer = np.int16(buffer * 32767)
        with _w.open(name+'.wav', 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(buffer.tobytes())

    
class Sine(Wave):
    def __init__(self, shape=0.5, sample_rate=44100):
        super().__init__(shape,sample_rate)
        self.period = 2 * np.pi
        self.f = np.vectorize(lambda x: np.sin(x) / (np.abs(np.sin(x)) ** (2*self.shape - 1)) if np.sin(x) != 0 else 0.0)

class Cos(Wave):
    def __init__(self, shape=0.5, sample_rate=44100):
        super().__init__(shape,sample_rate)
        self.period = 2 * np.pi
        self.f = np.vectorize(lambda x: np.cos(x) / (np.abs(np.cos(x)) ** (2*self.shape - 1)) if np.cos(x) != 0 else 0.0)

class SSine(Wave):
    def __init__(self, shape=0.5, sample_rate=44100):
        super().__init__(shape, sample_rate)
        self.period = 2 * np.pi
        self.f = np.vectorize(lambda x: np.sin((9*self.shape + 1)*np.sin(x)))

class Saw(Wave):
    def __init__(self, shape=0.5, sample_rate=44100):
        super().__init__(shape,sample_rate)
        saw = lambda x: x - np.floor(x)
        self.f = np.vectorize(lambda x: saw(x)/self.shape - 1 if saw(x) < self.shape else saw(-x)/(self.shape-1) + 1)

class Square(Wave):
    def __init__(self, shape=0.5, sample_rate=44100):
        super().__init__(shape,sample_rate)
        self.f = np.vectorize(lambda x: 1.0 if x%1 < self.shape else -1.0)

class Tri(Wave):
    def __init__(self, shape=0.5, sample_rate=44100):
        super().__init__(shape,sample_rate)
        saw = lambda x: x - np.floor(x)
        self.f = np.vectorize(lambda x: 2*saw(x)/self.shape - 1 if x%1 < self.shape else 2*saw(-x)/(1-self.shape) - 1)

class Fin(Wave):
    def __init__(self, shape=0.5, sample_rate=44100):
        super().__init__(shape,sample_rate)
        mod = lambda x: (2*x)%1
        self.f = np.vectorize(lambda x: 2*mod(x)**(1/self.shape) - 1 if x%1 < 0.5 else -2*mod(x)**(1/self.shape) + 1)

class Spike(Wave):
    def __init__(self, shape=0.5, sample_rate=44100):
        super().__init__(shape,sample_rate)
        mod = lambda x: (2*x)%1
        self.f = np.vectorize(lambda x: 2*mod(x)**(1/self.shape) - 1 if x%1 < 0.5 else 2*mod(-x)**(1/self.shape) - 1)

waves = {
    "sin":Sine,
    "cos":Cos,
    "ssi":SSine,
    "saw":Saw,
    "sqr":Square,
    "tri":Tri,
    "fin":Fin,
    "spk":Spike
}

def CreateSineFMKeyboard():
    c1 = 24
    v_sub = 8
    v_step = int(127/v_sub)
    start_dur = 64
    sine = Sine()
    tri = Tri(0.4)
    tri.set_adsr(0,0,1,0)
    tri_rad = 3
    cutoff_max = 5000
    cutoff_min = 800
    cutoff_step = (cutoff_max-cutoff_min)/v_sub
    for i in range(8):
        midi_note = c1 + 12*i
        fm_note = c1 + 12*(i-1)
        dur = start_dur/(2**i)
        sine.set_adsr(r=dur*950)
        for v in range(v_sub):
            vel = v_step*(v+1)
            note = LP(sine.FM(midi_note, vel, dur, tri, fm_note, vel, tri_rad), cutoff_min+cutoff_step*v)
            name = f"{bitSamples}/SineFM/C{i+1}v{v+1}"
            Wave.save(note, name)
            print(f"Saved {name}.wav!")

def CreateTriFMKeyboard():
    c1 = 24
    v_sub = 8
    v_step = int(127/v_sub)
    start_dur = 64
    tri = Tri(0.7)
    square = Square(0.2)
    square.set_adsr(0,0,1,0)
    square_rad = 2
    cutoff_max = 6000
    cutoff_min = 800
    cutoff_step = (cutoff_max-cutoff_min)/v_sub
    for i in range(8):
        midi_note = c1 + 12*i
        fm_note = midi_note + 7
        dur = start_dur/(2**i)
        tri.set_adsr(r=dur*950)
        for v in range(v_sub):
            vel = v_step*(v+1)
            note = LP(tri.FM(midi_note, vel, dur, square, fm_note, vel, square_rad), cutoff_min+cutoff_step*v)
            name = f"{bitSamples}/TriFM/C{i+1}v{v+1}"
            Wave.save(note, name)
            print(f"Saved {name}.wav!")

def CreateFinFMKeyboard():
    c1 = 24
    v_sub = 8
    v_step = int(127/v_sub)
    start_dur = 64
    fin = Fin(0.41)
    saw = Saw(0.22)
    saw.set_adsr(0,0,1,0)
    saw_rad = 3
    spike = Spike(0.83)
    spike.set_adsr(0,0,1,0)
    spike_rad = 0.08
    cutoff_max = 8000
    cutoff_min = 800
    cutoff_step = (cutoff_max-cutoff_min)/v_sub
    for i in range(8):
        midi_note = c1 + 12*i
        fm_note = midi_note + 7
        am_note = c1 + 12*(i-1)
        dur = start_dur/(2**i)
        fin.set_adsr(s=0.3, r=dur*950)
        for v in range(v_sub):
            vel = v_step*(v+1)
            buffer = spike.AM(fm_note, vel, dur, saw, am_note, vel, spike_rad)
            note = LP(fin.FM_from_buffer(midi_note, vel, dur, buffer, saw_rad), cutoff_min+cutoff_step*v)
            name = f"{bitSamples}/FinFM/C{i+1}v{v+1}"
            Wave.save(note, name)
            print(f"Saved {name}.wav!")

def CreateFinFM2Keyboard():
    c1 = 24
    v_sub = 8
    v_step = int(127/v_sub)
    start_dur = 64
    fin = Fin(0.67)
    saw = Saw(0.42)
    saw.set_adsr(0,0,1,0)
    saw_rad = 2.01
    spike = Spike(0.73)
    spike.set_adsr(0,0,1,0)
    spike_rad = 0.11
    cutoff_max = 2000
    cutoff_min = 500
    cutoff_step = (cutoff_max-cutoff_min)/v_sub
    for i in range(8):
        midi_note = c1 + 12*i
        fm_note = midi_note + 7
        am_note = c1 + 12*(i-1)
        dur = start_dur/(2**i)
        fin.set_adsr(s=0.3, r=dur*950)
        for v in range(v_sub):
            vel = v_step*(v+1)
            buffer = spike.AM(fm_note, vel, dur, saw, am_note, vel, spike_rad)
            note = LP(fin.FM_from_buffer(midi_note, vel, dur, buffer, saw_rad), cutoff_min+cutoff_step*v)
            name = f"{bitSamples}/FinFM2/C{i+1}v{v+1}"
            Wave.save(note, name)
            print(f"Saved {name}.wav!")

def CreateTriBellAMKeyboard():
    heads = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    c1 = 24
    v_sub = 8
    v_step = int(127/v_sub)
    num_of_notes = 7*12
    start_dur = 2
    end_dur = 1
    step_dur = (start_dur-end_dur)/num_of_notes
    tri = Tri(0.45)
    sine = Sine()
    sine.set_adsr(0,0,1,0)
    sine_rad = 0.21
    cutoff_max = 10000
    cutoff_min = 1000
    cutoff_step = (cutoff_max-cutoff_min)/v_sub
    for i in range(num_of_notes):
        midi_note = c1 + i
        am_note = midi_note + 12
        dur = start_dur - step_dur*i
        tri.set_adsr(a=min(10, 10*dur), d=min(35, 35*dur), s=0.15, r=dur*950)
        for v in range(v_sub):
            vel = v_step*(v+1)
            note = LP(tri.AM(midi_note, vel, dur, sine, am_note, vel, sine_rad), cutoff_min+cutoff_step*v)
            name = f"{bitSamples}/TriBellAM/{heads[i%12]}{i//12+1}v{v+1}"
            Wave.save(note, name)
            print(f"Saved {name}.wav!")

def CreateRandomPercKeyboard(name="RandomPerc", max_dur=2, min_dur=1):
    t0 = _t.time()
    folder = f"{bitSamples}/{name}"
    try:
        _p(folder).mkdir(parents=True)
    except FileExistsError:
        yn = input("Instrument already exists. Override? (y/n) ")
        if yn == "n": return
    heads = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    c1 = 24
    v_sub = 16
    v_step = int(127/v_sub)
    num_of_notes = 7*12
    start_dur = max_dur
    end_dur = min_dur
    step_dur = (start_dur-end_dur)/num_of_notes
    cutoff_max = 12000
    cutoff_min = 200
    cutoff_step = (cutoff_max-cutoff_min)/v_sub
    for i in range(num_of_notes):
        midi_note = c1 + i
        fm_note = midi_note + _r.randint(-23,23)
        dur = start_dur - step_dur*i
        wave = _r.choice(list(waves.values()))(_r.random())
        fm = _r.choice(list(waves.values()))(_r.random())
        wave.set_adsr(a=min(10, 10*dur), d=min(35, 35*dur), s=0.15, r=dur*950)
        fm.set_adsr(0,0,1,0)
        fm_rad = _r.random()*10+1
        for v in range(v_sub):
            vel = v_step*(v+1)
            note = LP(wave.FM(midi_note, vel, dur, fm, fm_note, vel, fm_rad), cutoff_min+cutoff_step*v)
            name = f"{folder}/{heads[i%12]}{i//12+1}v{v+1}"
            Wave.save(note, name)
            print(f"Saved {name}.wav")
    t1 = _t.time()
    print(f"Done! It took {int(t1-t0)} seconds to run.")

def CreateRandomWavePercKeyboard(wave_class=_r.choice(list(waves.values())), name="RandomWave", max_dur=2, min_dur=1):
    t0 = _t.time()
    folder = f"{bitSamples}/{name}"
    try:
        _p(folder).mkdir(parents=True)
    except FileExistsError:
        yn = input("Instrument already exists. Override? (y/n) ")
        if yn == "n": return
    heads = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    c1 = 24
    v_sub = 16
    v_step = int(127/v_sub)
    num_of_notes = 7*12
    start_dur = max_dur
    end_dur = min_dur
    step_dur = (start_dur-end_dur)/num_of_notes
    cutoff_max = 12000
    cutoff_min = 200
    cutoff_step = (cutoff_max-cutoff_min)/v_sub
    offstep = _r.choice([-12,12,7])
    fm_rad = _r.random() + 2
    for i in range(num_of_notes):
        midi_note = c1 + i
        fm_note = midi_note + offstep
        dur = start_dur - step_dur*i
        wave = wave_class(_r.random())
        fm = _r.choice(list(waves.values()))(_r.random())
        wave.set_adsr(a=min(10, 10*dur), d=min(35, 35*dur), s=0.15, r=dur*950)
        fm.set_adsr(0,0,1,0)
        for v in range(v_sub):
            vel = v_step*(v+1)
            note = LP(wave.FM(midi_note, vel, dur, fm, fm_note, vel, fm_rad), cutoff_min+cutoff_step*v)
            name = f"{folder}/{heads[i%12]}{i//12+1}v{v+1}"
            Wave.save(note, name)
            print(f"Saved {name}.wav")
    t1 = _t.time()
    print(f"Done! It took {int(t1-t0)} seconds to run.")

def main():
    CreateTriBellAMKeyboard()
    for i in range(1,3):
        CreateRandomWavePercKeyboard(Sine, f"Sine{i}", 12, 2)
        CreateRandomWavePercKeyboard(Cos, f"Cos{i}", 12, 2)
        CreateRandomWavePercKeyboard(SSine, f"SSine{i}", 12, 2)
        CreateRandomWavePercKeyboard(Tri, f"Tri{i}", 12, 2)
        CreateRandomWavePercKeyboard(Fin, f"Fin{i}", 12, 2)
    for i in range(1,16):
        CreateRandomPercKeyboard(name=f"Percussive{i}", max_dur=24, min_dur=2)
        CreateRandomWavePercKeyboard(name=f"Wave{i}")

if __name__ == "__main__":
    main()