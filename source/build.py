#!/usr/bin/env python3
"""Build the CS 329Z Chinese study site: content/*.md + originals -> site/ static HTML."""
import html
import json
import os
import re
import shutil
from pathlib import Path

import markdown as md_lib

ROOT = Path(__file__).parent
SITE = ROOT / "site"
# 课程 PDF/HTML 原件:默认取仓库根目录的 originals/,可用环境变量 CS329Z_MATERIALS 覆盖
_REPO_ORIGINALS = ROOT.parent / "originals"
SRC_MATERIALS = Path(os.environ.get("CS329Z_MATERIALS", _REPO_ORIGINALS if _REPO_ORIGINALS.exists() else "cs329z-materials"))
CONTENT = ROOT / "content"
WEEK_ORDER = [
    "week01_introduction", "week02a_llms_for_builders", "week02b_rag",
    "week03a_tool_use_mcp", "week03b_frameworks", "week04a_agent_patterns",
    "week04b_memory", "week05a_multi_agent", "week05b_optimization",
    "week06b_data", "week07a_data_selection", "week07b_evaluation",
    "week08a_llm_as_judge", "week08b_safety", "week09b_coding_agents",
    "week11a_proactive_agents", "week11b_open_problems",
]
WEEK_META = {
    "week01_introduction": ("第1周", "9/23", "课程导论"),
    "week02a_llms_for_builders": ("第2周", "9/28", "给开发者的 LLM"),
    "week02b_rag": ("第2周", "9/30", "检索增强生成 RAG"),
    "week03a_tool_use_mcp": ("第3周", "10/5", "工具调用与 MCP"),
    "week03b_frameworks": ("第3周", "10/7", "框架与编排"),
    "week04a_agent_patterns": ("第4周", "10/12", "Agent 设计模式"),
    "week04b_memory": ("第4周", "10/14", "Agent 记忆"),
    "week05a_multi_agent": ("第5周", "10/19", "多智能体系统"),
    "week05b_optimization": ("第5周", "10/21", "优化:测试时计算与提示优化"),
    "week06b_data": ("第6周", "10/28", "数据"),
    "week07a_data_selection": ("第7周", "11/2", "数据选择与质量"),
    "week07b_evaluation": ("第7周", "11/4", "评测基础"),
    "week08a_llm_as_judge": ("第8周", "11/9", "LLM-as-Judge"),
    "week08b_safety": ("第8周", "11/11", "安全与护栏"),
    "week09b_coding_agents": ("第9周", "11/18", "编程智能体"),
    "week11a_proactive_agents": ("第11周", "11/30", "主动式智能体"),
    "week11b_open_problems": ("第11周", "12/2", "开放问题"),
}
IMPORTANT_DATES = [
    ("第3周", "HW1《Build an Agentic Harness》发布", "10/5"),
    ("第3周", "Project Proposal 截止", "10/9"),
    ("第6周", "HW2《Evaluate an Agent》发布 · HW1 截止", "10/26 · 10/30"),
    ("第7周", "期中演示 · 期中报告截止", "11/4 · 11/6"),
    ("第8周", "论文视频截止", "11/13"),
    ("第9周", "HW2 截止", "11/20"),
    ("第11周", "互评截止(3 个视频)", "11/30"),
    ("期末周", "最终提交与系统演示", "12/7–11"),
]

BADGE_LABEL = {"must": "必读", "recommended": "推荐", "supplementary": "补充"}

# 官网(cs329z.stanford.edu)开课后放出的讲义;PDF 放在 slides/ 目录,存在即收录
LECTURES = [
    {"no": 1, "date": "9/23", "title_zh": "课程导论:什么是智能体系统?",
     "title": "Introduction — What Are Agentic Systems?", "file": "lecture01.pdf",
     "gdrive": "https://drive.google.com/file/d/1Wlf723d9-LBuTp56QYppaZwozOAetTsC/view"},
    {"no": 2, "date": "9/28", "title_zh": "给开发者的 LLM",
     "title": "LLMs for Builders", "file": "lecture02.pdf",
     "gdrive": "https://drive.google.com/file/d/1kekt_p0n-_Q4Y2dKYEkH87NEx6mr8nRE/view"},
]

