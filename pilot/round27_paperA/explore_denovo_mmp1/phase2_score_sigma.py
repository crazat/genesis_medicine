#!/usr/bin/env python
"""Phase2 reliability gate scorer — rank de novo candidates by structure-prediction reliability.

Two orthogonal reliability axes (the two-paper framework applied to GENERATED molecules):
  sigma_iptm : std of Boltz cofold iptm across diffusion samples (paper_B axis; low = stable pose)
  iptm_mean  : mean iptm (binding-confidence level; high = confident interface)
  (sigma_E from xtb on poses is added by phase2_xtb_sigma.py once cofold poses exist.)

Reads denovo_cofold_output/<cand>/.../confidence_*.json, computes per-candidate iptm stats,
merges QED/composite from the manifest, writes phase2_reliability_ranked.csv.

A candidate is a "reliable de novo hit" when iptm_mean is high AND sigma_iptm is low
(confident AND reproducible) — the gating contribution that distinguishes this 4th track.
Pure CPU, instant. No GPU.
"""
import os, csv, glob, json, statistics

EXP = "/home/crazat/genesis_medicine/pilot/round27_paperA/explore_denovo_mmp1"
OUT = os.path.join(EXP, "denovo_cofold_output")
MANIFEST = os.path.join(EXP, "phase2_manifest_combined.csv")
RESULT = os.path.join(EXP, "phase2_reliability_ranked.csv")

# manifest metadata
meta = {}
with open(MANIFEST) as fh:
    for row in csv.DictReader(fh):
        meta[row["cand_id"].strip()] = row

rows = []
for cdir in sorted(glob.glob(os.path.join(OUT, "denovo_mmp1_*"))):
    cid = os.path.basename(cdir)
    iptms = []
    for jf in glob.glob(os.path.join(cdir, "**", "confidence_*.json"), recursive=True):
        try:
            d = json.load(open(jf))
            v = d.get("iptm", d.get("ligand_iptm"))
            if v is not None:
                iptms.append(float(v))
        except Exception:
            continue
    if not iptms:
        continue
    n = len(iptms)
    mean = statistics.fmean(iptms)
    sd = statistics.pstdev(iptms) if n > 1 else 0.0
    m = meta.get(cid, {})
    # reliability gate score: confident (mean) AND reproducible (low sd), QED-weighted
    gate = mean * (1.0 - min(sd / 0.10, 1.0)) * float(m.get("qed", 0.5) or 0.5)
    rows.append(dict(
        cand_id=cid, n_samples=n,
        iptm_mean=round(mean, 4), sigma_iptm=round(sd, 4),
        qed=m.get("qed", ""), mw=m.get("mw", ""), zbg=m.get("zbg", ""),
        smiles=m.get("smiles", ""), composite_phase1=m.get("composite_score", ""),
        gate_score=round(gate, 4),
    ))

if not rows:
    print("no cofold confidence outputs yet — run phase2_cofold_gate.sh first")
    raise SystemExit(0)

rows.sort(key=lambda r: r["gate_score"], reverse=True)
cols = ["cand_id", "gate_score", "iptm_mean", "sigma_iptm", "n_samples",
        "qed", "mw", "zbg", "composite_phase1", "smiles"]
with open(RESULT, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols)
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in cols})

print(f"scored {len(rows)} candidates -> {RESULT}")
print("TOP 10 by reliability gate (high iptm_mean + low sigma_iptm):")
for r in rows[:10]:
    print(f"  {r['cand_id']}  gate={r['gate_score']:.3f}  "
          f"iptm={r['iptm_mean']:.3f}±{r['sigma_iptm']:.3f}  QED={r['qed']}  {r['zbg']}")
