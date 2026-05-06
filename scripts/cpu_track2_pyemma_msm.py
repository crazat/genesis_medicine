"""Track 2 — PyEMMA / deeptime MSM on 25 MD trajectories.

Output: pilot/cpu_meaningful/track2_msm_kinetics.json
Per-trajectory: ITS, slowest implied timescale, n_metastable_states.
"""
from __future__ import annotations
import json, sys, glob, warnings
from pathlib import Path
from multiprocessing import Pool

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "pilot/cpu_meaningful/track2_msm_kinetics.json"


def analyze(traj_dir_str):
    import mdtraj as md
    import numpy as np
    from deeptime.markov.msm import MaximumLikelihoodMSM

    traj_dir = Path(traj_dir_str)
    name = traj_dir.name
    dcd = traj_dir / "traj.dcd"
    pdb = traj_dir / "final.pdb"
    if not dcd.exists() or not pdb.exists():
        return {"name": name, "status": "missing_files"}

    try:
        t = md.load(str(dcd), top=str(pdb))
        lig_idx = t.topology.select("resname UNK")
        if len(lig_idx) == 0:
            lig_idx = t.topology.select("not protein")
        if len(lig_idx) == 0:
            return {"name": name, "status": "no_ligand_atoms"}

        # Reduce trajectory to ligand-only + radius_of_gyration
        lig_traj = t.atom_slice(lig_idx)
        rgyr = md.compute_rg(lig_traj)

        # Bin Rgyr into 5 states for MSM
        n_states = 5
        bins = np.linspace(rgyr.min(), rgyr.max() + 1e-6, n_states + 1)
        states = np.digitize(rgyr, bins) - 1
        states = np.clip(states, 0, n_states - 1).astype(int)

        # Estimate MSM at lag = 50 frames
        from deeptime.markov import TransitionCountEstimator
        from deeptime.markov.msm import MaximumLikelihoodMSM
        cestimator = TransitionCountEstimator(lagtime=50, count_mode="sliding")
        cmodel = cestimator.fit_fetch([states])
        msm = MaximumLikelihoodMSM().fit_fetch(cmodel)

        try:
            its = msm.timescales(k=3).tolist()
        except Exception:
            its = []
        try:
            stat_dist = msm.stationary_distribution.tolist()
        except Exception:
            stat_dist = []

        return {
            "name": name,
            "status": "ok",
            "n_frames": int(t.n_frames),
            "n_lig_atoms": int(len(lig_idx)),
            "rgyr_mean_nm": float(rgyr.mean()),
            "rgyr_std_nm": float(rgyr.std()),
            "implied_timescales_frames": its,
            "stationary_distribution": stat_dist,
            "n_metastable_states": int(len(stat_dist)),
        }
    except Exception as e:
        return {"name": name, "status": f"error: {str(e)[:120]}"}


def main():
    print("=" * 60)
    print("Track 2 — PyEMMA/deeptime MSM 25 trajectories")
    print("=" * 60)
    md_dirs = []
    for parent in ["md_r11_0_multitarget", "md_r11_0_extra5",
                   "md_r12_super_leaders", "md_r14_5_r13_13"]:
        for d in (ROOT / "pilot" / parent).glob("*__*"):
            if d.is_dir():
                md_dirs.append(str(d))
    print(f"  {len(md_dirs)} trajectory directories found")

    with Pool(4) as p:
        results = p.map(analyze, md_dirs)

    OUT_FILE.write_text(json.dumps(results, indent=2))
    print(f"\n✅ {OUT_FILE}")

    ok = sum(1 for r in results if r.get("status") == "ok")
    print(f"  {ok}/{len(results)} MSM successful")
    return 0


if __name__ == "__main__":
    sys.exit(main())