def parse_front_matter(text: str):
    if not text.startswith("---"):
        return {}, text
    parts = text.split("\n---", 2)
    if len(parts) < 3:
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
        if not m:
            return {}, text
        fm_raw, body = m.group(1), m.group(2)
    else:
        fm_raw, body = parts[0][3:], parts[2].lstrip("\n")
    meta = {}
    for line in fm_raw.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, body

EN_BLOCK = re.compile(r"^:::[ \t]*en[ \t]*\n(.*?)\n:::[ \t]*$", re.S | re.M)
MATH_DISPLAY = re.compile(r"\$\$(.+?)\$\$", re.S)
MATH_INLINE = re.compile(r"(?<![\w$])\$([^$\n]{1,200}?)\$(?![\w$])")

def preprocess_bilingual(text: str) -> str:
    """Turn '::: en ... :::' blocks into styled raw-HTML English-original blocks,
    and shield LaTeX math from markdown mangling with placeholder tokens."""
    def repl(m):
        esc = html.escape(m.group(1).strip()).replace("\n", "<br>")
        return f'<div class="en-orig"><span class="en-tag">EN</span><p>{esc}</p></div>'
    text = EN_BLOCK.sub(repl, text)

    math_store = []
    def stash(match, display):
        math_store.append((display, match.group(0)))
        return f"MATHPLACEHOLDER{len(math_store)-1}ENDMATH"
    text = MATH_DISPLAY.sub(lambda m: stash(m, True), text)
    text = MATH_INLINE.sub(lambda m: stash(m, False), text)
    return text, math_store

def restore_math(html_out: str, math_store) -> str:
    for i, (display, raw) in enumerate(math_store):
        cls = "math-display" if display else "math-inline"
        tag = "div" if display else "span"
        esc = html.escape(raw)
        html_out = html_out.replace(f"MATHPLACEHOLDER{i}ENDMATH", f'<{tag} class="{cls}">{esc}</{tag}>')
    return html_out

PAIR_RE = re.compile(
    r'(<div class="en-orig"><span class="en-tag">EN</span><p>.*?</p></div>)\s*(<p>.*?</p>)', re.S)

def pair_bilingual(html_out: str) -> str:
    """Wrap each EN block + its Chinese paragraph into a side-by-side pair container."""
    return PAIR_RE.sub(lambda m: f'<div class="pair">{m.group(1)}{m.group(2)}</div>', html_out)

def render_markdown(body: str):
    md = md_lib.Markdown(extensions=["tables", "fenced_code", "sane_lists", "toc"],
                         extension_configs={"toc": {"toc_depth": "2-3"}})
    html_out = md.convert(body)
    return html_out, md.toc_tokens

def flatten_toc(tokens):
    out = []
    for t in tokens:
        out.append((t["level"], t["name"], t["id"]))
        out.extend(flatten_toc(t.get("children", [])))
    return out

def toc_html(tokens):
    def render(items):
        h = "<ul>"
        for t in items:
            kids = t.get("children", [])
            cls = ' class="has-sub"' if kids else ""
            h += f'<li{cls}><a href="#{t["id"]}">{html.escape(t["name"])}</a>'
            if kids:
                h += render(kids)
            h += "</li>"
        return h + "</ul>"
    return render(tokens) if tokens else ""

