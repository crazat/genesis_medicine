#!/bin/bash
# Convert all preprint manuscripts to PDF (HTML intermediate via pandoc + chrome).
# Figures embedded as base64 in HTML; PDF includes inline images.

set -e
cd /home/crazat/genesis_medicine

for d in preprints/*/; do
    name=$(basename "$d")
    [ "$name" = "REVISION_PLAN.md" ] && continue
    [ ! -f "$d/manuscript.md" ] && continue

    echo "=== $name ==="
    cd "$d"
    pandoc manuscript.md -o manuscript.html \
        --embed-resources --standalone \
        --metadata title="$name" 2>&1 | tail -1

    google-chrome --headless --disable-gpu --no-sandbox \
        --print-to-pdf="manuscript.pdf" --print-to-pdf-no-header \
        "file://$(pwd)/manuscript.html" 2>/dev/null
    ls -la manuscript.pdf 2>&1 | awk '{print "  "$5" bytes ⇒ "$NF}'
    cd /home/crazat/genesis_medicine
done

echo ""
echo "=== ALL PDFs ==="
ls -la preprints/*/manuscript.pdf 2>&1 | awk '{print $5, $NF}'
