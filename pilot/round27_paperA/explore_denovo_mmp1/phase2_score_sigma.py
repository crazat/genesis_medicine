#!/usr/bin/env python
"""Phase2 reliability gate scorer — rank de novo candidates by structure-prediction reliability.

R2 FIX (2026-06-09): scan ALL tier output dirs, not just the (empty) legacy denovo_cofold_output.
The real cofolds live in denovo_{deep,t2,t3,t4,t5,...}_output/boltz_results_*/predictions/<cand>/.
Metadata now comes from combined_ranked.csv (covers all 1784), with the deep manifest as fallback.

Two orthogonal reliability axes (the two-paper framework applied to GENERATED molecules):
  sigma_iptm : std of Boltz cofold iptm across diffusion samples (paper_B axis; low = stable pose)
  iptm_mean  : mean iptm (binding-confidence level; high = confident interface)
  (sigma_E from xtb on poses is aggregated separately by phase3_build_labels.py.)

A candidate is a "reliable de novo hit" when iptm_mean is high AND sigma_iptm is low
(confident AND reproducible). Writes phase2_reliability_ranked.csv = the binding-axis feedback
that R3's surrogate and R4's Pareto layer consume. Pure CPU, instant. No GPU.
"""
import os, csv, glob, json, statistics

EXP = "/home/crazat/genesis_medicine/pilot/round27_paperA/explore_denovo_mmp1"
RANKED = os.path.join(EXP, "combined_ranked.csv")
MANIFEST = os.path.join(EXP, "phase2_manifest_combined.csv")
MANIFEST_R3 = os.path.join(EXP, "phase2_manifest_r3.csv")   # R6 round-3 GENERATED (denovo_mmp1_r3_*)
RESULT = os.path.join(EXP, "phase2_reliability_ranked.csv")

# metadata: combined_ranked.csv (all 1784) + R6 round-3 manifest (generated mols, separate id space)
meta = {}
for path in (MANIFEST, MANIFEST_R3, RANKED):           # RANKED loaded last => authoritative
    if not os.path.exists(path):
        continue
    with open(path) as fh:
        for row in csv.DictReader(fh):
            meta[row["cand_id"].strip()] = row

# gather iptm per candidate across EVERY tier output dir (union of confidence_*.json)
iptm_by_cand = {}
for jf in glob.glob(os.path.join(EXP, "denovo_*output", "**", "confidence_*.json"), recursive=True):
    # path .../predictions/denovo_mmp1_NNN/confidence_denovo_mmp1_NNN_model_K.json
    cid = os.path.basename(os.path.dirname(jf))
    if not cid.startswith("denovo_mmp1_"):
        continue
    try:
        d = json.load(open(jf))
        v = d.get("iptm", d.get("ligand_iptm"))
        if v is not None:
            iptm_by_cand.setdefault(cid, []).append(float(v))
    except Exception:
        continue

rows = []
for cid, iptms in iptm_by_cand.items():
    n = len(iptms)
    if n == 0:
        continue
    mean = statistics.fmean(iptms)
    sd = statistics.pstdev(iptms) if n > 1 else 0.0
    m = meta.get(cid, {})
    qed = float(m.get("qed", 0.5) or 0.5)
    # reliability gate: confident (mean) AND reproducible (low sd), QED-weighted
    gate = mean * (1.0 - min(sd / 0.10, 1.0)) * qed
    rows.append(dict(
        cand_id=cid, n_samples=n,
        iptm_mean=round(mean, 4), sigma_iptm=round(sd, 4),
        qed=m.get("qed", ""), mw=m.get("mw", ""), zbg=m.get("zbg", ""),
        smiles=m.get("smiles", ""), composite_phase1=m.get("composite_score", ""),
        gate_score=round(gate, 4),
    ))

if not rows:
    print("no cofold confidence outputs found under denovo_*output/")
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
