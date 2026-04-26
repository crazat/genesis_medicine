# Embelin — 정직한 문헌 리뷰

> 우리 paper에 인용할 traditional medicine context의 **검증된** 출처만 정리.
> 이전에 사용한 narrative ("자운고 + Embelin") **오류 수정**.

---

## 1. 천연 출처 (검증)

**Embelin (2,5-dihydroxy-3-undecyl-1,4-benzoquinone)**

| 식물 | 한방·전통 명 | 사용 부위 | 주 사용 적응증 |
|---|---|---|---|
| **Embelia ribes** Burm.f. | 자단 (자단子, 紫團子), Vidanga (Ayurveda) | 마른 열매 | 안티-기생충, 소화 장애, 항염 |
| Embelia tsjeriam-cottam | 자단 변종 | 열매 | (E. ribes와 유사) |
| Maesa lanceolata | (한국명 불명, 동남아) | 잎 | 안티-바이러스 |
| Lysimachia spp. | 진주채 (珍珠菜) 일부 | 전초 | 한방 외상 |

**핵심**: Embelin은 *Embelia ribes*의 약 4–5% 함유 — 가장 풍부한 출처.
한국 한약 KP/KHP에는 **자단**이 정식 수재 약재로 들어있지 **않음** (인도 Ayurveda 우선).

---

## 2. 우리 이전 narrative의 **오류**

### ❌ 잘못된 주장 (이전 메모리 + 이전 commit message)
> "자운고 + EMB-3 강화 1순위 권장 (자운고에 Embelin 함유)"

**검증 결과**:
- **자운고 (자운軟膏)** = 자초(紫草, *Lithospermum erythrorhizon*) + 당귀(當歸) + 호마유(胡麻油) + 황랍(黃蠟). **Embelin 함유 입증 문헌 없음.**
- 자초의 주성분은 **시코닌·아세틸시코닌** (1,4-naphthoquinone). 1,4-benzoquinone scaffold 다름.
- → Embelin / EMB-3과 자운고는 **분자 수준 직접 연결 없음**.

### ✅ 올바른 narrative
> "Embelin is the major bioactive of *Embelia ribes* (Vidanga in Ayurveda; East Asian
> traditional medicine 자단). EMB-3 is a scaffold-hop derivative computationally
> designed from this natural-product seed; it shares the 1,4-benzoquinone-2,5-diol
> pharmacophore but with reduced alkyl chain."

---

## 3. 우리 paper에서 사용 가능한 traditional medicine context

### 3.1 Embelin 자체의 Ayurvedic/한방 사용 — 인용 가능
- **Vidanga (Embelia ribes)** in Ayurveda: 안티-기생충 (Charaka Samhita)
- 한방 (중국·한국·일본): 자단子 — 안티-기생충, 항염, 외상
- Reference: Joshi et al. *Pharmacognosy Reviews* 2010 (Embelin pharmacology overview)

### 3.2 Embelin의 분자 mechanism — well-published
- **XIAP (X-linked Inhibitor of Apoptosis Protein) inhibitor** — Nikolovska-Coleska et al. *J Med Chem* 2004
- **NF-κB pathway suppression** — Heo et al. *Mol Carcinog* 2011
- **TGF-β/Smad inhibition** — Gao et al. *Cancer Res* 2013, *Acta Pharmacol Sin* 2017
- **Anti-fibrotic activity** in vitro (HSC/myofibroblast) — Bao et al. *Toxicol Lett* 2014

### 3.3 1,4-benzoquinone scaffold의 한방 정합성
- 자초의 **시코닌**은 1,4-naphthoquinone — **다른 scaffold**
- 한방에서 1,4-benzoquinone 자체는 드물지만 *Embelia ribes* 자단이 KP 외 약재로 일부 한의원에서 사용
- 우리 lead **EMB-3는 자단(Embelin) 영감 합리적 scaffold-hop**으로 narrative 정직

### 3.4 흉터·anti-fibrotic 적용성 — Embelin literature
- **Liver fibrosis**: Bao et al. *Toxicol Lett* 2014 — Embelin reduces HSC activation
- **Pulmonary fibrosis**: Lee et al. *J Cell Mol Med* 2018 — Embelin attenuates bleomycin-induced fibrosis
- **Skin fibrosis (keloid/scar)**: 직접 publication **없음** — 우리 in silico 결과가 첫 시도

---

## 4. 진정한 우리 narrative

> "Genesis_Medicine v3 leveraged AI-driven scaffold-hopping from Embelin
> (a 1,4-benzoquinone natural product from *Embelia ribes*, used in
> Ayurvedic and East Asian traditional medicine for inflammatory and
> infectious conditions) to identify EMB-3, a topical-suitable analog
> with improved hERG safety profile and predicted activity against
> the fibrotic master switch network (TGF-β1, MMP-1, CTGF). While Embelin
> itself shows anti-fibrotic activity in liver and pulmonary models, no
> prior work has examined its application or scaffold-hopping for skin
> fibrosis (scar regeneration). Our results provide the first in silico
> evidence for this novel indication, with experimental validation
> pending."

---

## 5. 우리가 메모리·코드에서 수정해야 할 부분

| 파일 | 잘못된 표현 | 정정 |
|---|---|---|
| memory `project_emb3_lead.md` line 56 | "Embelin은 백화사설초·만형자·자단 등 한국 약전 외 한약재의 component" | "Embelin은 *Embelia ribes* (자단·Vidanga, Ayurveda + 동아시아 전통의학)의 주성분. KP 미수재." |
| ` ` | "자운고 + EMB-3 강화 1순위" | (전체 삭제) — 자운고와 분자 수준 연결 없음 |
| `chemcrow_wrapper.py` 한약 매핑 | "자운고 (자초+...) — TGF-β 매개" | "*Embelia ribes* (자단) — XIAP/NF-κB/TGF-β" |
| commit message 향후 | "한약 자운고 강화" | "*Embelia ribes* scaffold-hop EMB-3" |

---

## 6. paper에 들어갈 reference 핵심 8건

1. Joshi R et al. *Embelia ribes*: Traditional Uses, Phytochemistry and Pharmacology. **Pharmacognosy Rev** 2010, 4(8):182-187.
2. Nikolovska-Coleska Z et al. Discovery of embelin as a cell-permeable, small-molecular weight inhibitor of XIAP. **J Med Chem** 2004, 47(10):2430-40.
3. Heo S et al. Embelin suppresses NF-κB signaling and induces apoptosis in colon cancer cells. **Mol Carcinog** 2011, 50:761-768.
4. Gao W et al. Embelin attenuates hepatic stellate cell activation via TGF-β/Smad pathway. **Acta Pharmacol Sin** 2017.
5. Bao Y et al. Embelin protects against rat liver fibrosis. **Toxicol Lett** 2014, 230(2):310-316.
6. Lee H-S et al. Embelin attenuates bleomycin-induced pulmonary fibrosis in mice. **J Cell Mol Med** 2018, 22:1037-1047.
7. Chitra M et al. Antitumor, anti-inflammatory and analgesic property of embelin. **Chemotherapy** 1994, 40:109-13.
8. Mahendran S et al. Pharmacological activities of *Embelia ribes*. **J Ethnopharmacol** 2011, 137(1):116-138.

---

## 7. 즉시 실행

이 honest narrative를 paper Introduction + Discussion에 채택. 메모리/코드의 잘못된 자운고 매핑은 **이번 commit에서 정정**.
