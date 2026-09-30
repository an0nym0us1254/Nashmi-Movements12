# Sahja / Raz'a clap: video analysis (السحجة / الرزعة)

Date: 2026-09-30 · Scope: the clap of the men's row in the Jordanian Dahiya / As-Samer ·
Status: **VIDEO EVIDENCE (human performers)**. These are measurements of people, not robot facts. Every number
below needs retargeting before it becomes a G1 joint target.

Media, frame sheets and scripts are in `research/reference_media/<videoid>/`. The full videos were deleted
after analysis. Only the cited frames and contact sheets were kept, as JPG.
Tools: yt-dlp (360p), ffmpeg frame extraction at 10–25 fps, MediaPipe PoseLandmarker (full model) on
3× upscaled crops of one dancer (`pose_track.py`), phase averaging over clap cycles (`cycle_average.py`), and
audio onset/autocorrelation (`clap_tempo.py`, `clap_onsets.py`).

> The `overview.jpg` timestamps are approximate (±half a sampling step). Every time quoted in this document
> comes from exact seeks (`-ss`) and is in the video's own seconds.

---

## 1. Sources

| id | URL | channel | title | origin | cred. | segment analysed |
|---|---|---|---|---|---|---|
| **v53H5a4-wz4** | https://www.youtube.com/watch?v=v53H5a4-wz4 | UNESCO | *As-Samer in Jordan* (the ICH nomination film by the Jordanian Ministry of Culture, Heritage Directorate) | Jordan (official) | **A** | 93.6–113.3 s: one 20 s shot of a frontal row in white thobes (staged). Also 480–489 s (field night samer, audio) |
| **HXpAg_Q7hzs** | https://www.youtube.com/watch?v=HXpAg_Q7hzs | AP Archive | *As-Samer dance on UNESCO cultural heritage list* | Amman, Jordan (news footage) | **A** | 8.3–13.4 s hands close-up; 13.4–18.4 s frontal-oblique; **30.4–36.4 s oblique view down the row** (the best view of depth) |
| **cTL7x57DpsQ** | https://www.youtube.com/watch?v=cTL7x57DpsQ | Hammam Alshawabkeh | شرح عن السامر الاردني السحجه الرقصه سحاب 1995 | Sahab (Amman gov.), Jordan, 1995 archive | **B** | 68.6–87.8 s: full-body frontal row of older men |
| **K9s1sjQx8pQ** | https://www.youtube.com/watch?v=K9s1sjQx8pQ | jo fa | سامر كركي أصيل قضاه وبشايشه | Karak, Jordan (phone video) | **B** | 15–30 s and 90–130 s (audio tempo; the image is too blurred for pose work) |
| **WjrHSz6N3gg** | https://www.youtube.com/watch?v=WjrHSz6N3gg | البادية الجنوبية | سامر ودحية السعيديين وادي عربة /الرزعة | Wadi Araba, south Jordan | **B** | **Raz'a.** 42–54 s (audio rhythm and 25 fps crop); 19.5–24.5 s (crouch) |
| **bQ7uabShRpw** | https://www.youtube.com/watch?v=bQ7uabShRpw | قبايل الاردن 🇯🇴 | رزعه شباب العجاجرة \| سامر قبيلة العجاجرة بالاردن | Jordan (Ajajra tribe, indoor wedding) | **B** | **Raz'a.** 0–3.2 s (one shot) |
| 3uEsl9l_pTQ | https://www.youtube.com/watch?v=3uEsl9l_pTQ | هايل العطوي | دحية شباب بني عطية في علقان | Bani Atiyah, at Alqan. The tribe spans Jordan and Saudi Arabia, and Alqan may be on the Saudi side | C | Montage of 1–4 s cuts with no audio track. Used only as a qualitative check of posture |
| lhOxLHIgjRM | https://www.youtube.com/watch?v=lhOxLHIgjRM | D tube | Jordan سحجه معانيه | Ma'an, Jordan (audio over still images) | C | Audio only. Not used for motion |

