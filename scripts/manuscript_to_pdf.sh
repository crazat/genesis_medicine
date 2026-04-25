#!/usr/bin/env bash
# manuscript.md → HTML/DOCX/PDF 변환.
#
# 사용:
#   bash scripts/manuscript_to_pdf.sh pilot/skin_scar/manuscript [csl_name]
#
# csl_name 예: nature, phytomedicine, journal-of-cheminformatics

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIR_RAW="${1:-pilot/bace1_boltz2/manuscript_demo}"
# 절대 경로 보장
if [[ "$DIR_RAW" = /* ]]; then
    DIR="$DIR_RAW"
else
    DIR="${ROOT}/${DIR_RAW}"
fi
CSL_NAME="${2:-nature}"

# CSL 파일 위치
CSL_FILE="${ROOT}/data/csl/${CSL_NAME}.csl"
if [ ! -f "$CSL_FILE" ]; then
    echo "❌ CSL 없음: $CSL_FILE"
    exit 1
fi
mkdir -p "$DIR"
cp "$CSL_FILE" "$DIR/${CSL_NAME}.csl"

cd "$DIR"

if [ ! -f manuscript.md ]; then
    echo "❌ manuscript.md 없음: $DIR/manuscript.md"
    exit 1
fi

PATH="$ROOT/.venv/bin:$PATH"

echo "=== Pandoc 변환 ($CSL_NAME) ==="

# HTML
pandoc manuscript.md \
    -o manuscript.html \
    --citeproc --bibliography references.bib \
    --csl "${CSL_NAME}.csl" \
    --standalone --mathjax \
    2>/dev/null || echo "  HTML 일부 경고 무시"
echo "  ✅ HTML: $(du -h manuscript.html | cut -f1)"

# DOCX
pandoc manuscript.md \
    -o manuscript.docx \
    --citeproc --bibliography references.bib \
    --csl "${CSL_NAME}.csl" \
    2>/dev/null
echo "  ✅ DOCX: $(du -h manuscript.docx | cut -f1)"

# PDF (weasyprint)
if command -v weasyprint > /dev/null; then
    pandoc manuscript.md \
        -o manuscript.pdf \
        --pdf-engine=weasyprint \
        --citeproc --bibliography references.bib \
        --csl "${CSL_NAME}.csl" \
        2>/dev/null
    echo "  ✅ PDF: $(du -h manuscript.pdf | cut -f1)"
else
    echo "  ⚠️  weasyprint 없음 — pip install weasyprint"
fi

echo ""
echo "=== 출력 ==="
ls -la "$DIR" | grep -E "manuscript\.(html|docx|pdf)$"
