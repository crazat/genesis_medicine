#!/usr/bin/env python
"""Phase2 input builder — turn the top-N de novo candidates into Boltz cofold YAMLs.

Each YAML = the (identical) MMP-1 catalytic-domain protein + reused protein-only MSA
+ one de novo candidate SMILES as the ligand. Protein/MSA are ligand-independent so we
reuse the validated reliability-cascade protein block verbatim (same target, same MSA).

Pure CPU, ~instant. No GPU, no interference with the xtb sigma_E matrix or boltz cascade.
Output: denovo_cofold_input/denovo_mmp1_NNN.yaml  (one per candidate).
"""
import os, csv
from rdkit import Chem, RDLogger
RDLogger.DisableLog("rdApp.*")

EXP = "/home/crazat/genesis_medicine/pilot/round27_paperA/explore_denovo_mmp1"
TEMPLATE = "/home/crazat/genesis_medicine/pilot/round27_paperA/boltz_input_v19_msa/mmp1_CHEMBL1207.yaml"
MANIFEST = os.path.join(EXP, "phase2_manifest_combined.csv")
OUTDIR = os.path.join(EXP, "denovo_cofold_input")

# pull the protein sequence + MSA path from the validated template
seq = msa = None
for line in open(TEMPLATE):
    s = line.strip()
    if s.startswith("sequence:"):
        seq = s.split("sequence:", 1)[1].strip()
    elif s.startswith("msa:"):
        msa = s.split("msa:", 1)[1].strip()
assert seq and msa, "could not parse protein seq / msa from template"
assert os.path.exists(msa), f"MSA missing: {msa}"

os.makedirs(OUTDIR, exist_ok=True)

YAML = """version: 1
sequences:
  - protein:
      id: A
      sequence: {seq}
      msa: {msa}
  - ligand:
      id: B
      smiles: "{smi}"
"""

n_ok = n_bad = 0
with open(MANIFEST) as fh:
    for row in csv.DictReader(fh):
        cid = row["cand_id"].strip()
        smi = row["smiles"].strip()
        m = Chem.MolFromSmiles(smi)
        if m is None:
            n_bad += 1
            continue
        can = Chem.MolToSmiles(m)  # canonical, boltz-safe
        with open(os.path.join(OUTDIR, f"{cid}.yaml"), "w") as out:
            out.write(YAML.format(seq=seq, msa=msa, smi=can))
        n_ok += 1

print(f"Phase2 cofold inputs built: {n_ok} YAMLs -> {OUTDIR} ({n_bad} invalid SMILES skipped)")
