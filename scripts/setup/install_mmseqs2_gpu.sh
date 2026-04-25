#!/usr/bin/env bash
# 자체 호스팅 MMseqs2-GPU 설치 (S4 — 상업 빌드 블로커 해소)
# https://github.com/soedinglab/MMseqs2 (BSD-2)
# 참고: https://www.nature.com/articles/s41592-025-02819-8 (MMseqs2-GPU, 1.65× 가속)

set -euo pipefail

DB_DIR="${MMSEQS2_DB:-${HOME}/genesis_medicine/.cache/mmseqs2_db}"
mkdir -p "${DB_DIR}"

# 1. Conda 환경에 mmseqs2 GPU 빌드 설치
echo "==> conda install mmseqs2 (GPU)"
conda install -y -c conda-forge -c bioconda 'mmseqs2=*=*gpu*' || \
    conda install -y -c conda-forge -c bioconda mmseqs2

# 2. ColabFold setup_databases.sh 다운로드
SETUP_SCRIPT="${DB_DIR}/setup_databases.sh"
if [ ! -f "${SETUP_SCRIPT}" ]; then
    echo "==> ColabFold setup_databases.sh 다운로드"
    curl -fsSL -o "${SETUP_SCRIPT}" \
        https://raw.githubusercontent.com/sokrypton/ColabFold/main/setup_databases.sh
    chmod +x "${SETUP_SCRIPT}"
fi

# 3. UniRef30 + ColabFoldDB 빌드 (GPU=1)
# ⚠️ 약 1TB 디스크, 24~48시간 소요
echo "==> setup_databases.sh GPU=1 (1TB, 24~48h)"
echo "    중단해도 재개 가능. 주의: ColabFoldDB 단일쿼리 모드는 768GB RAM 필요."
GPU=1 "${SETUP_SCRIPT}" "${DB_DIR}"

echo ""
echo "✅ MMseqs2-GPU 설치 완료. DB_DIR=${DB_DIR}"
echo ""
echo "사용법 (Hydra):"
echo "  python -m genesis_medicine.cli run msa.provider=mmseqs2_local msa.db_dir=${DB_DIR}"
