#!/usr/bin/env python3
"""从 references/types-*.md 的示例骨架生成 docs/画图指南.md 的示例图，并回填指南里的源码块。

用法:
  build_docs.py [type ...] [--min-side N] [--no-doc] [--examples]

  type         只处理这些图型（默认：全部）
  --min-side   导出 PNG 的长边像素下限（默认 2000；正式文档的图按规则要 4000）
  --no-doc     只出图，不回填指南
  --examples   同时运行 examples/*.py，重新生成 drawio 的整图示例

每种图的处理：
  Mermaid 图型             示例骨架 → palette.emitMermaid → docs/assets/<type>.mmd → mmdc --size 渲染 PNG
  sankey                   正文取 docs/assets/sankey.csv（英文|中文 写法）；另用 sankey_echarts.js 出 ECharts 版
  scatter / distribution   运行 docs/assets/<type>.py（$SKILL 换成本仓库路径）
  mindmap                  运行 docs/assets/mindmap.py 用 drawio_kit 出图：Mermaid 的 mindmap 是放射布局、斜线，达不到统一风格

依赖：mmdc 12+（--size 选项）；桑基图的 ECharts 版要 node + echarts + playwright；散点 / 直方图要 matplotlib；思维导图和 --examples 要 drawio 桌面版。
缺什么就跳过对应的图并在末尾列出。
"""
import glob
import math
import os
import re
import shutil
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import palette as P  # noqa: E402
from render_check import collectSamples  # noqa: E402

ASSETS = os.path.join(ROOT, 'docs', 'assets')
GUIDE = os.path.join(ROOT, 'docs', '画图指南.md')
EXAMPLES = os.path.join(ROOT, 'examples')
SID = P.DEFAULT_SCHEME


def pngSize(path):
    """读 PNG 头里的宽高。"""
    with open(path, 'rb') as fh:
        head = fh.read(24)
    return struct.unpack('>II', head[16:24])


# 这些图型撑满视口宽度、字号固定，放大视口只会把图拉宽；改成固定视口 + 设备倍数来放大
FILL_WIDTH_KINDS = {'gantt', 'journey'}
FILL_WIDTH_BASE = 1000
# 示例图不用 Mermaid、改用 drawio_kit 出的图型：docs/assets/<type>.py
DRAWIO_TYPES = {'mindmap'}


def renderMermaid(mmdc, mmd_path, png_path, bg, min_side, fill_width=False):
    """渲染一张 Mermaid 图，长边不低于 min_side。

    一般图型用 mmdc 的 --size（整图等比放大）；撑满宽度的图型用固定视口 + -s 倍数。
    返回:
        (宽, 高)
    抛出:
        RuntimeError: mmdc 失败
    """
    if fill_width:
        sizing = ['--size', str(FILL_WIDTH_BASE), '-s', str(math.ceil(min_side / FILL_WIDTH_BASE))]
    else:
        sizing = ['--size', str(min_side + 4)]  # --size 是"最长边最多这么大"，偶尔会少 1px
    for _ in range(3):
        r = subprocess.run([mmdc, '-i', mmd_path, '-o', png_path, *sizing, '-b', bg, '-q'], capture_output=True, text=True)
        if r.returncode:
            raise RuntimeError(_errorLine(r.stderr or r.stdout))
        pw, ph = pngSize(png_path)
        if max(pw, ph) >= min_side:
            break
        sizing[1] = str(math.ceil(int(sizing[1]) * 1.02))
    return pw, ph


def _errorLine(text):
    for ln in text.splitlines():
        if 'rror' in ln:
            return ln.strip()[:300]
    return text.strip()[-300:]


def buildMermaid(tids, min_side, skipped):
    """生成 Mermaid 图型的 .mmd 和 .png。

    返回:
        {图型: (宽, 高)}
    """
    mmdc = shutil.which('mmdc')
    if not mmdc:
        skipped.append('Mermaid 图型（没有 mmdc：npm i -g @mermaid-js/mermaid-cli）')
        return {}
    samples = collectSamples()
    s = P.resolveScheme(SID)
    done = {}
    for tid in tids:
        if P.TYPES[tid]['kind'] == 'chart' or tid in DRAWIO_TYPES:
            continue
        if tid == 'sankey':
            with open(os.path.join(ASSETS, 'sankey.csv'), encoding='utf-8') as fh:
                body = fh.read().rstrip('\n')
        elif tid in samples:
            body = samples[tid]
        else:
            skipped.append(f'{tid}（references 里没有示例）')
            continue
        mmd_path = os.path.join(ASSETS, f'{tid}.mmd')
        with open(mmd_path, 'w', encoding='utf-8') as fh:
            fh.write(P.emitMermaid(tid, SID, body) + '\n')
        png_path = os.path.join(ASSETS, f'{tid}.png')
        try:
            done[tid] = renderMermaid(mmdc, mmd_path, png_path, s['bg'], min_side,
                                      fill_width=P.TYPES[tid]['kind'] in FILL_WIDTH_KINDS)
            print(f'OK   {tid:<14} {done[tid][0]}x{done[tid][1]}')
        except RuntimeError as e:
            print(f'FAIL {tid:<14} {e}')
            skipped.append(f'{tid}（渲染失败：{e}）')
    return done


def buildCharts(tids, min_side, skipped):
    """运行 docs/assets 里的 matplotlib 示例脚本。"""
    try:
        import matplotlib  # noqa: F401
    except ImportError:
        skipped.append('散点 / 直方图（没有 matplotlib：pip install matplotlib）')
        return
    for tid in tids:
        if P.TYPES[tid]['kind'] != 'chart':
            continue
        script = os.path.join(ASSETS, f'{tid}.py')
        if not os.path.exists(script):
            skipped.append(f'{tid}（没有 {script}）')
            continue
        with open(script, encoding='utf-8') as fh:
            src = fh.read().replace('$SKILL', ROOT)
        runAssetScript(tid, src, min_side, skipped)


