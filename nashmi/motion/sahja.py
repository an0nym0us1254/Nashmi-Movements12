"""NASHMI_DAHIYA_SAHJA — the Jordanian Dahiya / As-Samer ROW CLAP (زقفة / سحجة).

Nashmi is one of the men standing in the Samer row. The clap is the star.
(The previous NASHMI_DAHIYA_AL_HASHI_V1 in `dahiya.py` is a different role and
is preserved untouched.)

Design
------
ONE phase clock drives everything. Phase 0 (== 1) is the moment of palm
contact. Every channel is a periodic profile over that phase:

    hand closure   open -> fast inward travel -> CONTACT -> dwell -> reopen
    hand position  one closure variable c(phase) moves the hands between the
                   OPEN pose (low, forward, apart) and the CONTACT pose (high,
                   in, lower sternum). So the hands separate DOWN/FORWARD/OUT
                   -- the sahja push «صفق الكفين مع دفعهما إلى الأمام», which
                   the video shows happens as the hands part -- and strike
                   back IN and UP.
    knee pulse     body lowers just after the impact, rises between claps
    torso          upright (calm) or hunched (raz'a)

Two arm key poses, CONTACT and OPEN, are solved by constrained IK (right
hand site in the torso frame, palms facing, wrists regularised, collision
margins), the left arm mirrored. The arms are driven between them in JOINT
space by the closure channel. (Per-sample Cartesian IK was tried first and
rejected: the palm-orientation constraint made the wrists branch-jump,
25-36 rad/s in the plan -- see EXPERIMENT_LOG EXP-S04.)

Contact is VISUAL, not physical: the hand collision capsules stop
`clap_gap` short of touching (the MJX scene has a real left_hand<->right_hand
contact pair, and slamming it throws the robot, EXP-020).

Labels: every number below is EMPIRICAL SIMULATION TUNING unless it says it
comes from the video analysis (research/SAHJA_VIDEO_ANALYSIS.md).
"""

from __future__ import annotations

import json
import math
import os

import mujoco
import numpy as np
from scipy.optimize import minimize

from ..trajectory import Sequence_, hold, move

ARM = ["shoulder_pitch", "shoulder_roll", "shoulder_yaw", "elbow",
       "wrist_roll", "wrist_pitch", "wrist_yaw"]
#: left-arm sign relative to the right arm for a mirror-symmetric pose
#: (MEASURED conventions: roll, yaw and wrist roll/yaw are mirrored).
MIRROR = [1, -1, -1, 1, -1, 1, -1]
RIGHT_ARM = [f"right_{j}_joint" for j in ARM]
LEFT_ARM = [f"left_{j}_joint" for j in ARM]


# --------------------------------------------------------------------------
# parameters
# --------------------------------------------------------------------------

