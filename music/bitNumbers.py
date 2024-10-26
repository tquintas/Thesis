import random2 as _r



def randomAround(center, rad, n):
    return [center + _r.uniform(-1.0, 1.0)*rad for _ in range(n)]

def randomScaleUp(begin, rad, interv, n):
    return [begin + (interv * i) + _r.uniform(-1.0, 1.0)*rad for i in range(n)]

def randomScaleDown(begin, rad, interv, n):
    return [begin - (interv * i) + _r.uniform(-1.0, 1.0)*rad for i in range(n)]

def linear(begin, end, sub):
    step = (end - begin) / sub
    return [begin + i*step for i in range(sub+1)]


def Resonance(idx, name, n, soundname):
    folder = "/Applications/bitklavier/preparations/Resonance"
    fundamental = _r.randint(60, 66)
    notes = sorted([_r.randint(0,127) for _ in range(n)])
    s = f"""<?xml version="1.0" encoding="UTF-8"?>
<resonance Id="{idx}" name="{name}{idx}">
  <params gain="1.059253692626953" gain_inc="0.0" gain_time="0" gain_maxN="0"
          blendronicGain="1.0" blendronicGain_inc="0.0" blendronicGain_time="0"
          blendronicGain_maxN="0" resonanceUseGlobalSoundSet="0" resonanceUseGlobalSoundSet_time="0"
          resonanceUseGlobalSoundSet_maxN="0" resonanceSoundSet="{soundname}" resonanceSoundSet_time="0"
          resonanceSoundSet_maxN="0" starttimeMin="400" starttimeMin_inc="0"
          starttimeMin_time="0" starttimeMin_maxN="0" starttimeMax="4000"
          starttimeMax_inc="0" starttimeMax_time="0" starttimeMax_maxN="0"
          maxSympStrings="{n}" maxSympStrings_inc="0" maxSympStrings_time="0"
          maxSympStrings_maxN="0" fundamentalKey="{fundamental}" fundamentalKey_inc="0"
          fundamentalKey_time="0" fundamentalKey_maxN="0" closestKeys_time="0"
          closestKeys_maxN="0" offsets_time="0" offsets_maxN="0" gains_time="0"
          gains_maxN="0">
    <ADSR f0="50" f0_inc="0" f0_time="0" f0_maxN="0" f1="3" f1_inc="0"
          f1_time="0" f1_maxN="0" f2="1.0" f2_inc="0.0" f2_time="0" f2_maxN="0"
          f3="50" f3_inc="0" f3_time="0" f3_maxN="0"/>
    <closestKeys {" ".join([f'i{i}="{notes[i]}"' for i in range(n)])}/>
    <closestKeys_inc i0="0"/>
    <offsets {" ".join([f'f{i}="{_r.randint(-20,20)}"' if i in notes else f'f{i}="0.0"' for i in range(127)])}/>
    <offsets_inc f0="0.0"/>
    <gains {" ".join([f'f{i}="{_r.randint(70,120)/100}"' if i in notes else f'f{i}="1.0"' for i in range(127)])}/>
    <gains_inc f0="0.0"/>
  </params>
</resonance>
"""
    with open(f"{folder}/{name}{idx}.xml", "w") as xml:
        xml.write(s)

Resonance(1, "IVLeft", 16, "Sine1")
Resonance(2, "IVLeft", 17, "Cos1")
Resonance(3, "IVLeft", 18, "Fin1")
Resonance(4, "IVLeft", 19, "SSine1")
Resonance(5, "IVLeft", 20, "Tri1")
Resonance(1, "IVRight", 16, "Sine2")
Resonance(2, "IVRight", 17, "Cos2")
Resonance(3, "IVRight", 18, "Fin2")
Resonance(4, "IVRight", 19, "SSine2")
Resonance(5, "IVRight", 20, "Tri2")