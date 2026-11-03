#!/usr/bin/env python3
"""把 docs/画图指南.md 生成为单页 HTML：左侧目录、搜索、每种图一个条目（说明、示例图、可复制的源码）。

用法:
  build_guide_html.py [--out DIR]

  --out   输出目录（默认在系统临时目录新建一个）。生成 DIR/index.html，并把指南引用到的图片
          复制到 DIR/assets、DIR/examples，页面里用相对路径引用，整个目录可直接发布。

样式和脚本取自同目录的 guide_html.css、guide_html.js。
"""
import html
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import palette as P  # noqa: E402

DOCS = os.path.join(ROOT, 'docs')
GUIDE = os.path.join(DOCS, '画图指南.md')
CAT_COLORS = ['#5383FF', '#0FB4A9', '#F29929', '#A771FF', '#FF8A58', '#EA629C', '#3D7A9E', '#2B59C3']
FACT_KEYS = ('什么时候用', '别用', '推荐工具')


# ---------- 行内与块级 Markdown ----------
def inline(s):
    """行内 Markdown → HTML：先转义，再处理代码、加粗、链接。"""
    out, parts = [], re.split(r'(`[^`]*`)', s)
    for p in parts:
        if p.startswith('`') and p.endswith('`') and len(p) >= 2:
            out.append('<code>' + html.escape(p[1:-1]) + '</code>')
            continue
        p = html.escape(p, quote=False)
        p = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', p)
        p = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', p)
        out.append(p)
    return ''.join(out)


def table(lines):
    rows = [[c.strip() for c in ln.strip().strip('|').split('|')] for ln in lines if not re.match(r'^\|?\s*:?-{2,}', ln)]
    head, body = rows[0], rows[1:]
    h = '<div class="table-wrap"><table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in head) + '</tr></thead><tbody>'
    for r in body:
        h += '<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>'
    return h + '</tbody></table></div>'


def list_html(items):
    """items: [(缩进, 文本)]，缩进 0 / 2，输出嵌套 ul。"""
    h, depth = '', 0
    for ind, text in items:
        level = 1 if ind >= 2 else 0
        if depth == 0 or level + 1 > depth:
            h += '<ul><li>' + inline(text)
            depth += 1
        elif level + 1 < depth:
            h += '</li></ul></li><li>' + inline(text)
            depth -= 1
        else:
            h += '</li><li>' + inline(text)
    return h + '</li></ul>' * depth


def blocks(lines):
    """通用块级转换：标题、段落、列表、表格、引用、围栏代码。"""
    out, i, n = [], 0, len(lines)
    while i < n:
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue
        if ln.startswith('```'):
            lang, j = ln[3:].strip(), i + 1
            while j < n and not lines[j].startswith('```'):
                j += 1
            code = html.escape('\n'.join(lines[i + 1:j]))
            out.append(f'<div class="code"><button class="copy" type="button">复制</button><pre><code class="language-{lang or "text"}">{code}</code></pre></div>')
            i = j + 1
            continue
        m = re.match(r'^(#{2,4})\s+(.*)', ln)
        if m:
            out.append(f'<h{len(m.group(1))}>{inline(m.group(2))}</h{len(m.group(1))}>')
            i += 1
            continue
        if ln.startswith('|'):
            j = i
            while j < n and lines[j].startswith('|'):
                j += 1
            out.append(table(lines[i:j]))
            i = j
            continue
        if ln.startswith('> '):
            j = i
            while j < n and lines[j].startswith('> '):
                j += 1
            out.append('<blockquote><p>' + inline(' '.join(x[2:] for x in lines[i:j])) + '</p></blockquote>')
            i = j
            continue
        if re.match(r'^\s*(-|\d+\.)\s', ln):
            items, j = [], i
            while j < n and re.match(r'^\s*(-|\d+\.)\s', lines[j]):
                ind = len(lines[j]) - len(lines[j].lstrip())
                items.append((ind, re.sub(r'^\s*(-|\d+\.)\s+', '', lines[j])))
                j += 1
            out.append(list_html(items))
            i = j
            continue
        if ln.startswith('<'):  # 原样保留的 HTML（锚点等）
            i += 1
            continue
        j = i
        while j < n and lines[j].strip() and not re.match(r'^(#{2,4}\s|\||> |```|\s*-\s|<)', lines[j]):
            j += 1
        out.append('<p>' + inline(' '.join(x.strip() for x in lines[i:j])) + '</p>')
        i = max(j, i + 1)
    return '\n'.join(out)