Rejected after overview: `oc2R3aK0vFw` (dancers too distant). Search hits that were Palestinian or Saudi
(`Irj6wckiPqU`, `2qawxcVas0A`, …) were not analysed.

---

## 2. Findings per question

### 2.1 Arm posture between claps (the "open" phase)
- **Upper arms hang close to the torso**, slightly forward of vertical (about 10–25°). The elbows stay near the
  flanks. The **forearms point forward**, roughly horizontal to slightly downward.
  Evidence: `HXpAg_Q7hzs/pair_oblique_4.jpg` (30.92 s and 31.84 s, oblique down the row); `v53H5a4-wz4/frame_0936_full.jpg`.
- **Elbow included angle** (MediaPipe world landmarks, phase-averaged, UNESCO 93.6–103.6 s, 9 cycles):
  **≈ 95° at contact → ≈ 130° (range 125–135°) at mid-open → back to ≈ 100–105° just before impact.**
  Raz'a (bQ7uabShRpw 1.13–1.6 s): **≈ 90° at contact → 125–140° open.**
- **Hand height.** Palms meet at the **lower sternum / xiphoid** (about 0.55–0.67 torso lengths below the shoulder line).
  When open they drop about 5–8 cm to **upper-abdomen / navel height** (0.75–0.80 torso lengths).
  In the raz'a they drop further, to **belt / hip height** (0.9–1.0 torso lengths). Evidence: pose CSVs, and
  `bQ7uabShRpw/pair_1.2_1.47.jpg` (top: contact at the chest; bottom: open at the belt).
- **Opening width.** Wrist-to-wrist distance in the open phase is **≈ 0.8–1.1 × the shoulder-joint width**, about
  **30–35 cm** (MediaPipe world 0.30–0.33 m). The palms are about 25–30 cm apart, roughly the width of the torso.
  In the raz'a it is ≈ 1.2–1.35 × shoulder width, about 35–40 cm. At contact the wrists stay about 15 cm apart
  because the hands form a "V" or prayer shape.
  Evidence: `v53H5a4-wz4/sheet_0936_25fps_man2.jpg` frames 24–36 (open) vs 13–19 (together).
- **Forward distance.** At contact the hands are about **25–35 cm in front of the chest** (visual estimate from the
  oblique AP view). When open they sit about the same distance forward or slightly further, lower and wider.
  MediaPipe's depth (z) gives only 0.10–0.12 m wrist-forward-of-shoulder. It is known to under-read depth,
  so the visual estimate is preferred.

### 2.2 Hand shape and orientation
- Palms are flat, fingers together, **palms facing each other** (thumbs up, hands vertical). Evidence:
  `v53H5a4-wz4/frame_0936_full.jpg` (2nd from right), `HXpAg_Q7hzs/grid_hands_front.jpg` (bottom two).
- Finger direction: **up and forward**, about 45–70° above horizontal in the frontal shots, which gives a
  "prayer" look at contact. In the AP close-up (`HXpAg_Q7hzs/sheet_0090_25fps_hands.jpg`) they are closer to 30–45°.
- The palms meet **flat and fully overlapping**, often with a slight offset: one hand's fingers extend past the
  other's. **No consistent "right strikes left" pattern was found.** The motion is symmetric to within the
  resolution of the footage.
- At contact the fingertips lean slightly toward each other, so the wrists stay apart (≈ 15 cm).

### 2.3 Where the palms meet
- In front of the **lower sternum / upper abdomen**, on the body midline, about 25–35 cm forward of the chest.
  There is individual variation: older men in the UNESCO shot (left dancer in `v53H5a4-wz4/sheet_0956_10fps_hands.jpg`)
  and in Sahab 1995 clap nearer the navel or high on the chest.

