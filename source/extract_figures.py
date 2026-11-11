#!/usr/bin/env python3
"""从原始材料(35 PDF + 13 HTML/MD)提取插图 → figures/<slug>/,供 build.py 展示。
PDF:pymupdf 抽取嵌入位图(过滤小图标,JPX 转 PNG)
HTML/MD:下载 <img src> / ![]() 指向的远程图片
"""
import hashlib
import json
import re
import shutil
import sys
import urllib.request
from pathlib import Path

import pymupdf

ROOT = Path(__file__).parent
MATERIALS = Path(os.environ.get("CS329Z_MATERIALS", ROOT.parent / "originals-parent"))  # 见 README:需指向材料目录
FIGURES = ROOT / "figures"

MIN_W, MIN_H = 160, 120      # 过滤小图标
MAX_FIGS = 25                # 每篇上限
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}


def extract_pdf(src: Path, out: Path) -> int:
    n = 0
    seen = set()
    doc = pymupdf.open(src)
    for page in doc:
        for img in page.get_images(full=True):
            xref = img[0]
            if xref in seen:
                continue
            seen.add(xref)
            try:
                pix = pymupdf.Pixmap(doc, xref)
                if pix.n - pix.alpha > 3:          # CMYK 等转 RGB
                    pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
                w, h = pix.width, pix.height
                if w < MIN_W or h < MIN_H:
                    continue
                # 重复图(logo 等)按像素哈希去重
                digest = hashlib.md5(pix.samples).hexdigest()
                if digest in seen:
                    continue
                seen.add(digest)
                n += 1
                pix.save(out / f"fig{n:02d}.png")
                if n >= MAX_FIGS:
                    return n
            except Exception:
                continue
    return n


def fetch(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=25) as r:
            data = r.read()
        if len(data) < 2500:                       # 过滤追踪像素/小图标
            return False
        ext = Path(url.split("?")[0]).suffix.lower()
        if ext not in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"):
            ext = ".png"
        dest = dest.with_suffix(ext)
        dest.write_bytes(data)
        return True
    except Exception:
        return False


def extract_web(src: Path, out: Path) -> int:
    from urllib.parse import unquote
    text = src.read_text(encoding="utf-8", errors="ignore")
    urls = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', text)
    urls += re.findall(r'!\[[^\]]*\]\(([^)\s]+)', text)
    n = 0
    seen = set()
    for u in urls:
        if n >= MAX_FIGS:
            break
        u = u.strip().replace("&amp;", "&")
        if u.startswith("/_next/image?url="):            # Next.js 图像代理 → 解出真实地址
            u = unquote(u.split("url=", 1)[1].split("&", 1)[0])
        elif not u.startswith("http"):
            continue
        if u in seen:
            continue
        seen.add(u)
        if fetch(u, out / f"fig{n + 1:02d}"):
            n += 1
    return n


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    manifest = json.loads((ROOT / "extracted" / "manifest.json").read_text(encoding="utf-8"))
    if FIGURES.exists():
        shutil.rmtree(FIGURES)
    FIGURES.mkdir(parents=True)
    report = []
    for m in manifest:
        slug, rel = m["slug"], m.get("file", "")
        if only and only not in slug:
            continue
        if not rel:
            continue
        src = MATERIALS / rel
        if not src.exists():
            continue
        out = FIGURES / slug
        out.mkdir(parents=True)
        try:
            n = extract_pdf(src, out) if src.suffix.lower() == ".pdf" else extract_web(src, out)
        except Exception as e:
            print(f"ERR {slug}: {e}")
            n = 0
        if n == 0:
            shutil.rmtree(out)
        report.append((slug[:44], src.suffix.lower(), n))
    for s, ext, n in report:
        print(f"{n:3d} 张  {ext:5s}  {s}")
    print(f"\n共 {sum(n for _, _, n in report)} 张 → {FIGURES}")


if __name__ == "__main__":
    main()
