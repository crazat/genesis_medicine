"""Rebuild all 14 preprints PDF with wide-table-safe CSS (word-break + auto layout)."""
from __future__ import annotations
import shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREPRINTS = ROOT / "preprints"

CSS = """
<style>
@page { size: A4; margin: 1.6cm 1.2cm; }
body { font-family: "DejaVu Sans", sans-serif; font-size: 10pt; line-height: 1.45; }
h1 { font-size: 16pt; margin-top: 0.6em; }
h2 { font-size: 13pt; margin-top: 1.0em; border-bottom: 1px solid #ccc; padding-bottom: 2px; }
h3 { font-size: 11pt; margin-top: 0.8em; }
code, pre { font-family: "DejaVu Sans Mono", monospace; font-size: 8.5pt; }
pre { background: #f5f5f5; padding: 6px 8px; overflow-wrap: break-word; white-space: pre-wrap; }
table {
  border-collapse: collapse;
  width: 100%;
  table-layout: auto;
  font-size: 8.5pt;
  margin: 0.6em 0;
  page-break-inside: auto;
}
th, td {
  border: 1px solid #bbb;
  padding: 3px 5px;
  vertical-align: top;
  word-break: break-word;
  overflow-wrap: anywhere;
  hyphens: auto;
  max-width: 18em;
}
th { background: #eee; font-weight: 600; }
img { max-width: 100%; height: auto; page-break-inside: avoid; }
figure { page-break-inside: avoid; margin: 0.8em 0; }
blockquote { border-left: 3px solid #ccc; margin: 0.6em 0; padding: 0.2em 0.8em; color: #444; }
</style>
"""


def rebuild(md: Path) -> bool:
    out_html = md.with_suffix(".html")
    out_pdf = md.with_suffix(".pdf")
    pandoc = shutil.which("pandoc")
    weasy = shutil.which("weasyprint")
    if not pandoc or not weasy:
        print(f"  ❌ pandoc / weasyprint not in PATH")
        return False

    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(CSS)
        header_path = f.name

    try:
        subprocess.run([
            pandoc, str(md),
            "-o", str(out_html),
            "--standalone",
            "--embed-resources",
            "-H", header_path,
            "--metadata", f"title=Genesis_Medicine — {md.parent.name}",
            "--toc", "--toc-depth=3",
            "--mathjax",
        ], check=True, capture_output=True, timeout=180)
    except subprocess.CalledProcessError as e:
        print(f"  ❌ pandoc HTML failed: {e.stderr.decode()[:200]}")
        return False
    except subprocess.TimeoutExpired:
        print(f"  ❌ pandoc HTML timeout")
        return False
    finally:
        Path(header_path).unlink(missing_ok=True)

    try:
        subprocess.run([
            weasy, str(out_html), str(out_pdf),
        ], check=True, capture_output=True, timeout=300)
    except subprocess.CalledProcessError as e:
        print(f"  ❌ weasyprint PDF failed: {e.stderr.decode()[:200]}")
        return False
    except subprocess.TimeoutExpired:
        print(f"  ❌ weasyprint PDF timeout")
        return False

    sz_pdf = out_pdf.stat().st_size // 1024
    print(f"  ✅ {md.parent.name}: HTML+{sz_pdf}KB PDF")
    return True


def main():
    targets = sorted([p for p in PREPRINTS.iterdir() if p.is_dir() and (p / "manuscript.md").exists()])
    print(f"Rebuilding {len(targets)} preprints with wide-table-safe CSS\n")
    ok = 0
    for d in targets:
        md = d / "manuscript.md"
        print(f"[{d.name}]")
        if rebuild(md):
            ok += 1
    print(f"\n✅ {ok}/{len(targets)} rebuilt")
    return 0 if ok == len(targets) else 1


if __name__ == "__main__":
    sys.exit(main())