### 2.4 One clap cycle, in sequence
Evidence: `v53H5a4-wz4/sheet_0936_25fps_man2.jpg` (25 fps, 2.4 s, one dancer); `v53H5a4-wz4/sheet_0956_10fps_hands.jpg`
(6 cycles); `HXpAg_Q7hzs/sheet_0306_25fps_crop.jpg` (oblique); phase-averaged pose data.

1. **Impact.** The hands close in the last **1–2 frames (40–80 ms)**. Every closing is motion-blurred
   (UNESCO frames 12 and 37; AP oblique frames 8–10 and 23–25), so the final approach is fast.
2. **Pressed hold.** The palms **stay together for ≈ 0.25–0.4 s**, about 30–40 % of the cycle
   (UNESCO frames 13–19 and 39–46). This hold is the most distinctive feature of the calm sahja.
3. **Separation.** Over ≈ 0.15 s the hands part while moving **down, slightly forward and out**. The elbows extend
   from about 95° to about 125°.
4. **Open plateau.** For ≈ 0.3 s the hands sit about 30–35 cm apart at navel height, palms facing, elbows about 130°.
5. **Return swing.** The hands move **inward and up** (elbows flex back toward 100°), accelerate, and strike at
   the lower sternum.

**The loop is therefore "open low and wide → strike high and in".** The forward extension happens while the
hands open, not at the clap. There is no forward thrust at the moment of contact (the elbow is at its most
bent then) and **no downward chop**: the striking stroke rises a little, by 5–8 cm (calm) and 10–15 cm (raz'a).
Most of the movement is at the **elbow**, with a little shoulder adduction and abduction (the hands travel
about 8–10 cm sideways each). Shoulder flexion is small. The shoulders themselves hardly move.

### 2.5 Knees and vertical body motion
- **Calm sahja: no visible dip on each clap.** Full-body shots (Sahab 1995, `cTL7x57DpsQ/sheet_076_10fps_crop.jpg`;
  UNESCO; AP) show men standing with near-straight, soft knees. Nose-height variation over the phase-averaged
  cycle is ±2–3 px on a body about 330 px tall, which is **< ~2 cm and at the noise floor**. Knees are hidden
  under thobes, and MediaPipe knee angles were unusable, so this is an upper bound, not a measurement.
- **Raz'a: deeper forward crouches occur, but not in step with each clap.** In the Wadi Araba video several men
  fold forward at hip and knee (torso about 30–45° forward, head down) for seconds at a time
  (`WjrHSz6N3gg/stack_227_241.jpg`, middle frame 23.3 s, and `sheet_0195_5fps.jpg` 22.5–24.5 s).
  In the Ajajra raz'a the head height at contact (1.2 s) and at open (1.47 s) is the same to within a few px
  (`bQ7uabShRpw/pair_1.2_1.47.jpg`), so there is no clear per-clap dip.
- If a per-clap bounce exists at all, it is small (≤ 2–3 cm) and could not be resolved. Treat any knee bounce as optional.

### 2.6 Torso
- Calm: **upright, with at most a slight stoop of about 5–10°** (older men in Sahab 1995 more so). No pitch
  forward on the clap could be seen. The MediaPipe "lean" values were too noisy to use and were discarded.
- Side sway: the shoulder-line roll changes by about 5–8° over the cycle (UNESCO phase average: +1° at contact,
  −5 to −7.5° mid-open). This is **low confidence**, because a small camera roll or pan could produce it.
  If real, it is secondary.
- Raz'a: noticeably more **forward-hunched**, with the shoulders rounded forward (Ajajra bottom frame,
  Wadi Araba 23.3 s), plus the episodic deep crouch described in 2.5.

