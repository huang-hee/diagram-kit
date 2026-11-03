#!/usr/bin/env python3
"""泳道图：每条泳道是一条横向分层带，步骤从左到右，跨泳道的线是单折 L 形，交接点用强调色。

用到：band 当泳道、带拐点的 edge、key 交接点、卡片图标（icon）、panel、legend、footer。
运行后在本目录生成 swimlane.drawio 和 swimlane.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('退款流程', '退款申请经过哪些角色，在哪里交接')
W = 1140
for name, y in (('用户', 120), ('客服', 260), ('财务', 400)):
    d.band(40, y, W, 120, name)

submit = d.box(200, 158, 160, 44, '提交退款', role='peach', shape='pill')
done = d.box(960, 158, 160, 44, '收到退款', role='peach', shape='pill')
check = d.box(180, 276, 200, 88, '符合规则?', role='apricot', shape='diamond')
review = d.box(460, 288, 200, 64, '人工审核', '48 小时内', role='lav', icon='ios7:user')
refund = d.box(720, 428, 200, 64, '原路退款', 'T+1 到账', role='key', icon='ios7:credit_card', icon_color=d.t.bg)

d.edge(submit, check, src='B', dst='T')
d.edge(check, review, '否', src='R', dst='L')
d.edge(check, refund, '是', src='B', dst='L', points=[(280, 460)], label_offset=-0.5)
d.edge(review, refund, src='R', dst='T', points=[(820, 320)])
d.edge(refund, done, src='R', dst='B', points=[(1040, 460)])

y = d.panel(40, 550, 560, '依据', ['R12 退款规则：7 天内且未发货自动通过', '人工审核超过 48 小时自动升级给主管'])
d.legend(40, y + 24, [('peach', '起止'), ('apricot', '判断'), ('lav', '处理'), ('key', '交接点'), ('edge', '流转')])
d.footer(40, y + 56, '读图：每条横带是一个角色，步骤从左到右；主色卡片是跨角色的交接点。')

name = os.path.join(HERE, 'swimlane')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