class SahjaParams:
    def __init__(self, **kw):
        # --- rhythm -------------------------------------------------------
        self.bpm = 90.0            # claps per minute
        self.claps = 12            # claps in the phrase

        # --- stance ---------------------------------------------------------
        self.stance_width = 0.10   # rad hip abduction per leg (validated, EXP-012)
        self.waist_pitch_bias = 0.05
        self.ankle_bias = 0.0      # rad added to both ankle_pitch: shifts the
                                   # whole body fore/aft over the planted feet
        self.hip_bias = 0.0        # rad added to both hip_pitch
        # Carrying both arms in front loads the posture servos: MEASURED sag at
        # READY is ankle_pitch -0.056 rad and waist_pitch +0.063 rad (the body
        # pitches ~5 deg forward, support margin 80 -> 16 mm). These feed-
        # forward offsets are applied whenever the arms are up (not in the
        # arms-down stand pose), so the entry ramps them in with the arms.
        self.ankle_comp = 0.03     # sweep 0.03/0.05/0.07: 0.03 levels the pelvis (-0.5 deg)
        self.waist_comp = -0.06

        # --- hand path, right hand site in TORSO frame (x fwd, y left, z up)
        # VIDEO (SAHJA_VIDEO_ANALYSIS.md), retargeted to G1 proportions at
        # ~0.6x human (G1 upper arm 0.18 m vs ~0.30 m). G1 torso frame:
        # shoulders at z=0.245, chest surface at x=0.084, torso origin = waist.
        #   contact: lower sternum, on the midline, ~25-35 cm (human) ahead
        #            of the chest, elbows at their MOST bent, fingers up.
        #   open   : lower (navel), slightly further forward, wrists about
        #            shoulder-width apart, elbows more extended.
        self.contact_x = 0.24
        self.contact_z = 0.13
        self.open_x = 0.26
        self.open_z = 0.05
        self.open_half = 0.13      # |y| of the right hand site when open
        self.clap_gap = 0.006      # capsule surface gap at "contact" (m)
        self.finger_up_contact = 1.2   # tan(elevation): ~50 deg, "prayer" hands
        self.finger_up_open = 0.9      # ~42 deg
        self.close_warp = 1.8      # >1 makes the closing stroke ACCELERATE into
                                   # the strike (VIDEO: last 40-80 ms blurred)

        # --- phase map (fractions of one clap cycle, contact at 0) ----------
        # VIDEO, calm sahja: pressed hold 0-0.30, separate down/forward/out
        # 0.30-0.45, open plateau 0.45-0.75, swing in+up 0.75-1.0.
        self.ph_dwell = 0.30       # palms held together until here
        self.ph_open = 0.45        # hands fully open here
        self.ph_close = 0.75       # hands start the stroke inward
        self.arm_lead = 0.0        # s the ARM reference runs ahead of the beat,
                                   # cancelling the measured servo lag so the
                                   # physical contact lands on the body's beat

        # --- body ---------------------------------------------------------
        # VIDEO, calm: no visible per-clap dip (head <2 cm, an upper bound);
        # torso upright, no pitch on the clap. Raz'a: hunched 10-20 deg.
        self.knee_pulse = 0.06     # rad of extra knee flexion at the low point
        self.ph_low = 0.05         # phase of the lowest point (just after impact)
        self.ph_high = 0.55        # phase of the highest point
        self.pitch_accent = 0.0    # rad of forward torso accent on the clap
        self.hunch = 0.0           # rad of constant forward torso carriage (raz'a)
        self.hunch_ankle = 0.0     # rad ankle comp for the hunch

        # --- phrase -------------------------------------------------------
        self.entry = 1.6           # s, stand -> READY
        self.settle = 0.6          # s, hold READY before the first clap
        self.ramp_claps = 2        # body pulse ramps in over these claps
        self.outro = 1.6           # s, READY -> stand

        for k, v in kw.items():
            if not hasattr(self, k):
                raise KeyError(f"unknown Sahja parameter {k!r}")
            setattr(self, k, v)

    @property
    def period(self) -> float:
        return 60.0 / self.bpm

    def as_dict(self):
        return {k: getattr(self, k) for k in vars(self)}


# --------------------------------------------------------------------------
# periodic piecewise-quintic profiles
# --------------------------------------------------------------------------