### 2.7 Head
- Head held level, facing forward or turned toward the poet (*bada'*) / *hashi*. No per-clap nod was measured
  (nose-y within noise). In the raz'a the head drops forward along with the torso during crouches.

### 2.8 Calm sahja vs raz'a

| | calm sahja | raz'a |
|---|---|---|
| clap period | **≈ 1.0 s (57–65 /min)** | **≈ 0.42–0.47 s (128–143 /min)** |
| pressed hold after impact | long, 0.25–0.4 s (30–40 % of cycle) | short, ≈ 0.1 s, except the held 4th beat (below) |
| open width (wrists) | 0.8–1.1 × shoulder width (30–35 cm) | 1.2–1.35 × shoulder width (35–40 cm) |
| open height | navel | belt / hip |
| elbow range | 95° ↔ 130° | 90° ↔ 135–140° |
| torso | upright | hunched forward, occasional deep forward crouch |
| sharpness | sharp impact, calm opening | sharp impact, whip-like both ways |

### 2.9 Rhythm pattern
- Calm (UNESCO, AP, Karak, Sahab): **regular single claps, one per beat, each followed by a pressed hold.**
  No double claps were seen.
- Wadi Araba raz'a (audio onsets 42–54 s): **groups of three claps 0.40–0.43 s apart, then a gap of 0.81–0.85 s**,
  for example 43.06 / 43.46 / 43.88 — gap — 44.71 / 45.14 / 45.56 — gap — 46.41 …, a bar of about 1.67 s.
  Video at 25 fps (`WjrHSz6N3gg/sheet_0429_25fps_crop.jpg`) shows that **during the gap the palms stay pressed
  together** (frames 25–39 ≈ 43.9–44.5 s), then open wide and strike. In effect this is "clap-clap-clap-hold"
  over 4 beats. It was seen in only one video, so treat it as a regional or ensemble variant.
- Ajajra raz'a: continuous single claps at about 0.43 s intervals (audio median IOI 0.42 s; pose contacts
  1.13 → 1.60 s).

---

## 3. One clap cycle: phase table (calm sahja, period T ≈ 1.0 s; phase 0 = palm impact)

Sources: UNESCO pose phase average (9 cycles) plus visual timing from the 25 fps sheets. The raz'a column
gives the changes to make, with T ≈ 0.45 s.

| phase | event | wrist separation | hand height | forward reach (wrist ahead of chest) | elbow incl. angle | knee | torso |
|---|---|---|---|---|---|---|---|
| 0.00 | **impact** (hands arrive at speed) | ≈ 0.15 m (palms touching) | lower sternum | ≈ 25–30 cm | ≈ 95° | soft, ~straight | upright |
| 0.00–0.30 | **pressed hold** | ≈ 0.15 m | lower sternum | same | 95–100° | – | – |
| 0.30–0.45 | separate: down, slightly forward, out | 0.15 → 0.30 m | drops 5–8 cm | +0–5 cm | 100 → 125° | – | – |
| 0.45–0.75 | **open plateau** | 0.30–0.33 m (max ≈ 0.6) | navel | ≈ 30–35 cm | 125–132° (max) | – | – |
| 0.75–0.92 | return: in and up, accelerating | 0.33 → 0.25 m | rises | –0–5 cm | 130 → 105° | – | – |
| 0.92–1.00 | **fast final closure** (40–80 ms) | 0.25 → 0.15 m | lower sternum | 25–30 cm | ≈ 100 → 95° | – | – |

Raz'a changes: hold shrinks to about 0–0.2 of the cycle; open plateau at belt height with wrists 0.35–0.40 m apart;
elbow up to 135–140°; torso hunched 10–20° forward, with occasional multi-second deep crouches of 30–45°.
Optional "3 claps + held 4th beat" bar.

---

## 4. Tempo estimates

