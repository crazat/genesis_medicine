# Genesis_Medicine OpenFold3 + AQAffinity orchestration patch — 2026-05-03

P1–P6 + glue patches written on C control shell. Per CLAUDE.md `D-native
canonical` policy, no commits/pushes from C; use the sync recipe at the
bottom to mirror to `Ubuntu-Genesis:/home/crazat/genesis_medicine`, then
commit + push from D.

## Files

### New (12)

| Path | Bytes | sha256 (short) | Purpose |
|---|---:|---|---|
| `src/genesis_medicine/affinity/__init__.py` | — | — | Module entry; exports `AQAffinityAdapter`. |
| `src/genesis_medicine/affinity/aqaffinity_adapter.py` | — | — | SandboxAQ AQAffinity head on top of OpenFold3 weights. structure-free pKd. |
| `src/genesis_medicine/structure/cofactor_registry.py` | — | — | Loader for the holo cofactor YAML; `augment_request_with_cofactors(req, target)`. |
| `conf/skin_targets/holo_cofactors.yaml` | — | — | 12 metal-/cofactor-dependent skin targets with CCD codes + holo PDB hints. |
| `conf/structure/openfold3.yaml` | — | — | OpenFold3 engine config; pixi env, low_mem runner, holo registry pointer. |
| `conf/structure/aqaffinity.yaml` | — | — | AQAffinity engine config (reuses OpenFold3 ckpt). |
| `scripts/run_openfold3_metal_smoke.sh` | — | — | MMP1 + 2×Zn + 3×Ca + inhibitor smoke; baseline JSON output. |
| `scripts/run_openfold3_consensus_smoke.sh` | — | — | Tri-engine consensus (Boltz-2 + Protenix-v2 + OpenFold3) + ligand-aware RMSD. |
| `scripts/build_of3_msa_template_cache.py` | — | — | 16-target query JSON + template hint cache; manifest. |
| `scripts/run_openfold3_chembl_calibration.py` | — | — | Boltz-2 vs AQAffinity Pearson on the 93-row CHEMBL holdout (--mode dryrun|execute). |
| `tests/unit/test_aqaffinity_adapter.py` | — | — | Capability + parse_output + metal-aware payload smoke. |
| `tests/unit/test_cofactor_registry.py` | — | — | Registry load + alias + augmentation tests. |

### Modified (8)

| Path | Change |
|---|---|
| `src/genesis_medicine/structure/base.py` | Adds `CovalentBondSpec`, `metal_ions`, `cofactor_ccds`, `covalent_bonds` fields to `StructurePredictionRequest`. |
| `src/genesis_medicine/structure/openfold3_adapter.py` | Adds `build_openfold3_query_payload(req, ...)` standalone function (metal/cofactor/bonds aware); `_write_input` now delegates to it. |
| `src/genesis_medicine/structure/__init__.py` | Re-exports `build_openfold3_query_payload`, `augment_request_with_cofactors`, `get_cofactors`, `load_registry`, `CovalentBondSpec`, `TargetCofactors`, `CofactorRegistry`. `get_predictor` now passes `use_templates`. |
| `src/genesis_medicine/structure/consensus.py` | `_pairwise_rmsd` extended to combine 0.6×CA + 0.4×ligand-heavy RMSD; ignores monatomic ions and waters. |
| `src/genesis_medicine/licensing/registry.py` | Adds `openfold3_weights_p2`, `aqaffinity`, `aqaffinity_weights` (all Apache-2.0 / commercial-safe). |
| `tests/test_license_gate.py` | New keys in commercial allowlist. |
| `pilot/scientific_gates.yaml` | Adds `openfold3_pilot_uncalibrated` (flag) and `metal_dependent_target_apo_warning` (flag). |
| `scripts/multi_fidelity_bo_scheduler.py` | Adds T1b OpenFold3 (cost 4 min, axes `of3_plddt_mean`, `of3_consensus_score`) and T1c AQAffinity (cost 0.5 min, axis `aqaffinity_pkd`) tiers between T1 and T2. |
| `scripts/run_openfold3_smoke.sh` | Cleaned of UNC residue, drain-mode aware, baseline.json + symlink. |

## Smoke test results (C side, drain mode OFF)

```
pytest tests/unit/test_aqaffinity_adapter.py
       tests/unit/test_cofactor_registry.py
       tests/test_license_gate.py
       tests/unit/test_openfold3_adapter.py        86 passed in 2.14s

build_evidence_ledger.py                            640 (compound, target) rows
multi_fidelity_bo_scheduler.py --top 5              603 rows; top5 0.94 / 0.88 / 0.88 / 0.85 / 0.84
                                                    (acquisition score scale shifted because
                                                     T1b/T1c cheap tiers now precede T2/T3)
auto_result_planner.py                              11 active gates (was 9)
                                                    + openfold3_pilot_uncalibrated
                                                    + metal_dependent_target_apo_warning
build_of3_msa_template_cache.py                     16 rows; 15 needs_uniprot_fasta
                                                    (only MMP1 stub seq is bundled in-tree)
run_openfold3_chembl_calibration.py --mode dryrun   reproduces Boltz-2 R = -0.4535
                                                    aqaffinity_* fields = null (pending execute on D)
```

## Wiring diagram