def _q5(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * u * (10.0 + u * (-15.0 + 6.0 * u))


def profile(knots, ph):
    """knots: [(phase, value), ...] sorted, phases in [0,1). Periodic; quintic
    between consecutive knots (zero velocity at every knot)."""
    ph = ph % 1.0
    ks = list(knots) + [(knots[0][0] + 1.0, knots[0][1])]
    if ph < ks[0][0]:
        ph += 1.0
    for (p0, v0), (p1, v1) in zip(ks[:-1], ks[1:]):
        if p0 <= ph <= p1:
            return v0 + (v1 - v0) * _q5((ph - p0) / max(p1 - p0, 1e-9))
    return ks[0][1]


def channels(p: SahjaParams, ph: float) -> dict:
    """All rhythmic channels at phase `ph`. closure: 1 = contact, 0 = open."""
    ph = ph % 1.0
    if ph <= p.ph_dwell:
        closure = 1.0
    elif ph <= p.ph_open:
        closure = 1.0 - _q5((ph - p.ph_dwell) / (p.ph_open - p.ph_dwell))
    elif ph <= p.ph_close:
        closure = 0.0
    else:
        u = (ph - p.ph_close) / (1.0 - p.ph_close)
        closure = _q5(u ** p.close_warp)
    low = profile([(p.ph_low, 1.0), (p.ph_high, 0.0)], ph)
    return dict(closure=closure, low=low)


# --------------------------------------------------------------------------
# model helpers
# --------------------------------------------------------------------------

def sahja_stance(nm, p: SahjaParams) -> dict:
    """Legs + waist of the verified widened `knees_bent` stance (EXP-012/014)."""
    pose = dict(nm.keyframe_pose("knees_bent"))
    pose.update(waist_yaw_joint=0.0, waist_roll_joint=0.0,
                waist_pitch_joint=p.waist_pitch_bias)
    for side in ("left", "right"):
        pose[f"{side}_ankle_pitch_joint"] += p.ankle_bias
        pose[f"{side}_hip_pitch_joint"] += p.hip_bias
    w = p.stance_width
    pose["left_hip_roll_joint"] += w
    pose["right_hip_roll_joint"] -= w
    pose["left_ankle_roll_joint"] -= w
    pose["right_ankle_roll_joint"] += w
    return {k: nm.clamp(k, v) for k, v in pose.items()}


def arms_pose(r) -> dict:
    out = {}
    for j, v, s in zip(ARM, r, MIRROR):
        out[f"right_{j}_joint"] = float(v)
        out[f"left_{j}_joint"] = float(s * v)
    return out


def body_pose(stance: dict, p: SahjaParams, ch: dict, scale: float = 1.0) -> dict:
    """Knee pulse (triple flexion keeps the pelvis over the feet) + torso accent."""
    a = p.knee_pulse * ch["low"] * scale
    out = {}
    for s in ("left", "right"):
        out[f"{s}_knee_joint"] = stance[f"{s}_knee_joint"] + a
        out[f"{s}_hip_pitch_joint"] = stance[f"{s}_hip_pitch_joint"] - 0.5 * a
        out[f"{s}_ankle_pitch_joint"] = stance[f"{s}_ankle_pitch_joint"] - 0.5 * a
        out[f"{s}_ankle_pitch_joint"] += p.ankle_comp
        out[f"{s}_ankle_pitch_joint"] += p.hunch_ankle
    out["waist_pitch_joint"] = (stance["waist_pitch_joint"] + p.waist_comp + p.hunch
                                + p.pitch_accent * ch["closure"] * scale)
    return out


class ArmIK:
    """Constrained FK/IK on a scratch MjData over a settled stance base."""

    def __init__(self, nm, stance: dict):
        self.nm, m = nm, nm.model
        self.m = m
        d = mujoco.MjData(m)
        nm.reset_to_keyframe("knees_bent")
        for jn, v in stance.items():
            nm.data.qpos[nm.joints[jn].qpos_adr] = v
        nm.data.qvel[:] = 0
        mujoco.mj_forward(m, nm.data)
        self.q0 = nm.data.qpos.copy()
        self.d = d
        G = lambda n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, n)
        self.g_lh, self.g_rh = G("left_hand_collision"), G("right_hand_collision")
        self.g_torso = G("torso_collision")
        self.g_arm = [G(n) for n in ("left_hand_collision", "right_hand_collision",
                                     "left_wrist_collision", "right_wrist_collision",
                                     "left_elbow_yaw_collision", "right_elbow_yaw_collision")]
        self.tb = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "torso_link")
        self.lo = np.array([nm.joints[n].lo for n in RIGHT_ARM])
        self.hi = np.array([nm.joints[n].hi for n in RIGHT_ARM])
        self._ft = np.zeros(6)

    def fk(self, r, extra=None):
        d, nm = self.d, self.nm
        d.qpos[:] = self.q0
        pose = dict(extra or {}); pose.update(arms_pose(r))
        for jn, v in pose.items():
            d.qpos[nm.joints[jn].qpos_adr] = v
        mujoco.mj_forward(self.m, d)
        return d

    def gd(self, a, b):
        return mujoco.mj_geomDistance(self.m, self.d, a, b, 0.5, self._ft)

    def measure(self, r):
        d = self.fk(r)
        Rt = d.xmat[self.tb].reshape(3, 3); tp = d.xpos[self.tb]
        rh = Rt.T @ (self.nm.site_pos("right_hand_site", d) - tp)
        return dict(rh=rh, gap=self.gd(self.g_lh, self.g_rh),
                    torso_gap=min(self.gd(self.g_torso, g) for g in self.g_arm))

    def solve(self, target, finger_up, seed, gap_min=0.004, lim_keep=0.12,
              torso_keep=0.03, want_gap=None, ref=None, reg=0.0, wrist_reg=0.05,
              orient_w=1.0):
        """Right-hand site to `target` (torso frame), palm normal along torso +y
        (palms facing each other), fingers forward with `finger_up` elevation.
        If `want_gap` is set the lateral coordinate is replaced by a gap target.
        `ref`/`reg` pull the solution toward another pose (joint continuity);
        `wrist_reg` keeps the weak wrists (5 N*m pitch/yaw) near neutral."""
        fdir = np.array([1.0, 0.0, finger_up]); fdir /= np.linalg.norm(fdir)
        nm = self.nm
        ref = np.zeros(7) if ref is None else np.asarray(ref)

        def f(x):
            d = self.fk(x)
            Rt = d.xmat[self.tb].reshape(3, 3); tp = d.xpos[self.tb]
            rh = Rt.T @ (nm.site_pos("right_hand_site", d) - tp)
            R = nm.site_mat("right_hand_site", d)
            g = self.gd(self.g_lh, self.g_rh)
            if want_gap is None:
                c = 4000 * np.sum((rh - target) ** 2)
            else:
                c = 4000 * np.sum((rh[[0, 2]] - target[[0, 2]]) ** 2)
                c += 4000 * (g - want_gap) ** 2
            c += 1e5 * max(gap_min - g, 0.0) ** 2
            c += orient_w * np.sum((R[:, 1] - Rt[:, 1]) ** 2)
            c += 0.5 * orient_w * np.sum((R[:, 0] - Rt @ fdir) ** 2)
            mrg = np.minimum(x - self.lo, self.hi - x)
            c += 200 * np.sum(np.clip(lim_keep - mrg, 0, None) ** 2)
            tg = min(self.gd(self.g_torso, gg) for gg in self.g_arm)
            c += 1e5 * max(torso_keep - tg, 0.0) ** 2
            c += wrist_reg * np.sum(x[4:] ** 2)
            c += reg * np.sum((x - ref) ** 2)
            return c

        res = minimize(f, np.clip(seed, self.lo, self.hi), method="L-BFGS-B",
                       bounds=list(zip(self.lo, self.hi)), options=dict(maxiter=600))
        return res.x, float(res.fun)


