"""Generic disease-screen runner — Boltz-2 cofold + ADMET-AI for a curated
compound library against a defined target panel.

Usage
-----
  python scripts/run_disease_screen.py \\
      --library data/screen_libraries/pigmentation_compounds.csv \\
      --targets TYR,TYRP1,DCT \\
      --out pilot/screen/pigmentation/

The compound library CSV needs columns: compound, smiles, source_herb, traditional_use.
Available cached MSAs (a3m): see data/msa/*.a3m. Targets specified as UniProt
gene symbols; mapped to sequences and MSA paths via the TARGET_REGISTRY below.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import warnings
from pathlib import Path

import pandas as pd
import yaml

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
MSA_CACHE = ROOT / "data/msa"


# UniProt sequences (mature/active region) for cached-MSA targets
TARGET_REGISTRY = {
    "TGFB1": {
        "uniprot": "P01137",
        "sequence": "ALDTNYCFSSTEKNCCVRQLYIDFRKDLGWKWIHEPKGYHANFCLGPCPYIWSLDTQYSKVLALYNQHNPGASAAPCCVPQALEPLPIVYYVGRKPKVEQLSNMIVRSCKCS",
        "msa": "tgfb1.a3m",
    },
    "MMP1": {
        "uniprot": "P03956",
        "sequence": "LFREMPGGPVWRKHYITYRINNYTPDMNREDVDYAIRKAFQVWSNVTPLKFSKINTGMADILVVFARGAHGDFHAFDGKGGILAHAFGPGSGIGGDAHFDEDERWTNNFREYNLHRVAAHELGHSLGLSHSTDIGALMYPSYTFSGDVQLAQDDIDGIQAIYG",
        "msa": "mmp1.a3m",
    },
    "TYR": {
        "uniprot": "P14679",
        "sequence": "MLLAVLYCLLWSFQTSAGHFPRACVSSKNLMEKECCPPWSGDRSPCGQLSGRGSCQNILLSNAPLGPQFPFTGVDDRESWPSVFYNRTCQCSGNFMGFNCGNCKFGFWGPNCTERRLLVRRNIFDLSAPEKDKFFAYLTLAKHTISSDYVIPIGTYGQMKNGSTPMFNDINIYDLFVWMHYYVSMDALLGGSEIWRDIDFAHEAPAFLPWHRLFLLRWEQEIQKLTGDENFTIPYWDWRDAEKCDICTDEYMGGQHPTNPNLLSPASFFSSWQIVCSRLEEYNSHQSLCNGTPEGPLRRNPGNHDKSRTPRLPSSADVEFCLSLTQYESGSMDKAANFSFRNTLEGFASPLTGIADASQSSMHNALHIYMNGTMSQVQGSANDPIFLLHHAFVDSIFEQWLQRHRPLQEVYPEANAPIGHNRESYMVPFIPLYRNGDFFISSKDLGYDYSYLQDSDPDSFQDYIKSYLEQASRIWSWLLGAAMVGAVLTALLAGLVSLLCRHKRKQLPEEKQPLLMEKEDYHSLYQSHL",
        "msa": "tyr.a3m",
    },
    "TYRP1": {
        "uniprot": "P17643",
        "sequence": "MSAPKLLSLGCIFFPLLLFQQARAQFPRQCATVEALRSGMCCPDLSPVSGPGTDRCGSSSGRGRCEAVTADSRPHSPQYPHDGRDDREVWPLRFFNRTCHCNGNFSGHNCGTCRPGWRGAACDQRVLIVRRNLLDLSKEEKNHFVRALDMAKRTTHPLFVIATRRSEEILGPDGNTPQFENISIYNYFVWTHYYSVKKTFLGVGQESFGEVDFSHEGPAFLTWHRYHLLRLEKDMQEMLQEPSFSLPYWNFATGKNVCDICTDDLMGSRSNFDSTLISPNSVFSQWRVVCDSLEDYDTLGTLCNSTEDGPIRRNPAGNVARPMVQRLPEPQDVAQCLEVRVFDTPPFYSNSTNSFRNTVEGYSDPTGKYDPAVRSLHNLAHLFLNGTGGQTHLSPNDPIFVLLHTFTDAVFDEWLRRYNADISTFPLENAPIGHNRQYNMVPFWPPVTNTEMFVTAPDNLGYTYEIQWPSREFSVPEIIAIAVVAALLLVALIFGTASYLIRARRSMDEANQPLLTDQYQCYAEEYEKLQNPNQSVV",
        "msa": "tyrp1.a3m",
    },
    "DCT": {
        "uniprot": "P40126",
        "sequence": "MGLVGWGLLLGCLGCGILLRARAQFPRVCMTVDSLVNKECCPRLGAESANVCGSQQGRGQCTEVRADTRPWSGPYILRNQDDRELWPRKFFHRTCKCTGNFAGYNCGDCKFGWTGPNCERKKPPVIRQNIHSLSPQEREQFLGALDLAKKRVHPDYVITTQHWLGLLGPNGTQPQFANCSVYDFFVWLHYYSVRDTLLGPGRPYRAIDFSHQGPAFVTWHRYHLLQLERDMQEMLQDPSFSLPYWNFATGKNECDVCTDQLFGAARPDDPTLISRNSRFSSWETVCDSLDDYNRRVTLCNGTYEGLLRRNQMGRNSRKLPTLKDIRDCLSLQKFDSPPFFQNSTFSFRNALEGFDKADGTLDSQVMSLHNLVHSFLNGTNALPHSAANDPIFVVLHSFTDAIFDEWMKRFNPPADAWPQELAPIGHNRMYNMVPFFPPVTNEELFLTSDQLGYSYAIDLPVSVEETPGWPTTLLVVMGTLVALVGLFVLLAFLQYRRLRKGYTPLMETHLSSKRYTEEA",
        "msa": "dct.a3m",
    },
    "AR": {
        "uniprot": "P10275",
        "sequence": "GTLGHLYKSRFLEILLEKFKAREDFDDLPLVENAYLGTAKVMSFDLRFWNMLMQSSWKVGMEDFLGTLFSDHVELLLSNSVPADFSLPLGSEDNVSLDSAEIAFPTPIQRVIKFDFEPPPGPLEQDPLTDLALAIDPPDPRHLRLNRPEKLHCIASGVGSRLNLLYKHFAGVTMEKKLHTLLVRSREALELCVSNSLPSPLQTLHFLALQDTAFVRQTNRRLKAPPNRSLRELTQQTLQQRLESELPDGNVLEEIASLMSVLNTLKLIVKLTFNAQGPLLSPSLLPLFRDSETLAHKVWHLKFLRGCSCWSFEKHAMVEKELLPFLERHGVPGDISDIRLNDSSSL",
        "msa": "ar.a3m",
    },
    "SRD5A2": {
        "uniprot": "P31213",
        "sequence": "MQLLVNLPGSKFEKGVEGHLPSSHRFIYKGLALVLFFGCLLAFVAFGSPNLSAYTRLPLLIYPLGYIGAPIIYFRVAFRKPLLEVDKEKLLAAPQGRGKCLYMDPKTSLVVIRYVLPPPVTRYFLLPFYAFIWFAPYAFMFADPHWVTYAFAANVLGHSGAVASYVLAQTYLNPNCLAFFLDSGPGYITWWQALMYLGPACVYLLFCWLLEHQEPPLVYKKCLKGEMMR",
        "msa": "srd5a2.a3m",
    },
    "CTNNB1": {
        "uniprot": "P35222",
        "sequence": "MATQADLMELDMAMEPDRKAAVSHWQQQSYLDSGIHSGATTTAPSLSGKGNPEEEDVDTSQVLYEWEQGFSQSFTQEQVADIDGQYAMTRAQRVRAAMFPETLDEGMQIPSTQFDAAHPTNVQRLAEPSQMLKHAVVNLINYQDDAELATRAIPELTKLLNDEDQVVVNKAAVMVHQLSKKEASRHAIMRSPQMVSAIVRTMQNTNDVETARCTAGTLHNLSHHREGLLAIFKSGGIPALVKMLGSPVDSVLFYAITTLHNLLLHQEGAKMAVRLAGGLQKMVALLNKTNVKFLAITTDCLQILAYGNQESKLIILASGGPQALVNIMRTYTYEKLLWTTSRVLKVLSVCSSNKPAIVEAGGMQALGLHLTDPSQRLVQNCLWTLRNLSDAATKQEGMEGLLGTLVQLLGSDDINVVTCAAGILSNLTCNNYKNKMMVCQVGGIEALVRTVLRAGDREDITEPAICALRHLTSRHQEAEMAQNAVRLHYGLPVVVKLLHPPSHWPLIKATVGLIRNLALCPANHAPLREQGAIPRLVQLLVRAHQDTQRRTSMGGTQQQFVEGVRMEEIVEGCTGALHILARDVHNRIVIRGLNTIPLFVQLLYSPIENIQRVAAGVLCELAQDKEAAEAIEAEGATAPLTELLHSRNEGVATYAAAVLFRMSEDKPQDYKKRLSVELTSSLFRTEPMAWNETADLGLDIGAQGEPLGYRQDDPSYRSFHSGGYGQDALGMDPMMEHEMGGHHPGADYPVDGLPDLGHAQDLMDGLPPGDSNQLAWFDTDL",
        "msa": "ctnnb1.a3m",
    },
    "SIRT1": {
        "uniprot": "Q96EB6",
        "sequence": "MADEAALALQPGGSPSAAGADREAASSPAGEPLRKRPRRDGPGLERSPGEPGGAAPEREVPAAARGCPGAAAAALWREAEAEAAAAGGEQEAQATAAAGEGDNGPGLQGPSREPPLADNLYDEDDDDEGEEEEEAAAAAIGYRDNLLFGDEIITNGFHSCESDEEDRASHASSSDWTPRPRIGPYTFVQQHLMIGTDPRTILKDLLPETIPPPELDDMTLWQIVINILSEPPKRKKRKDINTIEDAVKLLQECKKIIVLTGAGVSVSCGIPDFRSRDGIYARLAVDFPDLPDPQAMFDIEYFRKDPRPFFKFAKEIYPGQFQPSLCHKFIALSDKEGKLLRNYTQNIDTLEQVAGIQRIIQCHGSFATASCLICKYKVDCEAVRGDIFNQVVPRCPRCPADEPLAIMKPEIVFFGENLPEQFHRAMKYDKDEVDLLIVIGSSLKVRPVALIPSSIPHEVPQILINREPLPHLHFDVELLGDCDVIINELCHRLGGEYAKLCCNPVKLSEITEKPPRTQKELAYLSELPPTPLHVSEDSSSPERTSPPDSSVIVTLLDQAAKSNDDLDVSESKGCMEEKPQEVQTSRNVESIAEQMENPDLKNVGSSTGEKNERTSVAGTVRKCWPNRVAKEQISRRLDGNQYLFLPPNRYIFHGAEVYSDSEDDVLSSSSCGSNSDSGTCQSPSLEEPMEDESEIEEFYNGLEDEPDVPERAGGAGFGTDGDDQEAINEAISVKQEVTDMNYPSNKS",
        "msa": "sirt1.a3m",
    },
}


def step1_load_library(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    required = {"compound", "smiles", "source_herb", "traditional_use"}
    if not required.issubset(df.columns):
        raise ValueError(f"library CSV missing columns: {required - set(df.columns)}")
    print(f"  loaded {len(df)} compounds from {csv_path.name}")
    return df


def step2_admet(df: pd.DataFrame) -> pd.DataFrame:
    from rdkit import Chem, RDLogger
    from rdkit.Chem import Crippen, Descriptors, Lipinski
    RDLogger.DisableLog("rdApp.*")

    rows = []
    for _, r in df.iterrows():
        m = Chem.MolFromSmiles(r["smiles"])
        if m is None:
            print(f"  ⚠️ {r['compound']}: invalid SMILES, skip")
            continue
        rows.append({
            "compound": r["compound"], "smiles": Chem.MolToSmiles(m),
            "smiles_orig": r["smiles"],
            "source_herb": r["source_herb"],
            "traditional_use": r["traditional_use"],
            "MW": round(Descriptors.MolWt(m), 2),
            "logP": round(Crippen.MolLogP(m), 3),
            "HBD": Lipinski.NumHDonors(m),
            "HBA": Lipinski.NumHAcceptors(m),
            "TPSA": round(Descriptors.TPSA(m), 2),
        })
    cleaned = pd.DataFrame(rows)

    # ADMET-AI
    print(f"  ADMET-AI predicting {len(cleaned)} compounds…")
    from admet_ai import ADMETModel
    model = ADMETModel()
    adm = model.predict(cleaned["smiles"].tolist())
    for col in ["hERG", "Skin_Reaction", "AMES", "ClinTox",
                 "Bioavailability_Ma", "Solubility_AqSolDB"]:
        if col in adm.columns:
            cleaned[f"admet_{col}"] = [round(v, 4) for v in adm[col].values]

    # Topical sweet-spot flag
    cleaned["topical_friendly"] = (
        (cleaned["MW"].between(180, 500)) &
        (cleaned["logP"].between(1.5, 3.5)) &
        (cleaned["HBD"] <= 5) & (cleaned["HBA"] <= 10) &
        (cleaned["TPSA"] <= 140)
    )
    return cleaned


def step3_boltz_cofold(df: pd.DataFrame, targets: list[str],
                         out_dir: Path) -> pd.DataFrame:
    inp = out_dir / "boltz_inputs"
    inp.mkdir(parents=True, exist_ok=True)
    boltz_out = out_dir / "boltz_output"
    boltz_out.mkdir(parents=True, exist_ok=True)

    # Build YAML inputs
    n_jobs = 0
    for _, r in df.iterrows():
        comp_safe = "".join(c if c.isalnum() else "_" for c in r["compound"])[:30]
        for tgt in targets:
            if tgt not in TARGET_REGISTRY:
                print(f"  ⚠️ target {tgt} not in registry, skip")
                continue
            tgt_info = TARGET_REGISTRY[tgt]
            payload = {
                "version": 1,
                "sequences": [
                    {"protein": {"id": "A", "sequence": tgt_info["sequence"],
                                  "msa": str((MSA_CACHE / tgt_info["msa"]).absolute())}},
                    {"ligand": {"id": "B", "smiles": r["smiles"]}},
                ],
                "properties": [{"affinity": {"binder": "B"}}],
            }
            yaml_path = inp / f"{tgt.lower()}__{comp_safe}.yaml"
            yaml_path.write_text(yaml.safe_dump(payload, sort_keys=False))
            n_jobs += 1
    print(f"  prepared {n_jobs} cofold jobs ({len(df)} compounds × {len(targets)} targets)")

    # Run boltz
    boltz_bin = str(Path(sys.executable).parent / "boltz")
    cmd = [
        boltz_bin, "predict", str(inp),
        "--out_dir", str(boltz_out),
        "--sampling_steps", "25",
        "--diffusion_samples", "1",
        "--recycling_steps", "3",
        "--sampling_steps_affinity", "200",
        "--diffusion_samples_affinity", "5",
        "--affinity_mw_correction",
        "--devices", "1",
    ]
    print(f"  running Boltz-2…")
    t0 = time.time()
    rc = subprocess.run(cmd).returncode
    print(f"  ✅ Boltz-2 wall: {(time.time()-t0)/60:.1f}min, rc={rc}")

    # Collect results
    rows = []
    for aff in sorted(boltz_out.rglob("affinity_*.json")):
        d = json.loads(aff.read_text())
        stem = aff.stem.replace("affinity_", "")
        try:
            tgt_low, comp_safe = stem.split("__", 1)
        except ValueError:
            continue
        rows.append({
            "compound_safe": comp_safe,
            "target": tgt_low.upper(),
            "affinity_pred": d.get("affinity_pred_value"),
            "affinity_prob_binary": d.get("affinity_probability_binary"),
        })
    return pd.DataFrame(rows)


def step4_merge(adm_df: pd.DataFrame, boltz_df: pd.DataFrame,
                  targets: list[str], out_dir: Path) -> pd.DataFrame:
    # map compound_safe back
    adm_df["compound_safe"] = adm_df["compound"].apply(
        lambda c: "".join(ch if ch.isalnum() else "_" for ch in c)[:30])

    # pivot Boltz table: rows=compound, cols=targets
    pivot = boltz_df.pivot_table(
        index="compound_safe", columns="target",
        values="affinity_prob_binary", aggfunc="first")
    pivot["mean_affinity"] = pivot[targets].mean(axis=1)
    pivot = pivot.reset_index()

    final = adm_df.merge(pivot, on="compound_safe", how="left")
    final = final.sort_values("mean_affinity", ascending=False)
    final.to_csv(out_dir / "screen_results.csv", index=False)
    return final


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--library", type=Path, required=True)
    p.add_argument("--targets", required=True,
                    help="comma-separated UniProt gene symbols (must be in TARGET_REGISTRY)")
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    targets = [t.strip().upper() for t in args.targets.split(",")]
    args.out.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print(f"Disease screen — {args.library.stem}")
    print(f"  targets: {targets}")
    print(f"  out: {args.out}")
    print("=" * 72)

    df = step1_load_library(args.library)
    adm = step2_admet(df)
    print(f"\n  topical sweet spot: "
          f"{adm['topical_friendly'].sum()}/{len(adm)} compounds")

    boltz = step3_boltz_cofold(adm, targets, args.out)
    final = step4_merge(adm, boltz, targets, args.out)

    print("\n" + "=" * 72)
    print(f"top-5 by mean affinity (sweet spot first):")
    cols_to_show = ["compound", "source_herb", "MW", "logP",
                     "admet_hERG", "admet_Skin_Reaction"] + targets + ["mean_affinity", "topical_friendly"]
    show = [c for c in cols_to_show if c in final.columns]
    # Coerce all numeric columns to Python float for stable formatting
    final_show = final[show].head(8).copy()
    for c in final_show.columns:
        if final_show[c].dtype.kind in "fiu":
            final_show[c] = final_show[c].astype(float)
    print(final_show.to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    print("=" * 72)

    print(f"\n✅ {args.out}/screen_results.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
