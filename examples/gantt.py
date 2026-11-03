#!/usr/bin/env python3
"""甘特图：左侧任务列、顶部日期刻度，每个阶段一条横带，条形按阶段色区分，关键路径用主色，里程碑用菱形。

用到：band 阶段行、rect 时间条、line 刻度与今日线、box（diamond）里程碑、panel、legend、footer。
运行后在本目录生成 gantt.drawio 和 gantt.png。
"""
import datetime as dt
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram, SERIES  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('订单 V2 排期', '三个阶段各几天，关键路径在哪，什么时候灰度')
START = dt.date(2026, 11, 2)
DAYS, PX = 21, 40  # 显示天数、每天像素
X0, Y0, ROW = 240, 160, 40  # 时间轴起点、第一条带 y、任务行高
LABEL_W = X0 - 40 - 10


def day_x(date):
    return X0 + (date - START).days * PX


# 阶段 → 任务：(名称, 开始, 天数, 类型)，类型 done / active / crit / plain / milestone
SECTIONS = [
    ('设计', [('需求评审', dt.date(2026, 11, 2), 3, 'done'), ('技术方案', dt.date(2026, 11, 5), 4, 'active')]),
    ('开发', [('订单改造', dt.date(2026, 11, 9), 6, 'crit'), ('支付对接', dt.date(2026, 11, 9), 5, 'plain')]),
    ('上线', [('联调', dt.date(2026, 11, 15), 4, 'plain'), ('灰度发布', dt.date(2026, 11, 19), 0, 'milestone')]),
]
# 日期刻度
AX_Y = Y0 - 30
for i in range(DAYS + 1):
    x = X0 + i * PX
    d.line(x, AX_Y, x, AX_Y + 6, color=d.t.stroke('ext'), width=1)
    if i % 3 == 0 and i < DAYS:
        d.text(x - 24, AX_Y - 22, 48, 18, (START + dt.timedelta(days=i)).strftime('%m-%d'), size=11, color=d.t.muted, align='center')
d.line(X0, AX_Y + 6, X0 + DAYS * PX, AX_Y + 6, color=d.t.stroke('ext'), width=1)

y = Y0
for s, (section, tasks) in enumerate(SECTIONS):
    role = SERIES[s % len(SERIES)]
    fill, stroke, _ = d.t.roles[role]
    dk = d.t.deep(role)
    h = len(tasks) * ROW + 20
    d.band(40, y, X0 + DAYS * PX - 40, h, section, label_w=130)
    for i, (name, start, days, kind) in enumerate(tasks):
        ty = y + 10 + i * ROW
        d.text(180, ty + 2, LABEL_W - 140, 36, name, size=12, bold=kind == 'crit', align='left')
        if kind == 'milestone':
            d.box(day_x(start) - 14, ty + 6, 28, 28, '', role='key', shape='diamond')
            d.text(day_x(start) + 20, ty + 11, 120, 18, start.strftime('%m-%d') + ' 灰度', size=11, color=d.t.muted)
            continue
        bar_fill = {'crit': d.t.primary, 'done': d.t.fill('ext')}.get(kind, fill)
        bar_stroke = {'crit': d.t.primary, 'done': d.t.stroke('ext')}.get(kind, stroke)
        d.rect(day_x(start), ty + 10, days * PX - 4, 20, bar_fill, stroke=bar_stroke, extra='rounded=1;arcSize=6;absoluteArcSize=1;')
        if kind == 'active':  # 进行中：已完成部分加深（示意按一半画）
            d.rect(day_x(start), ty + 10, int(days * PX * 0.5), 20, dk, stroke='none', extra='rounded=1;arcSize=6;absoluteArcSize=1;')
        d.text(day_x(start) + days * PX + 2, ty + 11, 60, 18, f'{days}d', size=11, color=d.t.muted)
    y += h + 10

# 今日线
today = dt.date(2026, 11, 7)
d.line(day_x(today), AX_Y + 6, day_x(today), y - 10, color=d.t.stroke('bad'), width=1.5, dashed=True)
d.text(day_x(today) + 6, y - 30, 80, 18, '今天', size=11, color=d.t.stroke('bad'), bold=True)

p = d.panel(40, y + 20, 560, '口径', ['关键路径：技术方案 → 订单改造 → 联调 → 灰度，任一项延期灰度就延期', '不排周末，时长按工作日'])
d.legend(40, p + 24, [('lav', '设计'), ('peach', '开发'), ('mint', '上线'), ('key', '关键路径 / 里程碑'), ('ext', '已完成'), (('color', d.t.deep('lav')), '进行中已完成的部分'), ('line-dashed', '今天')])
d.footer(40, p + 56, '读图：横向是日期，一行一个任务；主色条是关键路径，菱形是里程碑，红虚线是今天。')

name = os.path.join(HERE, 'gantt')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
