"""Compile remaining preprint markdowns to PDF (#13, #14 are v0.1, no PDF yet)."""
from __future__ import annotations
import sys, subprocess, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def compile_one(md_path: Path) -> bool:
    out_pdf = md_path.with_suffix(".pdf")
    out_html = md_path.with_suffix(".html")
    if out_pdf.exists():
        return True
    pandoc = shutil.which("pandoc")
    if pandoc is None:
        print(f"⚠️  pandoc not in PATH; skipping {md_path.name}")
        return False
    try:
        # HTML self-contained
        subprocess.run([
            pandoc, str(md_path),
            "-o", str(out_html),
            "--standalone",
            "--metadata", "title=Genesis_Medicine preprint",
            "--toc", "--toc-depth=3",
            "--mathjax",
        ], check=True, capture_output=True, timeout=120)
        print(f"  ✅ HTML: {out_html.relative_to(ROOT)}")
    except subprocess.CalledProcessError as e:
        print(f"  ❌ HTML failed: {e.stderr.decode()[:200]}")
        return False
    except subprocess.TimeoutExpired:
        return False

    # PDF (try wkhtmltopdf or fall back to weasyprint)
    for converter, args in [
        ("wkhtmltopdf", [str(out_html), str(out_pdf)]),
        ("weasyprint", [str(out_html), str(out_pdf)]),
    ]:
        bin_path = shutil.which(converter)
        if bin_path:
            try:
                subprocess.run([bin_path] + args, check=True, capture_output=True, timeout=120)
                print(f"  ✅ PDF via {converter}: {out_pdf.relative_to(ROOT)}")
                return True
            except subprocess.CalledProcessError:
                continue
    print(f"  ❌ PDF not generated (no wkhtmltopdf or weasyprint)")
    return False


def main():
    pre_dir = ROOT / "preprints"
    targets = ["13_piezo1_mlck_alopecia", "14_topical_pbpk_methodology"]
    for t in targets:
        md = pre_dir / t / "manuscript.md"
        if md.exists():
            print(f"\n[{t}]")
            compile_one(md)
        else:
            print(f"⚠️  {md} missing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
