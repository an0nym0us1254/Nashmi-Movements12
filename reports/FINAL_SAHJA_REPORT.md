# NASHMI_DAHIYA_SAHJA_V1: the Jordanian Dahiya / As-Samer row clap

> **SIMULATION ONLY.** Nothing here has been validated on a physical G1.
> Simulation gains are not motor settings.

Nashmi stands as one of the men in the Samer row and performs the **زقفة / سحجة
الدحية**. The clap is the dominant feature. There is no cane, no Al-Hashi travel
and no side-to-side sway. The earlier `NASHMI_DAHIYA_AL_HASHI_V1` is preserved
unchanged (`nashmi/motion/dahiya.py`, `run_final.py`).

## Reproduce

```bash
PY=~/robotics/mujoco-mcp-server/.venv/bin/python
cd ~/robotics/nashmi
$PY run_sahja.py --watch                  # loop V1 in the live viewer
$PY run_sahja.py --variant RAZA --watch   # loop the energetic raz'a
$PY run_sahja.py --perturb                # 3 validation runs + 40 N pushes
MUJOCO_GL=egl $PY tools_render_sahja.py   # video + cycle strip
$PY run_sahja.py --rebuild                # re-solve the IK key poses and re-freeze
```

| artefact | path |
|---|---|
| motion code | `nashmi/motion/sahja.py` |
| frozen configuration (params) | `nashmi/motion/sahja_configs.py` |
| frozen trajectory (params, stance, CONTACT/OPEN key poses, READY) | `trajectories/NASHMI_DAHIYA_SAHJA_V1.json`, `trajectories/NASHMI_DAHIYA_SAHJA_RAZA_V1.json` |
| video reference analysis | `research/SAHJA_VIDEO_ANALYSIS.md`, frames in `research/reference_media/` |
| metrics | `experiments/logs/nashmi_dahiya_sahja_*_metrics.json`, `experiments/logs/sahja_validation.txt` |
| per-step logs | `experiments/logs/nashmi_dahiya_sahja_*_run{1,2,3}.csv` |
| videos | `videos/NASHMI_DAHIYA_SAHJA_V1_{front,threequarter}.mp4`, `videos/NASHMI_DAHIYA_SAHJA_RAZA_V1_*.mp4` |
| cycle strips | `reports/NASHMI_DAHIYA_SAHJA_V1_cycle_strip.png`, `reports/NASHMI_DAHIYA_SAHJA_RAZA_V1_cycle_strip.png` |
| experiment history | `experiments/EXPERIMENT_LOG.md`, EXP-S01 … S07 |

Replays load the frozen JSON and never re-solve IK. Three runs are bit-identical.

## What the video showed (VIDEO REFERENCE; details in `research/SAHJA_VIDEO_ANALYSIS.md`)

Sources analysed: UNESCO *As-Samer in Jordan* (Ministry of Culture film), AP Archive
Amman, Sahab 1995, Karak, and two raz'a videos (Wadi Araba, Ajajra).

**One calm clap cycle** (phase 0 = impact):

| phase | what happens |
|---|---|
| 0.75 → 1.00 | hands swing **in and up**, accelerating into the strike |
| **0.00** | **impact** at the lower sternum, on the midline, with the elbows at their most bent (~95°) |
| 0.00 → 0.30 | **palms stay pressed together** ("prayer" hands, fingers up), the calm-sahja signature |
| 0.30 → 0.45 | hands part **down, slightly forward and out**. This is the «دفع الكفين إلى الأمام»: the push comes as the hands open, not at impact |
| 0.45 → 0.75 | open plateau at navel height, wrists about shoulder-width apart, elbows ~130° |

- Tempo: calm ≈ **60/min**, raz'a ≈ **140/min**.
- The upper arms stay near the flanks and the shoulders barely move.
- No visible per-clap knee dip in the calm form (head motion < 2 cm), and the torso is upright.
- The raz'a is faster, with a short (~0.1 s) hold, a wider and lower opening, and the torso hunched 10–20°.

## How it is built (`sahja.py`)

- **One phase clock.** A single closure variable `c(phase)` follows the video timeline above.
  The closing stroke uses a warped min-jerk curve, so it *accelerates* into the strike.
- **Two IK key poses.** CONTACT and OPEN are solved on the right arm and mirrored to the left.
  The solver places the right palm site in the torso frame, keeps the palms facing each other, holds
  the fingers up (≈50° at contact, ≈42° open), keeps ≥30 mm clearance from the torso, stays
  ≥0.12 rad from joint limits, and keeps the weak 5 N·m wrists near neutral.