# ---------- 指南结构 ----------
def split_sections(lines):
    """按 <a id="..."> 锚点切块，返回 [(id, 行列表)]；锚点前的内容 id 为 None。"""
    parts, cur, buf = [], None, []
    for ln in lines:
        m = re.match(r'^<a id="([^"]+)"></a>\s*$', ln)
        if m:
            parts.append((cur, buf))
            cur, buf = m.group(1), []
        else:
            buf.append(ln)
    parts.append((cur, buf))
    return parts


def parse_type(tid, lines):
    """一种图的条目：标题、一句话、事实（dl）、列表段（h4 + ul）、图和源码；其余段落按通用块转换。"""
    t = {'id': tid, 'name': '', 'code': '', 'what': '', 'facts': [], 'lists': [], 'figs': [], 'notes': []}
    buf = []

    def flush():
        if not any(x.strip() for x in buf):
            buf.clear()
            return
        chunk = list(buf)
        buf.clear()
        if not t['what']:
            k = 0
            while not chunk[k].strip():
                k += 1
            if not re.match(r'^(#|\||> |```|\s*-\s|<)', chunk[k]):
                j = k
                while j < len(chunk) and chunk[j].strip():
                    j += 1
                t['what'] = ' '.join(x.strip() for x in chunk[k:j])
                chunk = chunk[j:]
        h = blocks(chunk)
        if h:
            t['notes'].append(h)

    i, n = 0, len(lines)
    while i < n:
        ln = lines[i]
        m = re.match(r'^###\s+(.*?)\s+·\s+`([^`]+)`\s*$', ln)
        if m:
            flush()
            t['name'], t['code'] = m.group(1), m.group(2)
            i += 1
            continue
        m = re.match(r'^- \*\*(.+?)\*\*[：:]\s*(.*)$', ln)
        if m:
            flush()
            key, val = m.group(1), m.group(2)
            kids, j = [], i + 1
            while j < n and lines[j].startswith('  - '):
                kids.append(lines[j][4:])
                j += 1
            if kids:
                t['lists'].append((key, kids, val))
            else:
                t['facts'].append((key, val))
            i = j
            continue
        m = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)', ln)
        if m:
            flush()
            t['figs'].append({'kind': 'img', 'alt': m.group(1), 'src': m.group(2), 'caption': ''})
            i += 1
            continue
        if ln.startswith('> ') and t['figs'] and t['figs'][-1]['kind'] == 'img' and not t['figs'][-1]['caption'] \
                and not any(x.strip() for x in buf):
            t['figs'][-1]['caption'] = ln[2:]
            i += 1
            continue
        if ln.startswith('<details>'):
            flush()
            j = i + 1
            summ = re.search(r'<summary>(.*?)</summary>', lines[j]).group(1)
            while not lines[j].startswith('```'):
                j += 1
            lang, k = lines[j][3:].strip(), j + 1
            while not lines[k].startswith('```'):
                k += 1
            t['figs'].append({'kind': 'src', 'summary': summ, 'lang': lang, 'code': '\n'.join(lines[j + 1:k])})
            while not lines[k].startswith('</details>'):
                k += 1
            i = k + 1
            continue
        if ln.startswith('```'):  # 围栏代码整块进缓冲，里面的行不做特殊识别
            j = i + 1
            while j < n and not lines[j].startswith('```'):
                j += 1
            buf.extend(lines[i:j + 1])
            i = j + 1
            continue
        buf.append(ln)
        i += 1
    flush()
    return t