def runAssetScript(tid, src, min_side, skipped):
    """在 docs/assets 下运行一段示例脚本，DIAGRAM_MIN_SIDE 传长边下限。"""
    env = dict(os.environ, DIAGRAM_MIN_SIDE=str(min_side))
    r = subprocess.run([sys.executable, '-c', src], cwd=ASSETS, env=env, capture_output=True, text=True)
    if r.returncode:
        print(f'FAIL {tid:<14} {_errorLine(r.stderr)}')
        skipped.append(f'{tid}（脚本失败）')
        return
    w, h = pngSize(os.path.join(ASSETS, f'{tid}.png'))
    flag = '' if max(w, h) >= min_side else f'  长边不足 {min_side}'
    print(f'OK   {tid:<14} {w}x{h}{flag}')


def buildDrawioTypes(tids, min_side, skipped):
    """运行 docs/assets 里用 drawio_kit 出图的示例脚本。"""
    wanted = [t for t in tids if t in DRAWIO_TYPES]
    if not wanted:
        return
    if not shutil.which('drawio'):
        skipped.append('、'.join(wanted) + '（没有 drawio 命令行）')
        return
    for tid in wanted:
        with open(os.path.join(ASSETS, f'{tid}.py'), encoding='utf-8') as fh:
            src = fh.read().replace('$SKILL', ROOT)
        runAssetScript(tid, src, min_side, skipped)


def buildSankeyEcharts(min_side, skipped):
    """桑基图的 ECharts 版（SVG + PNG）。"""
    node = shutil.which('node')
    if not node:
        skipped.append('桑基图 ECharts 版（没有 node）')
        return
    scale = max(2, math.ceil(min_side / 720))
    r = subprocess.run([node, os.path.join(HERE, 'sankey_echarts.js'), os.path.join(ASSETS, 'sankey.csv'), SID,
                        '--out', os.path.join(ASSETS, 'sankey-echarts'), '--png', '--scale', str(scale)],
                       capture_output=True, text=True)
    if r.returncode:
        print('FAIL sankey-echarts  ', _errorLine(r.stderr or r.stdout))
        skipped.append('桑基图 ECharts 版（' + (r.stderr or r.stdout).strip().splitlines()[-1][:120] + '）')
        return
    w, h = pngSize(os.path.join(ASSETS, 'sankey-echarts.png'))
    print(f'OK   {"sankey-echarts":<14} {w}x{h} @{scale}x')


def buildExamples(min_side, skipped):
    """运行 examples/*.py，生成 drawio 整图示例。"""
    if not shutil.which('drawio'):
        skipped.append('drawio 示例（没有 drawio 命令行）')
        return
    env = dict(os.environ, DIAGRAM_MIN_SIDE=str(min_side))
    for script in sorted(glob.glob(os.path.join(EXAMPLES, '*.py'))):
        name = os.path.basename(script)[:-3]
        r = subprocess.run([sys.executable, script], cwd=EXAMPLES, env=env, capture_output=True, text=True)
        if r.returncode:
            print(f'FAIL {name:<14} {_errorLine(r.stderr)}')
            skipped.append(f'examples/{name}.py（脚本失败）')
            continue
        png = os.path.join(EXAMPLES, f'{name}.png')
        w, h = pngSize(png) if os.path.exists(png) else (0, 0)
        print(f'OK   {name:<14} {w}x{h}')


def syncGuide(tids):
    """把 docs/assets 里的源码回填到指南的 <details> 块。

    返回:
        回填的图型列表
    """
    with open(GUIDE, encoding='utf-8') as fh:
        src = fh.read()
    out = src
    changed = []
    for tid in tids:
        ext = 'py' if P.TYPES[tid]['kind'] == 'chart' or tid in DRAWIO_TYPES else 'mmd'
        path = os.path.join(ASSETS, f'{tid}.{ext}')
        if not os.path.exists(path):
            continue
        with open(path, encoding='utf-8') as fh:
            code = fh.read().rstrip('\n')
        pat = re.compile(r'(<summary>示例源码（[^）]*assets/' + re.escape(f'{tid}.{ext}') + r'）</summary>\n\n```\w*\n)(.*?)(\n```)', re.S)
        new, n = pat.subn(lambda m: m.group(1) + code + m.group(3), out, count=1)
        if n and new != out:
            changed.append(tid)
        out = new
    if out != src:
        with open(GUIDE, 'w', encoding='utf-8') as fh:
            fh.write(out)
    return changed


def main(argv):
    args = argv[1:]
    min_side = 2000
    if '--min-side' in args:
        i = args.index('--min-side')
        min_side = int(args[i + 1])
        del args[i:i + 2]
    no_doc = '--no-doc' in args
    examples = '--examples' in args
    wanted = [a for a in args if not a.startswith('--')]
    unknown = [t for t in wanted if t not in P.TYPES]
    if unknown:
        raise SystemExit('图型不存在：' + '、'.join(unknown))
    tids = wanted or list(P.TYPES)
    skipped = []
    buildMermaid(tids, min_side, skipped)
    buildCharts(tids, min_side, skipped)
    buildDrawioTypes(tids, min_side, skipped)
    if 'sankey' in tids:
        buildSankeyEcharts(min_side, skipped)
    if examples:
        buildExamples(min_side, skipped)
    if not no_doc:
        changed = syncGuide(tids)
        print('指南源码块已回填：', ', '.join(changed) or '（无变化）')
    if skipped:
        print('跳过：\n  ' + '\n  '.join(skipped))
    return 1 if skipped else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
