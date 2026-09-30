"""NASHMI_DAHIYA_SAHJA — build / validate / watch the Dahiya row clap.

    $PY run_sahja.py                 # validate frozen V1: 3 runs + clap metrics
    $PY run_sahja.py --watch         # loop V1 in the live viewer
    $PY run_sahja.py --variant RAZA --watch
    $PY run_sahja.py --rebuild       # re-solve IK from the params and re-freeze
"""
import sys, os, argparse, json, time
sys.path.insert(0, os.path.expanduser('~/robotics/nashmi'))
os.chdir(os.path.expanduser('~/robotics/nashmi'))
import numpy as np, mujoco
from nashmi.derived import NashmiDerived
from nashmi.model import SCENE_MJX
from nashmi.control import apply_gain_preset, GAINS_NASHMI_V1
from nashmi.runner import MotionRunner, RunConfig
from nashmi.motion import sahja
from nashmi.motion.sahja_configs import VARIANTS

FROZEN = "trajectories/{name}.json"


def make_model():
    nd = NashmiDerived(SCENE_MJX)
    apply_gain_preset(nd, GAINS_NASHMI_V1)
    return nd


def init_stand(nd, traj, settle=1.5, sync=None):
    """Initialise directly into the widened stance (arms at the knees_bent
    carriage) and let the servos settle -- the verified standing pose."""
    m, d = nd.model, nd.data
    nd.reset_to_keyframe("knees_bent")
    st = traj.stand
    for jn, v in st.items():
        d.qpos[nd.joints[jn].qpos_adr] = v
    d.qvel[:] = 0; mujoco.mj_forward(m, d)
    for k in range(int(settle / m.opt.timestep)):
        d.ctrl[:] = nd.ctrl_from_pose(st, base=d.ctrl); mujoco.mj_step(m, d)
        if sync: sync(k)


def get_traj(nd, name, rebuild=False, verbose=True):
    cfg = VARIANTS[name]
    path = FROZEN.format(name=cfg["name"])
    if rebuild or not os.path.exists(path):
        p = sahja.SahjaParams(**cfg["params"])
        t0 = time.time()
        traj = sahja.build(nd, p, verbose=verbose)
        sahja.freeze(traj, path)
        if verbose: print(f"  solved + froze {path} in {time.time()-t0:.1f}s")
        return traj, p
    return sahja.load_frozen(nd, path)


# --------------------------------------------------------------------------
# clap-specific metrics, recomputed from the logged qpos
# --------------------------------------------------------------------------