- **Joint-space closure.** The arms are driven *in joint space* between the two key poses by `c`.
  Elbow flexion plus shoulder internal rotation is the human mechanism, and it cannot branch-jump.
  The plan's hand gap decreases monotonically through the stroke.
- **Retargeting.** Human proportions are scaled by ≈0.6 (G1 upper arm 0.18 m).
  - CONTACT: palm at torso-frame (0.24, ±0.065, 0.13).
  - OPEN: (0.26, ±0.13, 0.05).
  - Solved elbow: 0.05 rad at contact (≈93° included; video ≈95°) and 0.43 open.
- **Visual contact.** The hand collision capsules stop **≈5–6 mm apart** (measured with
  `mj_geomDistance`), so the palms never physically touch.
- **Timing compensation.** `arm_lead` pre-shifts the arm reference to cancel the measured servo lag,
  so the impact lands on the beat.
- **Body.** A knee pulse with triple flexion, lowest just after impact. It is kept small in V1 because
  the video shows no visible dip. RAZA adds the torso hunch and a deeper pulse.
- **Balance.**
  - The widened `knees_bent` stance is reused (EXP-012/014).
  - Feed-forward `ankle_comp` / `waist_comp` cancel the measured posture-servo sag caused by the
    forward arm load (EXP-S02).
  - RAZA adds `hunch_ankle` to cancel the hunch (EXP-S06).

All tuning numbers are **EMPIRICAL SIMULATION TUNING**. The shape, phase map and tempi are
**VIDEO REFERENCE**, retargeted.

## Final metrics (3 runs each, spread 0.000e+00)

| metric | **V1** (calm, 60/min, 12 claps, 16.3 s) | **RAZA** (140/min, 16 claps, 11.2 s) |
|---|---|---|
| hand gap at impact (physical, every clap) | **5.6–5.7 mm** | **5.0–6.6 mm** |
| hand separation when open (palm sites) | 272 mm | 322 mm |
| impact timing error vs beat | 0 ms | −2 ms |
| peak closing speed (relative) | 1.21 m/s | 2.31 m/s |
| peak hand speed | 0.95 m/s | 1.90 m/s |
| peak shoulder / elbow / wrist / knee speed (rad/s) | 1.22 / 3.77 / 1.44 / 0.24 | 2.16 / 9.79 / 2.27 / 0.97 |
| time above 10 rad/s | 0 | 0 |
| peak force ratio (worst joint) | **0.195** (shoulder pitch) | **0.363** (waist pitch) |
| saturation | none | none |
| self-collision | **0%** (arm↔torso ≥ 27.6 mm) | **0%** (arm↔torso ≥ 27.4 mm) |
| joint-limit margin | 0.157 rad (ankle roll) | 0.157 rad |
| max base tilt | 2.32° | 5.19° (steady pelvis pitch-back from the hunch compensation) |
| max base roll (sway) | **0.001°** | **0.008°** |
| pelvis vertical pulse | 8.0 mm | 16.0 mm |
| pelvis xy drift | 0.2 mm | 2.0 mm |
| min foot load share | **50.0%** | **46.7%** |
| foot lift | 0% | 0% |
| min CoM support margin | 73.5 mm | 26.3 mm |

**Perturbation (open loop, 40 N for 100 ms on the torso, mid-phrase):**
- **V1** survives fore, aft, left and right with no foot lift. Min load is ≥49.6% fore/aft and 32.5% lateral.
- **RAZA** survives all four, but the fore/aft pushes briefly unload a foot. That is its limit.

## Honest limitations

- **Video resolution.** The footage is 360p. Elbow angles come from MediaPipe estimates (±10–15°),
  forward distances are visual estimates (±10 cm), and knees are hidden by thobes.
- **Body pulse.** The small V1 knee pulse (8 mm pelvis) is an engineering choice to give the beat a
  body. The calm footage shows no visible dip, so it is kept below that visibility threshold.
- **Raz'a bar pattern.** The "3 claps + held beat" bar was seen in one raz'a video only and is not
  implemented. Claps are regular.
- **Lateral shoulder roll.** A possible 5–8° roll in the footage is low confidence and deliberately omitted.
- **Palm geometry.** The G1 hand is a rubber paddle, so "prayer" palms are approximated by palm
  normals facing each other with the fingers ~50° up.
- **No balance controller.** RAZA's fore/aft push tolerance is limited.