def render_type(t, cat_color, copy_img):
    search = ' '.join([t['name'], t['code'], t['what']] + [v for _, v in t['facts']]).lower()
    h = [f'<article class="type" id="{t["id"]}" data-search="{html.escape(search)}">',
         f'<header class="type-head"><h3>{inline(t["name"])}</h3><code class="tid">{html.escape(t["code"])}</code></header>',
         f'<p class="what">{inline(t["what"])}</p><div class="type-grid"><div class="type-text">']
    if t['facts']:
        h.append('<dl class="facts">' + ''.join(f'<div><dt>{inline(k)}</dt><dd>{inline(v)}</dd></div>' for k, v in t['facts']) + '</dl>')
    for key, kids, lead in t['lists']:
        h.append(f'<h4>{inline(key)}</h4>' + (f'<p>{inline(lead)}</p>' if lead else '') + '<ul>' + ''.join(f'<li>{inline(k)}</li>' for k in kids) + '</ul>')
    h.extend(t['notes'])
    h.append('</div><div class="type-fig">')
    for f in t['figs']:
        if f['kind'] == 'img':
            src = copy_img(f['src'])
            cap = f'<figcaption>{inline(f["caption"])}</figcaption>' if f['caption'] else ''
            h.append(f'<figure class="canvas" style="--canvas:#FFFFFF"><div class="canvas-inner"><img src="{src}" alt="{html.escape(f["alt"])}" loading="lazy"></div>{cap}</figure>')
        else:
            fn = re.search(r'[（(]([^）)]*)[）)]', f['summary'])
            fn = os.path.basename(fn.group(1)) if fn else ''
            h.append(f'<details class="src"><summary>示例源码 <span class="fn">{html.escape(fn)}</span></summary>'
                     f'<div class="code"><button class="copy" type="button">复制</button><pre><code class="language-{f["lang"] or "text"}">{html.escape(f["code"])}</code></pre></div></details>')
    h.append('</div></div></article>')
    return '\n'.join(h)


