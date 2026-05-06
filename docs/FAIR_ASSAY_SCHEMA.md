# FAIR Assay Schema

- timestamp: `2026-05-06T12:46:35+09:00`
- dictionary_csv: `pilot/cpu_meaningful/fair_assay_dictionary.csv`
- template_csv: `data/fair_assay_metadata_template.csv`
- schema_json: `data/fair_assay_schema.json`
- purpose: wet-lab/CRO 결과를 ISA/BAO/RO-Crate-ready metadata로 받아 compute loop와 논문 provenance에 재사용한다.

## Required Fields

| field | type | description |
|---|---|---|
| investigation_id | string | ISA investigation identifier |
| study_id | string | ISA study identifier or project arm |
| assay_id | string | assay run identifier |
| experiment_date | date | ISO date for experiment start |
| compound_id | string | Genesis candidate identifier |
| smiles | string | canonical or submitted SMILES |
| batch_id | string | compound batch or vendor lot |
| target_or_pathway | string | target, pathway, or phenotype axis |
| disease_context | controlled_string | scar, pigment, acne, alopecia, photoaging, or control |
| assay_type | controlled_string | qPCR, enzyme, Cell Painting, viability, IVRT, IVPT, etc. |
| cell_type_or_model | string | cell line, primary cell, organoid, skin model, or biochemical assay |
| dose | number | dose value |
| dose_unit | controlled_string | dose unit |
| timepoint | string | duration or sampling time |
| endpoint | string | measured endpoint |
| value | number | numeric readout |
| unit | controlled_string | endpoint unit |
| replicate_id | string | biological/technical replicate identifier |
| control_type | controlled_string | vehicle, positive, negative, untreated, reference drug |
| protocol_version | string | protocol or SOP version |
| raw_file | string | path or URI for raw data |
| raw_file_sha256 | sha256 | hash for raw file integrity |
| quality_flag | controlled_string | pass, review, fail |
| interpretation | controlled_string | promote, hold, deprioritize |

## Curator Rule

- raw assay value만 있는 CSV는 논문 근거로 쓰지 않는다. `dose`, `unit`, `replicate_id`, `control_type`, `quality_flag`, `raw_file_sha256`가 필요하다.
- `quality_flag=review/fail`은 음성 결과로 보존하되 lead promotion에는 쓰지 않는다.
- `interpretation=promote` row가 들어오면 active-learning/BO planner가 다음 compute 또는 assay를 승격해야 한다.
