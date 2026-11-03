#!/usr/bin/env python3
"""业务架构图：自上而下是用户触点 → 业务域 → 业务能力 → 共享能力，每层一条横向分层带，层内卡片等宽对齐。

用到：band、box 网格、panel、legend、footer。
运行后在本目录生成 biz_arch.drawio 和 biz_arch.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('电商业务架构', '业务分成哪几个域，每个域有什么能力，哪些能力是共享的')
BW, X0, CW, GAP = 1060, 200, 200, 20  # 带宽、第一列卡片 x、卡片宽、列距
LAYERS = [
    ('用户触点', '渠道', 120, [('App', 'sage'), ('小程序', 'sage'), ('Web', 'sage')]),
    ('业务域', '按业务划分', 230, [('商品域', 'peach'), ('交易域', 'peach'), ('营销域', 'peach'), ('履约域', 'peach')]),
    ('业务能力', '域内能力', 340, [('类目 · 库存', 'lav'), ('下单 · 支付', 'lav'), ('优惠券 · 秒杀', 'lav'), ('仓储 · 物流', 'lav')]),
    ('共享能力', '中台', 450, [('会员', 'mint'), ('支付', 'mint'), ('消息', 'mint')]),
]
for label, sub, y, cards in LAYERS:
    d.band(40, y, BW, 90, label, sub)
    n = len(cards)
    total = n * CW + (n - 1) * GAP
    x0 = X0 + (4 * CW + 3 * GAP - total) / 2  # 不足 4 张时居中
    for i, (title, role) in enumerate(cards):
        d.box(x0 + i * (CW + GAP), y + 20, CW, 50, title, role=role)

y = d.panel(40, 570, 560, '口径', ['业务域按交易链路划分，一个域一个负责人', '共享能力由中台团队维护，各域复用不重建'])
d.panel(640, 570, 460, '不在这张图里', ['技术组件与部署', '组织架构'], kind='soft', h=y - 570)
d.legend(40, y + 24, [('sage', '触点'), ('peach', '业务域'), ('lav', '业务能力'), ('mint', '共享能力')])
d.footer(40, y + 56, '读图：自上而下从触点到共享能力；同一列的域和能力对应，共享能力所有域都用。')

name = os.path.join(HERE, 'biz_arch')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