def page(title: str, body: str, extra_head: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="../assets/style.css">
{extra_head}
</head>
<body>
{body}
</body>
</html>"""

CATEGORIES = [
    ("导论与背景", ["week01_introduction"], "课程定位、复合 AI 系统与智能体设计模式总览"),
    ("LLM 与上下文工程", ["week02a_llms_for_builders"], "给开发者的 LLM 使用之道与上下文工程"),
    ("检索增强生成", ["week02b_rag"], "RAG 范式与稠密段落检索"),
    ("工具与框架", ["week03a_tool_use_mcp", "week03b_frameworks"], "MCP 协议规范与 DSPy 编程模型"),
    ("智能体模式与记忆", ["week04a_agent_patterns", "week04b_memory"], "ReAct 范式、MemGPT 与记忆架构"),
    ("多智能体系统", ["week05a_multi_agent"], "协作框架、失败分析与动态团队"),
    ("优化", ["week05b_optimization"], "测试时计算扩展与提示优化"),
    ("数据工程", ["week06b_data", "week07a_data_selection"], "数据飞轮、标注合成与数据选择"),
    ("评测", ["week07b_evaluation", "week08a_llm_as_judge"], "基准设计原则与 LLM-as-Judge"),
    ("安全与护栏", ["week08b_safety"], "隐私、提示注入与攻防搜索"),
    ("编程智能体", ["week09b_coding_agents"], "SWE 基准、ACI 接口与智能体平台"),
    ("前沿与开放问题", ["week11a_proactive_agents", "week11b_open_problems"], "主动式智能体与真实世界环境基准"),
]

def github_stars():
    try:
        import urllib.request
        with urllib.request.urlopen("https://api.github.com/repos/athlonk8/cs329z", timeout=6) as r:
            return json.load(r).get("stargazers_count")
    except Exception:
        return None

def topbar(prefix: str = "../") -> str:
    return f"""<header class="topbar">
  <div class="topbar-inner">
    <a class="brand" href="{prefix}index.html"><span class="brand-mark">CS</span>329Z<span class="brand-sub">中文学习站</span></a>
    <nav class="topnav">
      <a href="{prefix}materials.html">材料总目录</a>
      <a href="{prefix}index.html#syllabus">课程表</a>
      <a href="{prefix}index.html#lectures">课程讲义</a>
      <a href="{prefix}index.html#dates">重要日期</a>
      <a href="{prefix}index.html#about">关于本站</a>
    </nav>
    <div class="searchbox"><input id="search-input" type="search" placeholder="搜索材料 / 主题…" autocomplete="off"><div id="search-results" class="search-results" hidden></div></div>
  </div>
</header>"""

def main():
    manifest = json.loads((ROOT / "extracted" / "manifest.json").read_text(encoding="utf-8"))
    by_slug = {m["slug"]: m for m in manifest}

    # ---- load content ----
    entries = []
    missing, broken = [], []
    for m in manifest:
        bm = CONTENT / "bilingual" / f"{m['slug']}.md"
        cm = CONTENT / f"{m['slug']}.md"
        is_bilingual = bm.exists()
        src = bm if is_bilingual else cm
        if not src.exists():
            missing.append(m["slug"])
            continue
        meta, body = parse_front_matter(src.read_text(encoding="utf-8"))
        for field in ("title", "title_zh", "authors", "venue", "kind", "importance", "summary"):
            if not meta.get(field):
                broken.append((m["slug"], field))
        if len(body) < 800:
            broken.append((m["slug"], f"body_too_short:{len(body)}"))
        body, math_store = preprocess_bilingual(body)
        body_html, toc_tokens = render_markdown(body)
        body_html = restore_math(body_html, math_store)
        body_html = pair_bilingual(body_html)
        week_no, date, topic = WEEK_META[m["week"]]
        entries.append({
            **m, "meta": meta, "body_html": body_html, "bilingual": is_bilingual,
            "toc": toc_html(toc_tokens), "week_no": week_no, "date": date, "topic": topic,
        })
    if missing or broken:
        print("MISSING:", missing)
        print("BROKEN:", broken)

    # ---- extras: 背景阅读等特设页面 ----
    extras_dir = CONTENT / "extras"
    if extras_dir.exists():
        for cm in sorted(extras_dir.glob("*.md")):
            meta, body = parse_front_matter(cm.read_text(encoding="utf-8"))
            for field in ("title", "title_zh", "authors", "venue", "kind", "importance", "summary"):
                if not meta.get(field):
                    broken.append((cm.stem, field))
            body_html, toc_tokens = render_markdown(body)
            entries.append({
                "week": "extras", "week_label": "背景阅读", "week_topic": "课程背景",
                "file": "", "slug": cm.stem, "kind": meta.get("kind", "blog"),
                "meta": meta, "body_html": body_html, "toc": toc_html(toc_tokens),
                "week_no": "背景阅读", "date": "✦", "topic": "为什么值得学这门课",
            })

    order = {w: i for i, w in enumerate(WEEK_ORDER)}
    entries.sort(key=lambda e: (order.get(e["week"], 99), e["file"]))

    # ---- fresh output (preserve repo meta + project docs + source mirror) ----
    PRESERVE = {".git", "README.md", ".github", "CNAME", "LICENSE",
                "CONTRIBUTING.md", "docs", "source", ".gitignore",
                "requirements.txt"}
    if SITE.exists():
        for child in SITE.iterdir():
            if child.name in PRESERVE:
                continue
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    else:
        SITE.mkdir(parents=True)
    (SITE / "reading").mkdir(parents=True)
    (SITE / "assets").mkdir(parents=True)
    shutil.copy(ROOT / "assets" / "style.css", SITE / "assets" / "style.css")
    shutil.copy(ROOT / "assets" / "site.js", SITE / "assets" / "site.js")
    if (SITE / "assets" / "katex").exists():
        shutil.rmtree(SITE / "assets" / "katex")
    shutil.copytree(ROOT / "assets" / "katex", SITE / "assets" / "katex")
    shutil.copytree(SRC_MATERIALS, SITE / "originals",
                    ignore=shutil.ignore_patterns("README.md", ".DS_Store"))
    lectures = [l for l in LECTURES if (ROOT / "slides" / l["file"]).exists()]
    if lectures:
        (SITE / "slides").mkdir(exist_ok=True)
        for l in lectures:
            shutil.copy2(ROOT / "slides" / l["file"], SITE / "slides" / l["file"])

    # ---- reading pages ----
    stars = github_stars()
    star_text = f'(<b>{stars}</b> stars)' if stars else ''
    banner_stars = f' · {stars}' if stars else ''
    search_index = []
    for i, e in enumerate(entries):
        prev_e = entries[i - 1] if i > 0 else None
        next_e = entries[i + 1] if i < len(entries) - 1 else None
        kind_label = "全译对照" if e.get("bilingual") else ("全文中译" if e["meta"].get("kind") == "blog" else "论文精读")
        imp = e["meta"].get("importance", "recommended")
        orig_rel = f"../originals/{e['file']}" if e["file"] else ""
        orig_html = html.escape(orig_rel) if orig_rel else ""
        badge = f'<span class="badge badge-{imp}">{BADGE_LABEL.get(imp, imp)}</span>'
        kbadge = f'<span class="badge badge-kind">{kind_label}</span>'
        nav = '<nav class="pager">'
        nav += (f'<a class="pager-prev" href="{prev_e["slug"]}.html"><span>上一篇</span>{html.escape(prev_e["meta"]["title_zh"])}</a>'
                if prev_e else "<span></span>")
        nav += (f'<a class="pager-next" href="{next_e["slug"]}.html"><span>下一篇</span>{html.escape(next_e["meta"]["title_zh"])}</a>'
                if next_e else "<span></span>")
        nav += "</nav>"
        meta_line = " · ".join(x for x in [e["meta"].get("authors"), e["meta"].get("venue")] if x)
        orig_anchor = (f'<a class="orig-link" href="{orig_html}" target="_blank" rel="noopener">查看原文({e["kind"].upper()}) ↗</a>' if orig_html else "")
        star_line = f'觉得有帮助?欢迎在 GitHub 给本项目一个 ⭐ <a href="https://github.com/athlonk8/cs329z" target="_blank" rel="noopener">athlonk8/cs329z</a>{star_text}'
        body = f"""{topbar()}
<div class="read-layout">
  <aside class="read-toc"><div class="read-toc-title">本页目录</div>{e['toc']}</aside>
  <main class="read-main">
      <link rel="stylesheet" href="../assets/katex/katex.min.css">
      <script defer src="../assets/katex/katex.min.js"></script>
      <script defer src="../assets/katex/contrib/auto-render.min.js" onload="renderMathInElement(document.querySelector('.markdown-body'),{{delimiters:[{{left:'$$',right:'$$',display:true}},{{left:'$',right:'$',display:false}}],ignoredTags:['script','noscript','style','textarea','pre','code']}});"></script>
    <div class="crumb"><a href="../index.html">首页</a> / <a href="../index.html#week-{e['week']}">{e['week_no']} · {html.escape(e['topic'])}</a></div>
    <article class="read-article">
      <h1 class="read-title">{html.escape(e['meta']['title_zh'])}</h1>
      <p class="read-title-en">{html.escape(e['meta']['title'])}</p>
      <p class="read-meta">{html.escape(meta_line)}</p>
      <p class="read-badges">{badge}{kbadge}<button class="lang-toggle" id="lang-toggle" type="button">仅看中文</button>{orig_anchor}</p>
      <div class="markdown-body">
{e['body_html']}
      </div>
    </article>
    {nav}
    <div class="read-star">📖 {star_line}</div>
  </main>
</div>
<script src="../assets/site.js"></script>"""
        (SITE / "reading" / f"{e['slug']}.html").write_text(
            page(f"{e['meta']['title_zh']} · CS 329Z 中文学习站", body),
            encoding="utf-8")
        search_index.append({
            "slug": e["slug"], "title_zh": e["meta"]["title_zh"], "title": e["meta"]["title"],
            "summary": e["meta"].get("summary", ""), "tags": e["meta"].get("tags", ""),
            "week": f'{e["week_no"]}·{e["topic"]}', "importance": imp, "kind": kind_label,
        })

    (SITE / "assets" / "search.json").write_text(json.dumps(search_index, ensure_ascii=False), encoding="utf-8")

    # ---- index page(按主题大类归类) ----
    grouped = {}
    for e in entries:
        grouped.setdefault(e["week"], []).append(e)

    def topic_section(w, ws):
        week_no, date, topic = WEEK_META.get(w, ("背景阅读", "✦", "为什么值得学这门课"))
        rows = []
        for e in ws:
            imp = e["meta"].get("importance", "recommended")
            kind_label = "全译对照" if e.get("bilingual") else ("全文中译" if e["meta"].get("kind") == "blog" else "论文精读")
            rows.append(f"""        <li class="mat-row">
          <a class="mat-link" href="reading/{e['slug']}.html">
            <span class="badge badge-{imp}">{BADGE_LABEL.get(imp, imp)}</span>
            <span class="badge badge-kind">{kind_label}</span>
            <span class="mat-title">{html.escape(e['meta']['title_zh'])}</span>
          </a>
          <div class="mat-sub">{html.escape(e['meta']['title'])}</div>
          <div class="mat-summary">{html.escape(e['meta'].get('summary', ''))}</div>
        </li>""")
        return f"""    <section class="topic" id="week-{w}">
      <div class="topic-head">
        <div class="topic-date">{date}</div>
        <h2>{html.escape(topic)} <span class="topic-week">{week_no}</span></h2>
        <div class="topic-count">{len(ws)} 篇材料</div>
      </div>
      <ul class="mat-list">
{chr(10).join(rows)}
      </ul>
    </section>"""

    weeks_html, chips = [], []
    for ci, (cat_name, cat_weeks, cat_desc) in enumerate(CATEGORIES, 1):
        ws_all = [e for w in cat_weeks for e in grouped.get(w, [])]
        if not ws_all:
            continue
        chips.append(f'<a href="#cat-{ci}">{cat_name}</a>')
        inner = chr(10).join(topic_section(w, grouped[w]) for w in cat_weeks if grouped.get(w))
        weeks_html.append(f"""  <section class="cat-section" id="cat-{ci}">
    <div class="cat-head">
      <div class="cat-no">{ci:02d}</div>
      <div><h2 class="cat-title">{cat_name}</h2><p class="cat-desc">{cat_desc} · 共 {len(ws_all)} 篇</p></div>
    </div>
{inner}
  </section>""")
    if grouped.get("extras"):
        weeks_html.append(topic_section("extras", grouped["extras"]))
    chips_html = chr(10).join(f'      {c}' for c in chips)

    n_must = sum(1 for e in entries if e["meta"].get("importance") == "must")
    n_blogs = sum(1 for e in entries if e["meta"].get("kind") == "blog")
    n_papers = len(entries) - n_blogs
    n_bi = sum(1 for e in entries if e.get("bilingual"))
    dates_rows = "\n".join(
        f"""        <tr><td class="d-week">{w}</td><td>{html.escape(item)}</td><td class="d-date">{d}</td></tr>"""
        for w, item, d in IMPORTANT_DATES)
    lectures_rows = "\n".join(
        f"""        <tr>
          <td class="d-week">Lecture {l['no']}</td>
          <td>{html.escape(l['title_zh'])}<div class="mt-sub">{html.escape(l['title'])}</div></td>
          <td class="d-date">{l['date']}</td>
          <td class="lecture-links"><a class="slide-dl" href="slides/{l['file']}" target="_blank" rel="noopener">在线阅读 / 下载 PDF ↗</a><div class="mt-sub"><a href="{l['gdrive']}" target="_blank" rel="noopener">官网原始链接</a></div></td>
        </tr>"""
        for l in lectures)

    index_body = f"""{topbar("")}
<div class="hero">
  <div class="hero-inner">
    <p class="hero-kicker">Stanford CS 329Z · Fall 2026 · https://cs329z.stanford.edu/</p>
    <h1>Engineering AI Agents<br><span class="hero-cn">AI 智能体工程 · 中文学习站</span></h1>
    <p class="hero-desc">本站收录该课程全部 <b>{len(entries)}</b> 篇阅读材料({n_papers} 篇论文 + {n_blogs} 篇博客/规范)的中文版:论文提供逐章<b>精读笔记</b>(摘要全译 + 方法与实验详解),博客/规范提供<b>全文中译</b>,全部支持在线阅读,并可跳转原文。</p>
    <div class="hero-stats"><div class="stat"><b>12</b><span>主题大类</span></div><div class="stat"><b>{len(entries)}</b><span>篇材料</span></div><div class="stat"><b>{n_must}</b><span>篇必读</span></div><div class="stat"><b>100%</b><span>中文覆盖</span></div></div>
  </div>
</div>
<div class="star-banner">
  <div class="star-banner-text">
    <b>关于本站</b>:这是 Stanford CS 329Z《Engineering AI Agents》(2026 秋)全部 <b>49 篇</b>阅读材料的中文学习库——<b>35 篇论文已完成逐段中英对照全译</b>(2,035 个对照段、44.9 万中文字,宽屏下英文左栏/中文右栏),15 篇博客与规范全文中译,全部 PDF 原件在线可读;官网已放出前 {len(lectures)} 讲讲义,本站同步收录。完全免费、无广告、开源。
  </div>
  <a class="star-btn" href="https://github.com/athlonk8/cs329z" target="_blank" rel="noopener">⭐ 在 GitHub 点个 Star{banner_stars}</a>
</div>
<nav class="cat-nav">
  <div class="cat-nav-inner">
{chips_html}
  </div>
</nav>
<main class="index-main">
  <h2 class="sec-title" id="syllabus">课程表与阅读材料 <a class="all-mats" href="materials.html">材料总目录 →</a></h2>
  <div class="bi-progress">📖 论文逐段全译对照进度:<b>{n_bi} / {n_papers}</b> 篇已完成——完成篇带 <span class="badge badge-kind">全译对照</span> 徽章(正文每段英文原文+中文全译,页内可切换仅看中文);其余论文暂为 <span class="badge badge-kind">论文精读</span>(逐章精读笔记),博客类为 <span class="badge badge-kind">全文中译</span>。全译对照持续更新中。</div>
{chr(10).join(weeks_html)}

  <section class="dates lectures" id="lectures">
    <h2 class="sec-title">课程讲义 · Lecture Slides</h2>
    <div class="lecture-note">课程 9/23 开课后,官网随进度放出各讲幻灯片,本站同步收录 PDF 原件——已收录 <b>{len(lectures)} 讲</b>(Lecture 3 起待官网发布后跟进)。视频录像暂未公开(仅斯坦福内部 Canvas 可见)。</div>
    <table class="dates-table lecture-table">
      <tr><th>讲次</th><th>主题</th><th>日期</th><th>讲义</th></tr>
{lectures_rows}
    </table>
  </section>

  <section class="dates" id="dates">
    <h2 class="sec-title">课程重要日期</h2>
    <table class="dates-table">
      <tr><th>周次</th><th>事项</th><th>日期</th></tr>
{dates_rows}
    </table>
  </section>

  <section class="about" id="about">
    <h2 class="sec-title">关于本站</h2>
    <div class="markdown-body">
      <p><b>这是什么</b>:一个把斯坦福 CS 329Z《Engineering AI Agents》课程全部阅读材料翻译成中文的免费学习网站。课程是 AI 智能体工程方向最系统的研究生课之一——从 ReAct、RAG、MCP、记忆系统、多智能体,到测试时计算、数据工程、评测、安全与编程智能体,恰好是当前工业界最抢手的能力栈。</p>
      <p><b>怎么用</b>:按首页 12 个主题大类或「材料总目录」筛选浏览;🔴必读 = 该讲核心;论文页宽屏下自动<strong>英文原文/中文全译左右对照</strong>,点页面顶部按钮可只看中文;每页可跳转 PDF 原文核对;顶部搜索框支持全文检索。</p>
      <p><b>怎么读论文</b>:先看「导读」了解文章在课程中的位置 → 中英对照精读正文 → 「要点速览」巩固。公式均已排版,表格数据与原文逐项核对。</p>
      <p><b>支持本项目</b>:全部译文与网站代码开源于 <a href="https://github.com/athlonk8/cs329z" target="_blank" rel="noopener">GitHub · athlonk8/cs329z</a>{star_text}。如果这个站帮你省下了啃英文论文的时间,<b>欢迎去点一个 ⭐ Star</b>——这是对几十万字翻译工作最好的肯定,也会让更多需要的人看到它。欢迎 Issue 提错译与建议。</p>
      <ul>
        <li><b>翻译策略</b>:论文正文(摘要至结论,多数含实质附录)逐段英文原文+中文全译;参考文献列表不译;博客服从原文结构全文中译。</li>
        <li><b>重要度标记</b>:🔴 必读 = 该讲核心;🟡 推荐 = 强烈建议;⚪ 补充 = 拓展阅读(编者判断,仅供参考)。</li>
        <li><b>时效说明</b>:阅读材料下载于 2026-09-14(开课前);开课后官网放出的课程讲义(slides)已同步收录(见「课程讲义」),作业待官方发布后跟进。</li>
        <li><b>版权</b>:原文版权归原作者及机构所有,AI 辅助译文仅供个人学习研究使用,请勿商用。</li>
      </ul>
    </div>
  </section>
</main>
<footer class="footer">CS 329Z · Engineering AI Agents 中文学习站 · 译文仅供个人学习使用 · 原文版权归原作者所有</footer>
<script src="assets/site.js"></script>"""
    (SITE / "index.html").write_text(page("CS 329Z · Engineering AI Agents 中文学习站", index_body), encoding="utf-8")

    # ---- materials page(材料总目录) ----
    cat_blocks = []
    for ci, (cat_name, cat_weeks, cat_desc) in enumerate(CATEGORIES, 1):
        ws_all = [e for w in cat_weeks for e in grouped.get(w, [])]
        if not ws_all:
            continue
        rows = []
        for e in ws_all:
            imp = e["meta"].get("importance", "recommended")
            kind_label = "全译对照" if e.get("bilingual") else ("全文中译" if e["meta"].get("kind") == "blog" else "论文精读")
            rows.append(f"""      <tr data-row data-kind="{kind_label}" data-imp="{BADGE_LABEL.get(imp, imp)}">
        <td><a href="reading/{e['slug']}.html">{html.escape(e['meta']['title_zh'])}</a><div class="mt-sub">{html.escape(e['meta']['title'])}</div></td>
        <td><span class="badge badge-kind">{kind_label}</span></td>
        <td><span class="badge badge-{imp}">{BADGE_LABEL.get(imp, imp)}</span></td>
        <td class="mt-week">{e['week_no']} · {html.escape(e['topic'])}</td>
      </tr>""")
        cat_blocks.append(f"""  <section class="mat-cat" data-group data-kind="" >
    <h2 class="mat-cat-title"><span class="cat-no">{ci:02d}</span>{cat_name} <span class="mat-cat-count">{len(ws_all)} 篇</span></h2>
    <table class="mat-table">
      <thead><tr><th>材料</th><th>类型</th><th>重要度</th><th>讲次</th></tr></thead>
      <tbody>
{chr(10).join(rows)}
      </tbody>
    </table>
  </section>""")

    materials_body = f"""{topbar("")}
<div class="hero hero-compact">
  <div class="hero-inner">
    <p class="hero-kicker">CS 329Z 中文学习站</p>
    <h1>材料总目录 <span class="hero-cn">按主题大类归类 · 全部 {len(entries)} 篇</span></h1>
    <p class="hero-desc">按 12 个主题大类浏览全部阅读材料;可用下方按钮按<b>翻译类型</b>与<b>重要度</b>筛选。<a href="index.html">← 返回课程主页</a></p>
  </div>
</div>
<div class="filter-bar" id="filter-bar">
  <div class="fb-group"><b>类型</b>
    <button data-f="kind" data-v="all" class="on">全部</button>
    <button data-f="kind" data-v="全译对照">全译对照</button>
    <button data-f="kind" data-v="论文精读">论文精读</button>
    <button data-f="kind" data-v="全文中译">全文中译</button>
  </div>
  <div class="fb-group"><b>重要度</b>
    <button data-f="imp" data-v="all" class="on">全部</button>
    <button data-f="imp" data-v="必读">必读</button>
    <button data-f="imp" data-v="推荐">推荐</button>
    <button data-f="imp" data-v="补充">补充</button>
  </div>
</div>
<main class="materials-main">
{chr(10).join(cat_blocks)}
  <section class="mat-cat">
    <h2 class="mat-cat-title"><span class="cat-no">✦</span>背景阅读</h2>
    <table class="mat-table">
      <thead><tr><th>材料</th><th>类型</th><th>重要度</th><th>讲次</th></tr></thead>
      <tbody>
        <tr data-row data-kind="全文中译" data-imp="推荐"><td><a href="reading/extra_cs329a_article.html">年薪 85 万美元的绝活,斯坦福免费公开了——为什么值得学这门课</a></td><td><span class="badge badge-kind">全文中译</span></td><td><span class="badge badge-recommended">推荐</span></td><td class="mt-week">背景阅读</td></tr>
      </tbody>
    </table>
  </section>
</main>
<script src="assets/site.js"></script>"""
    (SITE / "materials.html").write_text(page("材料总目录 · CS 329Z 中文学习站", materials_body), encoding="utf-8")

    print(f"Built {len(entries)} reading pages -> {SITE}")
    print(f"missing={len(missing)} broken={len(broken)}")

if __name__ == "__main__":
    main()
