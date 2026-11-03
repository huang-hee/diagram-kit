#!/usr/bin/env python3
"""时间线：一条水平主轴分段着色，节点是带图标的圆，文字上下交替。

用到：rect 轴段、带图标的圆（box circle + icon）、line 连接线、text 文字块、按序循环交替摆位。
运行后在本目录生成 timeline.drawio 和 timeline.png。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'scripts'))
from drawio_kit import Diagram, SERIES  # noqa: E402

MIN_SIDE = int(os.environ.get('DIAGRAM_MIN_SIDE', 4000))

d = Diagram('订单系统演进', '从单体到订单 V2 经历了哪些节点')
EVENTS = [
    ('2023', '单体上线', '一个 Spring Boot 应用', 'ios7:box'),
    ('2024 上半年', '拆分服务', '订单、商品、用户三个服务', 'ios7:settings'),
    ('2024 下半年', '接入 MQ', '订单事件异步化', 'ios7:documents'),
    ('2025', '迁移 K8s', '容器化、灰度发布', 'ios7:folder'),
    ('2026', '订单 V2', '多仓发货、海外支付', 'ios7:bag'),
]
AXIS_Y, X0, SEG, R = 360, 60, 220, 28  # 主轴中线、起点、每段长度、圆半径
for i, (year, title, desc, icon) in enumerate(EVENTS):
    role = SERIES[i % len(SERIES)]
    dk = d.t.deep(role)
    x = X0 + i * SEG
    cx = x + SEG / 2
    d.rect(x, AXIS_Y - 7, SEG, 14, dk)  # 轴段
    d.vertex('', f'ellipse;aspect=fixed;fillColor={d.t.bg};strokeColor=none;', cx - 6, AXIS_Y - 6, 12, 12)  # 轴上的白点
    up = i % 2 == 0
    cy = AXIS_Y - 190 if up else AXIS_Y + 190
    d.line(cx, AXIS_Y - 7 if up else AXIS_Y + 7, cx, cy + R if up else cy - R, color=dk, width=2)
    d.box(cx - R, cy - R, 2 * R, 2 * R, '', role='white', shape='circle', extra=f'fillColor={dk};strokeColor={dk};')
    d.icon(cx - 12, cy - 12, 24, icon, color=d.t.bg)
    ty = AXIS_Y - 140 if up else AXIS_Y + 30  # 文字块在圆和轴之间，放在连接线右侧
    d.text(cx + 14, ty, SEG - 30, 110,
           f'<b style="font-size:14px;color:{dk}">{year}</b><br><b>{title}</b><br>'
           f'<span style="font-size:11px;color:{d.t.muted}">{desc}</span>', size=13, valign='top', html=True)

d.footer(60, AXIS_Y + 260, '读图：从左到右是时间，轴的颜色区分阶段；圆形图标上下交替，文字在连接线右侧。')

name = os.path.join(HERE, 'timeline')
d.save(name + '.drawio')
d.export(name + '.drawio', name + '.png', scale=d.scale_for(MIN_SIDE))
