#!/usr/bin/env python3
"""用户故事地图：顶部是用户活动骨架，每个活动下挂任务，再往下是故事卡；横线切出 MVP 和后续版本。

用到：chevron 活动条、box 任务卡、sticky 故事卡、line 版本切线、panel、legend、footer。
运行后在本目录生成 story_map.drawio 和 story_map.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('首次购买的故事地图', '用户从浏览到支付做什么，哪些故事进 MVP、哪些放后面')
X0, CW = 190, 280  # 第一列起点、列宽；箭头条首尾相接，列距 270
ACTS = [('浏览', '找到想买的', 'lav'), ('下单', '确认信息', 'peach'), ('支付', '完成付款', 'mint')]
col_x = [X0 + i * (CW - 10) for i in range(len(ACTS))]
for x, (act, sub, role) in zip(col_x, ACTS):
    d.chevron(x, 120, CW, 48, act, sub, role=role)
TASKS = ['搜索商品', '填写地址', '选择支付方式']
for x, task in zip(col_x, TASKS):
    d.box(x + 20, 190, CW - 40, 48, task, role='lav')

# 版本切线：线上方是 MVP，下方是后续版本
BW = col_x[-1] + CW - 40
LINES = [(270, 'MVP', '本期'), (400, '下一版', 'V2'), (500, '以后', '待定')]
for ly, label, sub in LINES:
    d.line(X0, ly, BW, ly, color=d.t.stroke('ext'), width=1, dashed=True)
    d.text(40, ly + 4, 140, 36, f'<b>{label}</b><br><span style="font-size:11px;color:{d.t.muted}">{sub}</span>', size=13, html=True)
STORIES = [(0, 0, '按类目筛选', 'note'), (0, 1, '搜索联想', 'white'), (1, 0, '手填地址', 'note'), (1, 1, '地址簿', 'white'),
           (2, 0, '微信 / 支付宝', 'note'), (2, 2, '分期付款', 'pending')]
for col, band, story, role in STORIES:
    y = LINES[band][0] + 10
    if role == 'pending':
        d.box(col_x[col] + 20, y, CW - 40, 56, story, role='pending', bold=False)
    else:
        d.sticky(col_x[col] + 20, y, CW - 40, 56, story, role=role)

y = d.panel(40, 600, 560, '切版本的依据', ['MVP 只保证一条能跑通的购买路径', '分期付款依赖外部额度服务，待定'])
d.legend(40, y + 24, [('lav', '任务'), ('note', 'MVP 故事'), ('white', '下一版'), ('pending', '待定')])
d.footer(40, y + 56, '读图：顶部箭头条是用户活动，下面一列是该活动的任务和故事；横虚线切出版本，越往下越晚。')

name = os.path.join(HERE, 'story_map')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
