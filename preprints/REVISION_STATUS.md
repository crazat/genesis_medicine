# Preprint Revision Status (live tracking)

작성: 2026-04-26 · Auto-updated as revisions complete

## Audit summary

User audit (2026-04-26) caught fabricated tables in preprints #4-#7 and #9.
Per A안 (run real screens + revise), revision is in progress.

## Revision status by preprint

| # | Preprint | v0.1 status | Real data source | v0.2 status | Commit |
|---|---|---|---|---|---|
| 1 | Embelia ribes review | ✅ no fabrication issue (literature review) | — | not required | — |
| 2 | Recover workflow | ✅ no fabrication issue (system architecture) | — | not required | — |
| 3 | EMB-3 scar case study | ⚠️ cross-disease 6/7 IPF claim was memory-based | Open Targets v4 reverse query (2026-04-26) | **v0.2 done (Section 3.5 + 4.2 corrected)** | b6abc02 |
| 4 | Pigmentation | ❌ ranking table fabricated | Pigmentation screen (TYR+TYRP1+DCT, 15 compounds) | 🔄 awaiting screen result | pending |
| 5 | Alopecia | ❌ ranking table fabricated | Alopecia screen (SRD5A2+AR+CTNNB1, 15 compounds) | ⏸ queued (after #4) | pending |
| 6 | Acne | ❌ ranking table fabricated | Acne screen (SRD5A2+AR; SREBP1+C.acnes deferred) | ⏸ queued | pending |
| 7 | Photoaging | ❌ 12-target scorecard fabricated | Photoaging screen (MMP1+SIRT1; FBN1+mTOR deferred) | ⏸ queued | pending |
| 8 | ABFE methodology | ⚠️ T4L calibration result placeholder | T4L99A·benzene calibration in progress | ⏸ awaiting calibration | pending |
| 9 | Cross-disease IPF | ❌ overlap percentages fabricated | Open Targets v4 forward + reverse queries | **v0.2 done (Sections 1, 4, 5, 7 honest correction)** | 90a0470 |
| 10 | Chronotherapy | ✅ no fabrication issue (conceptual framework) | — | not required | — |
| 11 | Korean PGx | ✅ no fabrication issue (panel design) | — | not required | — |
| 12 | Open-source perspective | ✅ no fabrication issue (resource paper) | — | not required | — |

## Real data files (committed)

- `pilot/sar_panel/panel_validated.csv` (7-compound ADMET panel for Preprint #3)
- `pilot/scaffold_hop/` (Round 1 EMB-3 emergence — used in #1, #3)
- `pilot/scaffold_hop_round3/round3_affinity.csv` (used in #3)
- `pilot/open_targets/fibrosis_targets.csv` (used in #3, #9)
- `pilot/open_targets/antifibrotic_targets_to_diseases.csv` (used in #9)
- `pilot/open_targets/emb3_cross_disease_overlap.csv` (used in #9)
- `pilot/screen/pigmentation/screen_results.csv` (in progress; for #4)
- `pilot/screen/alopecia/screen_results.csv` (queued; for #5)
- `pilot/screen/acne/screen_results.csv` (queued; for #6)
- `pilot/screen/photoaging/screen_results.csv` (queued; for #7)
- `pilot/calibration/t4l_benzene/result_corrected.json` (in progress; for #8)

## Currently running (autonomous mode)

| Process | PID | Started | Expected | For preprint |
|---|---|---|---|---|
| Pigmentation screen | 115847 | 14:39 | ~16:30 | #4 |
| Chain wrapper (alopecia → acne → photoaging) | 116865 | 15:43 | ~19:00 | #5, #6, #7 |
| T4L99A·benzene ABFE | 112376 | 14:39 | ~22:00 | #8 |

## Monitors armed

- `bd3rqz5kc` — Pigmentation `screen_results.csv`
- `babvrp1sf` — `pilot/screen/ALL_DONE` flag (after all 4 screens)
- T4L (manual check; no monitor armed yet — will arm on alarm)

## Quality gates

- [ ] All ranking tables traced to a `pilot/screen/.../screen_results.csv` row
- [x] Cross-disease overlap claims traced to real Open Targets queries (#9 v0.2 ✅)
- [ ] Generative-analog claims (LCA-7, EMD-3, BCL-7) — need to either run REINVENT real or remove (planned for v0.2 of #4-6)
- [x] No specific affinity value in #3, #9 v0.2 unsupported by real data
- [ ] Same gate for #4, #5, #6, #7, #8 v0.2 (in progress)

## Next autonomous actions (when monitors fire)

1. **bd3rqz5kc fires (pigmentation done)**: open `screen_results.csv`, revise preprint #4 v0.2
2. **babvrp1sf fires (ALL_DONE)**: revise preprints #5, #6, #7 v0.2 in turn
3. **T4L `result_corrected.json` appears**: revise preprint #8 v0.2 with PASS/FAIL + calibrated values

All revisions follow the spec in `REVISION_PLAN.md`.

## Honest summary at any given moment

We currently have:
- 7/12 preprints honest and not requiring revision (#1, #2, #3 v0.2, #9 v0.2, #10, #11, #12)
- 5/12 preprints awaiting real-data revision (#4, #5, #6, #7, #8)
- All revisions are scheduled, all data sources identified
- No fabricated value will appear in any v0.2 manuscript
- Limitations sections will explicitly note unscreened targets (MITF, SRD5A1, SREBP1, FBN1, mTOR, C. acnes proteins)

Per user instruction, autonomous mode: revisions execute as data lands without further user confirmation.
