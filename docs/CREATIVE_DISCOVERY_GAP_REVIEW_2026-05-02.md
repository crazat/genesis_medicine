# Creative Molecular Discovery Gap Review

- timestamp: `2026-05-02T19:00:00+09:00`
- scope: 새 물질 발굴의 창의성, novelty, 합성 가능성, biology translation을 높이기 위한 missing technology review
- local action taken: R17 완료 후 GPU idle을 막기 위해 `active_learning_next_boltz2_cofold` short-triage fallback을 planner에 추가하고 batch01을 시작했다.

## Executive Conclusion

현재 Genesis_Medicine은 평가/검증 gate는 빠르게 고도화되었지만, 창의적 생성 엔진은 아직 보수적이다. 특히 R16/R17 chromanol처럼 한 scaffold 주변을 치밀하게 탐색하는 능력은 강하지만, 전혀 다른 chemotype, 합성경로가 보장된 reaction-native 후보, cryptic/allosteric pocket 후보, phenotypic rescue 후보를 생성하는 계층은 아직 약하다.

가장 큰 gap은 `generate first, filter later`가 아니라 `synthesis/pathway/property/pocket/IP constraints를 처음부터 걸고 generate`하는 층이다.

## Gap Priority

| priority | missing layer | current local status | required next system behavior |
|---|---|---|---|
| P0 | synthesis-aware generation | route gate는 있으나 AiZynthFinder/ASKCOS 미설치, 생성은 post-filter 중심 | reaction template/building-block 기반 enumeration 또는 RGFN/SynFlowNet류로 합성 가능한 공간만 생성 |
| P0 | generative diversity beyond chromanol | R17은 constrained chromanol analog 탐색 | scaffold-hopping, shape-conditioned, pharmacophore-conditioned generation을 별도 queue로 운영 |
| P0 | active-learning GPU fallback | R17 완료 후 planner가 `task=none`을 반환 | active-learning 미검증 후보를 short Boltz-2 cofold로 자동 큐잉 |
| P1 | protein dynamics / cryptic pocket generation | 문서에는 있으나 실제 큐는 static/cofold 중심 | PocketMiner/BioEmu/AlphaFlow-style ensemble pocket scout 후 pocket-specific generation |
| P1 | ultra-large tangible chemical space | roadmap만 있음 | ZINC/Enamine/REAL subset의 descriptor/embedding pre-screen, top acquisition만 cofold |
| P1 | reward-hacking / novelty benchmark | decoy/uncertainty gate는 있음 | MolScore/Tartarus/DrugPose-style generation benchmark와 novelty/diversity guard |
| P1 | phenomics-first discovery | phenomics gate는 있음 | JUMP/OpenPhenom-style signature lookup과 disease-cell rescue objective를 generator score에 포함 |
| P2 | new modalities | covalent/quinone은 safety caveat 중심 | covalent/allosteric/degrader/glue는 별도 high-risk modality lane으로 분리 |
| P2 | multi-agent hypothesis evolution | deterministic curator loop 중심 | hypothesis generator, critic, IP reviewer, synthesis reviewer, wet-lab planner 분리 |

## Literature Signals

1. Structure cofolding alone is not enough. AlphaFold 3 and Boltz-2-style cofolding improved structure/affinity prediction, but PoseBusters-like work shows physical validity and generalization checks are still mandatory.
2. Generative chemistry is moving toward pocket/shape/pharmacophore-conditioned diffusion and multi-objective guidance, not simple substituent enumeration.
3. Synthesis is now a first-class design constraint. Reaction-space GFlowNets, retrosynthesis-optimized objectives, and virtual synthesis search reduce the risk of beautiful but unmakeable molecules.
4. Large tangible libraries such as ZINC/Enamine/REAL are too large for brute force. Active-learning compression and staged screening are the practical path.
5. Phenomics and Cell Painting are becoming discovery layers, not just validation. They can discover mechanism-adjacent rescue phenotypes where direct target docking is weak.
6. Autonomous chemistry agents are useful only if tool outputs are transparent, auditable, and connected to real experiments.

## Immediate Queue Policy

- Keep long-MD/FE blocked when FTO/Markush, ZAFF, or safety gates say hold.
- Fill idle GPU with short-triage Boltz-2 cofold batches from `active_learning_next_candidates.csv`.
- Prioritize non-MMP1 targets for this fallback because MMP-1 direct-binding remains blocked by the Zn/ZAFF gate.
- Do not promote active-learning cofold hits to lead claims until prior-art, synthesis, structure-consensus, safety, and phenomics gates pass.

## Implementation Notes

- Added `scripts/run_active_learning_next_cofold.py`.
- Updated `scripts/auto_result_planner.py` so that after R17 complete, planner returns `active_learning_next_boltz2_cofold` when unlabeled non-MMP1 active-learning pairs exist.
- First fallback batch: `pilot/cpu_meaningful/active_learning_next_cofold_batch01.csv` after completion.

## Source Pointers

- AlphaFold 3: https://www.nature.com/articles/s41586-024-07487-w
- Boltz-2: https://boltz.bio/boltz2
- PoseBusters: https://pmc.ncbi.nlm.nih.gov/articles/PMC10901501/
- REINVENT 4: https://link.springer.com/article/10.1186/s13321-024-00812-5
- Pocket2Mol: https://proceedings.mlr.press/v162/peng22b
- DiffSBDD: https://www.nature.com/articles/s43588-024-00737-x
- DiffLinker: https://www.nature.com/articles/s42256-024-00815-9
- DiffSMol: https://www.nature.com/articles/s42256-025-01030-w
- IDOLpro: https://pubs.rsc.org/en-gb/content/articlelanding/2025/sc/d5sc01778e
- RGFN: https://arxiv.org/abs/2406.08506
- SynFlowNet: https://arxiv.org/abs/2405.01155
- AiZynthFinder: https://pmc.ncbi.nlm.nih.gov/articles/PMC7672904/
- MolScore: https://jcheminf.biomedcentral.com/articles/10.1186/s13321-024-00861-w
- Tartarus: https://papers.neurips.cc/paper_files/paper/2023/hash/09f8b2469a3d1089a7c60d9ef1983271-Abstract-Datasets_and_Benchmarks.html
- JUMP Cell Painting: https://www.nature.com/articles/s41592-024-02241-6
- ChemCrow: https://www.nature.com/articles/s42256-024-00832-8
- Coscientist: https://www.nature.com/articles/s41586-023-06792-0
