#!/usr/bin/env python3
"""把 references/types-*.md 里的 Mermaid 示例按方案渲染一遍，抓语法或主题变量的问题。

用法:
  render_check.py [type ...] [--all] [--out DIR]

  type    只渲染这些图型（默认：所有带 Mermaid 示例的图型）
  --all   每个图型渲染全部方案（默认：只渲染默认方案）
  --out   .mmd / .png 的输出目录（默认：./render-check）

需要 mmdc 在 PATH 上；没有时不执行，提示安装。
"""
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import palette as P  # noqa: E402

REF = os.path.join(os.path.dirname(HERE), 'references')
SAMPLE_RE = re.compile(r'<!-- sample:(\w+) -->\s*```mermaid\n(.*?)\n```', re.S)


def collectSamples():
    """收集 types-*.md 里的示例。

    返回:
        {图型 id: Mermaid 正文}
    """
    found = {}
    for fn in sorted(os.listdir(REF)):
        if not fn.startswith('types-'):
            continue
        with open(os.path.join(REF, fn), encoding='utf-8') as fh:
            src = fh.read()
        for m in SAMPLE_RE.finditer(src):
            found[m.group(1)] = m.group(2)
    return found


def requireMmdc():
    """找 mmdc，找不到就退出并提示安装。

    返回:
        mmdc 可执行文件路径
    抛出:
        SystemExit: 没有 mmdc
    """
    mmdc = shutil.which('mmdc')
    if not mmdc:
        raise SystemExit('没有 mmdc，不执行渲染。请先安装：npm i -g @mermaid-js/mermaid-cli')
    return mmdc


def _errorLine(text):
    """从 mmdc 的输出里取第一行含 Error 的内容，没有就取末尾 300 字。"""
    for ln in text.splitlines():
        if 'Error' in ln or 'error' in ln:
            return ln.strip()[:300]
    return text.strip()[-300:]


def main(argv):
    """命令入口。

    返回:
        退出码，有失败为 1
    """
    args = argv[1:]
    all_schemes = '--all' in args
    out_dir = 'render-check'
    if '--out' in args:
        out_dir = args[args.index('--out') + 1]
        args = [a for a in args if a not in ('--out', out_dir)]
    wanted = [a for a in args if not a.startswith('--')]
    mmdc = requireMmdc()
    os.makedirs(out_dir, exist_ok=True)
    samples = collectSamples()
    # 指定的图型必须有示例
    unknown = [w for w in wanted if w not in samples]
    if unknown:
        raise SystemExit('这些图型没有示例：' + '、'.join(unknown) + '；可用：' + '、'.join(samples))
    fails = 0
    # 每个图型 × 方案渲染一张
    for tid, body in samples.items():
        if wanted and tid not in wanted:
            continue
        for sid in (list(P.SCHEMES) if all_schemes else [P.DEFAULT_SCHEME]):
            mmd_path = os.path.join(out_dir, f'{tid}__{sid}.mmd')
            with open(mmd_path, 'w', encoding='utf-8') as fh:
                fh.write(P.emitMermaid(tid, sid, body))
            r = subprocess.run([mmdc, '-i', mmd_path, '-o', mmd_path[:-4] + '.png', '-s', '2', '-b', P.resolveScheme(sid)['bg'], '-q'],
                               capture_output=True, text=True)
            ok = r.returncode == 0
            fails += not ok
            print('OK  ' if ok else 'FAIL', f'{tid:<14} {sid}', '' if ok else _errorLine(r.stderr or r.stdout))
    print(f'{fails} 张失败' if fails else '全部渲染成功', '->', out_dir)
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