# --------------------------------------------------------------------------
# the clap cycle: two solved key poses, blended by the closure channel
# --------------------------------------------------------------------------

SEEDS = [np.array(s) for s in (
    (-0.5, 0.0, 0.3, 0.2, 0.0, 0.0, 0.0),
    (-0.3, -0.2, -0.25, -0.5, 0.2, 0.5, 0.06),
    (-0.6, 0.1, 0.6, 0.0, 0.0, -0.3, 0.0),
    (-0.4, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0),
)]


def solve_keyposes(nm, p: SahjaParams, stance: dict, verbose=False):
    """CONTACT (gap mode) and OPEN (position mode) right-arm poses.

    The arms are then driven in JOINT space between the two by the closure
    channel. That is exactly the human mechanism seen in the video -- elbow
    flexion plus shoulder internal rotation swinging the hands in and up --
    and it cannot branch-jump the way per-sample IK does."""
    ik = ArmIK(nm, stance)
    best = None
    for sd in SEEDS:
        rc, fc = ik.solve(np.array([p.contact_x, -0.06, p.contact_z]),
                          p.finger_up_contact, sd, want_gap=p.clap_gap)
        if best is None or fc < best[1]:
            best = (rc, fc)
    rc = best[0]
    ro, _ = ik.solve(np.array([p.open_x, -p.open_half, p.open_z]),
                     p.finger_up_open, rc, ref=rc, reg=0.3)
    # check the closing stroke never touches before contact
    cs = np.linspace(0, 1, 41)
    gaps = np.array([ik.measure(ro + (rc - ro) * c)["gap"] for c in cs])
    tgs = np.array([ik.measure(ro + (rc - ro) * c)["torso_gap"] for c in cs])
    mc, mo = ik.measure(rc), ik.measure(ro)
    info = dict(contact=rc.tolist(), open=ro.tolist(),
                contact_hand=mc["rh"].tolist(), open_hand=mo["rh"].tolist(),
                kin_gap_contact_mm=1000 * float(mc["gap"]),
                kin_gap_open_mm=1000 * float(mo["gap"]),
                kin_gap_min_mm=1000 * float(gaps.min()),
                kin_gap_monotone=bool(np.all(np.diff(gaps) <= 1e-4)),
                kin_torso_gap_min_mm=1000 * float(tgs.min()))
    if verbose:
        np.set_printoptions(precision=3, suppress=True)
        print(f"  CONTACT {rc}  hand {mc['rh']}  gap {mc['gap']*1000:.1f} mm")
        print(f"  OPEN    {ro}  hand {mo['rh']}  gap {mo['gap']*1000:.1f} mm")
        print(f"  stroke: gap min {gaps.min()*1000:.1f} mm monotone={info['kin_gap_monotone']}"
              f"  torso gap >= {tgs.min()*1000:.1f} mm")
    return rc, ro, info


