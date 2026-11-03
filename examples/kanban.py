#!/usr/bin/env python3
"""看板：列等宽，列头按系列色深色实底并写 WIP 上限，卡片白底细描边、宽度统一，高优先级卡片带徽标。

用到：box（列头深色、卡片 white）、rect 列底、badge 优先级、panel、legend、footer。
运行后在本目录生成 kanban.drawio 和 kanban.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram, SERIES  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('订单 V2 看板', '每个任务当前在哪个阶段，哪一列堆积了')
X0, CW, GAP, Y0, CH = 60, 250, 20, 120, 250
COLS = [('待办', 'WIP 不限', [('订单导出', '张三 · JIRA-12', None), ('物流对接', '李四 · JIRA-15', None)]),
        ('进行中', 'WIP ≤ 2', [('支付对接', '王五 · JIRA-9', 'High')]),
        ('测试中', 'WIP ≤ 2', [('下单页', '赵六 · JIRA-7', None)]),
        ('已完成', '本迭代', [('需求评审', '全员 · JIRA-3', None)])]
for i, (title, wip, cards) in enumerate(COLS):
    role = SERIES[i % len(SERIES)]
    dk = d.t.deep(role)
    x = X0 + i * (CW + GAP)
    d.rect(x, Y0, CW, CH, d.t.soft, extra='rounded=1;arcSize=8;absoluteArcSize=1;')
    d.box(x, Y0, CW, 48, title, wip, role='white', extra=f'fillColor={dk};strokeColor={dk};fontColor={d.t.bg};', sub_color=d.t.bg)
    for j, (name, meta, prio) in enumerate(cards):
        cy = Y0 + 60 + j * 80
        d.box(x + 10, cy, CW - 20, 64, name, meta, role='white', align='left', extra='spacingLeft=10;')
        if prio:
            d.badge(x + CW - 40, cy + 10, '!', size=22, role='bad')

y = d.panel(X0, Y0 + CH + 30, 560, '规则', ['进行中、测试中各最多 2 张，超了先帮忙清列', '带红标的是高优先级，优先流转'])
d.legend(X0, y + 24, [('white', '任务卡'), ('bad', '高优先级'), (('color', d.t.deep('lav')), '待办'), (('color', d.t.deep('peach')), '进行中'), (('color', d.t.deep('mint')), '测试中'), (('color', d.t.deep('apricot')), '已完成')])
d.footer(X0, y + 56, '读图：从左到右是流转阶段，列头写 WIP 上限；卡片说明里是负责人和工单号。')

name = os.path.join(HERE, 'kanban')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