def build(out_dir):
    with open(GUIDE, encoding='utf-8') as fh:
        lines = fh.read().split('\n')
    css = open(os.path.join(HERE, 'guide_html.css'), encoding='utf-8').read()
    js = open(os.path.join(HERE, 'guide_html.js'), encoding='utf-8').read()
    copied = []

    def copy_img(rel):
        """把 docs 相对路径的图片复制到输出目录，返回页面里用的相对路径。"""
        src = os.path.normpath(os.path.join(DOCS, rel))
        dst_rel = os.path.relpath(src, ROOT) if rel.startswith('../') else rel
        dst = os.path.join(out_dir, dst_rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
        copied.append(dst_rel)
        return dst_rel

    parts = split_sections(lines)
    head = parts[0][1]
    head = head[:next((k for k, x in enumerate(head) if x.startswith('## ')), len(head))]  # 只取「目录」之前的开头说明
    title = next(x[2:] for x in head if x.startswith('# '))
    lead = next(x for x in head if x.strip() and not x.startswith('#') and not x.startswith('- '))
    notes = [x[2:] for x in head if x.startswith('- ') and 'claude.ai/artifact' not in x]

    cats, quick, topic = [], '', None
    for sid, body in parts[1:]:
        if sid == 'quick':
            quick = blocks(body)
        elif sid.startswith('cat-'):
            m = next(re.match(r'^##\s+(\d+)\.\s+(.*)', x) for x in body if x.startswith('## '))
            cats.append({'id': sid, 'no': m.group(1), 'name': m.group(2), 'intro': blocks([x for x in body if not x.startswith('## ')]), 'types': []})
        elif sid == 'drawio-examples':
            topic = body
        else:
            cats[-1]['types'].append(parse_type(sid, body))
    for i, c in enumerate(cats):
        c['color'] = CAT_COLORS[i % len(CAT_COLORS)]

    s = P.resolveScheme(P.DEFAULT_SCHEME)
    n_types = sum(len(c['types']) for c in cats)
    n_examples = sum(1 for x in (topic or []) if x.startswith('!['))

    nav = ['<a href="#quick">先选对图</a>']
    for c in cats:
        nav.append(f'<div class="nav-cat" style="--cat:{c["color"]}"><a class="nav-cat-name" href="#{c["id"]}"><span class="dot"></span>{c["no"]}. {inline(c["name"])}<span class="count">{len(c["types"])}</span></a><ul>'
                   + ''.join(f'<li><a href="#{t["id"]}">{inline(t["name"])}</a></li>' for t in c['types']) + '</ul></div>')
    if topic:
        nav.append(f'<div class="nav-cat" style="--cat:{CAT_COLORS[7]}"><a class="nav-cat-name" href="#drawio-examples"><span class="dot"></span>8. 整图示例<span class="count">{n_examples}</span></a></div>')

    main = [f'<section class="prose" id="quick">{quick}</section>']
    for c in cats:
        main.append(f'<section class="cat" id="{c["id"]}" style="--cat:{c["color"]}"><header class="cat-head"><span class="cat-no">{int(c["no"]):02d}</span><h2>{inline(c["name"])}</h2><span class="cat-count">{len(c["types"])} 种图</span></header>'
                    f'<div class="prose">{c["intro"]}</div>' + ''.join(render_type(t, c['color'], copy_img) for t in c['types']) + '</section>')
    if topic:
        tl, i = [], 0
        while i < len(topic):
            ln = topic[i]
            m = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)', ln)
            if m:
                src = copy_img(m.group(2))
                cap = ''
                j = i + 1
                while j < len(topic) and not topic[j].strip():
                    j += 1
                if j < len(topic) and topic[j].startswith('> '):
                    cap = f'<figcaption>{inline(topic[j][2:])}</figcaption>'
                    i = j
                tl.append(f'<figure class="canvas" style="--canvas:#FFFFFF"><div class="canvas-inner"><img src="{src}" alt="{html.escape(m.group(1))}" loading="lazy"></div>{cap}</figure>')
            else:
                tl.append(ln)
            i += 1
        body = blocks([x for x in tl if not x.startswith('<figure')])
        # 图按出现顺序插回各自的 h3 后面
        figs = [x for x in tl if x.startswith('<figure')]
        pieces = re.split(r'(?=<h3>)', body)
        rebuilt = pieces[0]
        for k, piece in enumerate(pieces[1:]):
            rebuilt += piece + (figs[k] if k < len(figs) else '')
        main.append(f'<section class="prose topic" id="drawio-examples">{rebuilt}</section>')

    slots = ''.join(f'<span class="slot" style="background:{f};border-color:{st};color:{tx}">槽 {i}</span>' for i, (f, st, tx) in enumerate(s['slots'][:4]))
    cat_links = ''.join(f'<a href="#{c["id"]}" style="--cat:{c["color"]}"><span class="dot"></span>{inline(c["name"])}</a>' for c in cats)
    page = f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{html.escape(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Noto+Sans+SC:wght@400;500;700;900&display=swap">
<style>
{css}
</style>
</head>
<body>
<header class="mast">
  <div class="wrap mast-grid">
    <div>
      <h1>{html.escape(title)}</h1>
      <p class="lead">{inline(lead)}</p>
      {''.join(f'<p class="note">{inline(x)}</p>' for x in notes)}
      <div class="stats"><span><b>{n_types}</b>种图</span><span><b>{len(cats)}</b>类用途</span><span><b>{len(P.SCHEMES)}</b>套配色</span><span><b>{n_examples}</b>张整图示例</span></div>
    </div>
    <div class="legend">
      <div>
        <div class="legend-label">四槽配色 · 示例图统一用默认方案 {s['id']}（{s['name']}）</div>
        <div class="slots">{slots}</div>
      </div>
      <div class="cats" aria-label="分类色">{cat_links}</div>
      <label class="search" for="q">
        <input id="q" type="search" placeholder="搜图：名称、用途或关键词，比如 交接、状态、占比" autocomplete="off">
        <span class="hits" id="hits"></span>
      </label>
    </div>
  </div>
</header>
<div class="wrap layout">
  <details class="index" open>
    <summary>目录</summary>
    <nav aria-label="目录">{''.join(nav)}</nav>
  </details>
  <main>
    {''.join(main)}
    <p class="empty" id="empty">没有找到匹配的图。换个说法试试，比如"流程""架构""占比"。</p>
  </main>
</div>
<script>
{js}
</script>
</body>
</html>
'''
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8') as fh:
        fh.write(page)
    with open(os.path.join(out_dir, 'files.json'), 'w', encoding='utf-8') as fh:
        json.dump(copied, fh, ensure_ascii=False, indent=0)
    return n_types, len(copied)


def main(argv):
    out = tempfile.mkdtemp(prefix='guide-')
    if '--out' in argv:
        out = argv[argv.index('--out') + 1]
    n_types, n_files = build(out)
    print(f'{out}/index.html  {n_types} 种图，{n_files} 张图片（清单 files.json）')


if __name__ == '__main__':
    main(sys.argv[1:])
