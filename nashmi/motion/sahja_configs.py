"""Frozen configurations of NASHMI_DAHIYA_SAHJA (see sahja.py).

The IK-solved key poses for each are frozen under trajectories/<name>.json,
so replays never re-solve IK.
"""

VARIANTS = {
    # calm sahja -- tempo from the video (≈60 claps/min: UNESCO 1.01 s,
    # AP 0.92 s, audio 0.96-1.05 s)
    "V1": dict(name="NASHMI_DAHIYA_SAHJA_V1", params=dict(
        bpm=60.0, clap_gap=0.008, arm_lead=0.07)),
    # energetic raz'a (الرزعة) -- VIDEO: ≈140 claps/min (Ajajra audio 0.42 s,
    # Wadi Araba 0.41-0.43 s), short ≈0.1 s pressed hold, open wider and
    # lower (belt height), torso hunched 10-20 deg forward.
    "RAZA": dict(name="NASHMI_DAHIYA_SAHJA_RAZA_V1", params=dict(
        bpm=140.0, clap_gap=0.016, arm_lead=0.095,
        ph_dwell=0.23, ph_open=0.42, ph_close=0.70,
        open_half=0.15, open_z=0.0, open_x=0.27,
        hunch=0.20, hunch_ankle=0.04, knee_pulse=0.12,
        claps=16, ramp_claps=3)),
}