```
                            holo_cofactors.yaml
                                    │
                                    ▼
                         cofactor_registry.augment_request_with_cofactors
                                    │
                ┌───────────────────┼────────────────────┐
                ▼                   ▼                    ▼
       OpenFold3Adapter       AQAffinityAdapter       Boltz-2Adapter
      (metal/cofactor)        (same metal/cof)        (existing)
                │                   │                    │
                └─→ build_openfold3_query_payload  ←─────┘
                         (incl. covalent_bonds)
                                    │
                                    ▼
                         pixi run -e openfold3-cuda12
                            run_openfold predict
                            aqaffinity predict
                                    │
                                    ▼
                  pilot/openfold3_smoke + pilot/calibration
                                    │
                                    ▼
              evidence_ledger + multi_fidelity_bo_scheduler
                                    │
                                    ▼
            curator (Claude Code) + auto_result_planner overlay
                                    │
                                    ▼
                  decision_graph.jsonl audit row
```

## Operating commands (after sync to D)

Run on `Ubuntu-Genesis:/home/crazat/genesis_medicine`:

```bash
# 0) (one-time) install AQAffinity and download binding head ckpt
pixi run -e openfold3-cuda12 pip install aqaffinity
mkdir -p .cache/openfold3
huggingface-cli download SandboxAQ/AQAffinity \
  binding_head.pt \
  --local-dir .cache/openfold3 \
  --local-dir-use-symlinks False
mv .cache/openfold3/binding_head.pt .cache/openfold3/aqaffinity_binding_head.pt

# 1) populate UniProt FASTA cache for the 16 skin-target sequences
mkdir -p .cache/uniprot
for u in P01137 P03956 P08254 P14780 P29279 P28300 P14679 P17643 P40126 \
         P18405 P31213 Q96EB6 P10275 P35354 Q92508 Q15746; do
  curl -s -o .cache/uniprot/$u.fasta https://www.uniprot.org/uniprotkb/$u.fasta
done

# 2) build per-target holo query JSON + template hint cache
.venv/bin/python scripts/build_of3_msa_template_cache.py

# 3) (drain mode lifted) ubiquitin smoke + MMP1 metal smoke + tri-engine consensus
GENESIS_OF3_DRAIN_OVERRIDE=1 bash scripts/run_openfold3_smoke.sh
GENESIS_OF3_DRAIN_OVERRIDE=1 bash scripts/run_openfold3_metal_smoke.sh
GENESIS_OF3_DRAIN_OVERRIDE=1 bash scripts/run_openfold3_consensus_smoke.sh

# 4) ChEMBL holdout cross-engine calibration (after AQAffinity is installed)
GENESIS_OF3_DRAIN_OVERRIDE=1 \
.venv/bin/python scripts/run_openfold3_chembl_calibration.py --mode execute

# 5) refresh ledger + scheduler so the new tiers + gates actually drive planner
.venv/bin/python scripts/build_evidence_ledger.py
.venv/bin/python scripts/multi_fidelity_bo_scheduler.py --top 50 --emit-directives
.venv/bin/python scripts/apply_curator_directives.py
.venv/bin/python scripts/auto_result_planner.py
```

## Drain mode invariants preserved

- `pilot/QUEUE_DRAIN_MODE` blocks all three smoke scripts and the `--mode
  execute` calibration.
- Override flag: `GENESIS_OF3_DRAIN_OVERRIDE=1`.
- Planner overlay never blocks GPU/CPU on `flag` action; only the existing
  `hold` / `suppress` gates do (mmp1_zinc_pending stays the gatekeeper for
  ABFE; the two new gates are caveats, not blockers).

## License safety (commercial profile)

| Asset | License | Commercial build |
|---|---|---|
| OpenFold3-preview2 code (`openfold3`) | Apache-2.0 | OK |
| OpenFold3 weight `of3-p2-155k.pt` (`openfold3_weights_p2`) | Apache-2.0 (Consortium portal) | OK |
| AQAffinity code (`aqaffinity`) | Apache-2.0 (HF, contact-info ack) | OK |
| AQAffinity binding head weights (`aqaffinity_weights`) | Apache-2.0 | OK |

All four are now in `src/genesis_medicine/licensing/registry.py` with
`COMMERCIAL_SAFE` tag and exercised by `tests/test_license_gate.py`.

## Sync recipe (C → D)

```bash
# On C (this shell):
cd /home/crazat/genesis_medicine
tar -czf /tmp/genesis_openfold3_patch_2026-05-03.tar.gz \
  src/genesis_medicine/affinity/__init__.py \
  src/genesis_medicine/affinity/aqaffinity_adapter.py \
  src/genesis_medicine/structure/cofactor_registry.py \
  src/genesis_medicine/structure/base.py \
  src/genesis_medicine/structure/openfold3_adapter.py \
  src/genesis_medicine/structure/__init__.py \
  src/genesis_medicine/structure/consensus.py \
  src/genesis_medicine/licensing/registry.py \
  conf/skin_targets/holo_cofactors.yaml \
  conf/structure/openfold3.yaml \
  conf/structure/aqaffinity.yaml \
  scripts/run_openfold3_smoke.sh \
  scripts/run_openfold3_metal_smoke.sh \
  scripts/run_openfold3_consensus_smoke.sh \
  scripts/build_of3_msa_template_cache.py \
  scripts/run_openfold3_chembl_calibration.py \
  scripts/multi_fidelity_bo_scheduler.py \
  pilot/scientific_gates.yaml \
  tests/test_license_gate.py \
  tests/unit/test_aqaffinity_adapter.py \
  tests/unit/test_cofactor_registry.py \
  docs/OPENFOLD3_AQAFFINITY_PATCH_MANIFEST_2026-05-03.md
sha256sum /tmp/genesis_openfold3_patch_2026-05-03.tar.gz
```

The on-D commit/push step is owner's call — manifest stops at "files
mirrored". No commit, push, or queue start initiated by this patch.
