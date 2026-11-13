#!/usr/bin/env python3
"""从 arXiv HTML 版(ar5iv)抓取论文全部图表(矢量 SVG + 位图通吃),带图注。
策略:标题搜 arXiv ID → 解析 ltx_figure → 下载 object/img 资产 → figures/<slug>/ + captions.json
比 PDF 位图提取更全(矢量图也能拿到)。失败的条目保留原位图提取结果。
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
FIGURES = ROOT / "figures"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
MAX_FIGS = 20


def get(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def title_of(slug):
    t = (CONTENT / f"{slug}.md").read_text(encoding="utf-8")
    m = re.search(r"^title:\s*(.+)$", t, re.M)
    if not m:
        return ""
    return m.group(1).strip().strip("\"'")


def arxiv_id_for(title):
    for q in (title, title.split(":")[0]):
        url = ("http://export.arxiv.org/api/query?search_query="
               + urllib.parse.quote(f'ti:"{q}"') + "&max_results=3")
        for attempt in range(3):
            try:
                xml = get(url).decode("utf-8", "ignore")
            except Exception:
                time.sleep(10); continue
            ids = re.findall(r"<id>http://arxiv.org/abs/([^<]+)</id>", xml)
            if ids:
                return ids[0].split("v")[0]
            time.sleep(8)                              # 可能被限流,稍候重试
    return None


def fetch_ar5iv(aid):
    """返回 [(图形URL, 图注)] 列表"""
    url = f"https://ar5iv.labs.arxiv.org/html/{aid}"
    h = get(url).decode("utf-8", "ignore")
    out = []
    for f in re.findall(r'<figure[^>]*class="ltx_figure"[^>]*>.*?</figure>', h, re.S):
        cap_m = re.search(r"<figcaption[^>]*>(.*?)</figcaption>", f, re.S)
        cap = re.sub(r"<[^>]+>", "", cap_m.group(1)).strip() if cap_m else ""
        cap = re.sub(r"\s+", " ", cap)[:160]
        srcs = re.findall(r'<object[^>]+type="image/svg\+xml"[^>]+data="([^"]+)"', f)
        srcs += re.findall(r'<object[^>]+data="([^"]+)"[^>]*type="image/svg\+xml"', f)
        srcs += re.findall(r'<img[^>]+src="([^"]+\.(?:png|jpe?g|gif))"', f)
        for s in srcs:
            s = s.replace("&amp;", "&")
            full = s if s.startswith("http") else f"https://ar5iv.labs.arxiv.org{s}"
            out.append((full, cap))
    return out


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    manifest = json.loads((ROOT / "extracted" / "manifest.json").read_text(encoding="utf-8"))
    stats = []
    for m in manifest:
        slug, rel = m["slug"], m.get("file", "")
        if only and only not in slug:
            continue
        if not rel or not rel.endswith(".pdf"):
            continue                                     # 只处理论文
        old = FIGURES / slug
        if (old / "captions.json").exists():
            continue                                    # 已用 arXiv 数据,跳过
        old_n = len([f for f in old.glob("*") if f.suffix != ".json"]) if old.exists() else 0
        title = title_of(slug)
        if not title:
            continue
        aid = arxiv_id_for(title)
        time.sleep(5)                                    # arXiv API 礼貌限速
        if not aid:
            stats.append((slug[:40], old_n, 0, "无 arXiv ID"))
            continue
        try:
            figs = fetch_ar5iv(aid)
        except Exception as e:
            stats.append((slug[:40], old_n, 0, f"抓取失败 {str(e)[:30]}"))
            continue
        if len(figs) < max(old_n, 3):
            stats.append((slug[:40], old_n, len(figs), "少于现有,保留位图"))
            continue
        new_dir = FIGURES / (slug + ".new")
        if new_dir.exists():
            import shutil
            shutil.rmtree(new_dir)
        new_dir.mkdir(parents=True)
        captions, n = {}, 0
        for url, cap in figs[:MAX_FIGS]:
            ext = Path(url.split("?")[0]).suffix.lower() or ".svg"
            if ext not in (".svg", ".png", ".jpg", ".jpeg", ".gif"):
                continue
            try:
                data = get(url)
            except Exception:
                continue
            if len(data) < 1500:
                continue
            n += 1
            name = f"fig{n:02d}{ext}"
            (new_dir / name).write_bytes(data)
            captions[name] = cap
        if n >= max(old_n, 3):
            import shutil
            if old.exists():
                shutil.rmtree(old)
            new_dir.rename(old)
            (old / "captions.json").write_text(json.dumps(captions, ensure_ascii=False), encoding="utf-8")
            stats.append((slug[:40], old_n, n, f"arXiv:{aid} ✓"))
        else:
            import shutil
            shutil.rmtree(new_dir)
            stats.append((slug[:40], old_n, n, "有效图不足,保留位图"))
    for s, old_n, new_n, note in stats:
        print(f"{old_n:3d}→{new_n:<3d} {note:24s} {s}")
    print(f"\n处理 {len(stats)} 篇")


if __name__ == "__main__":
    main()