def clap_metrics(nd, res, traj):
    res._finalize()
    m = nd.model; d = mujoco.MjData(m)
    G = lambda n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, n)
    lh, rh, to = G("left_hand_collision"), G("right_hand_collision"), G("torso_collision")
    arm_geoms = [G(n) for n in ("left_hand_collision", "right_hand_collision",
                                "left_wrist_collision", "right_wrist_collision",
                                "left_elbow_yaw_collision", "right_elbow_yaw_collision")]
    tb = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "torso_link")
    ft = np.zeros(6)
    t = np.array(res.t)
    gap, tg, rpos, lpos, torso_z, rel = [], [], [], [], [], []
    for q in res.qpos:
        d.qpos[:] = q; mujoco.mj_forward(m, d)
        gap.append(mujoco.mj_geomDistance(m, d, lh, rh, 1.0, ft))
        tg.append(min(mujoco.mj_geomDistance(m, d, to, g, 1.0, ft) for g in arm_geoms))
        r, l = nd.site_pos("right_hand_site", d), nd.site_pos("left_hand_site", d)
        rpos.append(r); lpos.append(l); torso_z.append(d.xpos[tb][2])
        Rt = d.xmat[tb].reshape(3, 3)
        rel.append(Rt.T @ (0.5 * (r + l) - d.xpos[tb]))
    gap, tg = np.array(gap), np.array(tg)
    rpos, lpos, rel = np.array(rpos), np.array(lpos), np.array(rel)
    dt = t[1] - t[0]
    vr = np.linalg.norm(np.gradient(rpos, dt, axis=0), axis=1)
    vl = np.linalg.norm(np.gradient(lpos, dt, axis=0), axis=1)
    closing = -np.gradient(gap, dt)

    jn = nd.joint_names
    V = np.array(res.qvel)
    def peak(sub):
        cols = [nd.joints[n].qvel_adr for n in jn if sub in n]
        return float(np.abs(V[:, cols]).max())

    # per-clap: minimum gap in a window around each planned contact
    per = []
    for tc in traj.clap_times():
        w = (t > tc - 0.35 * traj.T_cyc) & (t < tc + 0.35 * traj.T_cyc)
        if w.any():
            i = np.argmin(np.where(w, gap, np.inf))
            j = np.argmax(np.where(w, closing, -np.inf))
            # impact = first time the gap closes to within 3 mm of its minimum
            k = int(np.argmax(w & (gap < gap[i] + 0.003)))
            per.append(dict(t_plan=tc, t_impact=float(t[k]), gap_mm=float(gap[i] * 1000),
                            closing_speed=float(closing[j])))
    # open separation between claps
    c0, c1 = traj.t_claps0, traj.t_claps1
    body = (t > c0) & (t < c1)
    pel = np.array(res.qpos)[:, 2]
    return dict(
        clap_gap_min_mm=float(min(x["gap_mm"] for x in per)),
        clap_gap_max_mm=float(max(x["gap_mm"] for x in per)),
        clap_gap_mean_mm=float(np.mean([x["gap_mm"] for x in per])),
        open_gap_max_mm=float(gap[body].max() * 1000),
        hand_sep_open_mm=float(np.linalg.norm(rpos - lpos, axis=1)[body].max() * 1000),
        clap_timing_err_ms=float(np.mean([abs(x["t_impact"] - x["t_plan"]) for x in per]) * 1000),
        clap_timing_lag_ms=float(np.mean([x["t_impact"] - x["t_plan"] for x in per]) * 1000),
        peak_closing_speed=float(max(x["closing_speed"] for x in per)),
        peak_hand_speed=float(max(vr.max(), vl.max())),
        arm_torso_gap_min_mm=float(tg.min() * 1000),
        hands_forward_mm=(float(rel[body, 0].min() * 1000), float(rel[body, 0].max() * 1000)),
        hands_height_mm=(float(rel[body, 2].min() * 1000), float(rel[body, 2].max() * 1000)),
        pelvis_pulse_mm=float((pel[body].max() - pel[body].min()) * 1000),
        peak_elbow_speed=peak("elbow"), peak_shoulder_speed=peak("shoulder"),
        peak_wrist_speed=peak("wrist"), peak_knee_speed=peak("knee"),
        n_claps=len(per), per_clap=per,
    )


def print_run(tag, mm, cm):
    print(f" {tag}: fell={mm['fell']} tilt={mm['max_tilt_deg']:.2f}d "
          f"minLoad={mm['min_foot_load_frac']*100:.1f}% lift={mm['foot_lift_frac']*100:.1f}% "
          f"supp={mm['min_support_margin_mm']:.1f}mm f={mm['peak_force_ratio']:.3f} "
          f"sat={mm['any_saturation']} selfcol={mm['self_collision_frac']*100:.2f}% "
          f"lim={mm['joint_limit_margin_rad']:.3f}({mm['joint_limit_tightest']}) pk_f={mm['peak_force_joint']} selfpairs={mm['self_collision_pairs']} "
          f"vmax={mm['peak_joint_speed_rad_s']:.2f}")
    print(f"      claps={cm['n_claps']} gap@clap {cm['clap_gap_min_mm']:.1f}..{cm['clap_gap_max_mm']:.1f}mm "
          f"(mean {cm['clap_gap_mean_mm']:.1f}) open_sep={cm['hand_sep_open_mm']:.0f}mm "
          f"timing lag={cm['clap_timing_lag_ms']:+.0f}ms closing={cm['peak_closing_speed']:.2f}m/s "
          f"hand v={cm['peak_hand_speed']:.2f}m/s arm-torso>={cm['arm_torso_gap_min_mm']:.1f}mm "
          f"pulse={cm['pelvis_pulse_mm']:.1f}mm  dq: sh={cm['peak_shoulder_speed']:.2f} "
          f"el={cm['peak_elbow_speed']:.2f} wr={cm['peak_wrist_speed']:.2f} kn={cm['peak_knee_speed']:.2f}")