class SahjaTrajectory:
    """Continuous t -> pose for the complete phrase:
    stand -> READY (entry) -> hold -> N claps -> READY -> stand."""

    def __init__(self, nm, p: SahjaParams, stance: dict, r_contact, r_open, stand_arms: dict):
        self.p, self.stance = p, stance
        self.r_contact, self.r_open = np.asarray(r_contact), np.asarray(r_open)
        self.ph0 = 0.5 * (p.ph_open + p.ph_close)          # READY = mid-open
        self.T_cyc = p.period
        self.t_claps0 = p.entry + p.settle
        self.n_cyc = p.claps
        self.t_claps1 = self.t_claps0 + self.n_cyc * self.T_cyc
        self.duration = self.t_claps1 + p.outro + 0.5
        self.ready = {**stance, **body_pose(stance, p, channels(p, self.ph0), 0.0),
                      **self.arm(self.ph0)}
        self.stand = {**stance, **stand_arms}
        self.entry = move(self.stand, self.ready, p.entry)
        self.outro = move(self.ready, self.stand, p.outro)
        self.joint_names = sorted(self.ready)

    def arm(self, ph):
        c = channels(self.p, ph + self.p.arm_lead / self.p.period)["closure"]
        return arms_pose(self.r_open + (self.r_contact - self.r_open) * c)

    def phase(self, t):
        return (self.ph0 + (t - self.t_claps0) / self.T_cyc) % 1.0

    def clap_times(self):
        first = self.t_claps0 + (1.0 - self.ph0) * self.T_cyc
        return [first + k * self.T_cyc for k in range(self.n_cyc)]

    def at(self, t):
        p = self.p
        if t < p.entry:
            return self.entry.at(t)
        if t < self.t_claps0:
            return dict(self.ready)
        if t < self.t_claps1:
            ph = self.phase(t)
            k = (t - self.t_claps0) / self.T_cyc
            scale = min(1.0, (k + 0.5) / max(p.ramp_claps, 1e-9)) if p.ramp_claps else 1.0
            left = (self.t_claps1 - t) / self.T_cyc   # ramp the body out too
            scale = min(scale, max(0.0, min(1.0, left)))
            pose = dict(self.stance)
            pose.update(body_pose(self.stance, p, channels(p, ph), _q5(scale)))
            pose.update(self.arm(ph))
            return pose
        t2 = t - self.t_claps1
        if t2 < p.outro:
            return self.outro.at(t2)
        return dict(self.stand)

    __call__ = at


# --------------------------------------------------------------------------
# build / freeze / load
# --------------------------------------------------------------------------

def build(nm, p: SahjaParams | None = None, verbose=False):
    p = p or SahjaParams()
    stance = sahja_stance(nm, p)
    stand_arms = {k: v for k, v in nm.keyframe_pose("knees_bent").items()
                  if k in RIGHT_ARM + LEFT_ARM}
    rc, ro, info = solve_keyposes(nm, p, stance, verbose=verbose)
    traj = SahjaTrajectory(nm, p, stance, rc, ro, stand_arms)
    traj.info = info
    return traj


def freeze(traj, path):
    """Save everything needed to replay bit-identically without re-solving IK."""
    blob = dict(params=traj.p.as_dict(), stance=traj.stance,
                stand=traj.stand, ready=traj.ready,
                arm_joints=RIGHT_ARM, right_arm_contact=traj.r_contact.tolist(),
                right_arm_open=traj.r_open.tolist(),
                poses={"CONTACT": {**traj.stance, **arms_pose(traj.r_contact)},
                       "OPEN": {**traj.stance, **arms_pose(traj.r_open)}},
                info=getattr(traj, "info", {}))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(blob, f, indent=1)
    return path


def load_frozen(nm, path):
    with open(path) as f:
        blob = json.load(f)
    p = SahjaParams(**blob["params"])
    stand_arms = {k: v for k, v in blob["stand"].items() if k in RIGHT_ARM + LEFT_ARM}
    traj = SahjaTrajectory(nm, p, blob["stance"], blob["right_arm_contact"],
                           blob["right_arm_open"], stand_arms)
    traj.info = blob.get("info", {})
    return traj, p
