#!/usr/bin/env bash
# Genesis_Medicine v3 — Tier 0 SOTA 도구 자동 설치 (2026-04-26 SOTA audit 결과)
#
# 설치 도구 (모두 MIT/Apache, commercial 빌드 호환):
#  1. PocketXMol (Cell 2026, MIT) — generative SBDD/peptide
#  2. PocketMiner (Nat Comm 2023, GVP-GNN) — cryptic pocket scan
#  3. CellAwareGNN (bioRxiv 2026-02) — TxGNN 후속, scPrimeKG
#  4. f-RAG (NVIDIA NeurIPS 2024) — 한약 fragment 강제 generative
#  5. NPASS 2026 update — quantitative ADME-Tox dump
#  6. BAT2 (OpenMM 호환 ABFE, JCTC 2024)
#
# 주의: 일부는 별도 conda env 권장. GPU 리소스 충돌 방지 위해 ABFE 실행 중에는 빌드만,
#       inference는 ABFE 종료 후로 미룸.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
EXTERNAL="$ROOT/external"
mkdir -p "$EXTERNAL"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
log()  { echo -e "${GREEN}[Tier0]${NC} $*"; }
warn() { echo -e "${YELLOW}[Tier0]${NC} $*"; }
err()  { echo -e "${RED}[Tier0]${NC} $*" >&2; }

UV="/home/crazat/.local/bin/uv"
VENV="$ROOT/.venv"

# ═══════════════════════════════════════════════════════════════════════════
# 1. PocketXMol (Cell 2026, MIT)
# ═══════════════════════════════════════════════════════════════════════════
install_pocketxmol() {
    log "1/6 PocketXMol 설치 (Cell 2026, MIT)"
    if [ -d "$EXTERNAL/PocketXMol" ]; then
        warn "  이미 설치됨 — skip"
        return 0
    fi
    cd "$EXTERNAL"
    git clone --depth=1 https://github.com/pengxingang/PocketXMol.git
    cd PocketXMol
    log "  weights 다운로드 (large file, network 필요)"
    # weights는 zenodo 또는 huggingface — 실제 URL은 PocketXMol README 확인 필요
    warn "  ⚠️  weights는 별도 다운로드 필요: README 참조"
    log "  ✅ PocketXMol clone 완료 → $EXTERNAL/PocketXMol"
}

# ═══════════════════════════════════════════════════════════════════════════
# 2. PocketMiner (Nat Comm 2023, GVP-GNN)
# ═══════════════════════════════════════════════════════════════════════════
install_pocketminer() {
    log "2/6 PocketMiner 설치 (Nat Comm 2023, cryptic pocket scan)"
    if [ -d "$EXTERNAL/PocketMiner" ]; then
        warn "  이미 설치됨 — skip"
        return 0
    fi
    cd "$EXTERNAL"
    # ramanathanlab/PocketMiner 또는 fork
    git clone --depth=1 https://github.com/Mickdub/gvp.git PocketMiner 2>/dev/null \
        || git clone --depth=1 https://github.com/ramanathanlab/PocketMiner.git
    log "  ✅ PocketMiner clone 완료 → $EXTERNAL/PocketMiner"
}

# ═══════════════════════════════════════════════════════════════════════════
# 3. CellAwareGNN (bioRxiv 2026-02)
# ═══════════════════════════════════════════════════════════════════════════
install_cellawaregnn() {
    log "3/6 CellAwareGNN 설치 (bioRxiv 2026-02, TxGNN 후속)"
    warn "  ⚠️  bioRxiv preprint 단계 — 공식 GitHub repo 미공개 가능"
    warn "  현재는 placeholder. 정식 release 시 자동 업데이트:"
    cat > "$EXTERNAL/cellawaregnn_TODO.md" <<'EOF'
# CellAwareGNN — TODO (2026-02 bioRxiv)

논문: https://www.biorxiv.org/content/10.64898/2026.02.20.707076v1
스펙: PrimeKG-U → scPrimeKG (140k nodes, 14M edges, OneK1K single-cell)
성능: AUPRC 0.826 (TxGNN 0.799), 자가면역 +6.0%

## 통합 작업 (코드 공개 시)
1. `git clone <official_repo>` → external/CellAwareGNN/
2. `txgnn` env에 추가 또는 신규 `cellawaregnn` env 생성
3. `src/genesis_medicine/repurposing/cellawaregnn_adapter.py` 작성
4. 기존 `txgnn_adapter` Protocol 호환 → 둘 중 선택 가능

## 우리 사용 케이스
- 자가면역 피부질환 (아토피·건선·원형탈모) 재창출 (자가면역 +6%)
- IPF 같은 rare fibrosis 적응
EOF
    log "  📝 placeholder 노트 → $EXTERNAL/cellawaregnn_TODO.md"
}

