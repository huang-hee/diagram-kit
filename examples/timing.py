#!/usr/bin/env python3
"""时间图（UML）：每条生命线一行，状态段是横向矩形、宽度按时长，同一状态同一颜色；底部是统一的时间刻度。

用到：band 生命线行、rect 状态段、text、line 刻度轴与超时线、panel、legend、footer。
运行后在本目录生成 timing.drawio 和 timing.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('支付请求的状态变化', '一次支付请求和支付平台各在什么时间处于什么状态，哪里会超时')
X0, PX, Y0, RH = 180, 150, 120, 90  # 时间零点的 x、每秒像素、第一行 y、行高
STATE_ROLE = {'空闲': 'ext', '处理中': 'lav', '等待回调': 'apricot', '受理': 'peach', '回调发送': 'mint'}
LINES = [
    ('支付请求', [('空闲', 0, 1), ('处理中', 1, 3), ('等待回调', 3, 5), ('空闲', 5, 6)]),
    ('支付平台', [('空闲', 0, 1), ('受理', 1, 3), ('回调发送', 3, 5), ('空闲', 5, 6)]),
]
W = X0 + 6 * PX + 20 - 40
for i, (name, segs) in enumerate(LINES):
    y = Y0 + i * (RH + 16)
    d.band(40, y, W, RH, name)
    for state, t0, t1 in segs:
        fill, stroke, font = d.t.roles[STATE_ROLE[state]]
        d.rect(X0 + t0 * PX + 2, y + 22, (t1 - t0) * PX - 4, RH - 44, fill, stroke=stroke, extra='rounded=1;arcSize=6;absoluteArcSize=1;')
        d.text(X0 + t0 * PX, y + 22, (t1 - t0) * PX, RH - 44, state, size=12, color=font, bold=True, align='center')

# 时间刻度：每秒一格
AY = Y0 + 2 * (RH + 16) + 10
d.line(X0, AY, X0 + 6 * PX + 20, AY, width=1.5, arrow='block')
for s in range(7):
    x = X0 + s * PX
    d.line(x, AY - 5, x, AY + 5, width=1)
    d.text(x - 20, AY + 8, 40, 18, f'{s}s', size=11, color=d.t.muted, align='center')
d.text(X0 + 6 * PX + 24, AY - 9, 40, 18, 't', size=12, bold=True)
# 超时线
tx = X0 + 5 * PX
d.line(tx, Y0 - 6, tx, AY - 8, color=d.t.stroke('bad'), width=1.5, dashed=True)
d.text(tx + 6, Y0 - 24, 120, 18, '超时阈值 5s', size=11, color=d.t.stroke('bad'), bold=True)

y = d.panel(40, AY + 50, 560, '口径', ['时间从发起支付起算，刻度 1 秒', '5 秒没收到回调就按超时处理，请求回到空闲并记录异常'])
d.legend(40, y + 24, [('ext', '空闲'), ('lav', '处理中'), ('apricot', '等待回调'), ('peach', '受理'), ('mint', '回调发送')])
d.footer(40, y + 56, '读图：一行一个对象，横向是时间；同一颜色是同一种状态，红色虚线是超时阈值。')

name = os.path.join(HERE, 'timing')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