| video | kind | method | result |
|---|---|---|---|
| v53H5a4-wz4 93.6–101.6 s | calm | **visual count**: contacts ≈ 94.12, 95.08, 96.2, 97.2, 98.25, 99.2, 100.3, 101.2 s (`sheet_0936_25fps_man2`, `sheet_0956_10fps_hands`) | **1.01 s → ≈ 60 /min** |
| same | calm | pose-based contact detection (`cycle_average.py`) | median 1.00 s (60 /min); individual periods noisy |
| same | calm | audio autocorrelation (onset envelope, HP 1.5 kHz) | peaks 0.48 s and 0.96 s. The 0.48 s peak is the chant sub-beat; the clap period is 0.96 s |
| v53H5a4-wz4 480–493 s (field) | calm | audio AC | 1.05 s (57 /min) |
| HXpAg_Q7hzs 30.4–32.4 s | calm | visual (oblique 25 fps: contacts at frames 12 and 35) | 0.92 s (65 /min) |
| HXpAg_Q7hzs 0–20 s | calm | audio AC | 0.96 s (62 /min) |
| K9s1sjQx8pQ 15–30 s | calm (Karak) | audio AC | 1.05 s (57 /min) |
| cTL7x57DpsQ 70–100 s | calm (Sahab 1995) | audio AC / pose | 0.99 s (61 /min) / pose median 0.80 s (noisy, occlusions) |
| bQ7uabShRpw 0–8 s | **raz'a** | audio onset median IOI / pose | **0.42 s (143 /min)** / 0.43–0.47 s |
| WjrHSz6N3gg 2–27 s and 42–58 s | **raz'a** | audio AC and onsets | beat 0.41–0.43 s (≈ 140 /min); bar of 3 claps plus a held beat ≈ 1.65 s (AC peak 0.82 s = 2 beats) |
| lhOxLHIgjRM (Ma'an, audio only) | ? | onsets | very regular 0.21 s IOI (≈ 286 /min). Probably a percussion or fast-clap studio track; not used |

**Summary: calm sahja ≈ 60 claps/min (0.95–1.05 s); raz'a ≈ 130–145 claps/min (0.42–0.47 s).**
The onset-IOI medians from field recordings (0.27–0.36 s) were rejected, because sung consonants and
unsynchronised clappers dominate them. Autocorrelation plus visual counting is the reliable method.

---

## 5. Uncertainty notes
- **Resolution and occlusion.** 360p video. Thobes hide the knees and hips, so knee flexion is **not measured**,
  only bounded (no visible dip > ~2–3 cm in the calm sahja).
- **MediaPipe on crops.** Elbow angles come from 3D world landmarks. The pattern (flex at contact, extend
  when open) is consistent across UNESCO, Ajajra and the AP visuals, but absolute values carry about ±10–15°
  of error. Depth (forward reach) from MediaPipe under-reads, so forward distances are visual estimates (±10 cm).
  The torso-lean and knee channels were discarded as noise. Pose tracking of the Wadi Araba video failed
  because the legs are out of frame and the light is poor.
- **Staging.** The UNESCO shot at 93.6 s is a staged ensemble in white thobes. Its movement matches the AP
  footage and the Sahab 1995 field footage, but it is tidier and more uniform than a real wedding.
- **Individual variation.** Contact height ranges from high chest (Sahab 1995 elders) to navel. Some men barely
  open their hands (≈ 10–15 cm).
- **Rhythm variants.** The "3 claps + hold" bar was seen in only one video (Wadi Araba). Ma'an sahja rhythm is
  unresolved (audio only).
- **Hand dominance.** No consistent striking hand was resolved; the motion was modelled as symmetric.
- **Sway.** The ≈ 5–8° shoulder roll has low confidence because the camera may have rolled.

## 6. Reproducing the measurements
```bash
V=<scratch venv with mediapipe+opencv>/bin/python        # PoseLandmarker 'full' model .task file
$V research/reference_media/pose_track.py <video> 93.6 10 395 30 575 360 out.csv 25 45
$V research/reference_media/cycle_average.py out.csv 0.5
~/robotics/mujoco-mcp-server/.venv/bin/python research/reference_media/clap_tempo.py <video> 93.6 10
```
To reproduce, re-download the videos with yt-dlp (`-f "best[height<=360]"`) using the IDs above.
