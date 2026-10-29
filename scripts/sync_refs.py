#!/usr/bin/env python3
"""从 palette.py 重新生成 references/ 里的色表。

- references/schemes.md 整个重写。
- references/types-*.md 只替换 <!-- palette:<type> --> 和 <!-- /palette:<type> --> 之间的内容，周围手写的内容保留。

改过 palette.py 的 SCHEMES / TYPES 后执行：
  python scripts/sync_refs.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import palette as P  # noqa: E402

REF = os.path.join(os.path.dirname(HERE), 'references')
CMD = 'python $SKILL/scripts/palette.py'


def cell(f, st, tx):
    """一格：填充 / 描边 / 字色。"""
    return f'`{f}` `{st}` `{tx}`'


def typeBlock(tid):
    """图型的角色表：角色 -> token -> 默认方案下的三色。

    参数:
        tid: 图型 id
    返回:
        Markdown 文本
    """
    t = P.TYPES[tid]
    sid = P.DEFAULT_SCHEME
    s, rows = P.roleTable(tid, sid)
    head = ['角色', 'class', 'token', f'{sid}（默认）填充 / 描边 / 字色']
    lines = ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
    # 每个角色一行
    for cls, lbl, p, dashed, colors in rows:
        token = f'`{p}`' + ('，虚线' if dashed else '')
        lines.append(f'| {lbl} | `{cls}` | {token} | {cell(*colors)} |')
    lines.append(f'| 页面 / 连线 / 正文 | — | `bg` `line` `text` | `{s["bg"]}` `{s["line"]}` `{s["text"]}` |')
    # 取色命令按图型种类给
    kind = t['kind']
    if kind == 'chart':
        cmd = f'{CMD} chart [方案]'
    elif kind == 'drawio':
        cmd = f'{CMD} drawio {tid} [方案]'
    else:
        cmd = f'{CMD} mermaid {tid} [方案] --body 正文.mmd'
    return '\n'.join([f'**配色**（换方案时 token 不变，只换颜色）　取色：`{cmd}`', '', *lines])


def syncTypes():
    """替换 types-*.md 里的色表标记块。

    返回:
        改动过的文件名列表
    抛出:
        SystemExit: 标记里的图型不存在
    """
    changed = []
    for fn in sorted(os.listdir(REF)):
        if not fn.startswith('types-'):
            continue
        path = os.path.join(REF, fn)
        with open(path, encoding='utf-8') as fh:
            src = fh.read()

        def replace(m):
            tid = m.group(1)
            if tid not in P.TYPES:
                raise SystemExit(f'{fn}：标记里的图型不存在：{tid}')
            return f'<!-- palette:{tid} -->\n{typeBlock(tid)}\n<!-- /palette:{tid} -->'

        out = re.sub(r'<!-- palette:(\w+) -->.*?<!-- /palette:\1 -->', replace, src, flags=re.S)
        # 有变化才写回
        if out != src:
            with open(path, 'w', encoding='utf-8') as fh:
                fh.write(out)
            changed.append(fn)
    return changed


def syncSchemes():
    """重写 schemes.md。"""
    lines = [
        '# 配色方案总表',
        '',
        '由 `scripts/sync_refs.py` 从 `palette.py` 生成，改配色请改 `palette.py` 后重新生成。',
        '',
        f'- 全部方案对所有图型通用；不指定方案时用 `{P.DEFAULT_SCHEME}`。一篇文档或一批图只用一套。',
        '- 四槽语义：槽0 处理 / 任务 / 类 / 组件，槽1 起止 / 接口 / 库，槽2 文档 / 数据 / 枚举 / 制品，槽3 判断 / 网关 / 参与者 / 约束。',
        '- 主色独立于四个槽，只给"一张图里只有一处"的强调角色（关键路径、核心实体、中心主题、本次改动）。',
        '- 派生规则：浅填充的描边 = 填充加深 30%，字色 = 同色相加深到 4.5:1；深填充描边同填充、白字；'
        'soft 容器 = 描边色对底 90% 浅调；连线对底 ≥3:1；系列色 = 槽填充 + 方案附加色，不含主色。',
        '- 系列色用于数据图、思维导图分支、泳道 / 分组轮换；状态色（成功 / 警告 / 失败 / 信息 / 完成）所有方案共用。',
        '',
        '状态色：' + '、'.join(f'{k} `{v}`' for k, v in P.STATE.items()),
        '',
        '| 方案 | 名称 | 气质 | 底 / 正文 / 连线 | 主色 | 槽0–3 填充 | 系列色 |',
        '|---|---|---|---|---|---|---|',
    ]
    # 每个方案一行，默认加 ★
    for sid in P.SCHEMES:
        s = P.resolveScheme(sid)
        mark = '★ ' if sid == P.DEFAULT_SCHEME else ''
        slots = ' '.join(f'`{f}`' for f, _, _ in s['slots'])
        series = ' '.join(f'`{c}`' for c in s['series'])
        lines.append(f'| {mark}`{sid}` | {s["name"]} | {s["mood"]} | `{s["bg"]}` `{s["text"]}` `{s["line"]}` '
                     f'| `{s["primary"]}` | {slots} | {series} |')
    lines += ['', f'完整 token（含描边、字色、便签色、渐层）：`{CMD} show <方案>`', '']
    with open(os.path.join(REF, 'schemes.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines))


if __name__ == '__main__':
    syncSchemes()
    changed_files = syncTypes()
    print('schemes.md 已重新生成；色表有更新的文件：', ', '.join(changed_files) or '（无变化）')