def run_once(nd, traj, label):
    init_stand(nd, traj)
    r = MotionRunner(nd, RunConfig())
    res = r.run(traj, label=label, meta={"params": traj.p.as_dict()})
    return res, res.metrics(), clap_metrics(nd, res, traj)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="V1")
    ap.add_argument("--watch", action="store_true")
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--perturb", action="store_true", help="also run torso pushes")
    a = ap.parse_args()
    nd = make_model()
    traj, p = get_traj(nd, a.variant, rebuild=a.rebuild)
    name = VARIANTS[a.variant]["name"]
    if a.watch:
        import mujoco.viewer as mjv
        m, d = nd.model, nd.data
        dt = m.opt.timestep
        viewer = mjv.launch_passive(m, d)
        def _pace(w0, k):
            if k % 4 == 0:
                viewer.sync()
                lag = k * dt - (time.time() - w0)
                if lag > 0: time.sleep(lag)
        loop = 0
        while viewer.is_running():
            loop += 1
            w0 = time.time()
            init_stand(nd, traj, sync=lambda k: _pace(w0, k))
            w1 = time.time()
            res = MotionRunner(nd, RunConfig()).run(
                traj, label=f"{name}_watch{loop}", on_step=lambda k, tt, dd: _pace(w1, k))
            mm = res.metrics()
            print(f"loop {loop}: {name} fell={mm['fell']} tilt={mm['max_tilt_deg']:.2f}d "
                  f"minLoad={mm['min_foot_load_frac']*100:.1f}% f={mm['peak_force_ratio']:.3f}",
                  flush=True)
        sys.exit(0)

    print(f"=== {name}: {p.claps} claps @ {p.bpm:.0f}/min, duration {traj.duration:.2f}s ===")
    print(f"  kinematic plan: {traj.info}")
    rows = []
    for i in range(a.runs):
        res, mm, cm = run_once(nd, traj, f"{name}_run{i+1}")
        os.makedirs("experiments/logs", exist_ok=True)
        res.save(f"experiments/logs/{name.lower()}_run{i+1}")
        print_run(f"run{i+1}", mm, cm)
        rows.append((mm, cm))
    if a.runs > 1:
        spread = max(abs(r[0]["max_tilt_deg"] - rows[0][0]["max_tilt_deg"]) for r in rows)
        print(f"  reproducibility: max tilt spread across runs = {spread:.3e} deg")
    out = f"experiments/logs/{name.lower()}_metrics.json"
    mm, cm = rows[0]
    with open(out, "w") as f:
        json.dump({"metrics": mm, "clap": {k: v for k, v in cm.items() if k != "per_clap"},
                   "per_clap": cm["per_clap"], "params": p.as_dict(),
                   "plan": traj.info}, f, indent=1, default=float)
    print(f"  wrote {out}")

    if a.perturb:
        print("=== perturbation: 100 ms torso push mid-phrase (open-loop, no balance controller) ===")
        bid = mujoco.mj_name2id(nd.model, mujoco.mjtObj.mjOBJ_BODY, "torso_link")
        dt = nd.model.opt.timestep
        t_at = traj.clap_times()[len(traj.clap_times()) // 2]
        for lbl, F in [("fwd +x 40N", [40, 0, 0]), ("back -x 40N", [-40, 0, 0]),
                       ("left +y 40N", [0, 40, 0]), ("right -y 40N", [0, -40, 0])]:
            k0, k1 = int(t_at / dt), int((t_at + 0.10) / dt)
            def hook(k, tt, d, F=np.array(F, float)):
                d.xfrc_applied[bid, :3] = F if k0 <= k < k1 else 0.0
            init_stand(nd, traj)
            res = MotionRunner(nd, RunConfig()).run(traj, label="perturb", on_step=hook)
            nd.data.xfrc_applied[:] = 0
            mm = res.metrics()
            print(f"  {lbl:12s} fell={mm['fell']} tilt={mm['max_tilt_deg']:.2f}d "
                  f"minLoad={mm['min_foot_load_frac']*100:.1f}% lift={mm['foot_lift_frac']*100:.1f}% "
                  f"selfcol={mm['self_collision_frac']*100:.2f}%")
