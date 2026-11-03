#!/usr/bin/env python3
"""用户旅程图：顶部是阶段箭头条，下面每行一个维度（行为、触点、想法、情绪、痛点与机会），情绪由分值点连成折线。

用到：chevron 阶段条、band 维度行、按列循环摆卡片、带图标的触点卡片、badge 分值点 + line 折线、note 机会点。
运行后在本目录生成 journey.drawio 和 journey.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('首次下单的用户旅程', '新用户从发现到支付每一步做什么、碰到什么、情绪如何')
X0, CW = 190, 280  # 第一列起点、列宽；箭头条首尾相接，列距 = CW - 8
STAGES = [('发现', '搜索 · 浏览', 'lav'), ('下单', '地址 · 优惠', 'peach'), ('支付', '收银台', 'mint')]
col_x = [X0 + i * (CW - 8) for i in range(len(STAGES))]
for x, (stage, sub, role) in zip(col_x, STAGES):
    d.chevron(x, 120, CW, 48, stage, sub, role=role)

BW = col_x[-1] + CW - 40  # 分层带宽度：盖住最后一个箭头条
ROWS = {'行为': 190, '触点': 300, '想法': 410, '情绪': 520, '痛点与机会': 690}
for label, y in ROWS.items():
    d.band(40, y, BW, 140 if label == '情绪' else 90, label)


def card(col, row, title, sub=None, role='white', icon=None):
    """按列摆一张 56 高的卡片。"""
    return d.box(col_x[col] + 24, ROWS[row] + 17, CW - 48, 56, title, sub, role=role, icon=icon)


for i, t in enumerate(['搜索商品、看详情页', '填收货地址、选优惠券', '跳转收银台、付款']):
    card(i, '行为', t)
for i, (t, icon) in enumerate([('App 搜索框', 'ios7:smartphone'), ('确认订单页', 'ios7:document'), ('第三方收银台', 'ios7:credit_card')]):
    card(i, '触点', t, icon=icon)
for i, t in enumerate(['"有没有更便宜的"', '"地址怎么还要手填"', '"跳出去会不会丢单"']):
    card(i, '想法', t)

# 情绪：分值 1–5 映射到带内的高度，相邻点连成折线
SCORES = [4, 2, 5]
pts = []
for x, score in zip(col_x, SCORES):
    cx = x + CW / 2
    cy = ROWS['情绪'] + 120 - (score - 1) * 22
    pts.append((cx, cy))
for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
    d.line(x1, y1, x2, y2, color=d.t.primary, width=2)
for (cx, cy), score in zip(pts, SCORES):
    d.badge(cx - 13, cy - 13, score, role='ok' if score >= 4 else ('bad' if score <= 2 else 'lav'))

card(1, '痛点与机会', '地址手填 → 接入地址簿', role='note')
card(2, '痛点与机会', '担心丢单 → 页面内收银台', role='note')

y = d.panel(40, 810, 560, '数据来源', ['10 位新用户的访谈记录', '情绪分 1–5 由受访者自评'])
d.legend(40, y + 24, [('ok', '满意'), ('lav', '一般'), ('bad', '痛点'), ('note', '机会点')])
d.footer(40, y + 56, '读图：横向是阶段，纵向是维度；情绪折线越低越痛，机会点对着痛点写。')

name = os.path.join(HERE, 'journey')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
