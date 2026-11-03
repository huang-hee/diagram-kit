#!/usr/bin/env python3
"""路线图：顶部是 Now / Next / Later 阶段箭头条，每个主题一条横向分层带，卡片按确定程度用不同底色。

用到：chevron、band、white / pending 两种卡片、按列循环摆位。
运行后在本目录生成 roadmap.drawio 和 roadmap.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('2027 订单路线图', '三个主题在 Now / Next / Later 各做什么')
X0, CW = 180, 340  # 第一列起点、列宽；箭头条首尾相接时下一个 x = 上一个 x + CW - 8
STAGES = [('Now', 'Q1 · 已排期', 'lav'), ('Next', 'Q2 · 已评审', 'peach'), ('Later', 'H2 · 待定', 'mint')]
for i, (stage, sub, role) in enumerate(STAGES):
    d.chevron(X0 + i * (CW - 8), 120, CW, 48, stage, sub, role=role)

ROWS = [
    ('会员', [('会员体系', '等级 · 积分'), ('权益商城', '会员专享'), None]),
    ('交易', [('订单导出', '运营后台'), ('多仓发货', '就近分配'), ('海外支付', '待定')]),
    ('履约', [None, ('物流轨迹', '对接快递 API'), ('智能推荐', '待定')]),
]
CARD_ROLE = ['lav', 'white', 'pending']  # 确定程度：已排期 / 已评审 / 待定
for r, (theme, cards) in enumerate(ROWS):
    y = 190 + r * 110
    d.band(40, y, 1160, 90, theme)
    for i, card in enumerate(cards):
        if card:
            d.box(X0 + i * (CW - 8) + 30, y + 17, 280, 56, card[0], card[1], role=CARD_ROLE[i])

y = d.panel(40, 540, 560, '口径', ['Now：已排期，有负责人和交付日期', 'Next：方案已评审，待排期', 'Later：只有方向，待定'])
d.legend(40, y + 24, [('lav', '已排期'), ('white', '已评审'), ('pending', '待定')])
d.footer(40, y + 56, '读图：横向是时间，纵向是主题；卡片底色越实，确定程度越高。')

name = os.path.join(HERE, 'roadmap')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