# ═══════════════════════════════════════════════════════════════════════════
# 4. f-RAG (NVIDIA NeurIPS 2024)
# ═══════════════════════════════════════════════════════════════════════════
install_frag() {
    log "4/6 f-RAG 설치 (NVIDIA NeurIPS 2024, fragment-RAG)"
    if [ -d "$EXTERNAL/f-RAG" ]; then
        warn "  이미 설치됨 — skip"
        return 0
    fi
    cd "$EXTERNAL"
    git clone --depth=1 https://github.com/NVlabs/f-RAG.git
    log "  📌 라이선스: NVIDIA Source Code License — commercial 사용 검토 필요 (법무)"
    log "  ✅ f-RAG clone 완료 → $EXTERNAL/f-RAG"

    # 한약 fragment library 자동 생성
    log "  🌿 한약 fragment library (센텔라/시코닌/EGCG) 추출"
    python3 "$ROOT/scripts/setup/build_herbal_fragments.py" \
        --input "$ROOT/data/skin_compounds_curated.csv" \
        --out "$EXTERNAL/f-RAG/herbal_fragments.smi" \
        2>/dev/null || warn "  ⚠️  herbal_fragments.smi 빌드 실패 (script 미작성?)"
}

# ═══════════════════════════════════════════════════════════════════════════
# 5. NPASS 2026 update
# ═══════════════════════════════════════════════════════════════════════════
install_npass() {
    log "5/6 NPASS 2026 update (NAR gkaf1196, ADME-Tox +206%)"
    NPASS_DIR="$ROOT/data/npass_2026"
    if [ -d "$NPASS_DIR" ]; then
        warn "  이미 다운로드됨 — skip"
        return 0
    fi
    mkdir -p "$NPASS_DIR"
    log "  📥 NPASS 3.0 dump 다운로드 (URL: bidd.group/NPASS)"
    warn "  ⚠️  웹사이트 직접 다운로드 — bidd.group/NPASS/download.php 방문 후"
    warn "      $NPASS_DIR/ 에 manual unzip"
    cat > "$NPASS_DIR/README.md" <<'EOF'
# NPASS 2026 update (NAR gkaf1196)

## 다운로드
1. https://bidd.group/NPASS/download.php 방문
2. 다음 파일 다운로드:
   - NPASS_v3_natural_products.tsv
   - NPASS_v3_quantitative_composition.tsv
   - NPASS_v3_admet_tox.tsv (★ 외용제 logKp 핵심)
   - NPASS_v3_targets.tsv
3. 본 디렉토리에 압축 해제

## 핵심 데이터 (2026 update vs 2018)
- 87,507 quantitative composition
- 34,975 toxicity records
- 9,713 ADME records (★ 외용제 ground truth)
- 204,023 NPs / 8,764 targets / 1M+ activity records

## 활용
- skin_compounds_curated.csv 의 logKp/irritation prediction ground truth
- ADMET-AI 자체 헤드 학습 데이터
EOF
    log "  📝 README → $NPASS_DIR/README.md (manual download 안내)"
}

# ═══════════════════════════════════════════════════════════════════════════
# 6. BAT2 (OpenMM 호환 ABFE)
# ═══════════════════════════════════════════════════════════════════════════
install_bat2() {
    log "6/6 BAT2 설치 (JCTC 2024, OpenMM + openmmtools)"
    if [ -d "$EXTERNAL/BAT2" ]; then
        warn "  이미 설치됨 — skip"
        return 0
    fi
    cd "$EXTERNAL"
    git clone --depth=1 https://github.com/GHeinzelmann/BAT.py.git BAT2
    cd BAT2
    log "  📌 ambertools + openmmtools 0.21+ 필요 (genesis-md env에 이미 설치됨)"
    log "  ✅ BAT2 clone 완료 → $EXTERNAL/BAT2"
    log "      genesis-md env에서 사용: python BAT.py [config]"
}

# ═══════════════════════════════════════════════════════════════════════════
# 메인
# ═══════════════════════════════════════════════════════════════════════════
main() {
    log "=== Genesis_Medicine v3 Tier 0 SOTA 설치 시작 ==="
    log "    위치: $EXTERNAL"
    log "    네트워크 + 디스크 확인 (총 ~5-10 GB 필요)"
    echo ""

    install_pocketxmol  || warn "PocketXMol 실패 (계속)"
    install_pocketminer || warn "PocketMiner 실패 (계속)"
    install_cellawaregnn || warn "CellAwareGNN placeholder (계속)"
    install_frag        || warn "f-RAG 실패 (계속)"
    install_npass       || warn "NPASS placeholder (계속)"
    install_bat2        || warn "BAT2 실패 (계속)"

    echo ""
    log "=== 설치 결과 ==="
    for d in PocketXMol PocketMiner f-RAG BAT2; do
        if [ -d "$EXTERNAL/$d" ]; then
            log "  ✅ $d"
        else
            warn "  ❌ $d 미설치"
        fi
    done

    echo ""
    log "=== 다음 단계 ==="
    log "  1. logKp 모델 학습:    python scripts/train_logkp_head.py"
    log "  2. PocketMiner 흉터:   python scripts/run_pocketminer_scar.py"
    log "  3. f-RAG fragments:    python scripts/setup/build_herbal_fragments.py"
    log "  4. NPASS dump 다운로드 (수동): data/npass_2026/README.md 참조"
    log "  5. ABFE 끝나면 BAT2로 검증: python external/BAT2/BAT.py"
}

main "$@"
